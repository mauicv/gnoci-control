from gnoci.servo import Servo, DummyServo
from gnoci.loop import Loop
import time
from gnoci.hardware.hardware import init_pca9685
from gnoci.hardware.hardware import write_servos
from gnoci.config import CONTROL_HZ, MAX_DELTA_V


class ServoController:
    def __init__(
            self,
            bus,
            freq: int = CONTROL_HZ,
            control_hz: int = CONTROL_HZ,
            **kwargs
        ):
        super().__init__(**kwargs)
        generic_values = {
            "control_hz": control_hz,
            "max_delta_v": MAX_DELTA_V,
        }

        # TODO: asymetric in left_yoke__hip and right_yoke__hip reverse-True/False?
        # TODO: align servos with ordering in README.md
        self.servos: list[Servo] = [
            Servo(name="left_lower_leg__foot",          pin_limits=(-0.4, 0.7), init_value=0.0, offset=-0.3, reverse=False, **generic_values),
            DummyServo(),
            Servo(name="left_hip__upper_leg",           pin_limits=(-0.4, 0.6), init_value=0.0, offset=0.3, reverse=False, **generic_values),
            Servo(name="left_upper_leg__lower_leg",     pin_limits=(-0.6, 0.6), init_value=0.0, offset=-0.6, reverse=False, **generic_values),
            Servo(name="left_yoke__hip",                pin_limits=(-0.2, 0.3), init_value=0.0, offset=0.05, reverse=False, **generic_values),
            Servo(name="head__left_yoke",               pin_limits=(-0.4, 0.3), init_value=0.0, offset=0.0, reverse=False, **generic_values),
            DummyServo(),
            DummyServo(),
            Servo(name="head__right_yoke",              pin_limits=(-0.4, 0.3), init_value=0.0, offset=0.0, reverse=True, **generic_values),
            Servo(name="right_yoke__hip",               pin_limits=(-0.2, 0.3), init_value=0.0, offset=-0.05, reverse=True, **generic_values),
            Servo(name="right_hip__upper_leg",          pin_limits=(-0.4, 0.6), init_value=0.0, offset=0.3, reverse=True, **generic_values),
            Servo(name="right_upper_leg__lower_leg",    pin_limits=(-0.6, 0.6), init_value=0.0, offset=-0.6, reverse=True, **generic_values),
            DummyServo(),
            Servo(name="right_lower_leg__foot",         pin_limits=(-0.4, 0.7), init_value=0.0, offset=-0.3, reverse=True, **generic_values),
            DummyServo(),
            DummyServo(),
        ]
        self.servo_map = [5,4,2,3,0,8,9,10,11,13]

        self.bus = bus
        self.freq = freq

        init_pca9685(bus, freq=freq)
        self.servo_update_loop = Loop(
            hz=self.freq,
            func=self._write_servos
        )
        self.servo_update_loop.start()
        self.last_servo_set_ts = time.time()

    def update_value_delta(self, values: list[float]):
        for servo_idx, value in zip(self.servo_map, values):
            self.servos[servo_idx].update_value_delta(value)
        self.last_servo_set_ts = time.time()

    def update_value(self, values: list[float]):
        for servo_idx, value in zip(self.servo_map, values):
            self.servos[servo_idx].update_value(value)
        self.last_servo_set_ts = time.time()

    def _write_servos(self):
        servo_data = [servo.get_pwm() for servo in self.servos]
        write_servos(self.bus, servo_data, self.freq)

    def deinit(self):
        self.servo_update_loop.stop()

    def iter_servos(self):
        for i in range(10):
            yield self.servos[self.servo_map[i]]