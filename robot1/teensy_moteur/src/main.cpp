#include <Arduino.h>
#include <TimerOne.h>
#include <rolling_basis.h>
#include <util/atomic.h>
#include <messages.h>
#include <com.h>

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

void (*functions[256])(byte *msg, byte size);

extern void handle_callback(Com *com);

void handle();

void setup()
{
  com = new Com(&Serial, 115200);

  // only the messages received by the teensy are listed here
  // functions[GO_TO] = &go_to,

  Serial.begin(115200);

  // Change pwm frequency
  analogWriteFrequency(R_PWM, 40000);
  analogWriteFrequency(L_PWM, 40000);

  // Init motors
  rolling_basis_ptr->init_right_motor(R_IN1, R_IN2, R_PWM, RIGHT_MOTOR_POWER_FACTOR, 0);
  rolling_basis_ptr->init_left_motor(L_IN1, L_IN2, L_PWM, LEFT_MOTOR_POWER_FACTOR, 0);
  rolling_basis_ptr->init_motors();


  // Init motors handle timer
  //Timer1.initialize(10000);
  //Timer1.attachInterrupt(handle);
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
