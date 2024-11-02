// ******************************************************
//  Written by Luke Pan z5420133
//  Program to test H-bridge and moonitor PID controller 
//  - Atomcraft
//
// ******************************************************

// PIN Constants and Definitions
constexpr int TRIGGER = 2;
constexpr int PWMPIN_1 = 5;
constexpr int PWMPIN_2 = 11;
constexpr float MAX_CURRENT = 0.8;
constexpr int HALL_SENSOR_PIN = A0;

// Hall sensor variables
int sensorOffset =  0;

// Set PWM frequency/period (microsecs) and duty cycle for the TF coil
float dutyCycle = 0;

// Declare PID variables
float error = 0;
float errorSum = 0;
float errorDif = 0;
float oldError = 0;

float rawVal = 0;
float currentVal = 0;
float currentValDamped = 0;
float refVal = 0;

float kp = 5;
float ki = 0.00010;
float kd = 0;

float sampTimeBegin = 0;
float sampTimeEnd = 0;
float sampPeriod = 0;

int executePulse = 0;
int pulseStarted = 0;
int pulseTimeStart = 0;
int pulseTime = 0;

int timeStep = 0;
int oldTimeStep = 0;

// Declare data logging array
constexpr unsigned int MAX_ARRAY_SIZE = 50;
float currentData[MAX_ARRAY_SIZE];
float PWMData[MAX_ARRAY_SIZE];

// Debugging variables
int count = 0;
bool setTrigger = false;

// Setup
void setup() {
  Serial.begin(115200);

  // Set pin modes
  pinMode (TRIGGER, INPUT);      // Button to start pulse
  pinMode (PWMPIN_1, OUTPUT);    // Timer 2 "B" output: OC2B
  pinMode (PWMPIN_2, OUTPUT);    // Timer 2 "A" output: OC2A
  
  // Set OC2A on Compare Match when up-counting.
  // Clear OC2B on Compare Match when up-counting.
  // Some bit-selecting to configure the off phase PWM signals on the arduino (need to use two timers)
  TCCR2A = bit (WGM20) | bit (COM2B1) | bit (COM2A1) | bit (COM2A0);
  TCCR2B = bit (CS10);         // phase correct PWM, prescaler of 8

  TCCR0A = bit (WGM20) | bit (COM2B1) | bit (COM2A1) | bit (COM2A0);       
  TCCR0B = bit (CS10);         // phase correct PWM, prescaler of 8
  // Inverts signal (i think??)
  TCCR0A = 0b10110000 | (TCCR0A & 0b00001111);

  // Calibrate sensor
  sensorOffset = calibrateHallSensor();
  Serial.println("Running...");
}

// Enable PWM output for the TF coil
void loop() {
  // Get current measurement and convert
  rawVal = (analogRead(HALL_SENSOR_PIN) - sensorOffset);
  //currentVal = -(((rawVal - 512) / 1024) * 5.0 / 0.186);
  currentVal = -(((rawVal - 380) / 760) * 3.3 / 0.0624); // Gains for the On-Board H-bridge current sensor
  currentValDamped =  currentVal;

  // Set reference current
  executePulse = digitalRead(TRIGGER);
  if (executePulse == HIGH & pulseStarted == LOW) {
    pulseTimeStart = millis() / 32; // We modified timer so need to adjust millis
    pulseStarted = HIGH;
    count = 0;
  }
  if (pulseStarted == HIGH) {
    pulseTime = (millis() / 32 - pulseTimeStart);
    currentData[count] = currentValDamped;
    PWMData[count] = dutyCycle;
    count++;
  }

  if ((pulseTime < 25) && (pulseStarted == HIGH)) {
    refVal = pulseTime * MAX_CURRENT/25;
  } else if ((pulseTime < 475) && (pulseStarted == HIGH)) {
    refVal = MAX_CURRENT;
  } else if ((pulseTime < 500) && (pulseStarted == HIGH)) {
    refVal = MAX_CURRENT - (pulseTime - 475) * MAX_CURRENT/50;
  } else if ((pulseTime >= 500) && (pulseStarted == HIGH)) {
    pulseStarted = LOW;
    refVal = 0;
    Serial.print(currentData[0]);
    for (int i = 0; i < MAX_ARRAY_SIZE; i++) {
      Serial.print(i);
      Serial.print(", ");

      Serial.print(", ");
      Serial.println(PWMData[i]);
    }
    count = 0;
  } else {
    refVal = 0;
  }

  sampTimeEnd = micros();
  sampPeriod = sampTimeEnd - sampTimeBegin;
  sampTimeBegin = micros(); // Do not leave for over 8mins

  // Calculate errors
  error = refVal - currentValDamped;
  if (pulseStarted == HIGH) {
    errorSum += error;
    errorSum = constrain(errorSum, -100, 100);
  } else {
    errorSum = 0;
  }

  errorDif = error - oldError;

  // Calculate gains and output
  dutyCycle = (kp * error) + (ki * errorSum * sampPeriod) + (kd * errorDif / sampPeriod);
  dutyCycle = constrain(dutyCycle, 0, 127);

  // Send output
  //dutyCycle = 127;
  if (refVal == 0) {
    OCR2A = byte(0);
    OCR2B = byte(0);

    OCR0A = byte(0);
    OCR0B = byte(0);     // keep off
  } else {
    OCR2A = byte(dutyCycle + 128);           // duty cycle out of 255 
    OCR2B = 255 - byte(dutyCycle + 128);     // duty cycle out of 255

    OCR0A = byte(dutyCycle + 128);           // duty cycle out of 255 
    OCR0B = 255 - byte(dutyCycle + 128);     // duty cycle out of 255
  }

  // Calculate next PID step values
  oldError = error;

  // Debugging
  // Serial.println(count);
  // Serial.print(currentValDamped, 8);
  // Serial.print(", ");
  // Serial.print(refVal, 8);
  // Serial.print(", ");
  // Serial.print(kp * error, 8);
  // Serial.print(", ");
  // Serial.print(ki * errorSum * sampPeriod, 8);
  // Serial.print(", ");
  // Serial.print(kd * errorDif / sampPeriod, 8);
  // Serial.print(", ");
  // Serial.print(count);
  // Serial.print(", ");
  // Serial.print(refVal, 8);
  // Serial.print(", ");
  // Serial.println(dutyCycle);
}

double calibrateHallSensor() {
  double sensorOffset = 0;
  short numSamples = 30;
  for (int i = 0; i < numSamples; i++) {
    //sensorOffset = sensorOffset + analogRead(HALL_SENSOR_PIN) - 512;
    sensorOffset = sensorOffset + analogRead(HALL_SENSOR_PIN) - 380;
    delay(100);
    Serial.println("Calibrating...");
  } 
  return sensorOffset / numSamples;
}

int getTargetValue(int targetCurrentArray[], int pulseTime) {
  if (pulseTime < MAX_ARRAY_SIZE) {
    return -1;
  } else {
    return targetCurrentArray[pulseTime];
  }
}
