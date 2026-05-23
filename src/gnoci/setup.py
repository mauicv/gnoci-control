import time
from gnoci.servo import Servo
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


    servos: list[Servo] = [
        Servo(name="left_lower_leg__foot",          pin_limits=(-0.5, 0.5), init_value=0.0, offset=-0.2, reverse=False, **generic_values), # [x]
        Servo(name="dummy",                         pin_limits=(-0.02, 0.02), init_value=0.0, offset=0.0), 
        Servo(name="left_hip__upper_leg",           pin_limits=(-0.02, 0.02), init_value=0.0, offset=-0.3, reverse=True, **generic_values), # [x]
        Servo(name="dummy",                         pin_limits=(-0.02, 0.02), init_value=0.0, offset=0.0),
        Servo(name="left_yoke__hip",                pin_limits=(-0.02, 0.02), init_value=0.0, offset=0.0, reverse=False, **generic_values), # [ ]
        Servo(name="head__left_yoke",               pin_limits=(-0.02, 0.02), init_value=0.0, offset=0.0, reverse=False, **generic_values), # [ ]
        Servo(name="dummy",                         pin_limits=(-0.02, 0.02), init_value=0.0, offset=0.0),
        Servo(name="dummy",                         pin_limits=(-0.02, 0.02), init_value=0.0, offset=0.0),
        Servo(name="head__right_yoke",              pin_limits=(-0.02, 0.02), init_value=0.0, offset=0.0, reverse=False, **generic_values), # [ ]
        Servo(name="right_yoke__hip",               pin_limits=(-0.02, 0.02), init_value=0.0, offset=0.0, reverse=False, **generic_values), # [ ]
        Servo(name="right_hip__upper_leg",          pin_limits=(-0.02, 0.02), init_value=0.0, offset=-0.3, reverse=False, **generic_values), # [x]
        Servo(name="right_upper_leg__lower_leg",    pin_limits=(-0.02, 0.02), init_value=0.0, offset=0.4, reverse=False, **generic_values), # [x]
        Servo(name="dummy",                         pin_limits=(-0.02, 0.02), init_value=0.0, offset=0.0), 
        Servo(name="right_lower_leg__foot",         pin_limits=(-0.5, 0.5), init_value=0.0, offset=-0.2, reverse=True, **generic_values), # [x]
        Servo(name="dummy",                         pin_limits=(-0.02, 0.02), init_value=0.0, offset=0.0),
        Servo(name="dummy",                         pin_limits=(-0.02, 0.02), init_value=0.0, offset=0.0),
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

