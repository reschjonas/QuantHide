from PIL import Image
import numpy as np
import os

class Steganography:
    def __init__(self):
        self.delimiter = b'###END###'
    
    def hide_message(self, image_path, message_bytes, output_path=None):
        """Hide a byte message in an image using LSB steganography"""
        # Add delimiter to the message
        message_bytes = message_bytes + self.delimiter
        
        # Open the image and convert to numpy array
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Check if the image can hold the message
        max_bytes = img_array.size // 8
        if len(message_bytes) > max_bytes:
            raise ValueError(f"Message too large! Image can only hold {max_bytes} bytes but message is {len(message_bytes)} bytes")
        
        # Flatten the image array
        flat_array = img_array.flatten()
        
        # Convert message to bit array
        message_bits = []
        for byte in message_bytes:
            # Convert each byte to bits and add to our list
            bits = [int(bit) for bit in format(byte, '08b')]
            message_bits.extend(bits)
        
        # Modify the LSB of each pixel value to hide the message
        for i in range(len(message_bits)):
            flat_array[i] = (flat_array[i] & ~1) | message_bits[i]
        
        # Reshape the array back to original dimensions
        stego_array = flat_array.reshape(img_array.shape)
        
        # Convert back to image
        stego_img = Image.fromarray(stego_array.astype(np.uint8))
        
        # Save the steganographic image
        if output_path is None:
            base, ext = os.path.splitext(image_path)
            output_path = f"{base}_stego{ext}"
        
        stego_img.save(output_path)
        return output_path
    
    def retrieve_message(self, stego_image_path):
        """Retrieve a hidden message from an image"""
        # Open the steganographic image
        stego_img = Image.open(stego_image_path)
        stego_array = np.array(stego_img)
        
        # Extract LSBs from the image
        flat_array = stego_array.flatten()
        lsbs = [flat_array[i] & 1 for i in range(flat_array.size)]
        
        # Convert extracted bits to bytes
        extracted_bytes = bytearray()
        for i in range(0, len(lsbs), 8):
            if i + 8 <= len(lsbs):
                byte = 0
                for j in range(8):
                    if lsbs[i+j]:
                        byte |= (1 << (7-j))
                extracted_bytes.append(byte)
        
        # Find the delimiter in the extracted bytes
        try:
            delimiter_index = extracted_bytes.find(self.delimiter)
            
            if delimiter_index != -1:
                # Return only the message part
                return bytes(extracted_bytes[:delimiter_index])
            else:
                # If no delimiter found, it's probably not a valid steganographic image
                raise ValueError("No hidden message found in this image")
                
        except Exception as e:
            raise ValueError(f"Error retrieving message: {str(e)}") 