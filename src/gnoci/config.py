import math

NUM_JOINTS = 10
NUM_CONTACT_SENSORS = 4
NUM_IMU_SENSORS = 6
NUM_ROLL_PITCH = 2
ACTION_DIM = NUM_JOINTS
OBS_STACK_DIM = 8
ACTION_STACK_DIM = 8

OBSERVATION_DIM = (2 * NUM_JOINTS + NUM_CONTACT_SENSORS + NUM_IMU_SENSORS + NUM_ROLL_PITCH)
MODEL_INPUT_DIM = OBSERVATION_DIM * OBS_STACK_DIM + ACTION_DIM * ACTION_STACK_DIM

CONTROL_HZ = 60
FREQ = 120

# 270-degree-travel servos mapped to [-1, 1] over the 500-2500 us PWM range,
# so one servo command unit is 135 degrees = 0.75*pi rad.
SERVO_UNIT_RAD = 0.75 * math.pi

# Max joint angular velocity in rad/s — must match gnoci-sim's MAX_JOINT_VEL
# (the action-delta scale the policy was trained with).
MAX_JOINT_VEL = 6.0

# Per-second setpoint delta limit in servo units, derived so a full action
# moves the joint at MAX_JOINT_VEL rad/s, same as in sim.
MAX_DELTA_V = MAX_JOINT_VEL / SERVO_UNIT_RAD

ACTION_SCALE = 0.25 