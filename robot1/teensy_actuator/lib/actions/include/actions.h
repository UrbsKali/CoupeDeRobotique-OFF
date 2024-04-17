#include <Servo.h>
#include <Stepper.h>
#include <com.h>
#include <message.h>

extern void (*functions[256])(byte *msg, byte size);
extern void handle_callback(Com *com);
extern void servo_go_to(Servo* servo, int angle);
extern void stepper_step(Stepper* stepper, int step)

