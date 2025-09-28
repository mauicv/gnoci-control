#include <pigpiod_if2.h>
#include <iostream>
#include <chrono>
#include "scheduled_executor.h"
#include "servo.h"
#include <vector>
#include "MPU6050.h"
#include "channel.h"
#include <cstring>


MPU6050 mpu6050;


bool get_mpu6050_data(double dt) {
    mpu6050.get_sensor_data(dt);
    return true;
}

ScheduledExecutor mpu6050_executor(
    get_mpu6050_data,
    0.001
);

Response handle_message(Message message) {
    float* data = mpu6050.get_data();
    std::string response = std::to_string(data[0]) + " " + std::to_string(data[1]) + " " + std::to_string(data[2]);
    char content[response.length()];
    strcpy(content, response.c_str());
    std::cout << "response: " << content << std::endl;
    return Response{content, (int)response.length(), true};
}

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


int main() {
    // executor.start();
    // servos.update_setpoints({0, 0});

    // for (int i = 0; i < 3; i++) {
    //     servos.update_setpoints({0, 0});
    //     std::this_thread::sleep_for(std::chrono::seconds(2)); 
    //     servos.update_setpoints({-0.4, -0.2});
    //     std::this_thread::sleep_for(std::chrono::seconds(2)); 
    // }
    // std::this_thread::sleep_for(std::chrono::seconds(2)); 


    mpu6050_executor.start();
    
    Channel channel(8000, handle_message);
    channel.start();
    
    mpu6050_executor.stop();
    
    // pigpio_stop(pi); // disconnect from daemon
    // executor.stop();
    
    return 0;
}


