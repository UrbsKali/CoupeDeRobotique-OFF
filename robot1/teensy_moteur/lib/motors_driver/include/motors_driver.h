#include <Arduino.h>

// Motor class
class Motor {

private:
    // Pins Motor
    byte pin_forward;
    byte pin_backward;
    byte pin_pwm;  // PWM pin only !

    
public:
    // Correction speed factor
    float correction_factor;
    byte threshold_pwm_value;
    
    // Constructor
    Motor(byte pin_forward, byte pin_backward, byte pin_pwm, float correction_factor, byte threshold_pwm_value);

    // Methods
    void init();
    void set_motor(int8_t dir, byte pwmVal);
    void vroum(uint16_t speed, bool direction);
};