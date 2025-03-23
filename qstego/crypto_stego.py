import json
import base64
from quantcrypt.cipher import Krypton
from .steganography import Steganography
from .key_manager import KeyManager

class CryptoStego:
    def __init__(self, keys_dir='keys'):
        self.stego = Steganography()
        self.key_manager = KeyManager(keys_dir)
    
    def hide_encrypted_message(self, image_path, message, recipient_name, output_path=None):
        """
        Encrypt a message and hide it in an image
        
        Args:
            image_path: Path to the carrier image
            message: Text message to hide
            recipient_name: Name of the recipient's keypair
            output_path: Optional path to save the output image
            
        Returns:
            Path to the output steganographic image
        """
        # Convert message to bytes if it's a string
        if isinstance(message, str):
            message_bytes = message.encode('utf-8')
        else:
            message_bytes = message
        
        # Encrypt the message using quantum-safe encryption
        encryption_result = self.key_manager.encrypt_message(recipient_name, message_bytes)
        
        # Create a Krypton cipher with the derived encryption key
        krypton = Krypton(encryption_result['encryption_key'])
        
        # Encrypt the message
        krypton.begin_encryption()
        encrypted_message = krypton.encrypt(message_bytes)
        verification_data = krypton.finish_encryption()
        
        # Prepare metadata
        metadata = {
            'recipient': recipient_name,
            'kdf_salt': encryption_result['kdf_salt'],
            'cipher_text': encryption_result['cipher_text'],
            'verification_data': base64.b64encode(verification_data).decode('utf-8')
        }
        
        # Combine metadata and encrypted message
        stego_payload = {
            'metadata': metadata,
            'encrypted_message': base64.b64encode(encrypted_message).decode('utf-8')
        }
        
        # Convert to JSON and then to bytes
        payload_bytes = json.dumps(stego_payload).encode('utf-8')
        
        # Hide the encrypted message in the image
        output_path = self.stego.hide_message(image_path, payload_bytes, output_path)
        
        return output_path
    
    def retrieve_encrypted_message(self, stego_image_path, decryptor_name):
        """
        Retrieve and decrypt a message hidden in an image
        
        Args:
            stego_image_path: Path to the steganographic image
            decryptor_name: Name of the keypair to use for decryption
            
        Returns:
            The decrypted message as bytes
        """
        # Extract the hidden data from the image
        payload_bytes = self.stego.retrieve_message(stego_image_path)
        
        # Parse the JSON payload
        try:
            stego_payload = json.loads(payload_bytes.decode('utf-8'))
            
            metadata = stego_payload['metadata']
            encrypted_message = base64.b64decode(stego_payload['encrypted_message'])
            verification_data = base64.b64decode(metadata['verification_data'])
            
            # Prepare cipher data for decryption
            cipher_data = {
                'kdf_salt': metadata['kdf_salt'],
                'cipher_text': metadata['cipher_text']
            }
            
            # Decrypt the KEM ciphertext to get the encryption key
            encryption_key = self.key_manager.decrypt_message(decryptor_name, cipher_data)
            
            # Create a Krypton cipher with the decrypted key
            krypton = Krypton(encryption_key)
            
            # Decrypt the message
            krypton.begin_decryption(verification_data)
            decrypted_message = krypton.decrypt(encrypted_message)
            krypton.finish_decryption()
            
            return decrypted_message
            
        except Exception as e:
            raise ValueError(f"Error decrypting message: {str(e)}")
    
    def export_public_key(self, keypair_name):
        """Export public key of a keypair for sharing"""
        keypair = self.key_manager.get_keypair(keypair_name)
        if not keypair:
            raise ValueError(f"Keypair '{keypair_name}' not found")
        
        return keypair['public_key'] 