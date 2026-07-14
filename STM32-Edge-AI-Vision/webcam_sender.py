import cv2
import serial
import time

# Change this to match your microcontroller's COM port
SERIAL_PORT = 'COM10'
BAUD_RATE = 115200

# Connect to the serial port with timeouts to prevent the script from hanging
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1, write_timeout=2)
    print(f"Connected to {SERIAL_PORT}")
except Exception as e:
    print(f"Error opening port: {e}")
    exit()

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Webcam not found.")
    exit()

print("\n*** IMPORTANT: CLICK ON THE WEBCAM WINDOW FIRST, THEN PRESS 's' ***\n")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera read error.")
        break

    # 1. Main processing for transmission (Grayscale and resize to 16x16)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (16, 16))

    # 2. Display the primary webcam window
    cv2.imshow('Webcam - CLICK HERE THEN PRESS s', frame)

    # 3. Upscale the 16x16 image purely for visualization (without blurring pixels)
    display_resized = cv2.resize(
        resized, (200, 200), interpolation=cv2.INTER_NEAREST)

    # 4. Display the secondary window (What the STM32 actually sees)
    cv2.imshow('What STM32 Sees (16x16 scaled)', display_resized)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s') or key == ord('S'):
        print(f"-> Sending frame...")

        # The transmitted data is the 16x16 resized array (256 bytes), NOT the upscaled image!
        raw_bytes = resized.tobytes()

        try:
            # Send the raw bytes via USB to the microcontroller
            ser.write(raw_bytes)
            print("-> Success! 256 bytes sent to USB buffer.")

            # Read the response from the STM32 board (Optional)
            time.sleep(0.1)
            if ser.in_waiting > 0:
                print("-> STM32 replied:", ser.readline().decode().strip())

        except serial.SerialTimeoutException:
            print("\n[!] TIMEOUT ERROR: STM32 is not reading from USB.")
            print(
                "[!] Check if STM32 crashed, memory is full, or if an IDE (like Thonny) is blocking the port.")
        except Exception as e:
            print(f"-> Error: {e}")

    elif key == ord('q') or key == ord('Q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()
