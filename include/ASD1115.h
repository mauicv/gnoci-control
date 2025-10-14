#ifndef ASD1115_H
#define ASD1115_H


#include <iostream>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <chrono>
#include <cstdint>
#include <map>


#include "i2c_util.h"
#include <string>
using std::string;

static inline uint16_t bswap16(uint16_t w) { return uint16_t((w << 8) | (w >> 8)); }

extern "C" {
	#include <linux/i2c-dev.h>
	#include <i2c/smbus.h>
}

uint16_t read_word(int f_dev, uint8_t reg) {
    int32_t ret = i2c_smbus_read_word_data(f_dev, reg);
    if (ret < 0) {
        std::cout << "Error reading from ASD1115\n";
        return 0;
    }
    uint16_t word = static_cast<uint16_t>(ret);
    return word;
}


bool write_word(int f_dev, uint8_t reg, uint16_t val) {
    int32_t ret = i2c_smbus_write_word_data(f_dev, reg, val);
    if (ret < 0) {
        std::cout << "Error writing to ASD1115\n";
        return 0;
    }
    return 1;
}

std::string wordToBinaryString(uint16_t byte) {
    std::string bits;
    bits.reserve(16);

    for (int i = 15; i >= 0; --i) {
        bits.push_back((byte & (1 << i)) ? '1' : '0');
    }
    return bits;
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

class ASD1115 {
public:
    int f_dev;
    double data[4];
 
    ASD1115() {
        f_dev = open("/dev/i2c-1", O_RDWR);
        std::cout << "f_dev: " << f_dev << std::endl;
        if (f_dev < 0) {
            std::cout << "Failed to open /dev/i2c-1\n";
        }

        if (ioctl(f_dev, I2C_SLAVE, 0x48) < 0) {
            std::cout << "Failed to set I2C slave address\n";
        }
    }

    uint16_t get_rotary_data(int index)  {
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
        data[index] = static_cast<double>(value)/32767.0f;
        return value;
    }

    void get_sensor_data(double dt) {
        get_rotary_data(0);
        get_rotary_data(1);
        get_rotary_data(2);
        get_rotary_data(3);
    }

    double* get_data() {
        return data;
    }
};
#endif // ASD1115_H


// single shot on a3 - GND: 0b 10100011 1(111)0(101)
// default 0b10000011 1 000 010 1