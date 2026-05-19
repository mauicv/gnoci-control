from networking_utils.client import Client
from client.sample import Rollout
import torch
import uuid
from typing import Optional


class ClientInterface:
    def __init__(
            self,
            gnoci_client: Client,
        ):
        self.gnoci_client = gnoci_client

    def connect(self):
        self.gnoci_client.connect()

    def reset(self):
        self.camera_client.send_data({'command': 'reset'})

    def close(self):
        self.gnoci_client.close()
        self.camera_client.close()
