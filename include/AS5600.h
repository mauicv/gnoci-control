#ifndef AS5600_H
#define AS5600_H


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

class AS5600 {
public:
    int f_dev;
    double data;
 
    AS5600(){
        // initialize TCA9548A I2C bus
        f_dev = open("/dev/i2c-1", O_RDWR);
        std::cout << "f_dev: " << f_dev << std::endl;
        if (f_dev < 0) {
            std::cout << "Failed to open /dev/i2c-1\n";
        }

        if (ioctl(f_dev, I2C_SLAVE, 0x36) < 0) {
            std::cout << "Failed to set I2C slave address\n";
        }

        scan();
    }

    void scan() {
        uint8_t status = read_byte(f_dev, 0x0B);
        std::cout << toBinaryString(status) << std::endl;
    }

    void get_sensor_data(double dt) {
        uint8_t msb = read_byte(f_dev, 0x0E);
        uint8_t lsb = read_byte(f_dev, 0x0F);
        uint16_t value = (msb << 8) | lsb;
        data = static_cast<double>(value)/1000.0;
    }

    double get_data() {
        return data;
    }
};
#endif // AS5600_H
