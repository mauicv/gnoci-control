import click
import os
import numpy as np
import time
from gnoci.servo import DummyServo

def display(elapsed, imu_data, rot_enc_data, adc_data, flush=True):
    ax, ay, az, gx, gy, gz = imu_data
    imu_line = f"  IMU  | ax:{ax:+7.3f} ay:{ay:+7.3f} az:{az:+7.3f} gx:{gx:+7.1f} gy:{gy:+7.1f} gz:{gz:+7.1f}"
    rot_line = f"  ROT  | " + " ".join(f"{v:5.3f}" if v is not None else "  N/A" for v in rot_enc_data)
    adc_line = f"  ADC  | " + " ".join(f"{'ON' if v else 'OFF':>5}" if v is not None else "  N/A" for v in adc_data)
    if elapsed is not None:
        hz_line = f"  TIME | {elapsed:.1f}ms ({1000/elapsed:.0f} Hz)"
    else:
        hz_line = "  TIME | N/A"

    print(f"\033[4A{imu_line:<80}\n{rot_line:<80}\n{adc_line:<80}\n{hz_line:<80}", flush=flush)
    if not flush:
        print("\n\n\n\n")
        print('Press Enter to continue...')
        input()
        print("\n\n\n\n")

@click.command()
@click.option('--hz', type=int, default=100)
@click.option('--limit', type=int, default=1000)
def test_control_hz(hz: int, limit=1000):
    from gnoci.setup import setup_gnoci_control
    from gnoci.predict import PolicyRunner
    from gnoci.loop import Loop

    servo_controller, sensor_reader, policy = setup_gnoci_control(freq=hz)
    perf_times = []
    time.sleep(0.01)

    sensor_reader.deinit()
    servo_controller.deinit()

    print("\n\n\n\n")
    
    for i in range(limit):
        start = time.perf_counter()
        sensor_reader._read_hardware()
        policy.predict(np.ones(22))
        servo_controller.update_setpoint_delta([0]*10)
        elapsed = time.perf_counter() - start
        perf_times.append(elapsed)

        display(elapsed, sensor_reader.imu_data, sensor_reader.rot_enc_data, sensor_reader.adc_data)

    print("\n\n\n\n")
    print(f'Average time taken: {np.mean(perf_times)} seconds')
    print(f'Standard deviation: {np.std(perf_times)} seconds')
    print(f'Minimum time taken: {np.min(perf_times)} seconds')
    print(f'Maximum time taken: {np.max(perf_times)} seconds')


@click.command()
@click.option('--hz', type=int, default=100)
def run_checks(hz: int):
    from gnoci.setup import setup_gnoci_control
    servo_controller, sensor_reader, policy = setup_gnoci_control(freq=hz)

    for servo in gnoci.servo_controller.servos:
        if isinstance(servo, DummyServo):
            continue
        print(f'range test servo: {servo.name}:')
        servo_initial_value = servo.value
        for value in np.linspace(-1, 1, 10):
            servo.update_setpoint(value)
            time.sleep(0.1)
            display(
                elapsed=None,
                imu_data=sensor_reader.imu_data,
                rot_enc_data=sensor_reader.rot_enc_data,
                adc_data=sensor_reader.adc_data
            )
        servo.update_setpoint(servo_initial_value)
        time.sleep(0.01)
        print(f'value: {servo_initial_value}, pwm: {servo.get_pwm()}')



@click.command()
@click.option('--hz', type=int, default=100)
@click.option('--joint-name', type=str, default=None)
def measure_positions(hz: int, joint_name: str):
    from gnoci.setup import setup_gnoci_control
    servo_controller, sensor_reader, policy = setup_gnoci_control(freq=hz)

    for servo in gnoci.servo_controller.servos:
        if servo.name != joint_name:
            continue
        print(f'range test servo: {servo.name}:')
        servo.update_setpoint(0.0)
        display(
            elapsed=None,
            imu_data=sensor_reader.imu_data,
            rot_enc_data=sensor_reader.rot_enc_data,
            adc_data=sensor_reader.adc_data
            flush=False
        )

        servo.update_setpoint(-1)
        display(
            elapsed=None,
            imu_data=sensor_reader.imu_data,
            rot_enc_data=sensor_reader.rot_enc_data,
            adc_data=sensor_reader.adc_data
            flush=False
        )

        servo.update_setpoint(1)
        display(
            elapsed=None,
            imu_data=sensor_reader.imu_data,
            rot_enc_data=sensor_reader.rot_enc_data,
            adc_data=sensor_reader.adc_data
            flush=False
        )
