#ifndef SCHEDULED_EXECUTOR_H
#define SCHEDULED_EXECUTOR_H

class ScheduledExecutor {
public:
    ScheduledExecutor(){}
    ScheduledExecutor(
        // const std::function<bool(double)>& callback,
        double period
    ){
        initialize(period);
    }
    void initialize(
        // const std::function<bool(double)>& callback,
        double period
    ){
        period_ = period;
    };
    void start();
    double period(){
        std::cout << "period: " << period_ << std::endl;
        return period_;
    };

private:
    // std::function<bool(double)> callback_;
    double period_;
    // std::atomic<bool> keep_running_;
};


#endif // SCHEDULED_EXECUTOR_H