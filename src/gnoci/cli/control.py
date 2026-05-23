import click
import os
import numpy as np
import time
from gnoci.net_util.channel import Channel
from gnoci.servo import DummyServo


@click.command()
@click.option('--debug/--no-debug', default=False)
@click.option('--host', type=str, default=None)
@click.option('--port', type=int, default=8000)
@click.option('--freq', type=int, default=100)
def start(debug, host, port, freq):
    from gnoci.setup import setup_gnoci_control
    gnoci = setup_gnoci_control(freq=freq)
    channel = Channel(host=host, port=port)
    channel.serve(gnoci.handle_message)
    print("Gnoci control server started")


@click.command()
@click.option('--hz', type=int, default=100)
@click.option('--limit', type=int, default=1000)
def test_control_hz(hz: int, limit=1000):
    from gnoci.setup import setup_gnoci_control
    from gnoci.predict import PolicyRunner
    from gnoci.loop import Loop

    policy = PolicyRunner(obs_dim=10+4+6+2)
    gnoci = setup_gnoci_control(freq=hz)
    perf_times = []
    time.sleep(0.01)

    gnoci.sensor_reader.deinit()
    gnoci.servo_controller.deinit()
    
    for i in range(limit):
        start = time.perf_counter()
        gnoci.sensor_reader._read_hardware()
        policy.predict(np.ones(22))
        gnoci.servo_controller._write_servos()
        elapsed = time.perf_counter() - start
        perf_times.append(elapsed)
        print(f'Control HZ = {1.0 / elapsed}')

@click.command()
@click.option('--hz', type=int, default=100)
@click.option('--limit', type=int, default=None)
def control_loop(hz: int, limit=None):
    from gnoci.setup import setup_gnoci_control
    from gnoci.predict import PolicyRunner
    from gnoci.loop import Loop

    policy = PolicyRunner(obs_dim=10+4+6+2)
    gnoci = setup_gnoci_control(freq=hz)
    time.sleep(0.01)

    def _tick():
        time_start = time.perf_counter()
        state = gnoci.sense()
        action = policy.predict(state)
        gnoci.actuate([0]*10, delta=False)
        elapsed = time.perf_counter() - time_start
        if elapsed > 1.0 / hz:
            print(f"WARNING: tick overrun {elapsed*1000:.1f}ms")

    loop = Loop(hz=hz, func=_tick, limit=limit)
    loop.start()
    time.sleep(10)


@click.command()
@click.option('--hz', type=int, default=100)
def run_checks(hz: int):
    from gnoci.setup import setup_gnoci_control
    from gnoci.predict import PolicyRunner
    policy_runner = PolicyRunner(obs_dim=10+4+6+2)
    times = []
    for i in range(100):
        time_start = time.perf_counter()
        policy_runner.predict(np.ones(22))
        time_end = time.perf_counter()
        times.append(time_end - time_start)
    
    print(f'Average time taken: {np.mean(times)} seconds')
    print(f'Standard deviation: {np.std(times)} seconds')
    print(f'Minimum time taken: {np.min(times)} seconds')
    print(f'Maximum time taken: {np.max(times)} seconds')

    gnoci = setup_gnoci_control(freq=hz)

    for servo in gnoci.servo_controller.servos:
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


    # TODO: run hardware checks
