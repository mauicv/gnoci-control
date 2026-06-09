import smbus2 as smbus
import time
import struct
import math
import threading as th

IMU_ADDR = 0x68
I2C_MUX_ADDR_1 = 0x70
I2C_MUX_ADDR_2 = 0x71
ROT_ENC_ADDR = 0x36
A2D_ADDR = 0x49
PWM_MUX_ADDR = 0x40
PCA9685_LED0 = 0x06
NUM_SERVOS = 10

IMU_GYRO_SCALE = 250.0  # rad/s — clips to [-1, 1] at this angular velocity (1 is 250 deg/s)
IMU_ACC_SCALE  = 1.0 # m/s² (2g) — clips to [-1, 1] at 2g

bus_lock = th.Lock()

device_map = {
    I2C_MUX_ADDR_1: {
        "rot_encs": [0, 1, 4, 6, 7],
        "adcs": [2, 3],
    },
    I2C_MUX_ADDR_2: {
        "rot_encs": [2, 3, 4, 5, 7],
        "adcs": [0, 1],
    },
}

def init_pca9685(bus, addr=PWM_MUX_ADDR, freq=50):
    bus.write_byte_data(addr, 0x00, 0x10)  # sleep
    prescale = round(25_000_000 / (4096 * freq)) - 1
    bus.write_byte_data(addr, 0xFE, prescale)
    bus.write_byte_data(addr, 0x00, 0x20)  # wake + auto-increment
    time.sleep(0.005)  # oscillator settle

def init_mpu6050(bus, addr=IMU_ADDR):
    # Write 0 to PWR_MGMT_1 register (0x6B) to wake up
    bus.write_byte_data(addr, 0x6B, 0x00)
    time.sleep(0.1)  # settle

def init_adc(bus, addr=A2D_ADDR, channel=0):
    mux = (0x04 + channel) << 12
    config = mux | 0x0200 | 0x0060 | 0x0000 | 0x0003  # no 0x8000, continuous
    bus.write_i2c_block_data(addr, 0x01, [(config >> 8) & 0xFF, config & 0xFF])

def init_adcs(bus):
    for mux_addr in [0x70, 0x71]:
        for i in device_map[mux_addr]["adcs"]:
            bus.write_byte(mux_addr, 1 << i)
            init_adc(bus, A2D_ADDR, channel=0)
        bus.write_byte(mux_addr, 0)


def _read(bus, addr, reg, data_len):
    try:
        return bus.read_i2c_block_data(addr, reg, data_len)
    except IOError as e:
        # print(f"Error reading device from {addr}: {e}")
        return None

def read_muxes(bus):
    rot_enc_data = []
    adc_data = []
    for mux_addr in [0x70, 0x71]:
        for i in device_map[mux_addr]["rot_encs"]:
            bus.write_byte(mux_addr, 1 << i)
            dev_data = _read(bus, ROT_ENC_ADDR, 0x0C, 2)
            rot_enc_data.append(dev_data)

        for i in device_map[mux_addr]["adcs"]:
            bus.write_byte(mux_addr, 1 << i)
            dev_data = _read(bus, A2D_ADDR, 0x00, 2)
            adc_data.append(dev_data)
        bus.write_byte(mux_addr, 0)
    return rot_enc_data, adc_data

