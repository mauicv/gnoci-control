import click
from collections import deque
from gnoci.config import CONTROL_HZ
import matplotlib.pyplot as plt
import matplotlib.animation as animation


@click.command()
@click.option('--refresh-hz', type=int, default=10)
@click.option('--window', type=int, default=200)
def recieve_sensor_data(refresh_hz: int, window: int):
    from gnoci.net_util.client import Client
    client = Client(host='127.0.0.1', port=8000)
    client.connect()

    xs = deque(maxlen=window)
    pitches = deque(maxlen=window)
    rolls = deque(maxlen=window)

    fig, ax = plt.subplots()
    pitch_line, = ax.plot([], [], label='pitch')
    roll_line, = ax.plot([], [], label='roll')
    ax.set_ylim(-3.2, 3.2)          # radians; use -180/180 if degrees
    ax.set_xlabel('sample')
    ax.legend(loc='upper right')

    def update(frame):
        pitch, roll = client.send_data({})[-2:]
        xs.append(frame)
        pitches.append(pitch)
        rolls.append(roll)
        pitch_line.set_data(xs, pitches)
        roll_line.set_data(xs, rolls)
        ax.set_xlim(max(0, frame - window), max(window, frame))
        return pitch_line, roll_line

    ani = animation.FuncAnimation(
        fig, update,
        interval=1000 / refresh_hz,
        blit=False,
        cache_frame_data=False,
    )
    plt.show()