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

struct msg_Stepper_Go_To
{
    byte command = STEPPER_STEP;
    int steps;           // Number of steps to turn, positive or negative define direction
    int number_of_steps; // total number of steps this motor can take
    int pin_dir;         // pin to which the direction pin is connected
    int pin_step;        // pin to which the step pin is connected   
};