import click
import logging
import dotenv
import os
from storage import GCS_Interface
from filters.butterworth import ButterworthFilter
from networking_utils.client import Client
from client.functions import run_training, deploy_solution
from client.client_interface import ClientInterface

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s'
)


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('--name', type=str, default='test')
@click.option('--model-name', type=str, default=None)
@click.option('--test', is_flag=True)
@click.option('--num-steps', type=int, default=150)
@click.option('--interval', type=float, default=0.1)
@click.option('--noise-range', nargs=2, type=float, default=(0.3, 0.3))
@click.option('--weight-range', nargs=2, type=float, default=(0.0, 0.0))
@click.option('--random-model', is_flag=True)
@click.pass_context
def client(ctx, debug, test, name, model_name, num_steps, interval, noise_range, weight_range, random_model):
    ctx.ensure_object(dict) 
    import torch
    torch.set_grad_enabled(False)

    ctx.obj['DEBUG'] = debug
    ctx.obj['CAMERA_HOST'] = os.getenv("CAMERA_HOST") if os.getenv("CAMERA_HOST") else '192.168.0.23'
    ctx.obj['CAMERA_PORT'] = int(os.getenv("CAMERA_PORT")) if os.getenv("CAMERA_PORT") else 8000
    ctx.obj['GNOCI_HOST'] = os.getenv("GNOCI_HOST") if os.getenv("GNOCI_HOST") else '192.168.0.20'
    ctx.obj['GNOCI_PORT'] = int(os.getenv("GNOCI_PORT")) if os.getenv("GNOCI_PORT") else 8000
    ctx.obj['NUM_STEPS'] = num_steps
    ctx.obj['INTERVAL'] = interval
    ctx.obj['NOISE_RANGE'] = noise_range
    ctx.obj['WEIGHT_RANGE'] = weight_range
    ctx.obj['RANDOM_MODEL'] = random_model
    ctx.obj['TEST'] = test

    filter = ButterworthFilter(
        order=2,
        # cutoff=3.0,
        cutoff=5.0,
        fs=20.0,
        num_components=8 # 8 servo motors
    )

    ctx.obj['FILTER'] = filter

    gcs = GCS_Interface(
        experiment_name=name,
        model_name=model_name,
        credentials='world-model-rl-01a513052a8a.json',
        bucket='gnoci_wmrl',
        model_limits=4
    )
    ctx.obj['GCS'] = gcs
