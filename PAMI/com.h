#include <Arduino.h>

#define WS_COM_DEBUG

#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <Arduino.h>

#define DEFAULT_SERIAL_BAUDRATE 115200
#define JSON_RESPONSE_SIZE 200


class Channel
{
public:
    // Attributes
    String topic_path;
    String state;
    void (*function)(String data);

    // Constructor
    Channel(const String &topic_path, void (*function)(String data), const String &state = String("default value"));

    // Static Methods
    // Alloc memory to add a new channel to the pointer
    static Channel deep_copy(const Channel &channel_to_copy);
    static Channel *push_channel_to_array(Channel *old_ptr, const Channel &channel_to_push, unsigned short new_size);

    // Handle channels array
    static void handle_channel_array(Channel *channels_ptr, unsigned short nb_channels, const String &topic, String &state);
};



class Server_Manager
{
private:
    // WiFi
    const char *ssid;
    const char *password;

    // Server connection
    const char* server;
    int server_port;
    const char* root_path;

    // WiFi and WS client object
    WiFiClient wifi_client;
    WebSocketsClient ws_client;

    // WS event
    void ws_event(WStype_t type, uint8_t * payload, size_t length);
    String last_message;

    // Channels pointer to handle the channel when a new value is received
    Channel *channels_ptr;
    unsigned short nb_channels = 0;

    // Tools
   
    void send_request(String request);

public:
    // Attributes
    const char* username;

    // Constructor
    Server_Manager(
        const char *ssid,
        const char *password,

        const char* server,
        int server_port,
        const char* root_path,

        const char* username
    );

    // Start the server connection
    void begin();

    // Interact with the server
    void handle(uint16_t wait = 0);
    void add_channel(const String &topic_path, void (*function)(String data));
    
    // Api methods
    //void send(const String &topic_path, String *get_data);
};


class Com {

private:
  // Tools pointers
  Server_Manager *server_ptr;

public:
// Constructor
    Com(
        const char *ssid,
        const char *password,

        const char* server,
        int server_port,
        const char* root_path,

        const char* username
      );

    // Methods
    void begin();
    void handle();
    void subscribe(const String &topic_path, void (*function)(String data));

};