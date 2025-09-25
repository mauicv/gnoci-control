#include <gtest/gtest.h>
#include "../include/servo.h"
#include <iostream>

TEST(ServoTest, PWMAssertions) {
  Servo servo(0, "servo1", 17, 0.08, 0.01, 0.005, 0, 1, -1, 0);
  EXPECT_EQ(servo.get_pwm(), 1500);
}

TEST(ServoTest, SetpointAssertions) {
  Servo servo(0, "servo1", 17, 0.08, 0.01, 0.005, 0, 1, -1, 0);
  servo.update_setpoint(0.5);
  for (int i = 0; i < 200; i++) {
    servo.update_value(1);
  }
  EXPECT_GT(servo.get_pwm(), 1999);
  EXPECT_LT(servo.get_pwm(), 2001);
}