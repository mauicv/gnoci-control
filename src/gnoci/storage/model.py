import io
import os
import logging
logger = logging.getLogger(__name__)


def parse_version(blob_name):
    model_name = blob_name.split('/')[-1]
    return int(model_name.split('-')[-1].split('.')[0])


class GCSModel:
    def __init__(
            self,
            bucket,
            experiment_name,
        ) -> None:
        self.bucket = bucket
        self.model = None
        self.experiment_name = experiment_name
        self.version = self.get_latest_model_version()

    def remove_all_models(self):
        blobs = self.bucket.list_blobs(prefix=f'{self.experiment_name}/actor')
        for blob in blobs:
            blob.delete()

    def list_models(self):
        blobs = self.bucket.list_blobs(prefix=f'{self.experiment_name}/actor')
        return [blob.name for blob in blobs if blob.name.endswith('.onnx')]

    def get_latest_model_version(self):
        try:
            blobs = self.bucket.list_blobs(prefix=f'{self.experiment_name}/actor')
            filtered_blobs = [blob for blob in blobs if blob.name.endswith('.onnx')]
            versions = [parse_version(blob.name) for blob in filtered_blobs]
            logger.info(f'versions: {sorted(versions)}')
            if len(versions) == 0:
                version = None
            else:
                version = max(versions)
        except Exception as e:
            logger.error(f"Error getting latest model version: {e}")
            version = 0
        return version

    def upload_model(self, model, dummy_input):
        import torch
        try:
            version = self.get_latest_model_version()
            self.version = 0 if version is None else version + 1

            buf = io.BytesIO()
            torch.onnx.export(model, dummy_input, buf)
            buf.seek(0)

            blob_name = f"{self.experiment_name}/actor/actor-{self.version}.onnx"
            blob = self.bucket.blob(blob_name)
            blob.upload_from_file(buf, content_type='application/octet-stream')
            logger.info(f'uploaded model version {self.version}')
        except Exception as e:
            logger.error(f"Error uploading model: {e}")
            raise e

    def download_model(self):
        remote_version = self.get_latest_model_version()
        if remote_version is None:
            logger.info('no remote model found')
            return None
        if remote_version == self.version and self.model is not None:
            logger.info(f'model version {self.version} already loaded')
            return self.model

        blob_name = f"{self.experiment_name}/actor/actor-{remote_version}.onnx"
        blob = self.bucket.blob(blob_name)
        os.makedirs('model', exist_ok=True)
        for f in os.listdir('model'):
            if f.endswith('.onnx'):
                os.remove(os.path.join('model', f))
                logger.info(f'deleted old model {f}')
        local_path = f"model/actor-{remote_version}.onnx"
        blob.download_to_filename(local_path)
        self.model = local_path
        self.version = remote_version
        logger.info(f'downloaded model version {self.version} to {local_path}')
        return local_path
