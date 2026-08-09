import click
import os
import numpy as np
import time
from gnoci.net_util.channel import Channel
from gnoci.config import CONTROL_HZ, ACTION_SCALE

_has_i2c = os.path.exists('/dev/i2c-1')
if _has_i2c:
    print("using smbus")
    from smbus2 import SMBus
else:
    print("using mocked bus")
    from gnoci.hardware.mock_bus import MockedBus as SMBus


@click.command()
@click.option('--host', type=str, default=None)
@click.option('--port', type=int, default=8000)
@click.option('--ctl-hz', type=int, default=CONTROL_HZ)
@click.option('--limit', type=int, default=None)
@click.option('--configure-sensors', type=bool, default=True)
def start(host, port, ctl_hz: int, limit=None, configure_sensors: bool = True):
    from gnoci.setup import setup_gnoci_control
    from gnoci.predict import PolicyRunner
    from gnoci.loop import Loop

    bus = SMBus(1)
    gnoci = setup_gnoci_control(bus=bus, control_hz=ctl_hz)
    if configure_sensors:
        total_drift, average_drift = gnoci.configure_sensors()
        print(f"Total sensor drift: {total_drift:.3f}, Average sensor drift: {average_drift:.3f}")

    actions = []
    states = []

    def _tick():
        time_start = time.perf_counter()

        state = gnoci.sensor_reader.data
        gnoci.memory.add_state(state)
        observation = gnoci.memory.get_observation()
        action = gnoci.policy.predict(observation)
        gnoci.memory.add_action(action)
        action = action * 0.2
        action = action * ACTION_SCALE
        gnoci.servo_controller.update_value(action)
        actions.append(action.tolist())
        states.append(state.tolist())

        elapsed = time.perf_counter() - time_start
        if elapsed > 1.0 / ctl_hz:
            print(f"WARNING: tick overrun {elapsed*1000:.1f}ms")

    loop = Loop(hz=ctl_hz, func=_tick, limit=limit)
    loop.start()
    time.sleep(3)

    import json
    with open('rollout.json', 'w') as f:
        json.dump({
            'actions': actions,
            'states': states,
        }, f)
