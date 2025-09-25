#ifndef SERVO_H
#define SERVO_H

#include <vector>
#include <MiniPID.h>

#define SERVO_PWM_THRESHOLD_MIN 500
#define SERVO_PWM_THRESHOLD_MAX 2500
#define HALF_RANGE (SERVO_PWM_THRESHOLD_MAX - SERVO_PWM_THRESHOLD_MIN) / 2


class Servo {
public:
    std::string name;
    int pin;
    MiniPID pid;
    double setpoint;
    double upper_limit;
    double lower_limit;
    double value;
    double offset;

    Servo(
        std::string name,
        int pin,
        double p,
        double i,
        double d,
        double setpoint,
        double upper_limit,
        double lower_limit,
        double offset
    ): 
        pid(p, i, d),
        name(name),
        pin(pin),
        setpoint(setpoint),
        upper_limit(upper_limit),
        lower_limit(lower_limit),
        offset(offset)
    {
        pid.setOutputLimits(-1, 1);
        pid.setSetpoint(setpoint);
        value = setpoint;
    }

    void update_value() {
        value += pid.getOutput(value, setpoint);
        value = std::max(lower_limit, std::min(value, upper_limit));
    };

    void update_setpoint(double setpoint) {
        this->setpoint = setpoint;
        pid.setSetpoint(setpoint);
    }

    double get_pwm() {
        double pwm_val = (value + 1) * HALF_RANGE + SERVO_PWM_THRESHOLD_MIN;
        pwm_val = std::max<double>(
            SERVO_PWM_THRESHOLD_MIN,
            std::min<double>(
                pwm_val,
                SERVO_PWM_THRESHOLD_MAX
            )
        );
        return pwm_val;
    }
};


class ServoGroup {
public:
    std::vector<Servo>& servos;
    ServoGroup(
        std::vector<Servo>& servos
    ): servos(servos) {}

    void update_values() {
        for (auto& servo : servos) {
            servo.update_value();
        }
    };

    void update_setpoints(std::vector<double> setpoints) {
        for (int i = 0; i < servos.size(); i++) {
            servos[i].update_setpoint(setpoints[i]);
        }
    }
};

#endif // SERVO_H
