#pragma pack(1)
#include <Arduino.h>
#include <commands.h>

struct msg_VROUM
{
    byte command = VROUM;
    uint16_t speed;
    bool direction;
};

struct msg_ROTATE
{
    byte command = ROTATE;
    uint16_t speed;
    bool direction;
};

struct msg_L_MOTOR
{
    byte command = L_MOTOR_CONTROL;
    uint16_t speed;
    bool direction;
};

struct msg_R_MOTOR
{
    byte command = R_MOTOR_CONTROL;
    uint16_t speed;
    bool direction;
};

struct msg_STOP
{
    byte command = STOP;
};
