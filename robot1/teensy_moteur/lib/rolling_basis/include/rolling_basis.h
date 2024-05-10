#include <Arduino.h>
#include <motors_driver.h>

class Rolling_Basis
{
public:
    // Rolling basis's motors
    Motor *right_motor;
    Motor *left_motor;

    // Inits function
    void init_right_motor(byte pwm, byte in2, byte in1, float correction_factor, byte threshold_pwm_value);
    void init_left_motor(byte pwm, byte in2, byte in1, float correction_factor, byte threshold_pwm_value);
    void init_motors();

    // Actions
    void rotate(uint16_t speed, bool direction);
    void vroum(uint16_t speed, bool direction);
    void l_motor(uint16_t speed, bool direction);
    void r_motor(uint16_t speed, bool direction);
    void shutdown_motor();
};