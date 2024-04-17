#pragma pack(1)
// dans nos structures, nous avons des variables plus petites que la taille
// défaut du processeur (processeur 32 bits et variables 8 bits de type byte)
// cela indique au compilateur de ne pas ajouter de padding entre les variables
// (pack(1) indique que la taille de l'alignement est de 1 octet)

#include <Arduino.h>
#include <commands.h>

struct msg_Unknown_Msg_Type
{
    byte command = UNKNOWN_MSG_TYPE;
    byte type_id;
};

struct msg_Servo_Go_To
{
    byte command = SERVO_GO_TO;
    byte pin;
    byte angle;
};

struct msg_Stepper_Go_To
{
    byte command = STEPPER_GO_TO;
    int steps;    // Number of steps to turn, positive turn towrd direction,negative opposite one
    int motor_pin_1;
    int motor_pin_2;
    int motor_pin_3;
    int motor_pin_4; // 4 pins to control our stepper motor, can change to 2 or 5     
    int direction;  // Direction of rotation
    int number_of_steps;    // total number of steps this motor can take
};