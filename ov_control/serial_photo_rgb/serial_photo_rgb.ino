#include "esp_camera.h"
#include <string>

#define CAMERA_MODEL_XIAO_ESP32S3 // has PSRAM (needs to be enabled in Arduino IDE!)
#include "camera_pins.h"

bool takePicture = false;

void setup()
{
  Serial.begin(115200);
  while (!Serial)
    ;

  // Initialize camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_QVGA;     // Frame size
  config.pixel_format = PIXFORMAT_RGB565; // RGB format
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;

  if (psramFound())
  {
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.fb_count = 2; // Reduce frame buffer count to save memory
  }
  else
  {
    config.fb_location = CAMERA_FB_IN_DRAM;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK)
  {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
  pinMode(LED_GPIO_NUM, OUTPUT);
  digitalWrite(LED_GPIO_NUM, LOW);

  Serial.println("Camera initialized successfully!");

  // Get a pointer to the camera sensor
  sensor_t *s = esp_camera_sensor_get();

  // Set exposure time to maximum
  s->set_exposure_ctrl(s, false); // Disable automatic exposure control
  s->set_aec_value(s, 1964);      // Set maximum exposure value, adjust as needed

  // Set gain to maximum
  s->set_gain_ctrl(s, false); // Disable automatic gain control
  s->set_agc_gain(s, 63);     // Set maximum gain value, adjust as needed
}

void loop()
{
  if (Serial.available())
  {
    String command = Serial.readStringUntil('\n');
    if (command == "TAKE_PICTURE")
    {
      // Capture the image
      camera_fb_t *fb = esp_camera_fb_get();
      if (!fb)
      {
        Serial.println("Camera capture failed");
        return;
      }

      // Allocate buffer for RGB888 data
      size_t rgb888_size = fb->width * fb->height * 3;
      uint8_t *rgb888_data = (uint8_t *)malloc(rgb888_size);
      if (!rgb888_data)
      {
        Serial.println("RGB888 buffer allocation failed");
        esp_camera_fb_return(fb);
        return;
      }

      // Convert the captured image to RGB888
      bool conversion_success = fmt2rgb888(fb->buf, fb->len, PIXFORMAT_RGB565, rgb888_data);
      if (conversion_success)
      {
        // Send image size first
        Serial.printf("Captured image with size: %d bytes\n", rgb888_size);

        // Send the image data
        Serial.write(rgb888_data, rgb888_size);

        // Free the allocated buffer
        free(rgb888_data);
      }
      else
      {
        Serial.println("Image conversion to RGB888 failed");
        free(rgb888_data);
      }

      // Return the frame buffer back to the driver
      esp_camera_fb_return(fb);
    }
  }
}
