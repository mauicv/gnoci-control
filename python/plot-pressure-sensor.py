import socket
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dataclasses import dataclass, field
import numpy as np


@dataclass
class SensorDataArray:
    p1: list[float] = field(default_factory=list)

    def __post_init__(self):
        self.p1.append(0)

    def update(self, data: float):
        self.p1.append(data)

    def get_data(self, limit=100):
        return (
            self.p1[-limit:],
        )


def plot_base_sense_readings(client: socket.socket):
    fig, ax = plt.subplots()
    xs = np.arange(100)
    init_ys = np.zeros(100)
    sensor_data = SensorDataArray(
        p1=init_ys.tolist(),
    )

    p1_plot, = ax.plot(xs, init_ys)

    ax.set_ylim(-0.2, 5)

    def animate(i, client, sensor_data: SensorDataArray):
        data = client.get_data()
        data = data[0]
        sensor_data.update(data)
        p1 = sensor_data.get_data()
        p1_plot.set_ydata(p1)

    ani = animation.FuncAnimation(fig, animate, fargs=(client, sensor_data, ), interval=5)
    plt.show()


class Client:
    def __init__(self, host: str, port: int):
        self.s = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )
        self.s.connect((host, port))

    def get_data(self):
        data = self.s.sendall(b'-')
        data = self.s.recv(1024)
        print(data)
        return [float(data.decode('utf-8'))]
    
    def close(self):
        self.s.close()

client = Client('192.168.1.180', 8000)

plot_base_sense_readings(client)
client.close()
