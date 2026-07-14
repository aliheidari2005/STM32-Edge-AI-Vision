from machine import SoftI2C
from pyb import Pin
import bluelib
import gc
import time
import pyb


# ==========================================
# 1. OLED Display Hardware Configuration
# ==========================================
oled = SoftI2C(sda=Pin('Y10'), scl=Pin('Y9'), freq=400000)
display = bluelib.BOled_I2C(128, 32, oled)

# Display a welcome and ready message on the OLED
display.fill(0)
display.text("System Ready...", 0, 0, 1)
display.show()

# ==========================================
# 2. Variables and Template Dictionary
# ==========================================
# !!! NOTE: Copy/Paste your DIGIT_TEMPLATES dictionary here !!!
DIGIT_TEMPLATES = {
    0: [
        [0x00000000000007c0, 0x0ff00c181808180c,
            0x180c180c180c0c18, 0x07f001c000000000],
        [0x00000000000000f8, 0x01f8038c070c0e0c,
            0x0c081818183018e0, 0x1f800e0000000000],
        [0x00000000000001e0, 0x03f0031006180418,
            0x0c180c180c300c60, 0x0fc0078000000000],
        [0x0000000000000030, 0x00f801fc038c0618,
            0x0c18183018e01fc0, 0x1f00000000000000],
        [0x00000000000001f0, 0x03f807180c0c0c0c,
            0x180c180818181830, 0x0fe0078000000000],
        [0x0000000000000000, 0x03f007f80c0c180c,
            0x180c180c18381ff0, 0x0780000000000000],
        [0x00000000000003c0, 0x076006300c100c18,
            0x0c180c180c180630, 0x07e001c000000000],
        [0x00000000000001c0, 0x03e0032002300630,
            0x0430043004200660, 0x07c0038000000000],
        [0x00000000000003e0, 0x07f00ff80e381c18,
            0x1c1c1c181c380ff0, 0x07f003c000000000],
        [0x0000000000000070, 0x00f001f003300330,
            0x063004600c600dc0, 0x0f80060000000000],
        [0x00000000006001f0, 0x03f807980e180c18,
            0x1c18183818701fe0, 0x0fc0070000000000],
        [0x00000000002000f0, 0x01f8039807180618,
            0x0c300c3018601dc0, 0x0f80070000000000],
    ],
    1: [
        [0x00000000000001c0, 0x01c001c001c001c0,
            0x01c001c001c001c0, 0x01c0008000000000],
        [0x0000000000200020, 0x0060004000c000c0,
            0x0180018003000300, 0x0200020000000000],
        [0x0000000000000080, 0x0080008000800080,
            0x0080008000800080, 0x0080008000000000],
        [0x0000000000000018, 0x00300070006000c0,
            0x0180038007000e00, 0x0c00080000000000],
        [0x0000000000000080, 0x0080008000800180,
            0x0180018001800100, 0x0100010000000000],
        [0x0000000000000180, 0x0180018001800180,
            0x0180018001800180, 0x0180008000000000],
        [0x0000000000000030, 0x0070006000c000c0,
            0x0180038003000600, 0x0600040000000000],
        [0x0000000000000060, 0x00e000e000c001c0,
            0x01c0018003800380, 0x0300030000000000],
        [0x00000000000000c0, 0x00c000c000c00080,
            0x0180018001800180, 0x0180018000000000],
        [0x0000000000000040, 0x00c000c000c00080,
            0x0180018001000300, 0x0300020000000000],
        [0x0000000000000100, 0x0180018001800180,
            0x0180008000c000c0, 0x00c0004000000000],
        [0x0000000000000040, 0x004000c000c00080,
            0x0080018001800100, 0x0100010000000000],
    ],
    2: [
        [0x0000000000e001f0, 0x0130003000300060,
            0x00e007c01fe01ff0, 0x1c00000000000000],
        [0x00000000018000c0, 0x0040006000400040,
            0x00c003c007c00700, 0x0600000000000000],
        [0x0000000001e003f0, 0x00300030006000c0,
            0x0180030007000ff0, 0x0ff0000000000000],
        [0x00000000006000f8, 0x0018001800180030,
            0x07f01fe03be03f00, 0x1800000000000000],
        [0x00000000030007c0, 0x0060006000200020,
            0x006007e007f00ff0, 0x0780000000000000],
        [0x00000000000007c0, 0x07c000c000c001c0,
            0x018007800ffc0ff8, 0x0000000000000000],
        [0x0000000000000000, 0x0380018000000040,
            0x01c007f00fe00000, 0x0000000000000000],
        [0x00000000000001e0, 0x01e0002000200060,
            0x07e00ff01ff81f00, 0x0000000000000000],
        [0x00000000002001f0, 0x03f8031800100030,
            0x006003e00fc01fc0, 0x1e00000000000000],
        [0x0000000001c007e0, 0x0030001000100030,
            0x00300ff008f01dc0, 0x0f80000000000000],
        [0x00000000038007c0, 0x0040004000c00180,
            0x01800300070007f8, 0x03f0000000000000],
        [0x00000000000007c0, 0x0fe0006000600060,
            0x00c001c0038003c0, 0x07f0010000000000],
    ],
    3: [
        [0x0000000000000fe0, 0x1fe0006000e003e0,
            0x07f0003000180030, 0x04f007c000000000],
        [0x0000000000000000, 0x07c00040004000c0,
            0x03c001c000200020, 0x006000c000000000],
        [0x0000000000000f00, 0x1fc001c0018003c0,
            0x03f0001800180018, 0x01f001e000000000],
        [0x00000000000001c0, 0x00e0006000c00180,
            0x018000c0004000c0, 0x0180070000000000],
        [0x00000000018003c0, 0x006000c001c003e0,
            0x00600020002000e0, 0x0fc0030000000000],
        [0x00000000000001f0, 0x03f00230007001e0,
            0x03e00060006000e0, 0x1fc01f0000000000],
        [0x0000000003000fc0, 0x00c000c003c003e0,
            0x0030001000180030, 0x07f0038000000000],
        [0x00000000008007e0, 0x07e0006001e003f0,
            0x0130001800381cf0, 0x1fe0078000000000],
        [0x0000000000e003f0, 0x0030003000e003e0,
            0x00600020002010e0, 0x1fc00f0000000000],
        [0x00000000000000f0, 0x00f8003000f001e0,
            0x00e0002000e01fc0, 0x1f00000000000000],
        [0x00000000000003e0, 0x07e0006000e003c0,
            0x03e0002000200060, 0x05e0078000000000],
        [0x0000000000000780, 0x04c000c001800380,
            0x03c0006000200020, 0x00e003c000000000],
    ],
    4: [
        [0x0000000000000008, 0x0018013003200660,
            0x0fe007c001800300, 0x0200000000000000],
        [0x0000000000000000, 0x020806180c180c30,
            0x1ff00fe000c000c0, 0x0180018000000000],
        [0x0000000000000000, 0x0020022002600640,
            0x07c007c001800180, 0x0100010000000000],
        [0x0000000000000010, 0x0010023006200460,
            0x0fe00fc000c00080, 0x0180018000000000],
        [0x0000000000000000, 0x0040044004400640,
            0x07c000c000c000c0, 0x00c0008000000000],
        [0x0000000000000000, 0x0820183018301830,
            0x1ff00ff000300030, 0x0010001000000000],
        [0x0000000000000000, 0x046004600c600c60,
            0x0fe007e000600020, 0x0020002000000000],
        [0x0000000000000000, 0x010c031806300e30,
            0x0fe007c001800180, 0x0300020000000000],
        [0x0000000000000000, 0x04300c300c300c60,
            0x0fe007e000600040, 0x00c000c000000000],
        [0x0000000000000000, 0x060006100c100c30,
            0x0c301ff00e600020, 0x0020000000000000],
        [0x0000000000000000, 0x0200022006200420,
            0x066007e000400040, 0x0040004000000000],
        [0x0000000000000040, 0x00c001c003400640,
            0x0ee00ff000c000c0, 0x0040000000000000],
    ],
    5: [
        [0x00000000000003e0, 0x0780060007c007f0,
            0x0010001800180030, 0x07e003c000000000],
        [0x0000000000000000, 0x0000007c01c00300,
            0x0300000001800f00, 0x0000000000000000],
        [0x0000000000000000, 0x01f807c006000400,
            0x0600038000400040, 0x004001c000000000],
        [0x00000000000000f0, 0x01e0030002000300,
            0x0380004000600060, 0x00c0038000000000],
        [0x00000000000001f8, 0x01c00300030003e0,
            0x00600030002008e0, 0x0fc0030000000000],
        [0x000000000000003c, 0x00f8018003000300,
            0x038000c000c000c0, 0x0f80070000000000],
        [0x00000000000007e0, 0x0fc00c000c000fe0,
            0x0630001800080018, 0x033801e000000000],
        [0x00000000000003c0, 0x02000600060003c0,
            0x0060002000300020, 0x03e0018000000000],
        [0x00000000000001f8, 0x07f00600060007c0,
            0x07e0003000300030, 0x04e007c000000000],
        [0x0000000000000038, 0x03fc03c006000700,
            0x07c000e000600060, 0x0fc0078000000000],
        [0x0000000000000000, 0x001c01fc03000600,
            0x0700018000c00180, 0x0f80000000000000],
        [0x0000000000000000, 0x00fc01e0030007c0,
            0x01c0006000601fc0, 0x0f00000000000000],
    ],
    6: [
        [0x0000000002000600, 0x0600040004000478,
            0x04d80798079803f0, 0x00c0000000000000],
        [0x0000000000300060, 0x00c0018003000720,
            0x06f00df00fe00fc0, 0x0700000000000000],
        [0x00000000007000e0, 0x01c0038003000600,
            0x06e007f0063007e0, 0x03c0000000000000],
        [0x0000000000e001c0, 0x0180030006000678,
            0x0cf80d980ff00fe0, 0x0380000000000000],
        [0x0000000000c000c0, 0x0180010003000260,
            0x06f007b0077007e0, 0x0380000000000000],
        [0x00000000006000c0, 0x0080018001000300,
            0x03c00360036003c0, 0x0380000000000000],
        [0x0000000001800300, 0x070006000c000c78,
            0x0cfc0dd80ff807f0, 0x0180000000000000],
        [0x0000000000300070, 0x006000c001800300,
            0x03c007e0066007c0, 0x0780000000000000],
        [0x0000000000c00180, 0x0300020006000460,
            0x05f00718061807f0, 0x03e0000000000000],
        [0x0000000001800300, 0x0300020006000670,
            0x06f8079807f003e0, 0x0180000000000000],
        [0x0000000000000400, 0x0c0008000838187c,
            0x18cc0c8c0ff807f0, 0x0000000000000000],
        [0x0000000000800180, 0x0100030002000200,
            0x02e003b0032003e0, 0x01c0000000000000],
    ],
    7: [
        [0x0000000000000000, 0x00001fe008600020,
            0x0020006000600060, 0x0060004000400000],
        [0x0000000000000000, 0x0fc00fc000400040,
            0x00c000c000c000c0, 0x00c000c000800000],
        [0x0000000000000000, 0x03f003f000300060,
            0x00c001c003800300, 0x06000c0004000000],
        [0x0000000000000000, 0x0fe00ff000300030,
            0x006000e000c001c0, 0x0180030003000000],
        [0x0000000000000000, 0x01e007e000600060,
            0x0040004000c00080, 0x0180018001800000],
        [0x0000000000000000, 0x00001ff01f300030,
            0x00300060006000c0, 0x00c0018001800000],
        [0x0000000000000000, 0x001007f80f300430,
            0x0060004000c00180, 0x0300030002000000],
        [0x0000000000000000, 0x00000fe01ff01830,
            0x0030003000300020, 0x0020002000000000],
        [0x0000000000000000, 0x03800fe000200020,
            0x0060006000400040, 0x00c000c000800000],
        [0x0000000000000000, 0x03e0006000600040,
            0x00c000c001800180, 0x0100030001000000],
        [0x0000000000000000, 0x01f007f000200060,
            0x004000c001800180, 0x0300020006000000],
        [0x0000000000000000, 0x01f007f804380030,
            0x006000c001800380, 0x070006000c000000],
    ],
    8: [
        [0x00000000000000f0, 0x03f00330036003c0,
            0x01c003c006c006c0, 0x07c0078000000000],
        [0x00000000000001c0, 0x03600220034001c0,
            0x01c001c003400240, 0x03c001c000000000],
        [0x00000000000003c0, 0x07c00c60044007c0,
            0x03c001c001a00120, 0x01e000e000000000],
        [0x00000000000003e0, 0x07f00638067007e0,
            0x03c003c007600660, 0x07e003c000000000],
        [0x00000000000003c0, 0x0e600c20046007c0,
            0x03e0033002100210, 0x033001e000000000],
        [0x00000000000001e0, 0x0330023003e003c0,
            0x03c0066004200420, 0x07e0038000000000],
        [0x00000000000000e0, 0x01900110012001c0,
            0x01c0038003800480, 0x0780070000000000],
        [0x00000000000001e0, 0x03f0061004300660,
            0x03c001c003c00240, 0x02c003c000000000],
        [0x00000000000003e0, 0x07700c300c300ff0,
            0x07f006180c080c18, 0x0ff007c000000000],
        [0x0000000000000078, 0x00f80198013001e0,
            0x03c007800d800980, 0x1f000e0000000000],
        [0x0000000000000000, 0x01f8038c06180230,
            0x03e0038007800f80, 0x0f00060000000000],
        [0x00000000000000f8, 0x03f80318023003e0,
            0x03c003c006c00cc0, 0x0d800f8000000000],
    ],
    9: [
        [0x00000000000000c0, 0x03e006300c300830,
            0x08700de007600060, 0x0040004000000000],
        [0x0000000000000000, 0x01e0033006200460,
            0x07e000c000c00080, 0x0180018001000000],
        [0x0000000000000020, 0x00f00390063006f0,
            0x07e000c001800300, 0x0200060004000000],
        [0x0000000000000020, 0x01f0039806300c70,
            0x0fe007e000c00180, 0x0180030002000000],
        [0x0000000000000100, 0x07c004c00c600fe0,
            0x07e0006000600060, 0x0060006000000000],
        [0x0000000000000000, 0x03e007300c300c70,
            0x0fe007e0006000c0, 0x00c0018001800000],
        [0x0000000000000000, 0x01c00340024003c0,
            0x03c000c000800080, 0x0080018001000000],
        [0x0000000000000000, 0x03c00360066004e0,
            0x07e002c0004000c0, 0x00c0008000800000],
        [0x0000000000000000, 0x03c006600c600c60,
            0x0ce007e000200020, 0x0020002000200000],
        [0x0000000000000000, 0x03c0064004600440,
            0x05c0034000400040, 0x0040004000400000],
        [0x0000000000000000, 0x07c00c6018301830,
            0x18700ff000300030, 0x0010001000000000],
        [0x0000000000000040, 0x01e00320026007e0,
            0x03c000c000800180, 0x0300030002000000],
    ],
}

