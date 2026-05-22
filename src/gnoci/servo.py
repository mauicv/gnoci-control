from dataclasses import dataclass
from simple_pid import PID

SERVO_PWM_THRESHOLD_MIN: int = 500
SERVO_PWM_THRESHOLD_MAX: int = 2500
HALF_RANGE = (SERVO_PWM_THRESHOLD_MAX - SERVO_PWM_THRESHOLD_MIN) / 2 # 1000

@dataclass
class Servo:
    name: str
    pin_limits: tuple[float, float]
    init_value: float
    reverse: bool = False
    kp: float = 0.08
    ki: float = 0.0
    kd: float = 0.005
    _value: float = 0.0
    _update_value: float = 0.0
    pid_controller: PID = None
    offset: float = 0.0
    freq: int = 100

    def __post_init__(self):
        self.pid_controller = PID(
            self.kp, self.ki, self.kd,
            starting_output=0,
            setpoint=self.init_value,
            output_limits=(-0.05, 0.05),  # max 5 units/tick = 5 units/sec at 100Hz
            sample_time=1.0 / self.freq,
        )

    def update_setpoint_delta(self, setpoint_delta: float):
        updated_setpoint = self.pid_controller.setpoint + setpoint_delta
        if updated_setpoint > self.pin_limits[1]: updated_setpoint = self.pin_limits[1]
        elif updated_setpoint < self.pin_limits[0]: updated_setpoint = self.pin_limits[0]
        self.pid_controller.setpoint = updated_setpoint

    def update_setpoint(self, setpoint: float):
        self.pid_controller.setpoint = setpoint

    @property
    def value(self):
        value = self._value
        if value > self.pin_limits[1]: value = self.pin_limits[1]
        elif value < self.pin_limits[0]: value = self.pin_limits[0]
        value = -value if self.reverse else value
        value += self.offset
        return value

    def _value_to_pwm(self) -> int:
        pwm_val = int(SERVO_PWM_THRESHOLD_MIN + (1 + self.value) * HALF_RANGE)
        if pwm_val > SERVO_PWM_THRESHOLD_MAX: pwm_val = SERVO_PWM_THRESHOLD_MAX
        elif pwm_val < SERVO_PWM_THRESHOLD_MIN: pwm_val = SERVO_PWM_THRESHOLD_MIN
        return pwm_val

    def get_pwm(self):
        self._update_value = self.pid_controller(self._value)
        self._value += self._update_value
        return self._value_to_pwm()
