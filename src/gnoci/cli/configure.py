import click
import os
import numpy as np
import time
from gnoci.servo import DummyServo
from gnoci.config import MODEL_INPUT_DIM, CONTROL_HZ
import json
from tqdm import tqdm

_has_i2c = os.path.exists('/dev/i2c-1')
if _has_i2c:
    print("using smbus")
    from smbus2 import SMBus
else:
    print("using mocked bus")
    from gnoci.hardware.mock_bus import MockedBus as SMBus


def display(elapsed, imu_data, rot_enc_data, adc_data, flush=True):
    gx, gy, gz, ax, ay, az = imu_data
    imu_line = f"  IMU  | ax:{ax:+7.3f} ay:{ay:+7.3f} az:{az:+7.3f} gx:{gx:+7.1f} gy:{gy:+7.1f} gz:{gz:+7.1f}"
    rot_line = f"  ROT  | " + " ".join(f"{v:5.3f}" if v is not None else "  N/A" for v in rot_enc_data)
    adc_line = f"  ADC  | " + " ".join(f"{'ON' if v else 'OFF':>5}" if v is not None else "  N/A" for v in adc_data)
    if elapsed is not None:
        hz_line = f"  TIME | {elapsed:.1f}ms ({1/elapsed:.0f} Hz)"
    else:
        hz_line = "  TIME | N/A"

    print(f"\033[4A{imu_line:<80}\n{rot_line:<80}\n{adc_line:<80}\n{hz_line:<80}", flush=flush)
    if not flush:
        print("\n\n\n\n")
        print('Press Enter to continue...')
        input()
        print("\n\n\n\n")


@click.command()
@click.option('--limit', type=int, default=1000)
def test_control_hz(limit=1000):
    from gnoci.setup import setup_gnoci_control
    from gnoci.predict import PolicyRunner
    from gnoci.loop import Loop

    bus = SMBus(1)
    gnoci = setup_gnoci_control(bus=bus)
    total_drift, average_drift = gnoci.configure_sensors()
    print(f"Total sensor drift: {total_drift:.3f}, Average sensor drift: {average_drift:.3f}")

    servo_controller = gnoci.servo_controller
    sensor_reader = gnoci.sensor_reader
    policy = gnoci.policy
    perf_times = []
    time.sleep(0.01)

    sensor_reader.deinit()
    servo_controller.deinit()

    print("\n\n\n\n")
    servo_controller.update_value([0]*10)

    for i in range(limit):
        start = time.perf_counter()
        sensor_reader._read_hardware()
        sensor_reader.decode_hardware()
        policy.predict(np.ones(MODEL_INPUT_DIM))
        servo_controller._write_servos()
        elapsed = (time.perf_counter() - start)
        perf_times.append(elapsed)

        display(elapsed, sensor_reader.imu_data, sensor_reader.rot_enc_data, sensor_reader.adc_data)

    print("\n\n\n\n")
    print(f'Average time taken: {np.mean(perf_times)} seconds')
    print(f'Standard deviation: {np.std(perf_times)} seconds')
    print(f'Minimum time taken: {np.min(perf_times)} seconds')
    print(f'Maximum time taken: {np.max(perf_times)} seconds')


@click.command()
@click.option('--limit', type=int, default=10000)
def test_imu(limit=10000):
    ctl_hz = 10
    from gnoci.setup import setup_gnoci_control

    bus = SMBus(1)
    gnoci = setup_gnoci_control(bus=bus, without_servos=True)
    servo_controller = gnoci.servo_controller
    sensor_reader = gnoci.sensor_reader
    policy = gnoci.policy
    perf_times = []
    time.sleep(0.01)

    for i in range(100000):
        data = sensor_reader.data
        pitch, roll = data[-2:]
        print(f"pitch: {pitch:5.3f}, roll: {roll:5.3f}")
        time.sleep(0.01)


@click.command()
def run_checks():
    from gnoci.setup import setup_gnoci_control
    bus = SMBus(1)
    gnoci = setup_gnoci_control(bus=bus)
    servo_controller = gnoci.servo_controller
    sensor_reader = gnoci.sensor_reader
    policy = gnoci.policy

    for servo in servo_controller.servos:
        if isinstance(servo, DummyServo):
            continue
        print(f'range test servo: {servo.name}:')
        servo_initial_value = servo.value
        for value in np.linspace(-1, 1, 10):
            servo.update_value(value)
            time.sleep(0.1)
        servo.update_value(servo_initial_value)
        time.sleep(0.01)
        print(f'value: {servo_initial_value}, pwm: {servo.get_pwm()}')


