import glob
import os
import numpy as np
import onnxruntime as ort

_MODEL_DIR = 'model'


def _find_local_model():
    matches = glob.glob(os.path.join(_MODEL_DIR, '*.onnx'))
    if not matches:
        raise FileNotFoundError(f'No ONNX model found in {_MODEL_DIR}/')
    return matches[0]


class PolicyRunner:
    def __init__(self, obs_dim, model_path=None):
        if model_path is None:
            model_path = _find_local_model()
        self.session = None
        self.load_model(model_path)
        dummy = np.zeros((1, obs_dim), dtype=np.float32)
        self.session.run(None, {self.input_name: dummy})

    def load_model(self, path):
        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 1
        opts.intra_op_num_threads = 2
        self.session = ort.InferenceSession(path, opts)
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, obs):
        obs = np.array(obs, dtype=np.float32).reshape(1, -1)
        result = self.session.run(None, {self.input_name: obs})
        return result[0][0]
