#include <gtest/gtest.h>
#include "../include/servo.h"
#include <iostream>

TEST(ServoTest, GroupAssertions) {
    std::vector<Servo> servo_list;
    servo_list.emplace_back("servo1", 17, 0.08, 0.01, 0.005, 0, 1, -1, 0);
    servo_list.emplace_back("servo2", 27, 0.08, 0.01, 0.005, 0, 1, -1, 0);
    ServoGroup servos(servo_list);
    servos.update_setpoints({0.5, -0.5});
    for (int i = 0; i < 200; i++) {
        servos.update_values();
    }
    EXPECT_GT(servo_list[0].get_pwm(), 1999);
    EXPECT_LT(servo_list[0].get_pwm(), 2001);
    EXPECT_GT(servo_list[1].get_pwm(), 999);
    EXPECT_LT(servo_list[1].get_pwm(), 1001);
}
