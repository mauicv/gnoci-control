import time
from gnoci.filters.complementary import ComplementaryFilter
from gnoci.filters.low_pass import LowPassFilter
from gnoci.loop import Loop
from gnoci.hardware.hardware import (
    read_sensor_data,
    decode_imu,
    decode_angle,
    decode_foot_contact,
    init_mpu6050,
    init_adcs,
)
from dataclasses import dataclass
import json
import numpy as np


@dataclass
class SensorConfig:
    name: str
    index: int
    return_index: int
    center: float
    lo: float
    hi: float
    range: float

    def __post_init__(self):
        self.range = self.hi - self.lo
        assert self.index == self.return_index

with open('positioning_data.json', 'r') as f:
    rot_enc_sensor_configs_data = json.load(f)


class SensorReader:
    # left the right -> head__..._yoke, yoke__hip, hip__upper_leg, upper_leg__lower_leg, lower_leg__foot
    # sensor_map = [7, 8, 5, 9, 6,  3, 4, 1, 2, 0]
    sensor_map = [0, 1, 2, 3, 4,  5, 6, 7, 8, 9]
    sensor_orientations = [-1, -1, -1, -1, -1,  1, 1, 1, 1, 1]
    rot_enc_sensor_configs = [SensorConfig(**sensor) for sensor in rot_enc_sensor_configs_data]

    def __init__(
            self,
            bus,
            freq=100,
            center_angles=True,
            apply_obs_norm=False,
            **kwargs
        ):
        super().__init__(**kwargs)
        self.freq = freq
        self.center_angles = center_angles
        self.apply_obs_norm = apply_obs_norm
        self.c_filter = ComplementaryFilter(alpha=0.95)
        self.acc_low_pass_filters = [LowPassFilter(alpha=0.2) for _ in range(3)]
        self.angular_velocities_low_pass_filters = [LowPassFilter(alpha=0.3) for _ in range(10)]
        self.bus = bus
        init_mpu6050(bus)
        try:
            init_adcs(bus)
        except OSError as e:
            print(f"Error initializing ADCs: {e}")

        self.imu_raw = [0] * 6
        self.rot_enc_raw = [0] * 10
        self.adc_raw = [0] * 4

        self.imu_data = [0] * 6
        self.rot_enc_data = [0] * 10
        self.prev_rot_enc_data = None
        self.adc_data = [0] * 4

        # Cumulative unwrapped angles
        self.rot_enc_cumulative = [0.0] * 10
        self.rot_enc_prev = [None] * 10

        self.angular_velocities = [0.0] * 10
        self._vel_ts_prev = time.perf_counter()

        self.pitch = 0
        self.roll = 0

        self._hw_read_ts_new = time.perf_counter()
        self._hw_read_ts_old = self._hw_read_ts_new - 1.0 / self.freq
        self._hw_read_dt = 1.0 / self.freq
        self.hardware_loop = Loop(
            hz=self.freq,
            func=self._read_hardware
        )
        self.hardware_loop.start()

    def reset_filters(self):
        for filter in self.acc_low_pass_filters:
            filter.reset()
        for filter in self.angular_velocities_low_pass_filters:
            filter.reset()
        self.prev_rot_enc_data = None

    def _read_hardware(self):
        try:
            self.imu_raw, self.rot_enc_raw, self.adc_raw = read_sensor_data(self.bus)
            self.rot_enc_raw = [self.rot_enc_raw[i] for i in self.sensor_map] # reorder
            self._hw_read_ts_old = self._hw_read_ts_new
            self._hw_read_ts_new = time.perf_counter()
            self._hw_read_dt = self._hw_read_ts_new - self._hw_read_ts_old
        except OSError as e:
            print(f"Error reading hardware: {e}")

    def _unwrap_angle(self, i, raw_angle):
        if self.rot_enc_prev[i] is None:
            self.rot_enc_prev[i] = raw_angle
            self.rot_enc_cumulative[i] = raw_angle
            return raw_angle

        diff = raw_angle - self.rot_enc_prev[i]
        if diff > 1.0:
            diff -= 2.0
        elif diff < -1.0:
            diff += 2.0

        self.rot_enc_cumulative[i] += diff
        self.rot_enc_prev[i] = raw_angle
        return self.rot_enc_cumulative[i]

    def _center_angle(self, i, raw_angle):
        if not self.center_angles:
            return raw_angle
        sensor_config = self.rot_enc_sensor_configs[i]
        centered_angle = raw_angle - sensor_config.center
        centered_angle = centered_angle * self.sensor_orientations[i] 
        return centered_angle

    def decode_hardware(self):
        self.imu_raw = decode_imu(self.imu_raw)
        gyro_data, acc_data = self.imu_raw[:3], self.imu_raw[3:]
        gyro_data = [gyro_data[i] / 250.0 for i in range(3)]
        acc_data = [self.acc_low_pass_filters[i].update(acc_data[i]) for i in range(3)]
        self.imu_data = [*gyro_data, *acc_data]
        decoded = [decode_angle(item) for item in self.rot_enc_raw]
        self.rot_enc_data = [self._unwrap_angle(i, a) for i, a in enumerate(decoded)]
        self.rot_enc_data = [self._center_angle(i, a) for i, a in enumerate(self.rot_enc_data)]
        self.adc_data = [decode_foot_contact(item) for item in self.adc_raw]

    def update_filters(self):
        gyro_data, acc_data = self.imu_raw[:3], self.imu_raw[3:]
        self.c_filter.update(acc_data, gyro_data)
        self.pitch = self.c_filter.pitch
        self.roll = self.c_filter.roll

    def derive_angular_velocities(self):
        # dt must span the interval between successive data-property reads (the
        # control rate), not the faster hardware-loop interval, or velocities
        # are inflated by FREQ/CONTROL_HZ
        now = time.perf_counter()
        if self.prev_rot_enc_data is None:
            self.prev_rot_enc_data = self.rot_enc_data
            self._vel_ts_prev = now
            self.angular_velocities = [0.0] * 10
            return
        dt = now - self._vel_ts_prev
        self._vel_ts_prev = now
        # encoder units are pi-rad (decode_angle maps one revolution to [-1, 1]),
        # so scale by pi to get rad/s, matching sim's raw qvel observations
        self.angular_velocities = [
            np.pi * (self.rot_enc_data[i] - self.prev_rot_enc_data[i]) / (dt + 1e-8) for i in range(10)
        ]
        self.angular_velocities = [self.angular_velocities_low_pass_filters[i].update(v) for i, v in enumerate(self.angular_velocities)]
        self.prev_rot_enc_data = self.rot_enc_data

    def sensor_index_from_name(self, name: str):
        for sensor_config in self.rot_enc_sensor_configs:
            if sensor_config.name == name:
                return sensor_config.index
        return None

    @property
    def data(self):
        self.decode_hardware()
        self.update_filters()
        self.derive_angular_velocities()

        obs = np.array([
            *self.rot_enc_data,
            *self.angular_velocities,
            *self.adc_data,
            *self.imu_data,
            self.pitch,
            self.roll,
        ])
        return obs

    @property
    def overturned(self):
        _, _, az = self.imu_data[:3]
        return int(az * 10 < 1)

    def deinit(self):
        self.hardware_loop.stop()
