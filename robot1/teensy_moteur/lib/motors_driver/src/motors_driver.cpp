#include <motors_driver.h>
#include <Arduino.h>
#include <util/atomic.h>

Motor::Motor(byte pin_forward, byte pin_backward, byte pin_pwm, byte pin_enca, byte pin_encb, float kp, float kd, float ki, float correction_factor = 1.0, byte threshold_pwm_value=0)
{   
    this->pin_forward = pin_forward;
    this->pin_backward = pin_backward;
    this->pin_pwm = pin_pwm;   // PWM pin only !


    this->correction_factor = correction_factor;
    this->threshold_pwm_value = threshold_pwm_value;
}

void Motor::init(){
    pinMode(this->pin_forward, OUTPUT);
    pinMode(this->pin_backward, OUTPUT);
    pinMode(this->pin_pwm, OUTPUT);
}

void Motor::set_motor(int8_t dir, byte pwmVal)
{
    analogWrite(this->pin_pwm, pwmVal);
    if (dir == 1)
    {
        digitalWrite(this->pin_forward, HIGH);
        digitalWrite(this->pin_backward, LOW);
    }
    else if (dir == -1)
    {
        digitalWrite(this->pin_forward, LOW);
        digitalWrite(this->pin_backward, HIGH);
    }
    else
    {
        digitalWrite(this->pin_forward, LOW);
        digitalWrite(this->pin_backward, LOW);
    }
}


void Motor::vroum(byte speed, int8_t direction){
    float power = fabs(speed * this->correction_factor);
    // Increase power (to overcome friction)
    power += this->threshold_pwm_value;

    set_motor(direction, speed);
}