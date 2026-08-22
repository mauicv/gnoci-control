from dataclasses import dataclass
from gnoci.filters.low_pass import LowPassFilter
from gnoci.config import CONTROL_HZ, MAX_DELTA_V, MAX_ACTUATOR_VELOCITY_UNITS, SERVO_UNIT_RAD

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
    max_actuator_velocity: float = MAX_ACTUATOR_VELOCITY_UNITS
    low_pass_filter_alpha: float = 0.4
    low_pass_filter: LowPassFilter = None


    def __post_init__(self):
        self._value = self.init_value
        self.action_scale = self.max_delta_v / self.control_hz
        self.low_pass_filter = LowPassFilter(alpha=self.low_pass_filter_alpha)
        self.low_pass_filter.reset()

    def update_value_delta(self, value_delta: float):
        value_delta = value_delta * self.action_scale
        self.low_pass_filter.update(value_delta)
        self._value += self.low_pass_filter.value
        # clamp the stored setpoint like sim clips ctrl each step, so pushing
        # against a limit saturates instead of winding up past pin_limits
        if self._value > self.pin_limits[1]: self._value = self.pin_limits[1]
        elif self._value < self.pin_limits[0]: self._value = self.pin_limits[0]

    def update_value(self, value: float):
        self._value = value

    def update_target(self, value: float):
        # Slew-rate limit the commanded target against the last stored
        # setpoint, mirroring gnoci-sim's max_actuator_velocity clamp in
        # step() (a physical servo can't jump instantly to a new position).
        # Clamps against the raw unclipped setpoint, not pin_limits, so the
        # joint-range clip in `value` stays a safety bound rather than
        # feeding back into the rate limit (same as sim's ctrl clip vs.
        # _prev_target).
        max_step = self.max_actuator_velocity / self.control_hz
        if value > self._value + max_step:
            value = self._value + max_step
        elif value < self._value - max_step:
            value = self._value - max_step
        self.update_value(value)

    @property
    def prev_target(self):
        # Raw commanded setpoint converted to radians, matching gnoci-sim's
        # (unnormalized) _prev_target observation units.
        return self._value * SERVO_UNIT_RAD

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

    def update_value_delta(self, value_delta: float):
        self.value += value_delta

    def update_value(self, value: float):
        self.value = value

    def get_pwm(self):
        return self.value