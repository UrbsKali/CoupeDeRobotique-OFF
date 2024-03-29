#include "com.h"

#pragma region Channel
// Constructor
Channel::Channel(const String &topic_path, void (*function)(String data), const String &state)
{
    this->topic_path = topic_path;
    this->function = function;
    this->state = state;
}


// Static: Method(s)
Channel Channel::deep_copy(const Channel &channel_to_copy)
{
    return Channel(channel_to_copy.topic_path, channel_to_copy.function, channel_to_copy.state);
}


Channel *Channel::push_channel_to_array(Channel *old_ptr, const Channel &channel_to_push, unsigned short new_size)
{
    Channel *new_ptr;

    // If no element in the array
    if (new_size - 1 == 0)
        new_ptr = (Channel *)calloc(new_size, sizeof(Channel));
    else
    {
        new_ptr = (Channel *)calloc(new_size, sizeof(Channel));
        for (unsigned short k = 0; k < new_size - 1; k++)
            new_ptr[k] = Channel::deep_copy(old_ptr[k]);

        free(old_ptr);
    }

    // Add the new channel to the new_ptr
    new_ptr[new_size - 1] = Channel::deep_copy(channel_to_push);

    return new_ptr;
}


void Channel::handle_channel_array(Channel *channels_ptr, unsigned short nb_channels, const String &topic, String &state)
{
    for (unsigned short k = 0; k < nb_channels; k++)
    {
        if (channels_ptr[k].topic_path == topic)
        {
            // Check if the state has changed
            if (String(channels_ptr[k].state) != state)
            {
                channels_ptr[k].function(state);
                channels_ptr[k].state = state;
            }
        }
    }
} 

#pragma endregion

#pragma Server_Manager
Server_Manager::Server_Manager(
        const char *ssid,
        const char *password,

        const char* server,
        int server_port,
        const char* root_path,

        const char* username
    )
{
    // WiFi
    this->ssid = ssid;
    this->password = password;

    // Server connection
    this->server = server;
    this->server_port = server_port;
    this->root_path = root_path;

    this->username = username;
}

void Server_Manager::ws_event(WStype_t type, uint8_t * payload, size_t length)
{
    switch (type) {
        case WStype_DISCONNECTED:
            #ifdef WS_COM_DEBUG    
                Serial.printf("[WebSocket] Disconnected!\n");
            #endif     
            break;

        case WStype_CONNECTED:
            #ifdef WS_COM_DEBUG    
                Serial.printf("[WebSocket] Connected!\n");
            #endif  
            break;

        case WStype_TEXT:
            #ifdef WS_COM_DEBUG    
                Serial.printf("[WebSocket] New message: %s\n", payload);
            #endif  
            // Save the received message
            this->last_message = String((char *)payload);

            // 2 cases: 
            // 1. The message is a new value from a channel
            // 2. The message is a response to a request
            
            // 1. The message is a new value from a channel
            // If the message contains "type": "subscription_callback" it is a new value from a channel
            // Deserialize the message to get the type
            StaticJsonDocument<JSON_RESPONSE_SIZE> json_message;     
            DeserializationError error = deserializeJson(json_message, this->last_message);

            #ifdef WS_COM_DEBUG 
                if (error) {
                  Serial.print("deserializeJson() failed: ");
                  Serial.println(error.c_str());
                  break;
                } 
            #endif  

            // Decode the incoming message according to this format:
            // {
            //    "sender": str,
            //    "msg": str,
            //    "data": any,
            //    "ts": int  (Optionnal)
            // }

            // Check we receive a valid message
            if (json_message.containsKey("sender") && json_message.containsKey("msg") && json_message.containsKey("data"))  {
                // Get the topic and state
                String topic = json_message["msg"];
                String state = json_message["data"];

                Channel::handle_channel_array(this->channels_ptr, this->nb_channels, topic, state);
            }
            else
            {
              #ifdef WS_COM_DEBUG 
                Serial.print("Unvalid message received !");
              #endif  
            }

            break;    
    }
}

void Server_Manager::send_request(String request)
{
    #ifdef WS_COM_DEBUG    
      Serial.print("New Request: ");
      Serial.println(request);
    #endif  
    this->ws_client.sendTXT(request);
}

void Server_Manager::begin()
{
    // Connect to WiFi
    #ifdef WS_COM_DEBUG    
        Serial.println();
        Serial.print("Connecting to ");
        Serial.println(this->ssid);
    #endif  
    WiFi.begin(this->ssid, this->password);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        #ifdef WS_COM_DEBUG    
            Serial.print(".");
        #endif  
    }

    #ifdef WS_COM_DEBUG    
        Serial.println("");
        Serial.println("WiFi connected");
        Serial.println("IP address: ");
        Serial.println(WiFi.localIP());
    #endif  

    // Connect to WS
    this->ws_client.begin(this->server, this->server_port, this->root_path + String("?sender=") + this->username);
    this->ws_client.onEvent([this](WStype_t type, uint8_t * payload, size_t length) {
        this->ws_event(type, payload, length);
    });
    this->ws_client.setReconnectInterval(5000);
}

void Server_Manager::handle(uint16_t wait)
{
    this->ws_client.loop();
    delay(wait);
}

void Server_Manager::add_channel(const String &topic_path, void (*function)(String data))
{
    this->nb_channels++;
    this->channels_ptr = Channel::push_channel_to_array(
        this->channels_ptr,
        Channel(topic_path, (*function)),
        this->nb_channels);
}
#pragma endregion

#pragma Com
Com::Com(
    const char *ssid,
    const char *password,

    const char* server,
    int server_port,
    const char* root_path,

    const char* username)
{
    this->server_ptr = new Server_Manager(
        ssid,
        password,

        server,
        server_port,
        root_path,

        username
    );
}
// Public method(s)
void Com::begin()
{
    // Init Serial
    #ifdef WS_COM_DEBUG  
        if (!Serial)  
            Serial.begin(DEFAULT_SERIAL_BAUDRATE);
    #endif  

    // Init WiFi connection
    this->server_ptr->begin();
}


void Com::handle()
{
    this->server_ptr->handle();
}

void Com::subscribe(const String &topic_path, void (*function)(String data))
{
    this->server_ptr->add_channel(topic_path, function);
}

#pragma endregion










