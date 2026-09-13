import gc
import struct
import time
import bluelib
from machine import SoftI2C
import pyb
from pyb import Pin

# ==========================================
# 1. OLED Display Hardware Configuration
# ==========================================
oled = SoftI2C(sda=Pin('Y10'), scl=Pin('Y9'), freq=400000)
display = bluelib.BOled_I2C(128, 32, oled)

# Display initial status on OLED
display.fill(0)
display.text('System Ready...', 0, 0, 1)
display.show()

# ==========================================
# 2. Lookup Table & Template Loading
# ==========================================
# Fast 256-byte bit-count lookup table (avoids costly string allocations via bin())
BIT_COUNT_TABLE = bytes(bin(i).count('1') for i in range(256))

# Load templates from binary file (3840 bytes total)
DIGIT_TEMPLATES = {}
try:
    with open('templates.bin', 'rb') as f:
        for digit in range(10):
            DIGIT_TEMPLATES[digit] = []
            for _ in range(12):
                raw_bytes = f.read(32)
                if len(raw_bytes) == 32:
                    pattern = list(struct.unpack('>4Q', raw_bytes))
                    DIGIT_TEMPLATES[digit].append(pattern)
except OSError:
    DIGIT_TEMPLATES = {i: [] for i in range(10)}

# ==========================================
# 3. Digit Recognition Functions
# ==========================================
# Pre-allocated shifted buffer outside the loop to eliminate memory allocation churn
shifted_buffer = bytearray(256)


def pack_to_4x64bit(binary_list):
    """Pack 256 binary pixels into four 64-bit integers."""
    parts = []
    for i in range(4):
        chunk = binary_list[i * 64: (i + 1) * 64]
        val = 0
        for bit in chunk:
            val = (val << 1) | int(bit)
        parts.append(val)
    return parts


def get_hamming_distance(img_parts, template_parts):
    """Calculate bitwise difference using byte-level lookup without string conversions."""
    total_distance = 0
    for i in range(4):
        diff = img_parts[i] ^ template_parts[i]
        while diff:
            total_distance += BIT_COUNT_TABLE[diff & 0xFF]
            diff >>= 8
    return total_distance


def shift_image_16x16(binary_list, dx, dy, out_buffer):
    """Shift the 16x16 image into the provided pre-allocated buffer."""
    for i in range(256):
        out_buffer[i] = 0
    for y in range(16):
        for x in range(16):
            new_x = x + dx
            new_y = y + dy
            if 0 <= new_x < 16 and 0 <= new_y < 16:
                out_buffer[new_y * 16 + new_x] = binary_list[y * 16 + x]


def predict_digit(sensor_data_list):
    min_overall_distance = 257
    best_overall_match = -1

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            shift_image_16x16(sensor_data_list, dx, dy, shifted_buffer)
            img_parts = pack_to_4x64bit(shifted_buffer)

            for digit, templates in DIGIT_TEMPLATES.items():
                for template in templates:
                    distance = get_hamming_distance(img_parts, template)
                    if distance < min_overall_distance:
                        min_overall_distance = distance
                        best_overall_match = digit

    return best_overall_match, min_overall_distance


# ==========================================
# 4. Microcontroller-Specific Image Preprocessor
# ==========================================


def preprocess_mcu(image_pixels, img_w, img_h, threshold=127):
    """Find the bounding box of the digit and scale it to 16x16."""
    min_x, max_x = img_w, -1
    min_y, max_y = img_h, -1

    for y in range(img_h):
        for x in range(img_w):
            idx = y * img_w + x
            if image_pixels[idx] < threshold:
                if x < min_x:
                    min_x = x
                if x > max_x:
                    max_x = x
                if y < min_y:
                    min_y = y
                if y > max_y:
                    max_y = y

    binary_16x16 = bytearray(256)

    if min_x > max_x:
        return binary_16x16

    crop_w = max_x - min_x + 1
    crop_h = max_y - min_y + 1

    size = max(crop_w, crop_h)
    pad = int(size * 0.15)
    padded_size = size + (2 * pad)

    offset_x = pad + (size - crop_w) // 2
    offset_y = pad + (size - crop_h) // 2

    for tgt_y in range(16):
        for tgt_x in range(16):
            src_x = int(tgt_x * padded_size / 16) - offset_x
            src_y = int(tgt_y * padded_size / 16) - offset_y
            if 0 <= src_x < crop_w and 0 <= src_y < crop_h:
                orig_x = min_x + src_x
                orig_y = min_y + src_y
                if image_pixels[orig_y * img_w + orig_x] < threshold:
                    binary_16x16[tgt_y * 16 + tgt_x] = 1

    return binary_16x16


# ==========================================
# 5. Main Application Loop (USB Receiver + OLED Output)
# ==========================================
pyb.USB_VCP().setinterrupt(-1)
usb = pyb.USB_VCP()

IMG_SIZE = 16 * 16
image_buffer = bytearray()

pyb.LED(1).off()
pyb.LED(2).off()
pyb.LED(3).off()
pyb.LED(4).off()

gc.collect()

while True:
    if usb.any():
        pyb.LED(1).on()
        chunk = usb.read(IMG_SIZE - len(image_buffer))

        if chunk:
            pyb.LED(3).on()
            image_buffer.extend(chunk)

        if len(image_buffer) == IMG_SIZE:
            pyb.LED(4).on()

            start_time = time.ticks_ms()

            # Preprocess raw input frame to 16x16 binary array
            sensor_input_16x16 = preprocess_mcu(
                image_buffer, 16, 16, threshold=127)

            # Run pattern matcher
            predicted_number, dist = predict_digit(sensor_input_16x16)

            end_time = time.ticks_ms()
            processing_time = time.ticks_diff(end_time, start_time)

            # Refresh OLED screen
            try:
                display.fill(0)
                display.text('v : ' + str(predicted_number), 0, 0, 1)
                display.text('time: ' + str(processing_time) + 'ms', 0, 16, 1)
                display.show()
            except NameError:
                pass

            # Transmit inference result back over USB CDC
            response_msg = 'RESULT:{}\n'.format(predicted_number)
            usb.write(response_msg.encode('utf-8'))

            # Reset buffer and cleanup
            image_buffer = bytearray()
            pyb.LED(4).off()
            pyb.LED(3).off()
            pyb.LED(1).off()
            gc.collect()

    time.sleep_ms(1)
