#ifndef MUXAS5600_H
#define MUXAS5600_H


#include <iostream>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <chrono>
#include <cstdint>
#include <map>


#include "i2c_util.h"
#include <string>
using std::string;

extern "C" {
	#include <linux/i2c-dev.h>
	#include <i2c/smbus.h>
}

uint8_t write_byte_simple(int f_dev, uint8_t val) {
    int32_t ret = i2c_smbus_write_byte(f_dev, val);
    if (ret < 0) {
        std::cout << "Error writing\n";
        return 0;
    }
    return 1;
}

uint8_t read_byte_simple(int f_dev) {
    int32_t ret = i2c_smbus_read_byte(f_dev);
    if (ret < 0) {
        std::cout << "Error reading\n";
        return 0;
    }
    uint8_t byte = static_cast<uint8_t>(ret);
    return byte;
}


class MuxAS5600 {
public:
    int f_dev;
    int sensor_f_dev;
    double data[7];
    uint8_t channel_byte;
 
    MuxAS5600(uint8_t channel_byte): channel_byte(channel_byte) {
        // initialize TCA9548A I2C bus
        f_dev = open("/dev/i2c-1", O_RDWR);
        std::cout << "f_dev: " << f_dev << std::endl;
        if (f_dev < 0) {
            std::cout << "Failed to open /dev/i2c-1\n";
        }

        if (ioctl(f_dev, I2C_SLAVE, 0x70) < 0) {
            std::cout << "Failed to set I2C slave address\n";
        }

        // initialize AS5600 I2C bus
        sensor_f_dev = open("/dev/i2c-1", O_RDWR);
        std::cout << "sensor_f_dev: " << sensor_f_dev << std::endl;
        if (sensor_f_dev < 0) {
            std::cout << "Failed to open /dev/i2c-1\n";
        }

        if (ioctl(sensor_f_dev, I2C_SLAVE, 0x36) < 0) {
            std::cout << "Failed to set I2C slave address\n";
        }

        write_byte_simple(f_dev, 0b00000000);
        get_sensor_data(0.001);
    }

    void get_sensor_data(double dt) {
        for (int i = 7; i >= 0; --i) {
            if (channel_byte & (1 << i)) {
                write_byte_simple(f_dev, (1 << i));
                uint8_t msb = read_byte(sensor_f_dev, 0x0E);
                uint8_t lsb = read_byte(sensor_f_dev, 0x0F);
                uint16_t value = (msb << 8) | lsb;
                data[i] = static_cast<double>(value)/1000.0;
                std::cout << data[i] << std::endl;
            }
        }
    }

    void read_sensor_data(uint8_t sensor_address) {
        uint8_t ret = read_byte(sensor_f_dev, 0x00);
        std::cout << toBinaryString(ret) << std::endl;
    }

    double* get_data() {
        return data;
    }
};
#endif // MUXAS5600_H
