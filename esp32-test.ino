/*
ESP32 Bluetooth Test - Console Logger + LED Indicators
Receives data from Windows dashboard and logs to Serial Monitor
LEDs show which motor control pins would be triggered

Hardware: ESP32 (any model)
Libraries: BluetoothSerial (built-in)

Setup:
1. Upload this code to ESP32
2. Open Serial Monitor (115200 baud)
3. Run: python BT_Dashboard.py --com COMx --dashboard
4. Watch console for received data
5. Watch LEDs for motor control simulation

Expected data format:
F <throttle> <turn> <brake> <rotate> <gear_boost>
*/

#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

// Bluetooth device name (change this if needed)
String device_name = "ESP32-Sumobot";

// Motor control pins (simplified - no enable pins)
#define LEFT_RPWM    17   // GPIO 17 - Left Motor Forward (RPWM)
#define LEFT_LPWM    18   // GPIO 18 - Left Motor Backward (LPWM)
#define RIGHT_RPWM   19   // GPIO 19 - Right Motor Forward (RPWM)
#define RIGHT_LPWM   21   // GPIO 21 - Right Motor Backward (LPWM)

// LED indicators for motor control
#define LED_LEFT_FWD   17   // GPIO 17 - Left Motor Forward (RPWM)
#define LED_LEFT_BWD   18   // GPIO 18 - Left Motor Backward (LPWM)
#define LED_RIGHT_FWD  19   // GPIO 19 - Right Motor Forward (RPWM)
#define LED_RIGHT_BWD  21   // GPIO 21 - Right Motor Backward (LPWM)
#define LED_STATUS     33   // GPIO 33 - Bluetooth Status

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 Bluetooth Test Starting...");
  
  // Initialize LED pins
  pinMode(LED_LEFT_FWD, OUTPUT);
  pinMode(LED_LEFT_BWD, OUTPUT);
  pinMode(LED_RIGHT_FWD, OUTPUT);
  pinMode(LED_RIGHT_BWD, OUTPUT);
  pinMode(LED_STATUS, OUTPUT);
  
  // No enable pins needed - simplified control
  
  // Turn off all LEDs initially
  digitalWrite(LED_LEFT_FWD, LOW);
  digitalWrite(LED_LEFT_BWD, LOW);
  digitalWrite(LED_RIGHT_FWD, LOW);
  digitalWrite(LED_RIGHT_BWD, LOW);
  digitalWrite(LED_STATUS, LOW);
  
  // Enable pins tied to 5V - no software control needed
  
  // Initialize Bluetooth
  SerialBT.begin(device_name);
  Serial.println("Bluetooth device started: " + device_name);
  Serial.println("Waiting for connection...");
  Serial.println("Pair with this device from Windows");
  Serial.println("Then run: python BT_Dashboard.py --com COMx --dashboard");
  Serial.println("----------------------------------------");
  Serial.println("LED Mapping (Based on Wiring Diagram):");
  Serial.println("  GPIO 17 - Left Motor Forward (RPWM)");
  Serial.println("  GPIO 18 - Left Motor Backward (LPWM)");
  Serial.println("  GPIO 19 - Right Motor Forward (RPWM)");
  Serial.println("  GPIO 21 - Right Motor Backward (LPWM)");
  Serial.println("  GPIO 33 - Bluetooth Status");
  Serial.println("  Enable pins tied to 5V (no software control)");
  Serial.println("----------------------------------------");
  Serial.println("Motor Test: Forward for 2 seconds...");
  
  // Test motors for 2 seconds (manual control)
  digitalWrite(LEFT_RPWM, HIGH);
  digitalWrite(LEFT_LPWM, LOW);
  digitalWrite(RIGHT_RPWM, HIGH);
  digitalWrite(RIGHT_LPWM, LOW);
  delay(2000);
  
  // Stop motors
  digitalWrite(LEFT_RPWM, LOW);
  digitalWrite(LEFT_LPWM, LOW);
  digitalWrite(RIGHT_RPWM, LOW);
  digitalWrite(RIGHT_LPWM, LOW);
  
  Serial.println("Motor test complete. Check if motors moved!");
  Serial.println("----------------------------------------");
}

