from gnoci.servo import Servo
from gnoci.loop import Loop
import time
from gnoci.hardware.hardware import init_pca9685
from gnoci.hardware.hardware import write_servos


class ServoController:
    def __init__(
            self,
            bus,
            servos: list[Servo],
            freq=100,
            **kwargs):
        super().__init__(**kwargs)
        self.bus = bus
        self.freq = freq
        self.servos = servos

        init_pca9685(bus, freq=freq)
        self.servo_update_loop = Loop(
            hz=self.freq,
            func=self._write_servos
        )
        self.servo_update_loop.start()
        self.last_servo_set_ts = time.time()

    def update_setpoint_delta(self, values: list[float]):
        for servo, value in zip(self.servos, values):
            servo.update_setpoint_delta(value)
        self.last_servo_set_ts = time.time()

    def update_setpoint(self, values: list[float]):
        for servo, value in zip(self.servos, values):
            servo.update_setpoint(value)
        self.last_servo_set_ts = time.time()

    def _write_servos(self):
        servo_data = [servo.get_pwm() for servo in self.servos]
        write_servos(self.bus, servo_data)

    def deinit_servo_controller(self):
        self.servo_update_loop.stop()