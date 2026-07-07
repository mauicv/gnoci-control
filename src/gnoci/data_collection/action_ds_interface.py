import json
import os
from gnoci.config import CONTROL_HZ, FREQ


def _validate_config_settings(config: dict):
    if config['control_hz'] != CONTROL_HZ:
        raise ValueError(f"Control Hz mismatch: {config['control_hz']} != {CONTROL_HZ}")
    if config['hardware_hz'] != FREQ:
        raise ValueError(f"Hardware Hz mismatch: {config['hardware_hz']} != {FREQ}")
    return config


class ActionDSInterface:
    DATA_DIR = os.path.dirname(__file__) + '/dataset/dataset.json'

    def __init__(self):
        with open(self.DATA_DIR, 'r') as f:
            self.data = json.load(f)
        self.config = _validate_config_settings(self.data['config'])
        self.num_rollouts = len(self.data['data'])

    def iter_rollouts(self):
        for rollout in self.data['data']:
            yield rollout


if __name__ == '__main__':
    ds = ActionDSInterface()
    for rollout in ds.iter_rollouts():
        print(rollout['type'], rollout['motor_idx'])
        
