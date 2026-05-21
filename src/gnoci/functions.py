import time
from gnoci.gnoci import Gnoci

def move_robot(front_left_bottom, front_left_top, front_right_bottom, front_right_top, back_left_bottom, back_left_top, back_right_bottom, back_right_top):
    gnoci = Gnoci(
        servo_controller=servo_controller,
        sensor_reader=sensor_reader,
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

