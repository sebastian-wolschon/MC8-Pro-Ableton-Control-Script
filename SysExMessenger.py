import logging

logger = logging.getLogger(__name__)

class SysExMessenger(object):

    ACK_CODES = {
        0x00: "SUCCESS",
        0x01: "WRONG MODEL ID",
        0x02: "WRONG CHECKSUM",
        0x03: "WRONG PAYLOAD SIZE"
    }
        
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
            0xF0,  # SysEx Start
            0x00,  # Manufacturer ID 1
            0x21,  # Manufacturer ID 2
            0x24,  # Manufacturer ID 3
            0x08,  # Device Model ID
            0x00,  # Ignore
            0x70,  # Opcode 1
            0x01,  # Opcode 2 - Update Preset Short Name
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