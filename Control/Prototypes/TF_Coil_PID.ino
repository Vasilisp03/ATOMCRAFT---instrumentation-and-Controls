// Define PWM pin
const int pwmPin = 5;
const float MAX_CURRENT = 0.20;

// Define Hall sensor pin
const int hallSensorPin = A0;
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

float kp = 3000;
float ki = 0.007;
float kd = -0.05;

float sampTimeBegin = 0;
float sampTimeEnd = 0;
float sampPeriod = 0;

int executePulse = 0;
int pulseStarted = 0;
int pulseTimeStart = 0;
int pulseTime = 0;

// Setup
void setup() {
  Serial.begin(115200);

  // Set pin modes
  pinMode(2, INPUT); // Button
  pinMode(pwmPin,155);
  TCCR0B = TCCR0B & B11111000 | B00000010; //  7812.50 Hz (Note this also effects millis() and micros() making them 8x faster)

  for (int i = 0; i < 10; i++) {
    sensorOffset = sensorOffset + analogRead(hallSensorPin) - 512;
    delay(100);
    Serial.println("Calibrating...");
  } 
  sensorOffset = sensorOffset / 10;

  Serial.println("Running...");
}

// Enable PWM output for the TF coil
void loop() {
  // Get current measurement and convert
  rawVal = (analogRead(hallSensorPin) - sensorOffset);
  currentVal = ((rawVal - 512) / 1023) * 5 / 0.186;
  currentValDamped = currentValDamped * 0.99 + currentVal * 0.01;

  // Set reference current
  executePulse = digitalRead(2);
  if (executePulse == HIGH & pulseStarted == LOW) {
    pulseTimeStart = millis() / 8; // We modified timer so need to adjust millis
    pulseStarted = HIGH;
  }
  if (pulseStarted == HIGH) {
    pulseTime = (millis() / 8 - pulseTimeStart);
  }

  if ((pulseTime < 500) && (pulseStarted == HIGH)) {
    refVal = pulseTime * MAX_CURRENT/500;
  } else if ((pulseTime < 5500) && (pulseStarted == HIGH)) {
    refVal = MAX_CURRENT;
  } else if ((pulseTime < 6000) && (pulseStarted == HIGH)) {
    refVal = MAX_CURRENT - (pulseTime - 5500) * MAX_CURRENT/500;
  } else if ((pulseTime >= 6000) && (pulseStarted == HIGH)) {
    pulseStarted = LOW;
    refVal = 0;
  } else {
    refVal = 0;
  }

  sampTimeEnd = micros();
  sampPeriod = sampTimeEnd - sampTimeBegin;
  sampTimeBegin = micros(); // Do not leave for over 8mins

  // Calculate errors
  error = refVal - currentValDamped;
  errorSum += error;
  errorSum = constrain(errorSum, -2, 2);
  errorDif = error - oldError;

  // Calculate gains and output
  dutyCycle = (kp * error) + (ki * errorSum * sampPeriod) + (kd * errorDif / sampPeriod);
  dutyCycle = constrain(dutyCycle, 0, 255);

  // Send output
  analogWrite(pwmPin, int(dutyCycle));

  // Calculate next PID step values
  oldError = error;

  // Debugging
  Serial.print(currentValDamped, 8);
  Serial.print(", ");
  Serial.print(kp * error, 8);
  Serial.print(", ");
  Serial.print(ki * errorSum * sampPeriod, 8);
  Serial.print(", ");
  Serial.print(errorDif, 8);
  Serial.print(", ");
  Serial.print(refVal, 8);
  Serial.print(", ");
  Serial.println(dutyCycle);
}