void loop() {
  // Check for Bluetooth connection
  if (SerialBT.available()) {
    String received = SerialBT.readStringUntil('\n');
    received.trim(); // Remove any whitespace
    
    if (received.length() > 0) {
      Serial.println("Received: " + received);
      
      // Parse the data
      if (received.startsWith("F ")) {
        // Remove "F " prefix
        String data = received.substring(2);
        
        // Split by spaces
        int space1 = data.indexOf(' ');
        int space2 = data.indexOf(' ', space1 + 1);
        int space3 = data.indexOf(' ', space2 + 1);
        int space4 = data.indexOf(' ', space3 + 1);
        
        if (space1 > 0 && space2 > 0 && space3 > 0 && space4 > 0) {
          float throttle = data.substring(0, space1).toFloat();
          float turn = data.substring(space1 + 1, space2).toFloat();
          int brake = data.substring(space2 + 1, space3).toInt();
          int rotate = data.substring(space3 + 1, space4).toInt();
          int gear_boost = data.substring(space4 + 1).toInt();
          
          Serial.println("Parsed Data:");
          Serial.println("  Throttle: " + String(throttle, 3));
          Serial.println("  Turn: " + String(turn, 3));
          Serial.println("  Brake: " + String(brake));
          Serial.println("  Rotate: " + String(rotate));
          Serial.println("  Gear Boost: " + String(gear_boost));
          
          // Show movement interpretation and control LEDs
          if (brake == 1) {
            Serial.println("  -> BRAKING");
            // Turn off all motor LEDs
            digitalWrite(LED_LEFT_FWD, LOW);
            digitalWrite(LED_LEFT_BWD, LOW);
            digitalWrite(LED_RIGHT_FWD, LOW);
            digitalWrite(LED_RIGHT_BWD, LOW);
            // Enable pins tied to 5V - always enabled
          } else if (rotate == 1) {
            Serial.println("  -> ROTATING");
            // Left forward, right backward
            digitalWrite(LED_LEFT_FWD, HIGH);
            digitalWrite(LED_LEFT_BWD, LOW);
            digitalWrite(LED_RIGHT_FWD, LOW);
            digitalWrite(LED_RIGHT_BWD, HIGH);
            // Enable pins tied to 5V - always enabled
          } else if (abs(throttle) > 0.1 || abs(turn) > 0.1) {
            String direction = "";
            if (throttle > 0.1) direction += "Forward";
            else if (throttle < -0.1) direction += "Backward";
            
            if (abs(turn) > 0.1) {
              if (turn > 0) direction += " Right";
              else direction += " Left";
            }
            
            String speed = gear_boost ? " (BOOST)" : "";
            Serial.println("  -> " + direction + speed);
            
            // Calculate motor speeds (differential drive)
            float left_speed = throttle + turn;
            float right_speed = throttle - turn;
            
            // Control motors manually (GPIO control)
            // Left motor
            if (left_speed > 0.1) {
              digitalWrite(LEFT_RPWM, HIGH);
              digitalWrite(LEFT_LPWM, LOW);
              digitalWrite(LED_LEFT_FWD, HIGH);
              digitalWrite(LED_LEFT_BWD, LOW);
            } else if (left_speed < -0.1) {
              digitalWrite(LEFT_RPWM, LOW);
              digitalWrite(LEFT_LPWM, HIGH);
              digitalWrite(LED_LEFT_FWD, LOW);
              digitalWrite(LED_LEFT_BWD, HIGH);
            } else {
              digitalWrite(LEFT_RPWM, LOW);
              digitalWrite(LEFT_LPWM, LOW);
              digitalWrite(LED_LEFT_FWD, LOW);
              digitalWrite(LED_LEFT_BWD, LOW);
            }
            
            // Right motor
            if (right_speed > 0.1) {
              digitalWrite(RIGHT_RPWM, HIGH);
              digitalWrite(RIGHT_LPWM, LOW);
              digitalWrite(LED_RIGHT_FWD, HIGH);
              digitalWrite(LED_RIGHT_BWD, LOW);
            } else if (right_speed < -0.1) {
              digitalWrite(RIGHT_RPWM, LOW);
              digitalWrite(RIGHT_LPWM, HIGH);
              digitalWrite(LED_RIGHT_FWD, LOW);
              digitalWrite(LED_RIGHT_BWD, HIGH);
            } else {
              digitalWrite(RIGHT_RPWM, LOW);
              digitalWrite(RIGHT_LPWM, LOW);
              digitalWrite(LED_RIGHT_FWD, LOW);
              digitalWrite(LED_RIGHT_BWD, LOW);
            }
            // Enable pins tied to 5V - always enabled
          } else {
            Serial.println("  -> STOPPED");
            // Stop motors manually
            digitalWrite(LEFT_RPWM, LOW);
            digitalWrite(LEFT_LPWM, LOW);
            digitalWrite(RIGHT_RPWM, LOW);
            digitalWrite(RIGHT_LPWM, LOW);
            // Turn off all motor LEDs
            digitalWrite(LED_LEFT_FWD, LOW);
            digitalWrite(LED_LEFT_BWD, LOW);
            digitalWrite(LED_RIGHT_FWD, LOW);
            digitalWrite(LED_RIGHT_BWD, LOW);
          }
          
          // Blink status LED to show data received (no delay)
          digitalWrite(LED_STATUS, HIGH);
          digitalWrite(LED_STATUS, LOW);
        } else {
          Serial.println("Error: Could not parse data format");
        }
      } else {
        Serial.println("Unknown command: " + received);
      }
    }
  }
  
  // No delay for maximum responsiveness
}
