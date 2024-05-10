#include <Arduino.h>
#include <com.h>

// rasp -> teensy : 0-127 (Convention)
#define VROUM 0
#define ROTATE 1
#define L_MOTOR_CONTROL 2
#define R_MOTOR_CONTROL 3
#define STOP 4


// two ways : 127 (Convention)
#define NACK 127

// teensy -> rasp : 128-255 (Convention)
#define STRING 130
#define UNKNOWN_MSG_TYPE 255

extern void (*functions[256])(byte *msg, byte size);
extern void handle_callback(Com *com);

struct msg_Unknown_Msg_Type
{
    byte command = UNKNOWN_MSG_TYPE;
    byte type_id;
};