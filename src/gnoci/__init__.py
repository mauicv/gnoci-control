import click
import os
from gnoci.functions import move_robot
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


# @gnoci.command()
# @click.option('--front-left-bottom', type=float, default=0.0)
# @click.option('--front-left-top', type=float, default=0.0)
# @click.option('--front-right-bottom', type=float, default=0.0)
# @click.option('--front-right-top', type=float, default=0.0)
# @click.option('--back-left-bottom', type=float, default=0.0)
# @click.option('--back-left-top', type=float, default=0.0)
# @click.option('--back-right-bottom', type=float, default=0.0)
# @click.option('--back-right-top', type=float, default=0.0)
# def move(
#         front_left_bottom,
#         front_left_top,
#         front_right_bottom,
#         front_right_top,
#         back_left_bottom,
#         back_left_top,
#         back_right_bottom,
#         back_right_top
#     ):
#     """
#     Move the robot to the given angles.

#     example:
#         gnoci move --front-left-bottom=0.4 --front-right-bottom=0.4 --back-right-bottom=0.4 --back-left-bottom=0.4 --front-left-top=-0.3 --front-right-top=-0.3 --back-right-top=-0.3 --back-left-top=-0.3
#     """

#     move_robot(
#         front_left_bottom,
#         front_left_top,
#         front_right_bottom,
#         front_right_top,
#         back_left_bottom,
#         back_left_top,
#         back_right_bottom,
#         back_right_top
#     )

    