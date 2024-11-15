/*
  WiFi UDP Send and Receive String

  This sketch waits for a UDP packet on localPort using the WiFi module.
  When a packet is received an Acknowledge packet is sent to the client on port remotePort

  created 30 December 2012
  by dlf (Metodo2 srl)

  Find the full UNO R4 WiFi Network documentation here:
  https://docs.arduino.cc/tutorials/uno-r4-wifi/wifi-examples#wi-fi-udp-send-receive-string
 */


#include <WiFiS3.h>

int status = WL_IDLE_STATUS;
#include "arduino_secrets.h" 
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;            // your network key index number (needed only for WEP)

unsigned int localPort = 2390;      // local port to listen on

char packetBuffer[256]; //buffer to hold incoming packet
char  ReplyBuffer[] = "acknowledged\n";       // a string to send back

WiFiUDP Udp;

const int tempSensorPin = A0;
const int pressureSensorPin = A1;

void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  String fv = WiFi.firmwareVersion();
  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Please upgrade the firmware");
  }

  // attempt to connect to WiFi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(10000);
  }
  Serial.println("Connected to WiFi");
  printWifiStatus();

  Serial.println("\nStarting connection to server...");
  // if you get a connection, report back via serial:
  Udp.begin(localPort);
}

void loop() {

  // if there's data available, read a packet
  int packetSize = Udp.parsePacket();
  // if (packetSize) {
  Serial.print("Received packet of size ");
  Serial.println(packetSize);
  Serial.print("From ");
  IPAddress remoteIp = "192.168.0.28";
  Serial.print(remoteIp);
  Serial.print(", port ");
  Serial.println(Udp.remotePort());

  int tempReading = analogRead(tempSensorPin);          // Read analog value
  float voltage = (tempReading / 1024.0) * 5.0;         // Convert to voltage (5V reference)
  float temperatureC = (voltage - 0.5) * 100.0;         // Convert voltage to Celsius (adjust formula if needed)
  char sendTemp[10];  // Buffer to hold the temperature string
  dtostrf(temperatureC, 4, 2, sendTemp);  // Convert float to string with 2 decimal places


  // Read Pressure Sensor
  int pressureReading = analogRead(pressureSensorPin);  // Read analog value
  float pressureVoltage = (pressureReading / 1024.0) * 5.0;  // Convert to voltage (5V reference)
  float pressure_hPa = pressureVoltage * 100;           // Adjust this formula based on sensor's specs for hPa
  char sendPres[10];  // Buffer to hold the temperature string
  dtostrf(pressure_hPa, 4, 2, sendPres);  // Convert float to string with 2 decimal places


  // read the packet into packetBuffer
  int len = Udp.read(packetBuffer, 255);
  if (len > 0) {
    packetBuffer[len] = 0;
  }
  Serial.println("Contents:");
  Serial.println(packetBuffer);

  // send a reply, to the IP address and port that sent us the packet we received
  Udp.beginPacket("192.168.0.28", 2000);
  Udp.write(sendTemp);
  Udp.endPacket();

  Udp.beginPacket("192.168.0.28", 2020);
  Udp.write(sendPres);
  Udp.endPacket();
  delay(500);
  // }
}


void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}
