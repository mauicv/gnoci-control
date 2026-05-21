from google.cloud import storage
from gnoci.storage.model import GCSModel
from gnoci.storage.rollout import GCSRollout


class GCS_Interface:
    def __init__(
            self,
            experiment_name='none',
            model_name='none',
            credentials='gnoci-497019-ecf9e3fbc49e.json',
            project_id='gnoci',
            bucket='gnoci',
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

    def list_experiments(self):
        blobs = self.bucket.list_blobs(prefix='')
        return set(blob.name.split('/')[0] for blob in blobs)