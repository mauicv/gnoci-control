#ifndef MPU6050_H
#define MPU6050_H


#include <iostream>
#include <sys/ioctl.h>
#include <fcntl.h>

#include <cstdint>

#include "i2c_util.h"
#include <string>
using std::string;


extern "C" {
	#include <linux/i2c-dev.h>
	#include <i2c/smbus.h>
}


constexpr float ACC_LSB_PER_G = 16384.0f; // for ±2 g
constexpr float GYRO_LSB_PER_DPS = 131.0f; // for ±250 dps
constexpr float TEMP_LSB_PER_C = 340.0f; // for 340 C

class MPU6050 {
public:
    int f_dev;
    float data[6];

    MPU6050() {
        f_dev = open("/dev/i2c-1", O_RDWR);
        std::cout << "f_dev: " << f_dev << std::endl;
        if (f_dev < 0) {
            std::cout << "Failed to open /dev/i2c-1\n";
        }

        if (ioctl(f_dev, I2C_SLAVE, 0x68) < 0) {
            std::cout << "Failed to set I2C slave address\n";
        }

        uint8_t ret = read(f_dev, 0x75);
        std::cout << toBinaryString(ret) << std::endl;

        write(f_dev, 0x6B, 0x00);
        std::cout << "Verify write to 0x6B(Non-sleep mode): ";
        ret = read(f_dev, 0x6B);
        std::cout << (ret & (1 << 2)) << std::endl;

        std::cout << "Verify 2g scale: ";
        ret = read(f_dev, 0x1C);
        std::cout << (ret & (1 << 4)) << (ret & (1 << 3)) << std::endl;

        std::cout << "Verify 250dps scale: ";
        ret = read(f_dev, 0x1B);
        std::cout << (ret & (1 << 4)) << (ret & (1 << 3)) << std::endl;

        std::cout << "Config Output: ";
        // ret = write(f_dev, 0x1A, 0b00000011); // 44hz cuttof 4.9ms delay
        ret = write(f_dev, 0x1A, 0b00000000); // 260hz cuttof 0.0ms delay
        ret = read(f_dev, 0x1A);
        std::cout << toBinaryString(ret) << std::endl;
    }

    void get_sensor_data(double dt) {
        uint8_t sensor_data[14];
        read_block(f_dev, 0x3B, sensor_data, 14);

        int16_t x_acc = static_cast<int16_t>((static_cast<int16_t>(sensor_data[0]) << 8) | sensor_data[1]);
        int16_t y_acc = static_cast<int16_t>((static_cast<int16_t>(sensor_data[2]) << 8) | sensor_data[3]);
        int16_t z_acc = static_cast<int16_t>((static_cast<int16_t>(sensor_data[4]) << 8) | sensor_data[5]);
        int16_t temp = static_cast<int16_t>((static_cast<int16_t>(sensor_data[6]) << 8) | sensor_data[7]);
        int16_t x_gyro = static_cast<int16_t>((static_cast<int16_t>(sensor_data[8]) << 8) | sensor_data[9]);
        int16_t y_gyro = static_cast<int16_t>((static_cast<int16_t>(sensor_data[10]) << 8) | sensor_data[11]);
        int16_t z_gyro = static_cast<int16_t>((static_cast<int16_t>(sensor_data[12]) << 8) | sensor_data[13]);
        data[0] = (float)x_acc/ACC_LSB_PER_G;
        data[1] = (float)y_acc/ACC_LSB_PER_G;
        data[2] = (float)z_acc/ACC_LSB_PER_G;
        data[3] = (float)x_gyro/GYRO_LSB_PER_DPS;
        data[4] = (float)y_gyro/GYRO_LSB_PER_DPS;
        data[5] = (float)z_gyro/GYRO_LSB_PER_DPS;
    }

    float* get_data() {
        return data;
    }
};
#endif // MPU6050_H
