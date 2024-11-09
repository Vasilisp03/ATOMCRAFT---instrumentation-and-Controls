#include <WiFiS3.h>

const char* ssid     = "Optus_540FC8";
const char* password = "lased29799mq";

const char* serverIP = "192.168.0.28"; // Replace X with your Mac's IP address
const int serverPort = 8080;          // Port to send data to

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Connect to Wi-Fi network
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  // Wait until connected
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected to Wi-Fi.");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  WiFiClient client;

  if (client.connect(serverIP, serverPort)) {
    Serial.println("Connected to server.");
    client.println("Hello from the Arduino Uno R4 Wifi");
    client.stop();
  } else {
    Serial.println("Connection to server failed.");
  }

  delay(10000); // Wait 10 seconds before sending again
}
