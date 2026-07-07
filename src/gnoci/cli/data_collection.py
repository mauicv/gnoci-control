import click
import os
import numpy as np
import time
from gnoci.config import MODEL_INPUT_DIM, CONTROL_HZ
from gnoci.data_collection.action_ds_interface import ActionDSInterface
import json
from tqdm import tqdm


def record_rollout(gnoci: Gnoci, rollout: dict, config: dict):
    ctl_hz = config['control_hz']
    actions = rollout['actions_hw']
    rollout['measured_states'] = []
    rollout['times'] = []
    rollout_start_time = time.perf_counter()
    for action in actions:
        time_start = time.perf_counter()

        gnoci.servo_controller.update_setpoint(action)
        state = gnoci.sensor_reader.data
        rollout['measured_states'].append(state)
        rollout['times'].append(time.perf_counter() - rollout_start_time)

        elapsed = time.perf_counter() - time_start
        if elapsed < 1.0 / ctl_hz:
            time.sleep(1.0 / ctl_hz - elapsed)


@click.command()
@click.option('--file-name', type=str, default='data.json')
@click.option('--center-angles', type=bool, default=True)
@click.option('--ctl-hz', type=int, default=CONTROL_HZ)
@click.option('--configure-sensors', type=bool, default=True)
def record_data(file_name: str, center_angles: bool, ctl_hz: int, configure_sensors: bool = True):
    from gnoci.setup import setup_gnoci_control
    bus = SMBus(1)
    gnoci = setup_gnoci_control(bus=bus, center_angles=center_angles, control_hz=ctl_hz)
    if configure_sensors:
        total_drift, average_drift = gnoci.configure_sensors()
        print(f"Total sensor drift: {total_drift:.3f}, Average sensor drift: {average_drift:.3f}")

    action_ds = ActionDSInterface()
    for rollout in tqdm(action_ds.iter_rollouts()):
        gnoci.servo_controller.update_setpoint_delta(0)
        time.sleep(0.5)
        record_rollout(gnoci, rollout, action_ds.config)
        break

    # with open(file_name, 'w') as f:
    #     json.dump(state_data, f, indent=4)