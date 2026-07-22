import logging
import math

logger = logging.getLogger(__name__)

class SysExMessenger(object):

    ACK_CODES = {
        0x00: "SUCCESS",
        0x01: "WRONG MODEL ID",
        0x02: "WRONG CHECKSUM",
        0x03: "WRONG PAYLOAD SIZE"
    }

    SYSEX_HEADER = [
            0xF0,  # SysEx Start
            0x00,  # Manufacturer ID 1
            0x21,  # Manufacturer ID 2
            0x24,  # Manufacturer ID 3
            0x08,  # Device Model ID
            0x00,  # Ignore
            0x70,  # Opcode 1
    ]

    OPCODES = {
        'send_short_name': 0x01,
        "send_toggle_name": 0x02,
        "send_long_name": 0x03,
        "send_message": 0x04,
        "send_other_data": 0x05
    }

    ABLETON_TO_MC8_COLORS = {
        0: [59, 123],     #"LIGHT_PINK"
        1:[51, 115] ,     #"LIGHT_SALMON"
        2: [47, 111],     #"GOLD"
        3: [50, 114],     #"LIGHT_YELLOW"
        4: [12, 26],     #"PALE_GREEN"
        5: [29, 93],     #"AQUA"
        6: [10, 24],     #"LIGHT_BLUE"
        7: [33, 97],     #"LIGHT_STEEL_BLUE"
        8:[45, 109] ,     #"THISTLE"
        9: [38, 102],     #"LAVENDER"
        10: [56, 120],    # "SALMON"
        11: [52, 116],    # "TOMATO"
        12:[48, 112] ,    # "KHAKI"
        13: [7, 21],    # "KHAKI"
        14: [1, 15],    # "GREEN"
        15: [30, 94],    # "TURQUOISE"
        16:[31, 95] ,    # "CADET_BLUE"
        17: [32, 96],    # "STEEL_BLUE"
        18: [13, 27],    # "PALE_PURPLE"
        19: [61, 125],    # "PALE_VIOLET_RED"
        20:[60, 124] ,    # "HOT_PINK"
        21: [53, 117],    # "ORANGE_RED"
        22: [34, 98],    # "TAN"
        23: [4, 18],    # "YELLOW"
        24: [1, 15],    # "GREEN"
        25: [39, 103],    # "TEAL"
        26:[2, 16] ,    # "BLUE"
        27:[2, 16] ,    # "BLUE"
        28: [44, 108],    # "BLUE_VIOLET"
        29: [5, 19],    # "PINK"
        30: [9, 23],    # "RED"
        31: [54, 118],    # "DARK_ORANGE"
        32: [35, 99],    # "BROWN"
        33:[4, 18] ,    # "YELLOW"
        34: [1, 15],    # "GREEN"
        35: [39, 103],    # "TEAL"
        36: [2, 16],    # "BLUE"
        37: [2, 16],    # "BLUE"
        38:[3, 17] ,    # "PURPLE"
        39: [11, 25],    # "DARK_PINK"
        40: [55, 119],    # "INDIAN_RED"
        41: [8, 22],    # "ORANGE"
        42: [49, 113],    # "DARK_KHAKI"
        43: [42, 106],    # "OLIVE"
        44: [40, 104],    # "DARK_SEA_GREEN"
        45: [39, 103],    # "TEAL"
        46: [31, 95],    # "CADET_BLUE"
        47:[32, 96] ,    # "STEEL_BLUE"
        48: [46, 110],    # "REBECCA_PURPLE"
        49: [3, 17],    # "PURPLE"
        50: [57, 121],    # "FIRE_BRICK"
        51: [37, 101],    # "MAROON"
        52: [35, 99],    # "BROWN"
        53: [42, 106],    # "OLIVE"
        54: [41, 105],    # "FOREST_GREEN"
        55: [39, 103],    # "TEAL"
        56: [31, 95],    # "CADET_BLUE"
        57: [43, 107],    # "INDIGO"
        58: [43, 107],    # "INDIGO"
        59: [3, 17],    # "PURPLE"
        60:[58, 122] ,    # "DARK_RED"
        61: [37, 101],    # "MAROON"
        62: [35, 99],    # "BROWN"
        63: [42, 106],    # "OLIVE"
        64: [14, 28],    # "DARK_GREEN"
        65: [39, 103],    # "TEAL"
        66:[7, 21] ,    # "WHITE"
        67: [62, 126],    # "LIGHT_GRAY"
        68: [63, 127],    # "SLATE_GRAY"
        69: [0, 64],    # "BLACK
    }

    # Complete Ableton Live 70-Color Mapping with Hex, RGB tuples, and LOM Integers
    ABLETON_COLOR_PALETTE = [
        {'id':0,"hex": "#FF9999", "rgb": (255, 153, 153), "lom_int": 16751001},
        {'id':1,"hex": "#FFB399", "rgb": (255, 179, 153), "lom_int": 16757657},
        {'id':2,"hex": "#FFCC99", "rgb": (255, 204, 153), "lom_int": 16764057},
        {'id':3,"hex": "#FFE699", "rgb": (255, 230, 153), "lom_int": 16770713},
        {'id':4,"hex": "#FFFF99", "rgb": (255, 255, 153), "lom_int": 16777113},
        {'id':5,"hex": "#E6FF99", "rgb": (230, 255, 153), "lom_int": 15138713},
        {'id':6,"hex": "#CCFF99", "rgb": (204, 255, 153), "lom_int": 13434777},
        {'id':7,"hex": "#B3FF99", "rgb": (179, 255, 153), "lom_int": 11796377},
        {'id':8,"hex": "#99FF99", "rgb": (153, 255, 153), "lom_int": 10092441},
        {'id':9,"hex": "#99FFA6", "rgb": (153, 255, 166), "lom_int": 10092454},
        {'id':10,"hex": "#99FFB3", "rgb": (153, 255, 179), "lom_int": 10092467},
        {'id':11,"hex": "#99FFCC", "rgb": (153, 255, 204), "lom_int": 10092492},
        {'id':12,"hex": "#99FFE6", "rgb": (153, 255, 230), "lom_int": 10092518},
        {'id':13,"hex": "#99FFFF", "rgb": (153, 255, 255), "lom_int": 10092543},
        {'id':14,"hex": "#E6FFFF", "rgb": (230, 255, 255), "lom_int": 15138815},
        {'id':15,"hex": "#CCFFFF", "rgb": (204, 255, 255), "lom_int": 13434879},
        {'id':16,"hex": "#B3FFFF", "rgb": (179, 255, 255), "lom_int": 11796479},
        {'id':17,"hex": "#99FFFF", "rgb": (153, 255, 255), "lom_int": 10092543},
        {'id':18,"hex": "#99E6FF", "rgb": (153, 230, 255), "lom_int": 10086143},
        {'id':19,"hex": "#99CCFF", "rgb": (153, 204, 255), "lom_int": 10079743},
        {'id':20,"hex": "#99B3FF", "rgb": (153, 179, 255), "lom_int": 10073343},
        {'id':21,"hex": "#9999FF", "rgb": (153, 153, 255), "lom_int": 10066431},
        {'id':22,"hex": "#B399FF", "rgb": (179, 153, 255), "lom_int": 11770367},
        {'id':23,"hex": "#CC99FF", "rgb": (204, 153, 255), "lom_int": 13408767},
        {'id':24,"hex": "#E699FF", "rgb": (230, 153, 255), "lom_int": 15106559},
        {'id':25,"hex": "#FF99FF", "rgb": (255, 153, 255), "lom_int": 16751103},
        {'id':26,"hex": "#FF99E6", "rgb": (255, 153, 230), "lom_int": 16751078},
        {'id':27,"hex": "#FF99CC", "rgb": (255, 153, 204), "lom_int": 16751052},
        {'id':28,"hex": "#FF99B3", "rgb": (255, 153, 179), "lom_int": 16751027},
        {'id':29,"hex": "#FF4D4D", "rgb": (255, 77, 77),   "lom_int": 16731469},
        {'id':30,"hex": "#FF734D", "rgb": (255, 115, 77),  "lom_int": 16741197},
        {'id':31,"hex": "#FF994D", "rgb": (255, 153, 47),  "lom_int": 16751181},
        {'id':32,"hex": "#FFBF4D", "rgb": (255, 191, 47),  "lom_int": 16760909},
        {'id':33,"hex": "#FFE64D", "rgb": (255, 230, 77),  "lom_int": 16770637},
        {'id':34,"hex": "#D9FF4D", "rgb": (217, 255, 77),  "lom_int": 14286669},
        {'id':35,"hex": "#B3FF4D", "rgb": (179, 255, 77),  "lom_int": 11796301},
        {'id':36,"hex": "#8CFF4D", "rgb": (140, 255, 77),  "lom_int": 9240397},
        {'id':37,"hex": "#66FF4D", "rgb": (102, 255, 77),  "lom_int": 6749965},
        {'id':38,"hex": "#4DFF4D", "rgb": (77, 255, 77),   "lom_int": 5111629},
        {'id':39,"hex": "#4DFF73", "rgb": (77, 255, 115),  "lom_int": 5111667},
        {'id':40,"hex": "#4DFF99", "rgb": (77, 255, 153),  "lom_int": 5111705},
        {'id':41,"hex": "#4DFFBF", "rgb": (77, 255, 191),  "lom_int": 5111743},
        {'id':42,"hex": "#4DFFE6", "rgb": (77, 255, 230),  "lom_int": 5111782},
        {'id':43,"hex": "#4DFFFF", "rgb": (77, 255, 255),  "lom_int": 5111807},
        {'id':44,"hex": "#4DE6FF", "rgb": (77, 230, 255),  "lom_int": 5105407},
        {'id':45,"hex": "#4DC2FF", "rgb": (77, 194, 255),  "lom_int": 5096191},
        {'id':46,"hex": "#4D99FF", "rgb": (77, 153, 255),  "lom_int": 5085695},
        {'id':47,"hex": "#4D73FF", "rgb": (77, 115, 255),  "lom_int": 5075967},
        {'id':48,"hex": "#4D4DFF", "rgb": (77, 77, 255),   "lom_int": 5066239},
        {'id':49,"hex": "#734DFF", "rgb": (115, 77, 255),  "lom_int": 7556095},
        {'id':50,"hex": "#994DFF", "rgb": (153, 77, 255),  "lom_int": 10046463},
        {'id':51,"hex": "#BF4DFF", "rgb": (191, 77, 255),  "lom_int": 12536831},
        {'id':52,"hex": "#E64DFF", "rgb": (230, 77, 255),  "lom_int": 15093247},
        {'id':53,"hex": "#FF4DFF", "rgb": (255, 77, 255),  "lom_int": 16731391},
        {'id':54,"hex": "#FF4DE6", "rgb": (255, 77, 230),  "lom_int": 16731366},
        {'id':55,"hex": "#FF4DC2", "rgb": (255, 77, 194),  "lom_int": 16731330},
        {'id':56,"hex": "#FF4D99", "rgb": (255, 77, 153),  "lom_int": 16731289},
        {'id':57,"hex": "#FF4D73", "rgb": (255, 77, 115),  "lom_int": 16731251},
        {'id':58,"hex": "#FF0000", "rgb": (255, 0, 0),     "lom_int": 16711680},
        {'id':59,"hex": "#FF3300", "rgb": (255, 51, 0),    "lom_int": 16724736},
        {'id':60,"hex": "#FF6600", "rgb": (255, 102, 0),   "lom_int": 16737792},
        {'id':61,"hex": "#FF9900", "rgb": (255, 153, 0),   "lom_int": 16750848},
        {'id':62,"hex": "#FFCC00", "rgb": (255, 204, 0),   "lom_int": 16763904},
        {'id':63,"hex": "#FFFF00", "rgb": (255, 255, 0),   "lom_int": 16776960},
        {'id':64,"hex": "#CCFF00", "rgb": (204, 255, 0),   "lom_int": 13434624},
        {'id':65,"hex": "#99FF00", "rgb": (153, 255, 0),   "lom_int": 10092288},
        {'id':66,"hex": "#FFFFFF", "rgb": (255, 255, 255), "lom_int": 16777215},
        {'id':67,"hex": "#CCCCCC", "rgb": (204, 204, 204), "lom_int": 13421772},
        {'id':68,"hex": "#808080", "rgb": (128, 128, 128), "lom_int": 8421504},
        {'id':69,"hex": "#000000", "rgb": (0, 0, 0),       "lom_int": 0}
    ]
    
        
    def __init__(self, send_midi_callback):

        self._send_midi = send_midi_callback
        self._transaction_id = 0

    def _calculate_checksum(self, sysex_bytes):
        """
        Python equivalent of the C++ XOR checksum function.
        Processes the array from index 0 up to len - 1.
        """
        ptr = sysex_bytes
        c_sum = ptr[0]
        
        for i in range(1, len(ptr)):
            c_sum ^= ptr[i]
            
        c_sum &= 0x7F
        return c_sum

    def send_name_sysex(self, button_index, name_str):
        """Constructs and delivers the explicit padded SysEx packet format"""
        # Increment transaction ID (0-127 MIDI legal limit)
        self._transaction_id = (self._transaction_id + 1) & 0x7F

        # Build Fixed Header
        sysex_bytes = [
            *self.SYSEX_HEADER,
            self.OPCODES['send_short_name'],
            button_index & 0x7F, # Opcode 3 - Button index
            0x00,  # Opcode 4
            0x00,  # Opcode 5
            0x00,  # Opcode 6
            0x00,  # Opcode 7
            self._transaction_id, # Transaction ID
            0x00,  # Ignore
            0x00   # Ignore
        ]

        # Force the string to be EXACTLY 32 characters long using space padding (ASCII 32)
        padded_name = name_str[:32].ljust(32, ' ')

        # Convert the fixed 32-character string to ASCII bytes
        ascii_payload = [ord(char) & 0x7F for char in padded_name]
        sysex_bytes.extend(ascii_payload)

        # Calculate checksum using the XOR algorithm on the current array
        checksum_byte = self._calculate_checksum(sysex_bytes)
        sysex_bytes.append(checksum_byte)

        # Append End of SysEx
        sysex_bytes.append(0xF7)

        # Deliver packet to hardware via the provided framework callback
        self._send_midi(tuple(sysex_bytes))

    def send_color_sysex(self, button_index, color):
        """Constructs and delivers the explicit padded SysEx packet format"""
        # Increment transaction ID (0-127 MIDI legal limit)
        self._transaction_id = (self._transaction_id + 1) & 0x7F



        hexNumberDim = int(self.ABLETON_TO_MC8_COLORS[color][1]) 
        hexNumberFull = int(self.ABLETON_TO_MC8_COLORS[color][0])

        # Build Fixed Header
        sysex_bytes = [
            *self.SYSEX_HEADER,
            self.OPCODES['send_other_data'],
            button_index & 0x7F, # Opcode 3 - Button index
            0x00,  # Opcode 4
            0x00,  # Opcode 5
            0x00,  # Opcode 6
            0x00,  # Opcode 7
            self._transaction_id, # Transaction ID
            0x00,  # Ignore
            0x00,   # Ignore
            0x01,  # Preset Toggle: 7F = ON, 00 = OFF, Other = IGNORE
            0x01,  # Preset Blink: 7F = ON, 00 = OFF, Other = IGNORE
            0x01,  # Preset Message Scroll Mode: 7F = ON, 00 = OFF, Other = IGNORE
            0x11,  # Preset Global Toggle Group: 00 = Independent, 01-10 = Groups 1 to 16, Other = IGNORE
            hexNumberDim,  # Pos 1 LED Color        (PRO only) F7 = IGNORE
            hexNumberFull,  # Pos 2 LED Color        (PRO only) F7 = IGNORE
            0x7F,     # Shift LED Color        (PRO only) F7 = IGNORE
            0x7F,     # Pos 1 Text Color       (PRO only) F7 = IGNORE
            0x7F,     # Pos 2 Text Color       (PRO only) F7 = IGNORE
            0x7F,     # Shift Text Color       (PRO only) F7 = IGNORE
            0x7F,     # Pos 1 Background Color (PRO only) F7 = IGNORE
            0x7F,     # Pos 2 Background Color (PRO only) F7 = IGNORE
            0x7F     # Shift Background Color (PRO only) F7 = IGNORE
        ]

        # logger.info(sysex_bytes)

        # Calculate checksum using the XOR algorithm on the current array
        checksum_byte = self._calculate_checksum(sysex_bytes)
        sysex_bytes.append(checksum_byte)

        # Append End of SysEx
        sysex_bytes.append(0xF7)

        # Deliver packet to hardware via the provided framework callback
        self._send_midi(tuple(sysex_bytes))

    def parse_incoming_sysex(self, midi_bytes):
        """
        Validates the structure, verifies the checksum, 
        and logs error codes sent back from the hardware.
        """
        # 1. Structural Verification: Ensure minimum length matches expected format (18 bytes)
        if len(midi_bytes) < 18:
            return

        # 2. Check Header Signature (F0 00 21 24 08) and Opcodes (70 7F)
        if (midi_bytes[0] != 0xF0 or 
            midi_bytes[1] != 0x00 or 
            midi_bytes[2] != 0x21 or 
            midi_bytes[3] != 0x24 or 
            midi_bytes[4] != 0x08 or
            midi_bytes[6] != 0x70 or
            midi_bytes[7] != 0x7F):
            return # This packet is not meant for this script

        # 3. Checksum Verification: Slice all elements excluding Checksum and F7
        # Your C++ code loops up to len-2, which means it evaluates indices 0 through 15.
        body_to_verify = list(midi_bytes[:-2])
        calculated_cs = self._calculate_checksum(body_to_verify)
        received_cs = midi_bytes[16]

        if calculated_cs != received_cs:
            logger.error(f"[SysEx Error] Inbound Ack package failed checksum verification! "
                          f"Expected: {calculated_cs}, Received: {received_cs}")
            return

        # 4. Extract Payload Context
        ack_code = midi_bytes[8]
        transaction_id = midi_bytes[13]

        # 5. Handle and Log results
        ack_status = self.ACK_CODES.get(ack_code, f"UNKNOWN ERROR CODE ({hex(ack_code)})")
        
        if ack_code != 0x00:
            # Format and write an alert directly into Ableton Live's internal log file (Log.txt)
            logger.error(f"[Hardware Alert] Transaction ID {transaction_id} reported an error: {ack_status}")
        else:
            # Optional: Uncomment if you want to track successful handshakes while debugging
            # Live.Base.log(f"[Hardware Success] Transaction ID {transaction_id} acknowledged successfully.")
            pass

