import click
import os
from gnoci.net_util.channel import Channel
from gnoci.storage import GCS_Interface


@click.group()
def storage():
    pass


@storage.command()
@click.option('--experiment-name', type=str, default='test')
def list_models(experiment_name):
    gcs = GCS_Interface(
        credentials='gnoci-497019-ecf9e3fbc49e.json',
        bucket='gnoci',
        experiment_name='test'
    )
    print(gcs.model.list_models())

@storage.command()
@click.option('--experiment-name', type=str, default='test')
def list_rollouts(experiment_name):
    gcs = GCS_Interface(
        credentials='gnoci-497019-ecf9e3fbc49e.json',
        bucket='gnoci',
        experiment_name='test'
    )
    print(gcs.rollout.list_rollouts())


@storage.command()
def list_experiments():
    gcs = GCS_Interface(
        credentials='gnoci-497019-ecf9e3fbc49e.json',
        bucket='gnoci',
    )
    print(gcs.list_experiments())