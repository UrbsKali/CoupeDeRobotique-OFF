#include <Arduino.h>
#include <actions.h>
#include <Servo.h>

Com *com;
Servo* servos[48]={nullptr}; // higher than the maximum number of pin
int nb_servo = 0;
void (*functions[256])(byte *msg, byte size); // a tab a pointer to void functions

// Define a global array of Servo_Motor. Some name of variables are not allowed becaused they are used in Servo

bool is_declared(int i)
{
  if(servos[i]==nullptr) return false;
  return true;
}

void call_servo_go_to(byte *msg, byte size)
{
    msg_Servo_Go_To *servo_go_to_msg = (msg_Servo_Go_To*) msg;
    if (!is_declared(servo_go_to_msg->pin))
    {
      Servo* actuator = new Servo();
      actuator->attach(servo_go_to_msg->pin);
      servos[servo_go_to_msg->pin]=actuator;
      nb_servo ++;
    }
    servo_go_to(servos[servo_go_to_msg->pin],servo_go_to_msg->angle);
}

void setup()
{
  com = new Com(&Serial, 115200);

  // only the messages received by the teensy are listed here
  functions[SERVO_GO_TO] = &call_servo_go_to;

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
