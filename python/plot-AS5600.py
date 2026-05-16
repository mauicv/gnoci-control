import socket
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dataclasses import dataclass, field
import numpy as np


@dataclass
class SensorDataArray:
    j1: list[float] = field(default_factory=list)
    j2: list[float] = field(default_factory=list)
    j3: list[float] = field(default_factory=list)

    def __post_init__(self):
        self.j1.append(0)
        self.j2.append(0)
        self.j3.append(0)

    def update(self, data: list[float]):
        j1, j2, j3 = data
        self.j1.append(j1)
        self.j2.append(j2)
        self.j3.append(j3)

    def get_data(self, limit=100):
        return (
            self.j1[-limit:],
            self.j2[-limit:],
            self.j3[-limit:],
        )


def plot_base_sense_readings(client: socket.socket):
    fig, axs = plt.subplots(ncols=3)
    xs = np.arange(100)
    init_ys = np.zeros(100)
    sensor_data = SensorDataArray(
        j1=init_ys.tolist(),
        j2=init_ys.tolist(),
        j3=init_ys.tolist(),
    )

    j1_plot, = axs[0].plot(xs, init_ys)
    j2_plot, = axs[1].plot(xs, init_ys)
    j3_plot, = axs[2].plot(xs, init_ys)
    axs[0].set_title("Joint 1")
    axs[1].set_title("Joint 2")
    axs[2].set_title("Joint 3")

    axs[0].set_ylim(0, 4)
    axs[1].set_ylim(0, 4)
    axs[2].set_ylim(0, 4)

    def animate(i, client, sensor_data: SensorDataArray):
        data = client.get_data()
        # print(data)
        sensor_data.update(data[5:8])
        # sensor_data.update(data[:3])
        j1, j2, j3 = sensor_data.get_data()
        j1_plot.set_ydata(j1)
        j2_plot.set_ydata(j2)
        j3_plot.set_ydata(j3)

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
        array = data.decode('utf-8').split(' ')
        return [float(x) for x in array]
    
    def close(self):
        self.s.close()

client = Client('192.168.1.180', 8000)

plot_base_sense_readings(client)

client.close()
