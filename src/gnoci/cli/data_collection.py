import click
import os
import numpy as np
import time
from gnoci.config import MODEL_INPUT_DIM, CONTROL_HZ
from gnoci.data_collection.action_ds_interface import ActionDSInterface
from gnoci.setup import Gnoci
import json
from tqdm import tqdm
_has_i2c = os.path.exists('/dev/i2c-1')
if _has_i2c:
    print("using smbus")
    from smbus2 import SMBus
else:
    print("using mocked bus")
    from gnoci.hardware.mock_bus import MockedBus as SMBus


def record_rollout(gnoci: Gnoci, rollout: dict, config: dict):
    ctl_hz = config['action_hz']
    actions = rollout['actions_hw']
    rollout['measured_states'] = []
    rollout['times'] = []
    rollout_start_time = time.perf_counter()
    for action in actions:
        time_start = time.perf_counter()

        gnoci.servo_controller.update_value_delta(action)
        state = gnoci.sensor_reader.data
        rollout['measured_states'].append(state.tolist())
        rollout['times'].append(time.perf_counter() - rollout_start_time)

        elapsed = time.perf_counter() - time_start
        if elapsed < 1.0 / ctl_hz:
            time.sleep(1.0 / ctl_hz - elapsed)
    return rollout


@click.command()
@click.option('--file-name', type=str, default='sysid_data.json')
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
    sysid_data = {
        'config': action_ds.config,
        'data': [],
    }

    pbar = tqdm(total=len(action_ds))

    for rollout in tqdm(action_ds.iter_rollouts(), ):
        gnoci.servo_controller.update_value(np.zeros(10))
        time.sleep(2)
        rollout = record_rollout(gnoci, rollout, action_ds.config)
        sysid_data['data'].append(rollout)
        pbar.update(1)

    pbar.close()
    
    gnoci.servo_controller.update_value(np.zeros(10))
    time.sleep(2)

    with open(file_name, 'w') as f:
        json.dump(sysid_data, f, indent=4)