import click
import os
import numpy as np
import time
from gnoci.net_util.channel import Channel

_has_i2c = os.path.exists('/dev/i2c-1')
if _has_i2c:
    print("using smbus")
    from smbus2 import SMBus
else:
    print("using mocked bus")
    from gnoci.hardware.mock_bus import MockedBus as SMBus



@click.command()
@click.option('--debug/--no-debug', default=False)
@click.option('--host', type=str, default=None)
@click.option('--port', type=int, default=8000)
@click.option('--freq', type=int, default=100)
def start(debug, host, port, freq):
    pass
    # channel = Channel(host=host, port=port)
    # channel.serve(gnoci.handle_message)
    # print("Gnoci control server started")


@click.command()
@click.option('--hw-hz', type=int, default=100)
@click.option('--ctl-hz', type=int, default=80)
@click.option('--limit', type=int, default=None)
@click.option('--kp', type=float, default=0.08)
@click.option('--ki', type=float, default=0.0)
@click.option('--kd', type=float, default=0.005)
def control_loop(hw_hz: int, ctl_hz: int, limit=None, kp=0.08, ki=0.0, kd=0.005):
    from gnoci.setup import setup_gnoci_control
    from gnoci.predict import PolicyRunner
    from gnoci.loop import Loop

    bus = SMBus(1)
    gnoci = setup_gnoci_control(bus=bus, freq=hw_hz, kp=kp, ki=ki, kd=kd)

    def _tick():
        time_start = time.perf_counter()

        state = gnoci.sensor_reader.data
        action = gnoci.policy.predict(state)
        gnoci.servo_controller.update_setpoint_delta(action[0])

        elapsed = time.perf_counter() - time_start
        if elapsed > 1.0 / ctl_hz:
            print(f"WARNING: tick overrun {elapsed*1000:.1f}ms")

    loop = Loop(hz=ctl_hz, func=_tick, limit=limit)
    loop.start()
    time.sleep(10)
