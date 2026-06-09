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
    servo_controller = gnoci.servo_controller
    sensor_reader = gnoci.sensor_reader
    policy = gnoci.policy
    perf_times = []
    time.sleep(0.01)

    sensor_reader.deinit()
    servo_controller.deinit()

    print("\n\n\n\n")
    servo_controller.update_setpoint([0]*10)

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
            servo.update_setpoint(value)
            time.sleep(0.1)
        servo.update_setpoint(servo_initial_value)
        time.sleep(0.01)
        print(f'value: {servo_initial_value}, pwm: {servo.get_pwm()}')


def detect_joint_range(servo, sensor_reader, joint_name: str):
    r_d = []
    servo.update_setpoint(0.0)
    time.sleep(1)
    sensor_reader._read_hardware()
    sensor_reader.decode_hardware()
    r_d.append(sensor_reader.rot_enc_data)
    time.sleep(1)

    servo.update_setpoint(-1)
    time.sleep(1)
    sensor_reader._read_hardware()
    sensor_reader.decode_hardware()
    r_d.append(sensor_reader.rot_enc_data)
    time.sleep(1)

    servo.update_setpoint(1)
    time.sleep(1)
    sensor_reader._read_hardware()
    sensor_reader.decode_hardware()
    r_d.append(sensor_reader.rot_enc_data)
    time.sleep(1)

    servo.update_setpoint(0.0)
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


def run_response_recording(gnoci, joint_name: str, file_name: str, ctl_hz: int, action: float):

    for servo in gnoci.servo_controller.iter_servos():
        if isinstance(servo, DummyServo):
            continue
        if joint_name is not None and servo.name != joint_name:
            continue
        print(f'recording response for servo: {servo.name}:')
        index = gnoci.sensor_reader.sensor_index_from_name(servo.name)

        

        response_data = {
            "joint_name": joint_name,
            "action": action,
            "angular_pos": [],
            "angular_vel": [],
            "time": [],
        }

        for i in range(100):
            time_start = time.perf_counter()
            servo.update_setpoint_delta(action)
            state = gnoci.sensor_reader.data

            response_data["angular_pos"].append(state[index])
            response_data["angular_vel"].append(state[index + 10])
            response_data["time"].append(time.perf_counter())

            elapsed = time.perf_counter() - time_start
            if elapsed < 1.0 / ctl_hz:
                time.sleep(1.0 / ctl_hz - elapsed)
            else:
                print(f"WARNING: tick overrun {elapsed*1000:.1f}ms")

        servo.update_setpoint(0)
        time.sleep(0.5)

    return response_data



@click.command()
@click.option('--file-name', type=str, default='response_data.json')
@click.option('--center-angles', type=bool, default=True)
@click.option('--ctl-hz', type=int, default=CONTROL_HZ)
@click.option('--configure-sensors', type=bool, default=True)
def measure_response(file_name: str, center_angles: bool, ctl_hz: int, configure_sensors: bool = True):
    from gnoci.setup import setup_gnoci_control
    bus = SMBus(1)
    gnoci = setup_gnoci_control(bus=bus, center_angles=center_angles, control_hz=ctl_hz)
    if configure_sensors:
        total_drift, average_drift = gnoci.configure_sensors()
        print(f"Total sensor drift: {total_drift:.3f}, Average sensor drift: {average_drift:.3f}")
    response_data = []
    for action in [-1, 1]:
        for joint_name in [
                "head__left_yoke",
                "left_yoke__hip",
                "left_hip__upper_leg",
                "left_upper_leg__lower_leg",
                "left_lower_leg__foot",
                "head__right_yoke",
                "right_yoke__hip",
                "right_hip__upper_leg",
                "right_upper_leg__lower_leg",
                "right_lower_leg__foot",
            ]:
            response_data.append(run_response_recording(gnoci, joint_name, file_name, ctl_hz, action))

    with open(file_name, 'w') as f:
        json.dump(response_data, f, indent=4)


@click.command()
@click.option('--file-name', type=str, default='state_data.json')
@click.option('--center-angles', type=bool, default=True)
@click.option('--ctl-hz', type=int, default=CONTROL_HZ)
@click.option('--configure-sensors', type=bool, default=True)
def record_states(file_name: str, center_angles: bool, ctl_hz: int, configure_sensors: bool = True):
    from gnoci.setup import setup_gnoci_control
    bus = SMBus(1)
    gnoci = setup_gnoci_control(bus=bus, center_angles=center_angles, control_hz=ctl_hz)
    if configure_sensors:
        total_drift, average_drift = gnoci.configure_sensors()
        print(f"Total sensor drift: {total_drift:.3f}, Average sensor drift: {average_drift:.3f}")

    state_data = {
        "states": [],
        "actions": [],
        "times": [],
    }

    for i in tqdm(range(500)):
        time_start = time.perf_counter()

        state = gnoci.sensor_reader.data
        gnoci.memory.add_state(state)
        observation = gnoci.memory.get_observation()
        action = gnoci.policy.predict(observation)


        action = np.zeros((10))
        action[1] = np.sin(i / 50 * 2 * np.pi) / 25
        action[6] = np.cos(i / 50 * 2 * np.pi) / 25

        state_data["states"].append(state)
        state_data["actions"].append(action.tolist())
        state_data["times"].append(time.perf_counter())

        gnoci.memory.add_action(action)
        gnoci.servo_controller.update_setpoint_delta(action)

        elapsed = time.perf_counter() - time_start
        if elapsed < 1.0 / ctl_hz:
            time.sleep(1.0 / ctl_hz - elapsed)

    with open(file_name, 'w') as f:
        json.dump(state_data, f, indent=4)


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
@click.option('--file-name', type=str, default='state_data.json')
@click.option('--ctl-hz', type=int, default=CONTROL_HZ)
@click.option('--configure-sensors', type=bool, default=True)
def orient(file_name: str, ctl_hz: int, configure_sensors: bool = True):
    from gnoci.setup import setup_gnoci_control
    bus = SMBus(1)
    gnoci = setup_gnoci_control(bus=bus, center_angles=True, control_hz=ctl_hz)
    if configure_sensors:
        total_drift, average_drift = gnoci.configure_sensors()
        print(f"Total sensor drift: {total_drift:.3f}, Average sensor drift: {average_drift:.3f}")

    action = np.zeros((10))
    gnoci.servo_controller.update_setpoint(action)
    while True:
        time_start = time.perf_counter()
        state = gnoci.sensor_reader.data
        compute_major_change(state)
        elapsed = time.perf_counter() - time_start
        if elapsed < 1.0 / ctl_hz:
            time.sleep(1.0 / ctl_hz - elapsed)

    # with open(file_name, 'w') as f:
    #     json.dump(state_data, f, indent=4)

