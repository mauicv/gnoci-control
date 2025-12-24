#ifndef PRESSURE_SENSOR_H
#define PRESSURE_SENSOR_H


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

const std::map<int, unsigned int> pin_config_map = {
    {0, 0b0000000001000000},
    {1, 0b0000000001010000},
    {2, 0b0000000001100000},
    {3, 0b0000000001110000},
};

const std::map<int, unsigned int> SR_config_map = {
    {8, 0b0000000000000000},
    {16, 0b0010000000000000},
    {32, 0b0100000000000000},
    {64, 0b0110000000000000},
    {128, 0b1000000000000000},
    {250, 0b1010000000000000},
    {475, 0b1100000000000000},
    {860, 0b1110000000000000}
};

const std::map<int, unsigned int> config_map = {
    {0, 0b1110001111000011},
    {1, 0b1110001111010011},
    {2, 0b1110001111100011},
    {3, 0b1110001111110011}
};

class PressureSensor {
public:
    int f_dev;
    double data;
 
    PressureSensor() {
        f_dev = open("/dev/i2c-1", O_RDWR);
        std::cout << "f_dev: " << f_dev << std::endl;
        if (f_dev < 0) {
            std::cout << "Failed to open /dev/i2c-1\n";
        }

        if (ioctl(f_dev, I2C_SLAVE, 0x49) < 0) {
            std::cout << "Failed to set I2C slave address\n";
        }
    }

    uint16_t get_ADC_data(int index)  {
        write_word(f_dev, 0x01, config_map.at(index));
        while ((read_word(f_dev, 0x01) & 0b0000000010000000) == 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(2)); 
        }
        uint16_t raw = read_word(f_dev, 0x00);
        std::this_thread::sleep_for(std::chrono::milliseconds(2)); 
        raw = read_word(f_dev, 0x00);
        raw = static_cast<uint16_t>((raw << 8) | (raw >> 8));
        int16_t value = static_cast<int16_t>(raw);
        // std::cout << "new_value: " << new_value << std::endl;
        data = static_cast<double>(value)/32767.0f;
        return data;
    }

    void get_sensor_data(double dt) {
        get_ADC_data(0);
    }

    double get_data() {
        return data;
    }
};
#endif // PRESSURE_SENSOR_H


// single shot on a3 - GND: 0b 10100011 1(111)0(101)
// default 0b10000011 1 000 010 1