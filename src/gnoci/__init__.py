import click
import os
from net_util.channel import Channel


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('--host', type=str, default=None)
@click.option('--port', type=int, default=8000)
@click.pass_context
def gnoci(ctx, debug, host, port):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    ctx.obj['HOST'] = host if host else os.getenv("HOST")
    ctx.obj['POST'] = port if port else int(os.getenv("POST"))


@gnoci.command()
@click.pass_context
@click.option('--update-interval', type=float, default=0.01)
@click.option('--sensor-only', is_flag=True)
def start(ctx, update_interval, sensor_only):
    from gnoci.setup import setup_gnoci_control
    gnoci = setup_gnoci_control(update_interval=update_interval)
    channel = Channel(host=ctx.obj['HOST'], port=ctx.obj['POST'])
    channel.serve(gnoci.handle_message)
