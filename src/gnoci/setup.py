from networking_utils.channel import Channel
import time


def setup_gnoci_control(
    host: str,
    port: int,
    update_interval: float = 0.01,
):
    import pigpio
    from peripherals.gnoci.gnoci import Gnoci
    from peripherals.gnoci.mpu6050 import mpu6050

    gpio = pigpio.pi()
    mpu = mpu6050(0x68)
    gnoci = Gnoci(
        gpio=gpio,
        mpu=mpu,
        update_interval=update_interval,
    )
    channel = Channel(host=host, port=port)
    channel.serve(gnoci.handle_message)
