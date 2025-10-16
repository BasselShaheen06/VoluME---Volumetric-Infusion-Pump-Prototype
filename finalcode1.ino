// COLOR SENSOR (TCS230/TCS3200) PINS
#define S0 4
#define S1 5
#define S2 6
#define S3 7
#define sensorOut 8
#define buzzerPin 9

// PUMP CONTROL
#define pumpPin 11  // PWM pin for 2N2222

// FLOWMETER (YF-S401) PINS
#define flowMeterPin 3  // Flow sensor data pin

volatile int pulseCount = 0;  // Count flow sensor pulses
float flowRate = 0.0;         // Calculated flow rate (L/min)
unsigned long lastTime = 0;   // Time tracking for flow calculation

int redFreq = 0, greenFreq = 0, blueFreq = 0;
int pumpSpeed = 0;  // Default speed

void countPulse() {
    pulseCount++;  // Interrupt function to count pulses
}

void setup() {
    pinMode(S0, OUTPUT);
    pinMode(S1, OUTPUT);
    pinMode(S2, OUTPUT);
    pinMode(S3, OUTPUT);
    pinMode(sensorOut, INPUT);
    pinMode(pumpPin, OUTPUT);
    pinMode(buzzerPin, OUTPUT);
    
    pinMode(flowMeterPin, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(flowMeterPin), countPulse, RISING);

    // Set color sensor frequency scaling to 20%
    digitalWrite(S0, HIGH);
    digitalWrite(S1, LOW);

    Serial.begin(9600);
    Serial.println("Enter a pump speed (0-255) or type 'auto' for color-based control.");
}

void loop() {
    static bool autoMode = true; // Default to auto mode

    // Check Serial input for manual pump control
    if (Serial.available()) {
        String input = Serial.readStringUntil('\n');
        input.trim();

        if (input.equalsIgnoreCase("auto")) {
            autoMode = true;
            Serial.println("Switched to AUTO mode (color-based control).");
        } else {
            int userSpeed = input.toInt();
            if (userSpeed >= 0 && userSpeed <= 255) {
                pumpSpeed = userSpeed;
                autoMode = false;
                Serial.print("Manual Mode: Pump Speed Set To ");
                Serial.println(pumpSpeed);
            } else {
                Serial.println("Invalid input! Enter 0-255 or 'auto'.");
            }
        }
    }

    if (autoMode) {
        // Read RED
        digitalWrite(S2, LOW);
        digitalWrite(S3, LOW);
        redFreq = pulseIn(sensorOut, LOW);

        // Read GREEN
        digitalWrite(S2, HIGH);
        digitalWrite(S3, HIGH);
        greenFreq = pulseIn(sensorOut, LOW);

        // Read BLUE
        digitalWrite(S2, LOW);
        digitalWrite(S3, HIGH);
        blueFreq = pulseIn(sensorOut, LOW);

        // Convert frequencies to RGB values
        int red = map(redFreq, 30, 1000, 255, 0);
        int green = map(greenFreq, 30, 1000, 255, 0);
        int blue = map(blueFreq, 30, 1000, 255, 0);

        // Determine the highest color and set pump speed
        String highestColor;
        if (red >= green && red >= blue) {
            highestColor = "BLOOD LEAKAGE";
            pumpSpeed = 240;  // High speed if blood detected
            buzzerOn();
        } else {
            highestColor = "NORMAL";
            pumpSpeed = 180;  // Lower speed if normal
            digitalWrite(buzzerPin, LOW);
        }
    }

    // Apply PWM to pump
    analogWrite(pumpPin, pumpSpeed);

    // Calculate Flow Rate every second
    unsigned long currentTime = millis();
    if (currentTime - lastTime >= 1000) {  
        flowRate = (pulseCount / 450.0) * 60;  // Convert pulses to L/min (adjust calibration)
        pulseCount = 0;
        lastTime = currentTime;
    }

    // Print all outputs in one line
    Serial.print("Status: "); Serial.print(autoMode ? (pumpSpeed == 240 ? "BLOOD LEAKAGE" : "NORMAL") : "MANUAL");
    Serial.print(" | Pump Speed: "); Serial.print(pumpSpeed);
    Serial.print(" | Flow Rate: "); Serial.print(flowRate, 2);
    Serial.println(" mL/min");

    delay(500);
}

void buzzerOn() {
    digitalWrite(buzzerPin, HIGH);
    delay(740);
    digitalWrite(buzzerPin, LOW);
}