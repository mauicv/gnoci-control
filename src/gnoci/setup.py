import time
import smbus2 as smbus
from gnoci.hardware import SensorReader
from gnoci.hardware import ServoController
from gnoci.predict import PolicyRunner
from gnoci.memory import Memory
from gnoci.config import OBSERVATION_DIM, ACTION_DIM, OBS_STACK_DIM, ACTION_STACK_DIM, MODEL_INPUT_DIM, FREQ, CONTROL_HZ
import json


class Gnoci:
    def __init__(
            self,
            bus: smbus.SMBus,
            center_angles: bool = True,
            control_hz: int = CONTROL_HZ,
            without_servos: bool = False,
        ):
        self.bus = bus
        self.policy = PolicyRunner(obs_dim=MODEL_INPUT_DIM)
        if not without_servos:
            self.servo_controller = ServoController(bus=self.bus, freq=control_hz, control_hz=control_hz)
        else:
            self.servo_controller = None
        self.sensor_reader = SensorReader(bus=self.bus, freq=FREQ, control_hz=control_hz, center_angles=center_angles)
        self.memory = Memory(
            num_states=OBS_STACK_DIM,
            num_actions=ACTION_STACK_DIM,
            action_dim=ACTION_DIM,
            state_dim=OBSERVATION_DIM
        )
        time.sleep(0.01)

    def configure_sensors(self):
        self.sensor_reader.center_angles = False
        self.sensor_reader.apply_obs_norm = False
        self.servo_controller.update_value([0.0]*10)
        time.sleep(0.5)
        center_angles = self.sensor_reader.data[0:10]
        total_drift = 0.0
        for sensor in self.sensor_reader.rot_enc_sensor_configs:
            drift = abs(center_angles[sensor.index] - sensor.center)
            total_drift += drift
            average_drift = total_drift / len(self.sensor_reader.rot_enc_sensor_configs)
            sensor.center = center_angles[sensor.index]
        self.sensor_reader.center_angles = True
        self.sensor_reader.apply_obs_norm = True
        # the data read above stored uncentered positions as prev_rot_enc_data;
        # reset so the first control tick reports zero velocity instead of a
        # centered-minus-uncentered spike
        self.sensor_reader.reset_filters()
        time.sleep(0.1)
        return total_drift, average_drift

    def configure_sensors_from_file(self, file_name: str):
        with open(file_name, 'r') as f:
            data = json.load(f)
        for sensor in self.sensor_reader.rot_enc_sensor_configs:
            sensor.center = data[sensor.name]
        self.sensor_reader.center_angles = True
        self.sensor_reader.apply_obs_norm = True
        self.sensor_reader.reset_filters()
        time.sleep(0.1)


    def reset(self):
        self.servo_controller.update_value([0.0]*10)
        print('resetting servos')
        time.sleep(0.5)
        self.sensor_reader.reset_filters()
        print('resetting filters')
        self.memory.reset()
        print('resetting memory')
        time.sleep(1)


def setup_gnoci_control(
    bus: smbus.SMBus,
    center_angles: bool = True,
    control_hz: int = CONTROL_HZ
):
    return Gnoci(bus=bus, center_angles=center_angles, control_hz=control_hz)
