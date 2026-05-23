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
    init_adcs
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

        # 10 for rotencs, 4 for adcs, 3 for acc, 3 for gyro, 
        self.imu_raw = [0] * 6
        self.rot_enc_raw = [0] * 10
        self.adc_raw = [0] * 4


        self.imu_data = [0] * 6
        self.rot_enc_data = [0] * 10
        self.adc_data = [0] * 4
        self.pitch = 0
        self.roll = 0

        self.hardware_loop = Loop(
            hz=self.freq,
            func=self._read_hardware
        )
        self.hardware_loop.start()

    def _read_hardware(self):
        """Background task to continuously update filtered MPU readings"""
        try:
            self.imu_raw, self.rot_enc_raw, self.adc_raw = read_sensor_data(self.bus)
        except OSError as e:
            print(f"Error reading hardware: {e}")

    def decode_hardware(self):
        self.imu_data = decode_imu(self.imu_raw)
        self.rot_enc_data = [decode_angle(item) for item in self.rot_enc_raw]
        self.adc_data = [decode_foot_contact(item) for item in self.adc_raw]
        self.c_filter.update(self.imu_data[:3], self.imu_data[3:])
        self.pitch = self.c_filter.pitch
        self.roll = self.c_filter.roll

    @property
    def data(self):
        """Returns the most recent filtered MPU data"""
        self.decode_hardware()
        return [
            *self.imu_data,
            *self.rot_enc_data,
            *self.adc_data,
            self.roll,
            self.pitch,
        ]

    @property
    def overturned(self):
        _, _, az = self.imu_data[:3]
        overturned = az * 10 < 1
        return int(overturned)

    def deinit(self):
        """Clean up resources"""
        self.hardware_loop.stop()