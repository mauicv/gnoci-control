from dataclasses import dataclass
from gnoci.filters.low_pass import LowPassFilter
from gnoci.config import CONTROL_HZ, MAX_DELTA_V

SERVO_PWM_THRESHOLD_MIN: int = 500
SERVO_PWM_THRESHOLD_MAX: int = 2500
HALF_RANGE = (SERVO_PWM_THRESHOLD_MAX - SERVO_PWM_THRESHOLD_MIN) / 2 # 1000


@dataclass
class Servo:
    name: str
    pin_limits: tuple[float, float]
    init_value: float
    reverse: bool = False
    _value: float = 0.0
    offset: float = 0.0
    control_hz: int = CONTROL_HZ
    max_delta_v: float = MAX_DELTA_V
    low_pass_filter_alpha: float = 0.4
    low_pass_filter: LowPassFilter = None
    action_queue: list[float] = []


    def __post_init__(self):
        self._value = self.init_value
        self.action_scale = self.max_delta_v / self.control_hz
        self.low_pass_filter = LowPassFilter(alpha=self.low_pass_filter_alpha)
        self.low_pass_filter.reset()

    def update_value_delta(self, value_delta: float):
        value_delta = value_delta * self.action_scale
        self.low_pass_filter.update(value_delta)
        self._value += self.low_pass_filter.value

    def update_value(self, value: float):
        self._value = value

    @property
    def value(self):
        value = self._value
        if value > self.pin_limits[1]: value = self.pin_limits[1]
        elif value < self.pin_limits[0]: value = self.pin_limits[0]
        value = -value if self.reverse else value
        value += self.offset * (1 if not self.reverse else -1)
        return value

    def _value_to_pwm(self) -> int:
        pwm_val = int(SERVO_PWM_THRESHOLD_MIN + (1 + self.value) * HALF_RANGE)
        if pwm_val > SERVO_PWM_THRESHOLD_MAX: pwm_val = SERVO_PWM_THRESHOLD_MAX
        elif pwm_val < SERVO_PWM_THRESHOLD_MIN: pwm_val = SERVO_PWM_THRESHOLD_MIN
        return pwm_val

    def get_pwm(self):
        return self._value_to_pwm()


class DummyServo():
    def __init__(self):
        self.value = 0.0

    def update_setpoint_delta(self, setpoint_delta: float):
        self.value += setpoint_delta

    def update_setpoint(self, setpoint: float):
        self.value = setpoint

    def get_pwm(self):
        return self.value