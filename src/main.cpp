// #include <pigpiod_if2.h>
#include <iostream>
#include <chrono>
#include "scheduled_executor.h"
// #include "servo.h"
#include <vector>
// #include "MPU6050.h"
#include "channel.h"
#include <cstring>
// #include "pressure_sensor.h"
#include "mux_AS5600.h"
// #include "AS5600.h"
#include <functional>
#include "mux_pwm.h"
using namespace std::placeholders;


// bool get_mux_as5600_data(MuxAS5600& mux_as5600, double dt) {
//     mux_as5600.get_sensor_data(dt);
//     return true;
// };

// bool get_as5600_data(AS5600& as5600, double dt) {
//     as5600.get_sensor_data(dt);
//     return true;
// };

// bool get_pressure_sensor_data(PressureSensor& pressure_sensor, double dt) {
//     pressure_sensor.get_sensor_data(dt);
//     return true;
// }


// bool get_mpu6050_data(MPU6050& mpu6050, double dt) {
//     mpu6050.get_sensor_data(dt);
//     return true;
// }

// bool set_servo_values(ServoGroup& servos, double dt) {
//     servos.update_values(dt);
//     return true;
// }


// Response handle_message(
//         // MuxAS5600& mux_as5600,
//         // PressureSensor& pressure_sensor,
//         // MPU6050& mpu6050,
//         AS5600& as5600,
//         // ServoGroup& servos,
//         Message message,
//         int count
//     ) {

    
//     //     test code
//     // if ((count / 20) % 2) {
//     //     servos.update_setpoints({-1, -1, -1});
//     // } else {
//     //     servos.update_setpoints({1, 1, 1});
//     // }
//     //     end test code

//     double data = as5600.get_data();
//     std::string response = std::to_string(data);
//     char content[response.length()];
//     strcpy(content, response.c_str());
//     std::cout << "response: " << content << std::endl;
//     return Response{content, (int)response.length(), true};
// }


// --------------------- MAIN CODE --------------------- //
int main() {
    MuxPWM mux_pwm;
    // mux_pwm.set_pwm(1, 1000);
    // mux_pwm.set_pwm(2, 1000);
    // mux_pwm.set_pwm(3, 1000);
    // mux_pwm.set_pwm(4, 1000);
    // mux_pwm.set_pwm(5, 1000);
    // mux_pwm.set_pwm(6, 1000);
    // mux_pwm.set_pwm(7, 1000);
    // mux_pwm.set_pwm(8, 1000);
    // mux_pwm.set_pwm(9, 1000);
    // mux_pwm.set_pwm(10, 1000);
    // mux_pwm.set_pwm(11, 1000);
    // mux_pwm.set_pwm(12, 1000);
    // mux_pwm.set_pwm(13, 1000);
    // mux_pwm.set_pwm(14, 1000);
    // mux_pwm.set_pwm(15, 1000);
    // mux_pwm.set_pwm(16, 1000);

    int values_1[16] = {2000, 2000, 2000, 2000, 2000, 2000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000};
    int values_2[16] = {1000, 1000, 1000, 1000, 1000, 1000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000};
    // mux_pwm.ai_write(values_2);
    while (true) {
        std::cout << "writing values 1" << std::endl;
        mux_pwm.ai_write(values_1);
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));

        std::cout << "writing values 2" << std::endl;
        mux_pwm.ai_write(values_2);
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }

    // --------------------- MUX AS5600 CODE --------------------- //
    // MuxAS5600 mux_as5600(0b11111111);
//     ScheduledExecutor mux_as5600_executor(
//         std::bind(get_mux_as5600_data, std::ref(mux_as5600), _1),
//         0.001
//     );

//     // --------------------- Pressure Sensor CODE --------------------- //
//     // PressureSensor pressure_sensor;
//     // ScheduledExecutor pressure_sensor_executor(
//     //     std::bind(get_pressure_sensor_data, std::ref(pressure_sensor), _1),
//     //     0.001
//     // );

//     // --------------------- MPU6050 CODE --------------------- //
//     // MPU6050 mpu6050;
    
//     // ScheduledExecutor mpu6050_executor(
//     //     std::bind(get_mpu6050_data, std::ref(mpu6050), _1),
//     //     0.001
//     // );
        
//     // --------------------- SERVO CODE --------------------- //
    
// //     int pi = pigpio_start(nullptr, nullptr);
// //     if (pi < 0) {
// //         std::cerr << "Failed to connect to pigpiod\n";
// //         return 1;
// //     };
    
// //     std::vector<Servo> servo_list;
// //     // servo_list.emplace_back(pi, "servo1", 17, 0.18, 0.01, 0.005, -0.5, -0.2, -0.7, 0);
// //     // servo_list.emplace_back(pi, "servo2", 27, 0.18, 0.01, 0.005, -0.75, -0.5, -1, 0);
// //     // servo_list.emplace_back(pi, "servo3", 22, 0.18, 0.01, 0.005, 0, 0.2, -0.7, 0);
// //     ServoGroup servos(servo_list);
    
// //     // ScheduledExecutor servo_executor(
// //     //     std::bind(set_servo_values, std::ref(servos), _1),
// //     //     0.001
// //     // );

// //     // --------------------------------------------------------- //

// //     // servo_executor.start();
//     mux_as5600_executor.start();
//     // pressure_sensor_executor.start();
//     // as5600_executor.start();
// //     // mpu6050_executor.start();

    
    // Channel channel(
    //     8000,
    //     std::bind(handle_message, std::ref(as5600), _1, _2)
    // );
    // channel.start();
    
    // int i = 0;
    // while (true) {
    //     // i++;
    //     // if ((i / 40) % 2) {
    //     //     std::cout << "i: " << i << std::endl;
    //     //     servos.update_setpoints({-1, -1, -1});
    //     // } else {
    //     //     servos.update_setpoints({1, 1, 1});
    //     // }
    //     // std::this_thread::sleep_for(std::chrono::milliseconds(100));
    //     mux_as5600.scan();
    //     // double* data = mux_as5600.get_data();
    //     // std::string response = std::to_string(data[0]) + " " + std::to_string(data[1]) + " " + std::to_string(data[2]) + " " + std::to_string(data[3]);
    //     // char content[response.length()];
    //     // strcpy(content, response.c_str());
    //     // std::cout << "response: " << content << std::endl;
    //     // std::this_thread::sleep_for(std::chrono::seconds(1));
    // }

    
//     pigpio_stop(pi); // disconnect from daemon
//     // mpu6050_executor.stop();
    // mux_as5600_executor.stop();
    // pressure_sensor_executor.stop();
    // as5600_executor.stop();
//     // servo_executor.stop();
    return 0;
}
