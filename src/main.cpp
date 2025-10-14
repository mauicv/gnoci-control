#include <pigpiod_if2.h>
#include <iostream>
#include <chrono>
#include "scheduled_executor.h"
#include "servo.h"
#include <vector>
#include "MPU6050.h"
#include "channel.h"
#include <cstring>
#include "ASD1115.h"
#include <functional>
using namespace std::placeholders;


bool get_asd1115_data(ASD1115& asd1115, double dt) {
    asd1115.get_sensor_data(dt);
    return true;
};

bool get_mpu6050_data(MPU6050& mpu6050, double dt) {
    mpu6050.get_sensor_data(dt);
    return true;
}

bool set_servo_values(ServoGroup& servos, double dt) {
    servos.update_values(dt);
    return true;
}


Response handle_message(
        ASD1115& asd1115,
        // MPU6050& mpu6050,
        ServoGroup& servos,
        Message message,
        int count
    ) {

    
//     test code
    if ((count / 20) % 2) {
        servos.update_setpoints({-1, -1, -1});
    } else {
        servos.update_setpoints({1, 1, 1});
    }
//     end test code

    double* data = asd1115.get_data();
    std::string response = std::to_string(data[0]) + " " + std::to_string(data[1]) + " " + std::to_string(data[2]) + " " + std::to_string(data[3]);
    char content[response.length()];
    strcpy(content, response.c_str());
    std::cout << "response: " << content << std::endl;
    return Response{content, (int)response.length(), true};
}


// --------------------- MAIN CODE --------------------- //
int main() {
    // --------------------- ASD1115 CODE --------------------- //
    ASD1115 asd1115;

    ScheduledExecutor asd1115_executor(
        std::bind(get_asd1115_data, std::ref(asd1115), _1),
        0.001
    );

    // --------------------- MPU6050 CODE --------------------- //
    // MPU6050 mpu6050;
    
    // ScheduledExecutor mpu6050_executor(
    //     std::bind(get_mpu6050_data, std::ref(mpu6050), _1),
    //     0.001
    // );
        
    // --------------------- SERVO CODE --------------------- //
    
    int pi = pigpio_start(nullptr, nullptr);
    if (pi < 0) {
        std::cerr << "Failed to connect to pigpiod\n";
        return 1;
    };
    
    std::vector<Servo> servo_list;
    servo_list.emplace_back(pi, "servo1", 17, 0.18, 0.01, 0.005, -0.5, -0.2, -0.7, 0);
    servo_list.emplace_back(pi, "servo2", 27, 0.18, 0.01, 0.005, -0.75, -0.5, -1, 0);
    servo_list.emplace_back(pi, "servo3", 22, 0.18, 0.01, 0.005, 0, 0.2, -0.7, 0);
    ServoGroup servos(servo_list);
    
    ScheduledExecutor servo_executor(
        std::bind(set_servo_values, std::ref(servos), _1),
        0.001
    );

    // --------------------------------------------------------- //

    servo_executor.start();
    asd1115_executor.start();
    // mpu6050_executor.start();

    
    Channel channel(
        8000,
        std::bind(handle_message, std::ref(asd1115), std::ref(servos), _1, _2)
    );
    channel.start();
    
    // int i = 0;
    // while (true) {
    //     i++;
    //     if ((i / 40) % 2) {
    //         std::cout << "i: " << i << std::endl;
    //         servos.update_setpoints({-1, -1, -1});
    //     } else {
    //         servos.update_setpoints({1, 1, 1});
    //     }
    //     std::this_thread::sleep_for(std::chrono::milliseconds(100));
    //     double* data = asd1115.get_data();
    //     std::string response = std::to_string(data[0]) + " " + std::to_string(data[1]) + " " + std::to_string(data[2]) + " " + std::to_string(data[3]);
    //     char content[response.length()];
    //     strcpy(content, response.c_str());
    //     std::cout << "response: " << content << std::endl;
    // }

    // std::this_thread::sleep_for(std::chrono::seconds(2));
    
    pigpio_stop(pi); // disconnect from daemon
    // mpu6050_executor.stop();
    asd1115_executor.stop();
    servo_executor.stop();
    return 0;
}


