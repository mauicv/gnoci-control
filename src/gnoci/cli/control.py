import click
import os
from gnoci.net_util.channel import Channel


@click.command()
@click.option('--debug/--no-debug', default=False)
@click.option('--host', type=str, default=None)
@click.option('--port', type=int, default=8000)
@click.option('--update-interval', type=float, default=0.01)
def start(debug, host, port, update_interval):
    from gnoci.setup import setup_gnoci_control
    gnoci = setup_gnoci_control(update_interval=update_interval)
    channel = Channel(host=host, port=port)
    channel.serve(gnoci.handle_message)
    print("Gnoci control server started")
