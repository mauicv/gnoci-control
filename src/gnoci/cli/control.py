import click
import os
import numpy as np
import time
from gnoci.net_util.channel import Channel


@click.command()
@click.option('--debug/--no-debug', default=False)
@click.option('--host', type=str, default=None)
@click.option('--port', type=int, default=8000)
@click.option('--update-interval', type=float, default=0.01)
def start(debug, host, port, update_interval):
    from gnoci.setup import setup_gnoci_control
    gnoci = setup_gnoci_control(update_interval=update_interval)
    channel = Channel(host=host, port=port)
    channel.serve(gnoci.handle_message)
    print("Gnoci control server started")


@click.command()
@click.option('--hz', type=int, default=100)
def control_loop(hz: int):
    from gnoci.setup import setup_gnoci_control
    from gnoci.predict import PolicyRunner
    policy = PolicyRunner(obs_dim=10+4+6+2)
    gnoci = setup_gnoci_control(freq=hz)


    def _tick(self):
        start = time.perf_counter()

        state = gnoci.sense()
        action = policy.predict(state)
        gnoci.actuate(action, delta=True)

        elapsed = time.perf_counter() - start
        if elapsed > 1.0 / self.loop.interval:
            print(f"WARNING: tick overrun {elapsed*1000:.1f}ms")

    loop = Loop(hz=hz, func=_tick)
    loop.start()


@click.command()
def run_checks():
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