# ==========================================
# 3. Digit Recognition Functions (Pattern Matcher)
# ==========================================

# [IMPORTANT]: Ensure the DIGIT_TEMPLATES file is generated using the
# 16x16 training code (each template list should have a length of 4).
# from templates import DIGIT_TEMPLATES


def pack_to_4x64bit(binary_list):
    """Pack 256 binary pixels into four 64-bit integers."""
    parts = []
    for i in range(4):
        chunk = binary_list[i*64: (i+1)*64]
        val = 0
        for bit in chunk:
            val = (val << 1) | int(bit)
        parts.append(val)
    return parts


def get_hamming_distance(img_parts, template_parts):
    """Calculate the bitwise difference (Hamming Distance) across 4 parts for 16x16."""
    total_distance = 0
    for i in range(4):
        diff = img_parts[i] ^ template_parts[i]
        total_distance += bin(diff).count('1')
    return total_distance


def shift_image_16x16(binary_list, dx, dy, out_buffer):
    """Shift the 16x16 image using a pre-allocated 256-byte buffer."""
    for i in range(256):
        out_buffer[i] = 0
    for y in range(16):
        for x in range(16):
            new_x = x + dx
            new_y = y + dy
            if 0 <= new_x < 16 and 0 <= new_y < 16:
                out_buffer[new_y * 16 + new_x] = binary_list[y * 16 + x]


