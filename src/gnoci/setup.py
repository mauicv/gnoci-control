import time
from gnoci.servo import Servo, DummyServo
import smbus2 as smbus
from gnoci.hardware import SensorReader
from gnoci.hardware import ServoController
from gnoci.predict import PolicyRunner
from gnoci.loop import Loop
from gnoci.memory import Memory


class Gnoci:
    def __init__(self, bus: smbus.SMBus, freq: int = 100, kp: float = 0.08, ki: float = 0.0, kd: float = 0.005):
        self.freq = freq
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.bus = bus
        self.policy = PolicyRunner(obs_dim=10+4+6+2)
        self.servo_controller = ServoController(bus=self.bus, freq=self.freq, kp=self.kp, ki=self.ki, kd=self.kd)
        self.sensor_reader = SensorReader(bus=self.bus, freq=self.freq)
        self.memory = Memory(num_states=3, num_actions=2, action_dim=10, state_dim=10+4+6+2)
        time.sleep(0.01)


def setup_gnoci_control(
    bus: smbus.SMBus,
    freq: int = 100,
    kp: float = 0.08,
    ki: float = 0.0,
    kd: float = 0.005,
):
    return Gnoci(bus=bus, freq=freq, kp=kp, ki=ki, kd=kd)
