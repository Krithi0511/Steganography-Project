import hashlib

class TextSteganography:
    def __init__(self):
        self.KEY = "CYBERSECURE2026"
    
    def hide_text(self, cover_text, secret_text):
        # Unicode spacing variations (invisible embedding)
        binary_secret = ''.join(format(ord(c), '08b') for c in secret_text)
        
        stego_chars = []
        secret_idx = 0
        
        # Use a more robust embedding by placing zero-width characters at the end or within spaces
        for i, char in enumerate(cover_text):
            stego_chars.append(char)
            if secret_idx < len(binary_secret):
                # Embed 1 bit in Unicode spacing (ZWSP/ZWNJ)
                bit = binary_secret[secret_idx]
                if bit == '1':
                    stego_chars.append(chr(0x200C))  # ZWNJ
                else:
                    stego_chars.append(chr(0x200B))  # ZWSP
                secret_idx += 1
        
        # If there are remaining bits, append them to the end
        while secret_idx < len(binary_secret):
            bit = binary_secret[secret_idx]
            if bit == '1':
                stego_chars.append(chr(0x200C))
            else:
                stego_chars.append(chr(0x200B))
            secret_idx += 1
        
        return ''.join(stego_chars)
    
    def reveal_text(self, stego_text, max_length=1000000):
        binary = []
        for char in stego_text:
            if char in [chr(0x200B), chr(0x200C)]:
                binary.append('0' if char == chr(0x200B) else '1')
        
        # Convert binary to text
        text_chars = []
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                try:
                    char_code = int(''.join(byte), 2)
                    if char_code == 0: break # Null terminator
                    text_chars.append(chr(char_code))
                except:
                    break
                if len(text_chars) >= max_length:
                    break
        return ''.join(text_chars)
