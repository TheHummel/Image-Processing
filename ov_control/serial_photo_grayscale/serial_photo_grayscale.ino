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
    config.frame_size = FRAMESIZE_QVGA; // Frame size
    config.pixel_format = PIXFORMAT_GRAYSCALE;
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
}

void loop()
{
    if (Serial.available() > 0)
    {
        String command = Serial.readStringUntil('\n');
        if (command == "TAKE_PICTURE")
        {
            takePicture = true;
        }
    }

    if (takePicture)
    {
        takePicture = false;
        Serial.println("Start new capture");
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb)
        {
            Serial.println("Camera capture failed");
            return;
        }

        Serial.printf("Captured image with size: %zu bytes\n", fb->len);

        // Send image over Serial in smaller chunks
        const int chunkSize = 256; // Smaller chunk size
        for (size_t i = 0; i < fb->len; i += chunkSize)
        {
            size_t len = (fb->len - i < chunkSize) ? (fb->len - i) : chunkSize;
            Serial.write((uint8_t *)(fb->buf + i), len);
            delay(10); // Delay to ensure Serial buffer can handle the transmission
        }

        esp_camera_fb_return(fb);
        Serial.println("Photo capture and transmission completed");
    }
}
