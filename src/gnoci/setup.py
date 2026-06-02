import time
from gnoci.servo import Servo, DummyServo
import smbus2 as smbus
from gnoci.hardware import SensorReader
from gnoci.hardware import ServoController
from gnoci.predict import PolicyRunner
from gnoci.loop import Loop
from gnoci.memory import Memory
from gnoci.config import OBSERVATION_DIM, ACTION_DIM, OBS_STACK_DIM, ACTION_STACK_DIM, MODEL_INPUT_DIM, FREQ, KP, KI, KD, CONTROL_HZ


class Gnoci:
    def __init__(self, bus: smbus.SMBus, center_angles: bool = True, control_hz: int = CONTROL_HZ):
        self.bus = bus
        self.policy = PolicyRunner(obs_dim=MODEL_INPUT_DIM)
        self.servo_controller = ServoController(bus=self.bus, freq=FREQ, kp=KP, ki=KI, kd=KD, control_hz=control_hz)
        self.sensor_reader = SensorReader(bus=self.bus, freq=FREQ, center_angles=center_angles)
        self.memory = Memory(
            num_states=OBS_STACK_DIM,
            num_actions=ACTION_STACK_DIM,
            action_dim=ACTION_DIM,
            state_dim=OBSERVATION_DIM
        )
        time.sleep(0.01)


def setup_gnoci_control(
    bus: smbus.SMBus,
    center_angles: bool = True,
    control_hz: int = CONTROL_HZ
):
    return Gnoci(bus=bus, center_angles=center_angles, control_hz=control_hz)
