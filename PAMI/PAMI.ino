#include "com.h"

Com com(
    "DVB_CDR",
    "ROAD_T0_TOP1",

    "rc.local",
    8080,
    "/pami",

    "pami2"
);

void update(String data){
  Serial.print("############################# Data received from update function: ");
  Serial.println(data);
}

void setup() {
  com.begin();
  com.subscribe("test", update);
}

void loop() {
  com.handle();

}