def detect_joint_range(servo, sensor_reader, joint_name: str):
    r_d = []
    servo.update_value(0.0)
    time.sleep(1)
    sensor_reader._read_hardware()
    sensor_reader.decode_hardware()
    r_d.append(sensor_reader.rot_enc_data)
    time.sleep(1)

    servo.update_value(-1)
    time.sleep(1)
    sensor_reader._read_hardware()
    sensor_reader.decode_hardware()
    r_d.append(sensor_reader.rot_enc_data)
    time.sleep(1)

    servo.update_value(1)
    time.sleep(1)
    sensor_reader._read_hardware()
    sensor_reader.decode_hardware()
    r_d.append(sensor_reader.rot_enc_data)
    time.sleep(1)

    servo.update_value(0.0)
    time.sleep(1)

    max_diff = 0
    for i,(a,b,c) in enumerate(zip(r_d[0], r_d[1], r_d[2])):
        diff = abs(b - c)
        if diff > max_diff:
            max_diff = diff
            max_diff_index = i

    print(f'Detected {joint_name} at index {max_diff_index}')
    center, lo, hi = r_d[0][max_diff_index], r_d[1][max_diff_index], r_d[2][max_diff_index]
    print(f'center: {center:5.3f}, lo: {lo:5.3f}, hi: {hi:5.3f}')
    print(f'lo - center: {lo - center:5.3f}, center - hi: {center - hi:5.3f}')
    print(f'range: {hi - lo:5.3f}')

    return max_diff_index, center, lo, hi


@click.command()
@click.option('--joint-name', type=str, default=None)
@click.option('--file-name', type=str, default='positioning_data.json')
@click.option('--center-angles', type=bool, default=False)
def measure_positions(joint_name: str, file_name: str, center_angles: bool):
    from gnoci.setup import setup_gnoci_control
    bus = SMBus(1)
    gnoci = setup_gnoci_control(bus=bus, center_angles=center_angles)

    count = 0
    positioning_data = []
    for servo in gnoci.servo_controller.iter_servos():
        if isinstance(servo, DummyServo):
            continue
        if joint_name is not None and servo.name != joint_name:
            continue
        print(f'range test servo: {servo.name}:')
        index, center, lo, hi = detect_joint_range(servo, gnoci.sensor_reader, joint_name)
        positioning_data.append({
            "name": servo.name,
            "return_index": count,
            "index": index,
            "center": center,
            "lo": lo,
            "hi": hi,
            "range": hi - lo,
        })
        count += 1
    with open(file_name, 'w') as f:
        json.dump(positioning_data, f, indent=4)


@click.command()
def test_hardware():
    from gnoci.hardware.hardware import (
        init_mpu6050,
        init_adcs,
        test_all
    )
    bus = SMBus(1)
    init_mpu6050(bus)
    init_adcs(bus)
    time.sleep(0.01)
    test_all(bus)


def compute_major_change(state: np.ndarray):
    gx, gy, gz, ax, ay, az = state[24], state[25], state[26], state[27], state[28], state[29]
    gyro_vector = np.array([gx, gy, gz])
    names = ["x", "y", "z"]
    directions = ["-", "+"]
    max_gyro = np.argmax(np.abs(gyro_vector))
    rotation_direction = int(np.sign(gyro_vector[max_gyro]) + 1) // 2

    accel_vector = np.array([ax, ay, az])
    max_accel = np.argmax(np.abs(accel_vector))
    accel_direction = int(np.sign(accel_vector[max_accel]) + 1) // 2

    print(f"gyro {names[max_gyro]} {directions[rotation_direction]} | accel {names[max_accel]} {directions[accel_direction]}", end="\r")


@click.command()
@click.option('--ctl-hz', type=int, default=CONTROL_HZ)
def stream_sensor_data(ctl_hz: int):
    from gnoci.setup import setup_gnoci_control
    from gnoci.net_util.channel import Channel
    channel = Channel(host='127.0.0.1', port=8000)
    bus = SMBus(1)
    gnoci = setup_gnoci_control(bus=bus, center_angles=True, control_hz=ctl_hz, without_servos=True)
    # gnoci.configure_sensors_from_file('positioning_data.json')
    channel.serve(lambda message: gnoci.sensor_reader.data.tolist())


@click.command()
@click.option('--overwrite', type=bool, default=False)
def measure_imu_offsets(overwrite: bool = False):
    from gnoci.hardware.hardware import init_mpu6050, read_sensor_data, decode_imu
    bus = SMBus(1)
    init_mpu6050(bus)
    time.sleep(0.01)

    gyro_data = []
    accel_data = []
    sample_rate = 60
    seconds = 3
    for _ in tqdm(range(sample_rate*seconds)):
        time_start = time.perf_counter()
        imu_data, *_ = read_sensor_data(bus)
        gx, gy, gz, ax, ay, az = decode_imu(imu_data)
        gyro_data.append([gx, gy, gz])
        accel_data.append([ax, ay, az])
        elapsed = time.perf_counter() - time_start
        if elapsed < 1.0 / sample_rate:
            time.sleep(1.0 / sample_rate - elapsed)

    gyro_data = np.array(gyro_data)
    accel_data = np.array(accel_data)
    gyro_mean = gyro_data.mean(axis=0)
    accel_mean = accel_data.mean(axis=0) - np.array([0.0, 0.0, 1.0])

    print(f"gyro mean: {gyro_mean}")
    print(f"accel mean: {accel_mean}")

    if overwrite:
        with open('imu_offsets.json', 'w') as f:
            json.dump({
                "gyro_mean": gyro_mean.tolist(),
                "accel_mean": accel_mean.tolist(),
            }, f, indent=4)