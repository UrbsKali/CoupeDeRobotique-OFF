#include <Arduino.h>
#include <actions.h>
#include <Servo.h>
#include <Bonezegei_A4988.h>

Com *com;
Servo* servos[48]={nullptr}; // higher than the maximum number of pin, track using pin
Bonezegei_A4988* steppers[48]={nullptr}; // higher than the maximum number of pin, track using motor_pin_1
void (*functions[256])(byte *msg, byte size); // a tab a pointer to void functions

// Define a global array of Servo_Motor. Some name of variables are not allowed becaused they are used in Servo

bool is_servo_declared(int i)
{
  if(servos[i]==nullptr) return false;
  return true;
}

bool is_stepper_declared(int i)
{
  if(steppers[i]==nullptr) return false;
  return true;
}

void call_servo_go_to(byte *msg, byte size)
{
    msg_Servo_Go_To *servo_go_to_msg = (msg_Servo_Go_To*) msg;
    if (!is_servo_declared(servo_go_to_msg->pin))
    {
      Servo* actuator = new Servo();
      actuator->attach(servo_go_to_msg->pin);
      servos[servo_go_to_msg->pin]=actuator;
    }
    servo_go_to(servos[servo_go_to_msg->pin],servo_go_to_msg->angle);
}

void call_servo_go_to_detach(byte *msg, byte size)
{
    msg_Servo_Go_To_Detach *servo_go_to_msg = (msg_Servo_Go_To_Detach*) msg;
    Servo* actuator = new Servo();
    actuator->attach(servo_go_to_msg->pin);
    servos[servo_go_to_msg->pin]=actuator;
    servo_go_to(servos[servo_go_to_msg->pin],servo_go_to_msg->angle);
    delay(servo_go_to_msg->detach_delay);
    servos[servo_go_to_msg->pin]->detach();
}

void call_stepper_step(byte *msg, byte size)
{
    msg_Stepper_Go_To *stepper_go_to_msg = (msg_Stepper_Go_To*) msg;
    if (!is_stepper_declared(stepper_go_to_msg->pin_dir))
    {
       Bonezegei_A4988* stepper = new Bonezegei_A4988(
        stepper_go_to_msg->pin_dir,
        stepper_go_to_msg->pin_step
      );
      stepper->begin();
      steppers[stepper_go_to_msg->pin_dir]=stepper;
      pinMode(stepper_go_to_msg->pin_driver, OUTPUT);
    }
    steppers[stepper_go_to_msg->pin_dir]->setSpeed(stepper_go_to_msg->speed);
    stepper_step(
      steppers[stepper_go_to_msg->pin_dir],
      stepper_go_to_msg->steps,
      stepper_go_to_msg->dir,
      stepper_go_to_msg->pin_driver,
      stepper_go_to_msg->driver_on
      );
}


void setup()
{
  com = new Com(&Serial, 115200);

  // only the messages received by the teensy are listed here
  functions[SERVO_GO_TO] = &call_servo_go_to;
  functions[STEPPER_STEP] = &call_stepper_step;
  functions[SERVO_GO_TO_DETACH] = &call_servo_go_to_detach;

  Serial.begin(115200);
}

void loop()
{

  // Com
  handle_callback(com);
}

/*

 This code was realized by Florian BARRE
    ____ __
   / __// /___<
  / _/ / // _ \
 /_/  /_/ \___/

*/
