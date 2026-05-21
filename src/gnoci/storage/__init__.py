from google.cloud import storage
from gnoci.storage.model import GCSModel
from gnoci.storage.rollout import GCSRollout


class GCS_Interface:
    def __init__(
            self,
            experiment_name,
            model_name=None,
            credentials='gnoci-497019-ecf9e3fbc49e.json',
            project_id='gnoci',
            bucket='gnoci',
            num_runs=0,
            rollout_length=100,
            state_dim=14,
            action_dim=8,
            num_time_steps=25,
        ) -> None:
        if credentials:
            client = storage.Client.from_service_account_json(credentials)
        elif project_id:
            client = storage.Client(project=project_id)

        if model_name is None:
            model_name = experiment_name

        self.bucket = client.bucket(bucket)
        self.model = GCSModel(
            self.bucket,
            experiment_name=model_name
        )
        self.rollout = GCSRollout(
            self.bucket,
            experiment_name=experiment_name
        )