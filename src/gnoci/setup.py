import time
from gnoci.servo import Servo
import smbus2 as smbus
from gnoci.gnoci import Gnoci
from gnoci.hardware import SensorReader
from gnoci.hardware import ServoController


generic_values = {
    "kp": 0.08,
    "ki": 0.01,
    "kd": 0.005,
}

def setup_gnoci_control(
    update_interval: float = 0.01,
):
    servos: list[Servo] = [
        Servo(name="front_right_top", pin_id=0, pin=4, pin_limits=(-0.3, 0.9), init_value=-0.4, offset=0.0, **generic_values),
        Servo(name="front_right_bottom", pin_id=1, pin=18, pin_limits=(-0.9, 0.9), init_value=-0.4, offset=0.0, **generic_values),
        Servo(name="front_left_top", pin_id=2, pin=27, pin_limits=(-0.3, 0.9), init_value=-0.4, offset=0.1, reverse=True, **generic_values),
        Servo(name="front_left_bottom", pin_id=3, pin=10, pin_limits=(-0.9, 0.9), init_value=-0.4, offset=0.0, reverse=True, **generic_values),
        Servo(name="back_right_top", pin_id=4, pin=20, pin_limits=(-0.9, 0.2), init_value=-0.4, offset=0.0, **generic_values),
        Servo(name="back_right_bottom", pin_id=5, pin=19, pin_limits=(-0.9, 0.9), init_value=-0.4, offset=0.0, **generic_values),
        Servo(name="back_left_top", pin_id=6, pin=13, pin_limits=(-0.9, 0.2), init_value=-0.4, offset=-0.6, reverse=True, **generic_values),
        Servo(name="back_left_bottom", pin_id=7, pin=6, pin_limits=(-0.9, 0.9), init_value=-0.4, offset=0.0, reverse=True, **generic_values),
    ]

    bus = smbus.SMBus(1)

    servo_controller = ServoController(
        bus=bus,
        freq=update_interval,
        servos=servos,
    )
    sensor_reader = SensorReader(
        bus=bus,
        freq=update_interval,
    )
    gnoci = Gnoci(
        servo_controller=servo_controller,
        sensor_reader=sensor_reader,
    )
    return gnoci