def write_servos(bus, data, freq):
    period_us = 1_000_000 / freq
    ticks_per_us = 4096 / period_us
    byte_data = []
    for pwm_us in data:
        on = 0
        off = min(4095, round(pwm_us * ticks_per_us))
        byte_data += [on & 0xFF, on >> 8, off & 0xFF, off >> 8]
    chunk = 32  # 8 channels * 4 bytes
    with bus_lock:
        for i in range(0, len(byte_data), chunk):
            reg = PCA9685_LED0 + (i // 4) * 4
            bus.write_i2c_block_data(PWM_MUX_ADDR, reg, byte_data[i:i + chunk])

def read_sensor_data(bus):
    with bus_lock:
        imu_data = bus.read_i2c_block_data(IMU_ADDR, 0x3B, 14)
        rot_enc_data, adc_data = read_muxes(bus)
    return imu_data, rot_enc_data, adc_data

def decode_imu(raw):
    vals = []
    for i in range(0, 14, 2):
        val = struct.unpack('>h', bytes(raw[i:i+2]))[0]
        vals.append(val)
    # vals = [ax, ay, az, temp, gx, gy, gz]
    ax, ay, az = [v / (16384.0) for v in vals[0:3]]  # ±2g default
    gx, gy, gz = [v / (131.0) for v in vals[4:7]]   # ±250°/s default (1 is 250 deg/s)
    return gx, gy, gz, ax, ay, az

def decode_angle(raw):
    if raw is None:
        return None
    return (((raw[0] & 0x0F) << 8) | raw[1]) / 4095 * 2 - 1  # -1 to 1

def decode_foot_contact(raw):
    if raw is None:
        return None
    value = struct.unpack('>h', bytes(raw))[0]
    return value > 1000  # tune this threshold


def test_rot_encs(bus):
    for mux_addr in [I2C_MUX_ADDR_1, I2C_MUX_ADDR_2]:
        for channel in device_map[mux_addr]["rot_encs"]:
            try:
                bus.write_byte(mux_addr, 1 << channel)
                status = bus.read_i2c_block_data(ROT_ENC_ADDR, 0x0B, 1)[0]
                magnet_high = (status >> 3) & 1
                magnet_low = (status >> 4) & 1
                magnet_detected = (status >> 5) & 1
                print(f"{mux_addr:02x}:{channel:02x}: detected: {magnet_detected}, too strong: {magnet_high}, too weak: {magnet_low}")
            except IOError as e:
                print(f"{mux_addr:02x}:{channel:02x}: error: {e}")
        bus.write_byte(mux_addr, 0)


def test_adcs(bus):
    for mux_addr in [I2C_MUX_ADDR_1, I2C_MUX_ADDR_2]:
        for channel in device_map[mux_addr]["adcs"]:
            bus.write_byte(mux_addr, 1 << channel)
            dev_data = _read(bus, A2D_ADDR, 0x00, 2)
            print(f"{mux_addr:02x}:{channel:02x}: {dev_data}")
        bus.write_byte(mux_addr, 0)


def test_mpu6050(bus):
    bus.write_byte_data(IMU_ADDR, 0x6B, 0x00)
    time.sleep(0.1)
    imu_data = bus.read_i2c_block_data(IMU_ADDR, 0x3B, 14)
    print(f"IMU: {imu_data}")
    ax, ay, az, gx, gy, gz = decode_imu(imu_data)
    print(f"ax: {ax}, ay: {ay}, az: {az}, gx: {gx}, gy: {gy}, gz: {gz}")


def test_all(bus):
    test_rot_encs(bus)
    test_adcs(bus)
    test_mpu6050(bus)


if __name__ == "__main__":
    import os
    bus = smbus.SMBus(1)
    test_rot_encs(bus)    
    init_pca9685(bus, PWM_MUX_ADDR, freq=50)
    init_mpu6050(bus, IMU_ADDR)
    init_adcs(bus)

    def display(elapsed, imu_data, rot_enc_data, adc_data):
        ax, ay, az, gx, gy, gz = imu_data
        imu_line = f"  IMU  | ax:{ax:+7.3f} ay:{ay:+7.3f} az:{az:+7.3f} gx:{gx:+7.1f} gy:{gy:+7.1f} gz:{gz:+7.1f}"
        rot_line = f"  ROT  | " + " ".join(f"{v:5.3f}" if v is not None else "  N/A" for v in rot_enc_data)
        adc_line = f"  ADC  | " + " ".join(f"{'ON' if v else 'OFF':>5}" if v is not None else "  N/A" for v in adc_data)
        hz_line = f"  TIME | {elapsed:.1f}ms ({1000/elapsed:.0f} Hz)"

        print(f"\033[4A{imu_line:<80}\n{rot_line:<80}\n{adc_line:<80}\n{hz_line:<80}", flush=True)

    # Print initial blank lines for the cursor to overwrite
    print("\n\n\n\n")

    while True:
        start = time.perf_counter()
        imu_raw, rot_enc_data, adc_data = read_sensor_data()
        elapsed = (time.perf_counter() - start) * 1000

        imu_data = decode_imu(imu_raw)
        rot_enc_data = [decode_angle(item) for item in rot_enc_data]
        adc_data = [decode_foot_contact(item) for item in adc_data]

        display(elapsed, imu_data, rot_enc_data, adc_data)
        time.sleep(0.1)
