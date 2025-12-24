#ifndef I2C_UTIL_H
#define I2C_UTIL_H

#include <iostream>
#include <sys/ioctl.h>
#include <fcntl.h>

#include <cstdint>

#include <string>
using std::string;


extern "C" {
	#include <linux/i2c-dev.h>
	#include <i2c/smbus.h>
}

static inline uint16_t bswap16(uint16_t w) { return uint16_t((w << 8) | (w >> 8)); }

std::string toBinaryString(uint8_t byte) {
    std::string bits;
    bits.reserve(8);

    for (int i = 7; i >= 0; --i) {
        bits.push_back((byte & (1 << i)) ? '1' : '0');
    }
    return bits;
}

std::string wordToBinaryString(uint16_t byte) {
    std::string bits;
    bits.reserve(16);

    for (int i = 15; i >= 0; --i) {
        bits.push_back((byte & (1 << i)) ? '1' : '0');
    }
    return bits;
}

std::string bit32ToBinaryString(uint32_t byte) {
    std::string bits;
    bits.reserve(32);

    for (int i = 31; i >= 0; --i) {
        bits.push_back((byte & (1 << i)) ? '1' : '0');
    }
    return bits;
}

uint8_t read_byte(int f_dev, uint8_t reg) {
    int32_t ret = i2c_smbus_read_byte_data(f_dev, reg);
    if (ret < 0) {
        std::cout << "Error reading from ASD1115\n";
        return 0;
    }
    uint8_t byte = static_cast<uint8_t>(ret);
    return byte;
}

uint8_t write_byte(int f_dev, uint8_t reg, uint8_t val) {
    int32_t ret = i2c_smbus_write_byte_data(f_dev, reg, val);
    if (ret < 0) {
        std::cout << "Error writing to ASD1115\n";
        return 0;
    }
    return 1;
}

bool read_block(int f_dev, uint8_t reg, uint8_t* data, uint8_t length) {
    int32_t ret = i2c_smbus_read_i2c_block_data(f_dev, reg, length, data);
    if (ret < 0) {
        std::cout << "Error reading from ASD1115\n";
        return false;
    }
    return true;
}

uint16_t read_word(int f_dev, uint8_t reg) {
    int32_t ret = i2c_smbus_read_word_data(f_dev, reg);
    if (ret < 0) {
        std::cout << "Error reading from TCA9548A\n";
        return 0;
    }
    uint16_t word = static_cast<uint16_t>(ret);
    return word;
}


bool write_word(int f_dev, uint8_t reg, uint16_t val) {
    int32_t ret = i2c_smbus_write_word_data(f_dev, reg, val);
    if (ret < 0) {
        std::cout << "Error writing to TCA9548A\n";
        return 0;
    }
    return 1;
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


#endif // I2C_UTIL_H