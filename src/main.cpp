#include <pigpiod_if2.h>
#include <iostream>
#include <thread>
#include <chrono>
#include "scheduled_executor.h"
#include "servo.h"
#include <vector>


// MiniPID pid1=MiniPID(.08,.01,.005);
// MiniPID pid2=MiniPID(.08,.01,.005);



// void setup(int pi){
// 	pid1.setOutputLimits(-1,1);
// 	pid1.setOutputRampRate(10);
// 	pid2.setOutputLimits(-1,1);
// 	pid2.setOutputRampRate(10);

// 	set_mode(pi, 17, PI_OUTPUT);
// 	set_mode(pi, 27, PI_OUTPUT);
// }

int main() {
    // int pi = pigpio_start(nullptr, nullptr);
    // if (pi < 0) {
    //     std::cerr << "Failed to connect to pigpiod\n";
    //     return 1;
    // }
    

    std::vector<Servo> servo_list;
    servo_list.emplace_back("servo1", 17, 0.08, 0.01, 0.005, 0, 1, -1, 0);
    servo_list.emplace_back("servo2", 27, 0.08, 0.01, 0.005, 0, 1, -1, 0);
    ServoGroup servos(servo_list);

    // ScheduledExecutor executor;
    // std::cout << "period: " << executor.period() << std::endl;

    for (int i = 0; i < 100; i++) {
        servos.update_values();
        servos.update_setpoints({0.4, 0.4});
        std::cout << "pwm1: " << servos.servos[0].get_pwm() << " pwm2: " << servos.servos[1].get_pwm() << std::endl;
    }

    // setup(pi);
    // set_servo_pulsewidth(pi, 17, 1500);
    // set_servo_pulsewidth(pi, 27, 1500);
    // std::cout << "Starting main loop" << std::endl;
    // pigpio_stop(pi); // disconnect from daemon


    return 0;
}


