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

class MuxAS5600 {
public:
    uint8_t addr;
    int f_dev;
    int rot_enc_f_dev;
    int press_f_dev;
    double data[8];
    uint8_t channel_byte;
 
    MuxAS5600(uint8_t addr, uint8_t channel_byte): addr(addr), channel_byte(channel_byte) {
        // initialize TCA9548A I2C bus
        f_dev = open("/dev/i2c-1", O_RDWR);
        std::cout << "f_dev: " << f_dev << std::endl;
        if (f_dev < 0) {
            std::cout << "Failed to open /dev/i2c-1\n";
        }

        if (ioctl(f_dev, I2C_SLAVE, addr) < 0) {
            std::cout << "Failed to set I2C slave address\n";
        }

        // initialize AS5600 I2C bus
        rot_enc_f_dev = open("/dev/i2c-1", O_RDWR);
        std::cout << "rot_enc_f_dev: " << rot_enc_f_dev << std::endl;
        if (rot_enc_f_dev < 0) {
            std::cout << "Failed to open /dev/i2c-1\n";
        }

        if (ioctl(rot_enc_f_dev, I2C_SLAVE, 0x36) < 0) {
            std::cout << "Failed to set I2C slave address\n";
        }

        // initialize pressure sensor I2C bus
        press_f_dev = open("/dev/i2c-1", O_RDWR);
        std::cout << "press_f_dev: " << press_f_dev << std::endl;
        if (press_f_dev < 0) {
            std::cout << "Failed to open /dev/i2c-1\n";
        }

        if (ioctl(press_f_dev, I2C_SLAVE, 0x49) < 0) {
            std::cout << "Failed to set I2C slave address\n";
        }

        write_byte_simple(f_dev, 0b00000000);

        // scan();
    }

    void scan() {
        for (int i = 7; i >= 0; --i) {
            if (channel_byte & (1 << i)) {
                write_byte_simple(f_dev, (1 << i));
                int32_t ret = 0;
                
                ret = i2c_smbus_write_quick(rot_enc_f_dev, I2C_SMBUS_WRITE);
                if (ret >= 0) {
                    std::cout << i << " rotary encoder found\n";
                }
                
                ret = i2c_smbus_write_quick(press_f_dev, I2C_SMBUS_WRITE);
                if (ret >= 0) {
                    std::cout << i << " pressure sensor found\n";
                }


                // uint8_t status = read_byte(sensor_f_dev, 0x0B);
                // std::cout << toBinaryString(1 << i) << " -> " << toBinaryString(status) << std::endl;
            }
        }
        write_byte_simple(f_dev, 0b00000000);
    }

    void open_channel(int channel) {
        write_byte_simple(f_dev, (1 << channel));
    }

    void test_channel(int channel) {
        write_byte_simple(f_dev, (1 << channel));
        int32_t ret = i2c_smbus_write_quick(rot_enc_f_dev, I2C_SMBUS_WRITE);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        write_byte_simple(f_dev, 0b00000000);
    }

    // void get_sensor_data(double dt) {
    //     for (int i = 7; i >= 0; --i) {
    //         if (channel_byte & (1 << i)) {
    //             write_byte_simple(f_dev, (1 << i));
    //             uint8_t msb = read_byte(sensor_f_dev, 0x0E);
    //             uint8_t lsb = read_byte(sensor_f_dev, 0x0F);
    //             uint16_t value = (msb << 8) | lsb;
    //             data[i] = static_cast<double>(value)/1000.0;
    //         }
    //     }
    // }

    double* get_data() {
        return data;
    }
};
#endif // MUXAS5600_H
