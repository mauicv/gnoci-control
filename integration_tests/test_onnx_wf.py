from reflect.components.latent_world_model.models import MLPEncoder, MLPActor
from reflect.components.latent_world_model.models.encoder_actor import EncoderActor
from gnoci.storage import GCS_Interface
import torch
import logging
import sys
import os

logger = logging.getLogger(__name__)


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s'
    )

    encoder = MLPEncoder(
        input_dim=10+4+6+2,
        output_dim=512,
    )

    actor = MLPActor(
        latent_dim=512,
        action_dim=10,
        num_layers=2,
        hidden_dim=512,
    )

    encoder_actor = EncoderActor(
        latent_dim=512,
        encoder=encoder,
        actor=actor,
    )

    gcs = GCS_Interface(
        credentials='gnoci-497019-ecf9e3fbc49e.json',
        bucket='gnoci',
        experiment_name='onnx-wf'
    )

    gcs.model.upload_model(encoder_actor, torch.randn(1, 10+4+6+2))
    gcs.model.download_model()