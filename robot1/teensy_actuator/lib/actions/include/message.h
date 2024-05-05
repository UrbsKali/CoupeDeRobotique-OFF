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
    byte pin;   // pin to which the servo is connected
    byte angle; // angle to which the servo should be moved in degrees
};

struct msg_Servo_Go_To_Detach
{
    byte command = SERVO_GO_TO_DETACH;
    byte pin;   // pin to which the servo is connected
    byte angle; // angle to which the servo should be moved in degrees
    int detach_delay;  // delay in milliseconds before detaching the servo
};

struct msg_Stepper_Go_To
{
    byte command = STEPPER_STEP;
    int steps; // total number of steps this motor can take
    bool dir;  // direction of the motor
    byte pin_dir;         // pin to which the direction pin is connected
    byte pin_step;        // pin to which the step pin is connected   
};