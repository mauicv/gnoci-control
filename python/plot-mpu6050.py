import socket
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dataclasses import dataclass, field
import numpy as np


@dataclass
class SensorDataArray:
    acc_xs: list[float] = field(default_factory=list)
    acc_ys: list[float] = field(default_factory=list)
    acc_zs: list[float] = field(default_factory=list)

    def __post_init__(self):
        self.acc_xs.append(0)
        self.acc_ys.append(0)
        self.acc_zs.append(0)

    def update(self, data: list[float]):
        acc_x, acc_y, acc_z = data[0:3]
        self.acc_xs.append(acc_x)
        self.acc_ys.append(acc_y)
        self.acc_zs.append(acc_z)

    def get_data(self, limit=100):
        return (
            self.acc_xs[-limit:],
            self.acc_ys[-limit:],
            self.acc_zs[-limit:],
        )


def plot_base_sense_readings(client: socket.socket):
    fig, axs = plt.subplots(ncols=3)
    xs = np.arange(100)
    init_ys = np.zeros(100)
    sensor_data = SensorDataArray(
        acc_xs=init_ys.tolist(),
        acc_ys=init_ys.tolist(),
        acc_zs=init_ys.tolist(),
    )

    acc_xs_plot, = axs[0].plot(xs, init_ys)
    acc_ys_plot, = axs[1].plot(xs, init_ys)
    acc_zs_plot, = axs[2].plot(xs, init_ys)
    axs[0].set_title("Side Accelerometer")
    axs[1].set_title("Forward Accelerometer")
    axs[2].set_title("Up Accelerometer")

    axs[0].set_ylim(-2, 2)
    axs[1].set_ylim(-2, 2)
    axs[2].set_ylim(-2, 2)

    def animate(i, client, sensor_data: SensorDataArray):
        data = client.get_data()
        sensor_data.update(data)
        acc_xs, acc_ys, acc_zs = sensor_data.get_data()
        acc_xs_plot.set_ydata(acc_xs)
        acc_ys_plot.set_ydata(acc_ys)
        acc_zs_plot.set_ydata(acc_zs)

    ani = animation.FuncAnimation(fig, animate, fargs=(client, sensor_data, ), interval=25)
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
