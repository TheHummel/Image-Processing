import serial
import time

# Configure the serial connection
ser = serial.Serial("COM7", 115200)  # Change to the correct port


# Function to request and save image
def request_image():
    ser.write(b"TAKE_PICTURE\n")
    ser.flush()
    time.sleep(1)  # Wait for the ESP32 to process

    # Read image size from the serial
    while True:
        line = ser.readline().decode("utf-8").strip()
        if "Captured image with size" in line:
            size = int(line.split(":")[1].strip().split()[0])
            break

    print(f"Image size: {size} bytes")

    # Read image data
    image_data = bytearray()
    while len(image_data) < size:
        image_data.extend(ser.read(size - len(image_data)))
        print(f"Received {len(image_data)} bytes, total: {size}")

    print(f"Received {len(image_data)} bytes")

    # Save image data to file
    with open("captured_image.jpg", "wb") as image_file:
        image_file.write(image_data)

    print("Image saved to captured_image.jpg")


if __name__ == "__main__":
    request_image()
