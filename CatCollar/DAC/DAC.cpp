/*
 * Cat Collar Alert System for ESP32-C3 with PCM5102 DAC
 * Purpose: Plays a 2-second sound burst when triggered via ping
 * Features:
 * - Uses PCM5102 external DAC for high-quality audio
 * - Sound frequency designed to be audible but not harmful to cats
 */

// Include necessary library
#include "driver/i2s.h"  // ESP32's I2S driver for digital audio output

// Pin Definitions for ESP32-C3 with PCM5102 DAC
#define TRIGGER_PIN  10  // GPIO10: Connect to motion/ping sensor (LOW = triggered)
#define BCK_PIN      23  // GPIO23: Bit Clock for PCM5102 (connects to BCK pin)
#define WS_PIN       22  // GPIO22: Word Select/LRCK (Left/Right clock) to LCK pin
#define DATA_PIN     24  // GPIO24: Audio data line to DIN pin

// Sound Configuration
#define SAMPLE_RATE 44100       // Standard audio sample rate (44.1kHz)
#define ALERT_DURATION_MS 2000  // 2-second alert duration
#define DEBOUNCE_TIME_MS 1000   // Wait time after alert to prevent rapid triggering

// Sound Frequency Settings
// Cats hear 45Hz to 64kHz (vs human 20Hz-20kHz)
// Using 8-12kHz is audible to humans but less intense for cats
#define ALERT_FREQUENCY_HZ 10000  // 10kHz tone - audible but not harmful to cats

// Function declarations
void initI2S();
void playAlert();

void setup() {
  // Initialize Serial Monitor for debugging
  Serial.begin(115200);
  Serial.println("Initializing cat collar alert system...");

  // Configure trigger pin (internal pullup resistor avoids floating input)
  pinMode(TRIGGER_PIN, INPUT_PULLUP);

  // Initialize I2S for PCM5102 DAC
  initI2S();
  
  Serial.println("System ready. Waiting for trigger...");
}

void loop() {
  // Check trigger pin state (LOW = active due to pullup)
  if (digitalRead(TRIGGER_PIN) == LOW) {  
    Serial.println("Trigger detected!");
    playAlert();                // Play 2-second alert sound
    delay(DEBOUNCE_TIME_MS);    // Prevent rapid re-triggering
  }
  
  // Small delay to prevent CPU hogging
  delay(10);
}

/**
 * Initialize I2S interface for PCM5102 DAC
 * 
 * PCM5102 Configuration:
 * - Connect FMT pin to GND for standard I2S format
 * - Connect SCK pin to GND for slave mode
 * - Connect DMP pin to 3.3V to disable DSD mode
 * - Connect FLT pin to GND for normal operation
 */
void initI2S() {
  Serial.println("Initializing I2S for PCM5102...");
  
  // Define I2S configuration
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),  // ESP32 is I2S master, transmit only
    .sample_rate = SAMPLE_RATE,                           // 44.1kHz standard sample rate
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,         // 16-bit audio samples
    .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,         // Stereo output
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,    // Standard I2S format
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,             // Interrupt priority
    .dma_buf_count = 8,                                   // Number of DMA buffers
    .dma_buf_len = 64,                                    // Size of each DMA buffer
    .use_apll = false,                                    // Don't use APLL for simplicity
    .tx_desc_auto_clear = true                            // Auto-clear DMA descriptors
  };
  
  // Define pin configuration for PCM5102
  i2s_pin_config_t pin_config = {
    .bck_io_num = BCK_PIN,         // Bit clock pin
    .ws_io_num = WS_PIN,           // Word select pin (LRCK)
    .data_out_num = DATA_PIN,      // Data output pin (DIN on PCM5102)
    .data_in_num = I2S_PIN_NO_CHANGE  // Not used (PCM5102 is output only)
  };
  
  // Install and configure I2S driver
  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);
  
  Serial.println("I2S initialized successfully");
}

/**
 * Generates a cat-friendly alert tone for specified duration
 * 
 * Sound characteristics:
 * - 10kHz tone (audible to humans, less intense for cats)
 * - 2-second duration
 * - Moderate volume to avoid startling the cat
 */
void playAlert() {
  Serial.println("ALERT: Playing alert sound");
  
  const float volume = 0.7;  // 70% volume (adjust as needed: 0.0-1.0)
  int16_t sample;
  int num_samples = (ALERT_DURATION_MS * SAMPLE_RATE) / 1000;  // Total samples needed
  
  // Generate audio samples
  for (int i = 0; i < num_samples; i++) {
    // Create sine wave tone at specified frequency
    // sin() produces values from -1.0 to 1.0
    // Scale to 16-bit range (-32768 to 32767)
    sample = volume * 32767 * sin(2 * PI * ALERT_FREQUENCY_HZ * i / SAMPLE_RATE);
    
    // Send to both left and right channels (stereo)
    size_t bytes_written;
    i2s_write(I2S_NUM_0, &sample, sizeof(sample), &bytes_written, portMAX_DELAY);
    i2s_write(I2S_NUM_0, &sample, sizeof(sample), &bytes_written, portMAX_DELAY);
  }
  
  Serial.println("Alert sound complete");
}