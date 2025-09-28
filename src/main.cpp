#include <pigpiod_if2.h>
#include <iostream>
#include <chrono>
#include "scheduled_executor.h"
#include "servo.h"
#include <vector>
#include "MPU6050.h"

int main() {
    // int pi = pigpio_start(nullptr, nullptr);
    // if (pi < 0) {
    //     std::cerr << "Failed to connect to pigpiod\n";
    //     return 1;
    // }

    // std::vector<Servo> servo_list;
    // servo_list.emplace_back(pi, "servo1", 17, 0.08, 0.01, 0.005, 0, 0.2, -1, 0);
    // servo_list.emplace_back(pi, "servo2", 27, 0.08, 0.01, 0.005, 0, 0.7, -1, 0);
    // ServoGroup servos(servo_list);

    // ScheduledExecutor executor(
    //     [&](double dt) {
    //         servos.update_values(dt);
    //         return true;
    //     },
    //     0.001
    // );

    // executor.start();
    // servos.update_setpoints({0, 0});
    // // for (int i = 0; i < 3; i++) {
    // //     servos.update_setpoints({0, 0});
    // //     std::this_thread::sleep_for(std::chrono::seconds(2)); 
    // //     servos.update_setpoints({-0.4, -0.2});
    // //     std::this_thread::sleep_for(std::chrono::seconds(2)); 
    // // }
    // std::this_thread::sleep_for(std::chrono::seconds(2)); 
    // pigpio_stop(pi); // disconnect from daemon
    // executor.stop();

    MPU6050 mpu6050;
    ScheduledExecutor mpu6050_executor(
        [&](double dt) {
            mpu6050.get_sensor_data(dt);
            return true;
        },
        0.001
    );
    mpu6050_executor.start();

    for (int i = 0; i < 100; i++) {
        float* data = mpu6050.get_data();
        std::cout << "acc: " << data[0] << " " << data[1] << " " << data[2] << std::endl;
        std::cout << "gyro: " << data[3] << " " << data[4] << " " << data[5] << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    mpu6050_executor.stop();
    return 0;
}


