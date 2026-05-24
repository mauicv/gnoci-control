import time
from gnoci.servo import Servo, DummyServo
import smbus2 as smbus
from gnoci.hardware import SensorReader
from gnoci.hardware import ServoController
from gnoci.predict import PolicyRunner
from gnoci.loop import Loop


def setup_gnoci_control(
    freq: int = 100,
    kp: float = 0.08,
    ki: float = 0.0,
    kd: float = 0.005,
):
    bus = smbus.SMBus(1)
    policy = PolicyRunner(
        obs_dim=10+4+6+2
    )

    servo_controller = ServoController(
        bus=bus,
        freq=freq,
        kp=kp,
        ki=ki,
        kd=kd,
    )

    sensor_reader = SensorReader(
        bus=bus,
        freq=freq,
    )

    time.sleep(0.01)

    return servo_controller, sensor_reader, policy
