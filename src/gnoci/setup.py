import time
from gnoci.servo import Servo, DummyServo
import smbus2 as smbus
from gnoci.gnoci import Gnoci
from gnoci.hardware import SensorReader
from gnoci.hardware import ServoController


def setup_gnoci_control(
    freq: int = 100,
    kp: float = 0.08,
    ki: float = 0.0,
    kd: float = 0.005,
):
    generic_values = {
        "kp": kp,
        "ki": ki,
        "kd": kd,
        "freq": freq,
    }

    # TODO: asymetric in left_yoke__hip and right_yoke__hip reverse-True/False?

    servos: list[Servo] = [
        Servo(name="left_lower_leg__foot",          pin_limits=(-0.5, 0.5), init_value=0.0, offset=-0.3, reverse=False, **generic_values),
        DummyServo(),
        Servo(name="left_hip__upper_leg",           pin_limits=(-0.6, 0.4), init_value=0.0, offset=-0.3, reverse=True, **generic_values),
        Servo(name="left_upper_leg__lower_leg",     pin_limits=(-0.5, 0.5), init_value=0.0, offset=0.6, reverse=True, **generic_values),
        Servo(name="left_yoke__hip",                pin_limits=(-0.2, 0.3), init_value=0.0, offset=0.0, reverse=False, **generic_values),
        Servo(name="head__left_yoke",               pin_limits=(-0.4, 0.3), init_value=0.0, offset=0.0, reverse=False, **generic_values),
        DummyServo(),
        DummyServo(),
        Servo(name="head__right_yoke",              pin_limits=(-0.4, 0.3), init_value=0.0, offset=0.0, reverse=True, **generic_values),
        Servo(name="right_yoke__hip",               pin_limits=(-0.2, 0.3), init_value=0.0, offset=0.0, reverse=False, **generic_values),
        Servo(name="right_hip__upper_leg",          pin_limits=(-0.6, 0.4), init_value=0.0, offset=-0.3, reverse=False, **generic_values),
        Servo(name="right_upper_leg__lower_leg",    pin_limits=(-0.5, 0.5), init_value=0.0, offset=0.6, reverse=False, **generic_values),
        DummyServo(),
        Servo(name="right_lower_leg__foot",         pin_limits=(-0.5, 0.5), init_value=0.0, offset=-0.3, reverse=True, **generic_values),
        DummyServo(),
        DummyServo(),
    ]

    bus = smbus.SMBus(1)

    servo_controller = ServoController(
        bus=bus,
        freq=freq,
        servos=servos,
    )
    sensor_reader = SensorReader(
        bus=bus,
        freq=freq,
    )
    gnoci = Gnoci(
        servo_controller=servo_controller,
        sensor_reader=sensor_reader,
    )
    return gnoci

