import time
from gnoci.filters.complementary import ComplementaryFilter
from gnoci.filters.identity import IdentityFilter
from gnoci.loop import Loop
from gnoci.hardware.hardware import (
    read_sensor_data,
    decode_imu,
    decode_angle,
    decode_foot_contact,
    init_mpu6050,
    init_adcs,
    test_all
)

class SensorReader:
    def __init__(
            self,
            bus,
            freq=100,
            **kwargs
        ):
        super().__init__(**kwargs)
        self.freq = freq
        self.c_filter = ComplementaryFilter(alpha=0.95)
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
        self.prev_rot_enc_data = [0] * 10
        self.adc_data = [0] * 4

        # Cumulative unwrapped angles
        self.rot_enc_cumulative = [0.0] * 10
        self.rot_enc_prev = [None] * 10

        self.angular_velocities = [0.0] * 10

        self.pitch = 0
        self.roll = 0

        self._hw_read_ts_new = time.perf_counter()
        self._hw_read_ts_old = time.perf_counter() - 1.0 / self.freq
        self._hw_read_dt = None
        self.hardware_loop = Loop(
            hz=self.freq,
            func=self._read_hardware
        )
        self.hardware_loop.start()

    def _read_hardware(self):
        try:
            self.imu_raw, self.rot_enc_raw, self.adc_raw = read_sensor_data(self.bus)
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
        if diff > 0.5:
            diff -= 1.0
        elif diff < -0.5:
            diff += 1.0

        self.rot_enc_cumulative[i] += diff
        self.rot_enc_prev[i] = raw_angle
        return self.rot_enc_cumulative[i]

    def decode_hardware(self):
        self.imu_data = decode_imu(self.imu_raw)
        decoded = [decode_angle(item) for item in self.rot_enc_raw]
        self.rot_enc_data = [self._unwrap_angle(i, a) for i, a in enumerate(decoded)]
        self.adc_data = [decode_foot_contact(item) for item in self.adc_raw]
        self.c_filter.update(self.imu_data[:3], self.imu_data[3:])
        self.pitch = self.c_filter.pitch
        self.roll = self.c_filter.roll

    def derive_angular_velocities(self):
        self.angular_velocities = [
            (self.rot_enc_data[i] - self.prev_rot_enc_data[i]) / (self._hw_read_dt + 1e-8) for i in range(10)
        ]
        self.prev_rot_enc_data = self.rot_enc_data

    @property
    def data(self):
        self.decode_hardware()
        return [
            *self.rot_enc_data,
            *self.angular_velocities,
            *self.adc_data,
            *self.imu_data,
            self.roll,
            self.pitch,
        ]

    @property
    def overturned(self):
        _, _, az = self.imu_data[:3]
        return int(az * 10 < 1)

    def deinit(self):
        self.hardware_loop.stop()