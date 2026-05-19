import time
from peripherals.gnoci.gnoci import Gnoci
from peripherals.gnoci.mpu6050 import mpu6050
import pigpio

def move_robot(front_left_bottom, front_left_top, front_right_bottom, front_right_top, back_left_bottom, back_left_top, back_right_bottom, back_right_top):

    gpio = pigpio.pi()
    mpu = mpu6050(0x68)
    gnoci = Gnoci(
        gpio=gpio,
        mpu=mpu,
        update_interval=0.01,
    )

    gnoci.set_servo_states([
        front_right_top,
        front_right_bottom,
        front_left_top,
        front_left_bottom,
        back_right_top,
        back_right_bottom,
        back_left_top,
        back_left_bottom
    ])

    time.sleep(3)
    gnoci.deinit()