def predict_digit(sensor_data_list):
    min_overall_distance = 257  # Maximum possible difference for 256 pixels
    best_overall_match = -1
    shifted_buffer = bytearray(256)  # Pre-allocated 256-byte memory buffer

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

    # Set buffer size to 256 bytes for memory efficiency
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

    # Scale the cropped image to fit into 16x16
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

# Set buffer to expect exactly 256 bytes (16x16)
IMG_SIZE = 16 * 16
image_buffer = bytearray()

# Initialize LEDs to OFF state
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

        # Trigger processing only when exactly 256 bytes are received
        if len(image_buffer) == IMG_SIZE:
            pyb.LED(4).on()

            start_time = time.ticks_ms()

            # Preprocess the incoming 16x16 image data
            sensor_input_16x16 = preprocess_mcu(
                image_buffer, 16, 16, threshold=127)

            predicted_number, dist = predict_digit(sensor_input_16x16)

            end_time = time.ticks_ms()
            processing_time = time.ticks_diff(end_time, start_time)

            # Update OLED display with results
            try:
                display.fill(0)
                display.text("v : " + str(predicted_number), 0, 0, 1)
                display.text("time: " + str(processing_time) + "ms", 0, 16, 1)
                display.show()
            except NameError:
                pass  # Prevent crash if the display object is not defined or disconnected

            # Send response back to the host (Laptop/PC)
            response_msg = 'RESULT:{}\n'.format(predicted_number)
            usb.write(response_msg.encode('utf-8'))

            # Clear the buffer to prepare for the next frame
            image_buffer = bytearray()

            pyb.LED(4).off()
            pyb.LED(3).off()
            pyb.LED(1).off()

            gc.collect()

    time.sleep_ms(1)
