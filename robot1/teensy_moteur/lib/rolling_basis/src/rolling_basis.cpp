#include <rolling_basis.h>
#include <Arduino.h>
#include <util/atomic.h>


// Methods
// Inits function
void Rolling_Basis::init_right_motor(byte pwm, byte in2, byte in1, float correction_factor = 1.0, byte threshold_pwm_value = 0)
{
    this->right_motor = new Motor(pwm, in2, in1, correction_factor, threshold_pwm_value);
}

void Rolling_Basis::init_left_motor(byte pwm, byte in2, byte in1, float correction_factor = 1.0, byte threshold_pwm_value = 0)
{
    this->left_motor = new Motor(pwm, in2, in1, correction_factor, threshold_pwm_value);
}

void Rolling_Basis::init_motors()
{
    this->right_motor->init();
    this->left_motor->init();
}

void Rolling_Basis::shutdown_motor()
{
    this->right_motor->set_motor(1, 0);
    this->left_motor->set_motor(1, 0);
}
