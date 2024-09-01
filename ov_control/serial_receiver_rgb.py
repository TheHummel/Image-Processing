import os
import serial
import time
import struct

# Configure the serial connection
ser = serial.Serial("COM7", 115200)


def clear_serial_buffer(ser):
    ser.flushInput()
    ser.flushOutput()


def request_image(output_path: str = "captured_image.bmp"):
    clear_serial_buffer(ser)
    ser.write(b"TAKE_PICTURE\n")
    ser.flush()
    time.sleep(1)  # Wait for the ESP32 to process

    # Read image size from the serial
    size = None
    while True:
        line = ser.readline().decode("utf-8").strip()
        print(line)
        if "Captured image with size" in line:
            size = int(line.split(":")[1].strip().split()[0])
            break

    if size is None:
        print("Failed to get image size")
        return

    print(f"Image size: {size} bytes")

    # Read image data
    image_data = bytearray()
    last_read_time = time.time()
    timeout = 5  # seconds
    while len(image_data) < size:
        current_time = time.time()
        if current_time - last_read_time > timeout:
            print("Timeout while reading data")
            break
        bytes_to_read = size - len(image_data)
        chunk = ser.read(bytes_to_read if bytes_to_read < 512 else 512)
        if chunk:
            image_data.extend(chunk)
            last_read_time = time.time()
        else:
            print("No data received, waiting...")

    print(f"Received {len(image_data)} bytes")

    # Save as BMP
    if len(image_data) > 0:
        width, height = 320, 240  # QVGA resolution
        bmp_header = create_bmp_header(width, height)

        if os.path.exists(output_path):
            output_path = output_path.split(".")[0] + "_" + str(time.time()) + ".bmp"

        with open(output_path, "wb") as image_file:
            image_file.write(bmp_header)
            image_file.write(image_data)

        print("Image saved at", output_path)
    else:
        print("No image data received")


def create_bmp_header(width, height):
    file_size = 54 + width * height * 3
    header = struct.pack(
        "<2sIHHIIIIHHIIIIII",
        b"BM",  # Signature
        file_size,  # File size
        0,  # Reserved
        0,  # Reserved
        54,  # File offset to pixel array
        40,  # DIB header size
        width,  # Width
        height,  # Height
        1,  # Planes
        24,  # Bits per pixel
        0,  # Compression
        width * height * 3,  # Image size (can be 0 for BI_RGB)
        0,  # X pixels per meter
        0,  # Y pixels per meter
        0,  # Total colors
        0,
    )  # Important colors
    return header


if __name__ == "__main__":
    output_dir = "C:/Users/janni/Downloads"
    file_name = "captured_image.bmp"
    output_path = os.path.join(output_dir, file_name)
    request_image(output_path)
