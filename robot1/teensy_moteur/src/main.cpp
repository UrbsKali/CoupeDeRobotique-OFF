#include <Arduino.h>
#include <TimerOne.h>
#include <rolling_basis.h>
#include <util/atomic.h>
#include <messages.h>


#define RIGHT_MOTOR_POWER_FACTOR 1.0
#define LEFT_MOTOR_POWER_FACTOR 1.0

// Creation Rolling Basis
// Motor Left
#define L_PWM 5
#define L_IN2 4
#define L_IN1 3

// Motor Right
#define R_PWM 2
#define R_IN2 0
#define R_IN1 1

Rolling_Basis *rolling_basis_ptr = new Rolling_Basis();

/* Strat part */
Com *com;

void vroum(byte *msg, byte size)
{
  msg_VROUM *vroum = (msg_VROUM *)msg;
  rolling_basis_ptr->vroum(vroum->speed, vroum->direction);
}

void rotate(byte *msg, byte size)
{
  msg_ROTATE *rotate = (msg_ROTATE *)msg;
  rolling_basis_ptr->rotate(rotate->speed, rotate->direction);
}

void l_motor(byte *msg, byte size)
{
  msg_L_MOTOR *l_motor = (msg_L_MOTOR *)msg;
  rolling_basis_ptr->l_motor(l_motor->speed, l_motor->direction);
}

void r_motor(byte *msg, byte size)
{
  msg_R_MOTOR *r_motor = (msg_R_MOTOR *)msg;
  rolling_basis_ptr->r_motor(r_motor->speed, r_motor->direction);
}

void stop(byte *msf, byte size){
   rolling_basis_ptr->shutdown_motor();
}

void (*functions[256])(byte *msg, byte size);

extern void handle_callback(Com *com);

void setup()
{
  com = new Com(&Serial, 115200);

  // only the messages received by the teensy are listed here
  functions[VROUM] = &vroum;
  functions[ROTATE] = &rotate;
  functions[L_MOTOR_CONTROL] = &l_motor;
  functions[R_MOTOR_CONTROL] = &r_motor;
  functions[STOP] = &stop;

  Serial.begin(115200);

  // Change pwm frequency
  analogWriteFrequency(R_PWM, 40000);
  analogWriteFrequency(L_PWM, 40000);

  // Init motors
  rolling_basis_ptr->init_right_motor(R_IN1, R_IN2, R_PWM, RIGHT_MOTOR_POWER_FACTOR, 0);
  rolling_basis_ptr->init_left_motor(L_IN1, L_IN2, L_PWM, LEFT_MOTOR_POWER_FACTOR, 0);
  rolling_basis_ptr->init_motors();

  // Init motors handle timer
  // Timer1.initialize(10000);
  // Timer1.attachInterrupt(handle);
}

void loop()
{
  // Com
  handle_callback(com);
}

/*
 This code was distroyed by Urbain
          _____                    _____                    _____                    _____                    _____
         /\    \                  /\    \                  /\    \                  /\    \                  /\    \
        /::\____\                /::\    \                /::\    \                /::\    \                /::\    \
       /:::/    /               /::::\    \              /::::\    \              /::::\    \               \:::\    \
      /:::/    /               /::::::\    \            /::::::\    \            /::::::\    \               \:::\    \
     /:::/    /               /:::/\:::\    \          /:::/\:::\    \          /:::/\:::\    \               \:::\    \
    /:::/    /               /:::/__\:::\    \        /:::/__\:::\    \        /:::/__\:::\    \               \:::\    \
   /:::/    /               /::::\   \:::\    \      /::::\   \:::\    \      /::::\   \:::\    \              /::::\    \
  /:::/    /      _____    /::::::\   \:::\    \    /::::::\   \:::\    \    /::::::\   \:::\    \    ____    /::::::\    \
 /:::/____/      /\    \  /:::/\:::\   \:::\____\  /:::/\:::\   \:::\ ___\  /:::/\:::\   \:::\    \  /\   \  /:::/\:::\    \
|:::|    /      /::\____\/:::/  \:::\   \:::|    |/:::/__\:::\   \:::|    |/:::/  \:::\   \:::\____\/::\   \/:::/  \:::\____\
|:::|____\     /:::/    /\::/   |::::\  /:::|____|\:::\   \:::\  /:::|____|\::/    \:::\  /:::/    /\:::\  /:::/    \::/    /
 \:::\    \   /:::/    /  \/____|:::::\/:::/    /  \:::\   \:::\/:::/    /  \/____/ \:::\/:::/    /  \:::\/:::/    / \/____/
  \:::\    \ /:::/    /         |:::::::::/    /    \:::\   \::::::/    /            \::::::/    /    \::::::/    /
   \:::\    /:::/    /          |::|\::::/    /      \:::\   \::::/    /              \::::/    /      \::::/____/
    \:::\__/:::/    /           |::| \::/____/        \:::\  /:::/    /               /:::/    /        \:::\    \
     \::::::::/    /            |::|  ~|               \:::\/:::/    /               /:::/    /          \:::\    \
      \::::::/    /             |::|   |                \::::::/    /               /:::/    /            \:::\    \
       \::::/    /              \::|   |                 \::::/    /               /:::/    /              \:::\____\
        \::/____/                \:|   |                  \::/____/                \::/    /                \::/    /
         ~~                       \|___|                   ~~                       \/____/                  \/____/
*/
