#ifndef SCHEDULED_EXECUTOR_H
#define SCHEDULED_EXECUTOR_H

#include <functional>
#include <atomic>
#include <thread>

using update_function = std::function<bool(double)>;

class ScheduledExecutor {
public:
    ScheduledExecutor(
        const update_function& callback,
        double period
    ):
        callback_(callback),
        keep_running_(false)
    {
        period_ = std::chrono::duration<double>(period);
    };

    void start() {
        keep_running_ = true;
        period_count_ = 0;
        thread_ = std::thread(&ScheduledExecutor::loop, this);
    }

    void stop(){
        keep_running_ = false;
        try {
            thread_.join();
        }
        catch(const std::system_error& /* e */)
        { }
    };


private:
    static constexpr double MinSleepTime = 1E-9;
    typedef std::chrono::high_resolution_clock clock;
    typedef std::chrono::duration<double, std::ratio<1>> duration;

    std::function<bool(double)> callback_;
    duration period_;
    std::atomic<bool> keep_running_;
    std::thread thread_;
    unsigned long period_count_;


    void loop() {
        clock::time_point start = clock::now();
        while (keep_running_) {
            clock::time_point call_start = clock::now();
            if (period_count_ > 0 && !callback_(period_.count())) 
                break;
            clock::time_point call_end = clock::now();
            duration call_duration = call_end - call_start;
            duration sleep_duration = period_ - call_duration;
            period_count_++;
            if (sleep_duration.count() > MinSleepTime) {
                std::this_thread::sleep_for(sleep_duration);
            }
        }
    }
};


#endif // SCHEDULED_EXECUTOR_H