#ifndef MUX_PWM_H
#define MUX_PWM_H


#include <iostream>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <chrono>
#include <cstdint>
#include <map>
#include "i2c_util.h"
#include <string>
#include <gpiod.h>
using std::string;

extern "C" {
	#include <linux/i2c-dev.h>
	#include <i2c/smbus.h>
}

constexpr int PRESCALE = 0b001111001;

constexpr int START_REG = 0x06;

const std::map<int, unsigned int> channel_map = {
    {1, 0x06},
    {2, 0x0A},
    {3, 0x0E},
    {4, 0x12},
    {5, 0x16},
    {6, 0x1A},
    {7, 0x1E},
    {8, 0x22},
    {9, 0x26},
    {10, 0x2A},
    {11, 0x2E},
    {12, 0x32},
    {13, 0x36},
    {14, 0x3A},
    {15, 0x3E},
    {16, 0x42}
};




class MuxPWM {
    public:
    int f_dev;
    uint8_t buf[64] = {0};
    // In MuxPWM class:
    struct gpiod_chip* chip = nullptr;
    struct gpiod_line* oe_line = nullptr;
 
    MuxPWM() {
        // initialize PCA9685 I2C bus
        f_dev = open("/dev/i2c-1", O_RDWR);
        std::cout << "f_dev: " << f_dev << std::endl;
        if (f_dev < 0) {
            std::cout << "Failed to open /dev/i2c-1\n";
        }

        if (ioctl(f_dev, I2C_SLAVE, 0x40) < 0) {
            std::cout << "Failed to set I2C slave address\n";
        }
        
        // set prescale sequence - sleep mode, prescale value write, wake up mode
        // set auto increment mode
        write_byte(f_dev, 0x00, 0b00110001);
        write_byte(f_dev, 0xFE, PRESCALE);
        int prescale = read_byte(f_dev, 0xFE);
        write_byte(f_dev, 0x00, 0b00100001);
        uint8_t mode = read_byte(f_dev, 0x00);
        
        std::cout << "prescale: " << prescale << std::endl;
        std::cout << "mode_1: " << toBinaryString(mode) << std::endl;

        init_oe();
    }
    
    
    void init_oe(int gpio_pin = 28) {
        chip = gpiod_chip_open("/dev/gpiochip0");
        oe_line = gpiod_chip_get_line(chip, gpio_pin);
        gpiod_line_request_output(oe_line, "mux_pwm_oe", 0); // start LOW (enabled)
    }
    
    void disable_output() {
        gpiod_line_set_value(oe_line, 1); // HIGH = outputs off
    }
    
    void enable_output() {
        gpiod_line_set_value(oe_line, 0); // LOW = outputs on
    }
    
    void set_pwm(int channel, int pwm) {
        // pwm vale should be in the range of 0-4095
        write_byte(f_dev, channel_map.at(channel), 0x00);
        write_byte(f_dev, channel_map.at(channel) + 1, 0x00);

        pwm = std::max(0, std::min(pwm, 4095));
        uint16_t pwm_16 = static_cast<uint16_t>(pwm);
        uint8_t pwm_H = pwm_16 >> 8;
        uint8_t pwm_L = pwm_16 & 0xFF;
        write_byte(f_dev, channel_map.at(channel) + 2, pwm_L);
        write_byte(f_dev, channel_map.at(channel) + 3, pwm_H);
    }

    void ai_write(int* values) {
        // servo values are in the range 102 to 512, center is 307
        for (int i = 0; i < 16; i++) {
            buf[i*4 + 2] = values[i] & 0xFF; // LSB
            buf[i*4 + 3] = values[i] >> 8; // MSB
        }
        i2c_smbus_write_i2c_block_data(f_dev, START_REG, 32, buf);
        i2c_smbus_write_i2c_block_data(f_dev, START_REG + 32, 32, buf + 32);
    }

    void ai_off() {
        memset(buf, 0, 64);
        for (int i = 0; i < 16; i++) {
            buf[i*4 + 3] = 0x10;  // full-off bit in OFF_H
        }
        i2c_smbus_write_i2c_block_data(f_dev, START_REG, 32, buf);
        i2c_smbus_write_i2c_block_data(f_dev, START_REG + 32, 32, buf + 32);
    }

};
#endif // MUXAS5600_H
