import serial
import time


def clear_serial_buffer(ser):
    ser.flushInput()
    ser.flushOutput()


def request_image(ser):
    clear_serial_buffer(ser)
    ser.write(b"TAKE_PICTURE\n")
    ser.flush()
    time.sleep(1)  # Wait for the ESP32 to process

    size = None
    while True:
        line = ser.readline().decode("utf-8").strip()
        if "Captured image with size" in line:
            size = int(line.split(":")[1].strip().split()[0])
            break

    if size is None:
        print("Failed to get image size")
        return

    print(f"Image size: {size} bytes")

    width = 320  # Replace with actual width of your image
    height = size // width  # Calculate height from size

    image_data = bytearray()
    while len(image_data) < size:
        chunk = ser.read(size - len(image_data))
        if chunk:
            image_data.extend(chunk)
            print(f"Received {len(chunk)} bytes, total: {len(image_data)}")
        else:
            print("No data received, waiting...")

    print(f"Received {len(image_data)} bytes")

    if len(image_data) > 0:
        with open("captured_image.pgm", "wb") as image_file:
            # Write PGM header
            image_file.write(b"P5\n")
            image_file.write(f"{width} {height}\n".encode())
            image_file.write(b"255\n")  # Max grayscale value

            # Write image data
            image_file.write(image_data)

        print("Grayscale image data saved to captured_image.pgm")
    else:
        print("No image data received")


if __name__ == "__main__":
    ser = serial.Serial("COM7", 115200)
    request_image(ser)
