import math
import numpy as np
GRAVITY = 9.80665


class ComplementaryFilter:
    def __init__(self, alpha=0.95, dt=None):
        self.rollG = 0
        self.pitchG = 0
        self.rollComp = 0
        self.pitchComp = 0
        self.a_roll = 0
        self.a_pitch = 0
        self.alpha = alpha
        # fixed integration step (1/control_hz), matching sim's fixed-dt filter
        self.dt = dt

    def update(self, acc_data, gyro_data):
        x_accel, y_accel, z_accel = acc_data
        x_gyro, y_gyro, _ = gyro_data

        self.a_roll = math.atan2(-x_accel, z_accel)*180/math.pi
        self.a_pitch = math.atan2(y_accel, z_accel)*180/math.pi

        self.rollComp = self.a_roll * (1 - self.alpha) \
            + self.alpha * (self.rollComp + y_gyro * self.dt)
        self.pitchComp = self.a_pitch * (1 - self.alpha) \
             + self.alpha * (self.pitchComp + x_gyro * self.dt)

    @property
    def roll(self):
        return self.rollComp / 180

    @property
    def pitch(self):
        return self.pitchComp / 180
        
    @property
    def g_x(self):
        return GRAVITY*math.cos(self.roll*math.pi/180)

    @property
    def g_y(self):
        return GRAVITY*math.sin(self.pitch*math.pi/180)
    
    @property
    def g_xy(self):
        return self.g_x, self.g_y
