import os
import json
from pathlib import Path
import base64
from quantcrypt.kem import MLKEM_1024
from quantcrypt.kdf import Argon2
import qrcode
from io import BytesIO
from PIL import Image
import pyperclip

class KeyManager:
    def __init__(self, keys_dir='keys'):
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(exist_ok=True, parents=True)
        self.kem = MLKEM_1024()
        self.keypairs = {}
        self.load_keypairs()
    
    def load_keypairs(self):
        """Load all keypairs from the keys directory"""
        self.keypairs = {}
        
        # Load keypairs from JSON files
        for key_file in self.keys_dir.glob('*.json'):
            try:
                with open(key_file, 'r') as f:
                    keypair_data = json.load(f)
                    name = keypair_data.get('name')
                    if name:
                        self.keypairs[name] = keypair_data
            except Exception as e:
                print(f"Error loading keypair from {key_file}: {str(e)}")
    
    def generate_keypair(self, name):
        """Generate a new quantum-safe keypair"""
        public_key, secret_key = self.kem.keygen()
        
        # Convert binary keys to armored format for storage
        armored_public = self.kem.armor(public_key)
        armored_secret = self.kem.armor(secret_key)
        
        # Create keypair data structure
        keypair = {
            'name': name,
            'algorithm': 'MLKEM_1024',
            'public_key': armored_public,
            'secret_key': armored_secret
        }
        
        # Save to file
        key_path = self.keys_dir / f"{name}.json"
        with open(key_path, 'w') as f:
            json.dump(keypair, f, indent=2)
        
        # Add to in-memory keypairs
        self.keypairs[name] = keypair
        return keypair
    
    def get_keypair(self, name):
        """Retrieve a keypair by name"""
        return self.keypairs.get(name)
    
    def get_keypair_names(self):
        """Get a list of all keypair names"""
        return list(self.keypairs.keys())
    
    def import_public_key(self, name, armored_public_key):
        """Import just a public key for encryption to others"""
        # Validate the public key
        try:
            binary_public_key = self.kem.dearmor(armored_public_key)
            
            # Create keypair data with only public key
            keypair = {
                'name': name,
                'algorithm': 'MLKEM_1024',
                'public_key': armored_public_key,
                'secret_key': None  # No secret key available for imported public keys
            }
            
            # Save to file
            key_path = self.keys_dir / f"{name}.json"
            with open(key_path, 'w') as f:
                json.dump(keypair, f, indent=2)
            
            # Add to in-memory keypairs
            self.keypairs[name] = keypair
            return keypair
        except Exception as e:
            raise ValueError(f"Invalid public key: {str(e)}")
    
    def delete_keypair(self, name):
        """Delete a keypair"""
        if name in self.keypairs:
            key_path = self.keys_dir / f"{name}.json"
            if key_path.exists():
                key_path.unlink()
            del self.keypairs[name]
            return True
        return False
    
    def encrypt_message(self, recipient_keypair_name, message):
        """Encrypt a message using the recipient's public key"""
        if recipient_keypair_name not in self.keypairs:
            raise ValueError(f"Keypair '{recipient_keypair_name}' not found")
        
        keypair = self.keypairs[recipient_keypair_name]
        if not keypair.get('public_key'):
            raise ValueError(f"Public key not available for '{recipient_keypair_name}'")
        
        # Get binary public key
        binary_public_key = self.kem.dearmor(keypair['public_key'])
        
        # Generate ciphertext and shared secret
        cipher_text, shared_secret = self.kem.encaps(binary_public_key)
        
        # Derive encryption key from shared secret using Argon2
        argon = Argon2.Key(shared_secret)
        encryption_key = argon.secret_key
        
        # Return both the ciphertext (for decryption) and the key (for Krypton)
        return {
            'kdf_salt': argon.public_salt,
            'cipher_text': base64.b64encode(cipher_text).decode('utf-8'),
            'encryption_key': encryption_key
        }
    
    def decrypt_message(self, owner_keypair_name, cipher_data):
        """Decrypt a message using the owner's secret key and the ciphertext"""
        if owner_keypair_name not in self.keypairs:
            raise ValueError(f"Keypair '{owner_keypair_name}' not found")
        
        keypair = self.keypairs[owner_keypair_name]
        if not keypair.get('secret_key'):
            raise ValueError(f"Secret key not available for '{owner_keypair_name}'")
        
        # Get binary secret key
        binary_secret_key = self.kem.dearmor(keypair['secret_key'])
        
        # Decode ciphertext from base64
        cipher_text = base64.b64decode(cipher_data['cipher_text'])
        
        # Recover the shared secret
        shared_secret = self.kem.decaps(binary_secret_key, cipher_text)
        
        # Derive encryption key from shared secret using Argon2 with same salt
        argon = Argon2.Key(shared_secret, cipher_data['kdf_salt'])
        encryption_key = argon.secret_key
        
        return encryption_key
        
    def generate_key_qr_code(self, keypair_name, size=400):
        """Generate a QR code containing the public key"""
        if keypair_name not in self.keypairs:
            raise ValueError(f"Keypair '{keypair_name}' not found")
            
        keypair = self.keypairs[keypair_name]
        if not keypair.get('public_key'):
            raise ValueError(f"Public key not available for '{keypair_name}'")
            
        # Create a simplified object with just name and public key
        key_data = {
            'name': keypair['name'],
            'algorithm': keypair['algorithm'],
            'public_key': keypair['public_key']
        }
        
        # Convert to JSON and create QR code
        key_json = json.dumps(key_data)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(key_json)
        qr.make(fit=True)
        
        # Create an image from the QR Code
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize to desired size
        img = img.resize((size, size))
        
        return img
        
    def read_key_from_qr_code(self, image):
        """Extract a public key from a QR code image"""
        try:
            from pyzbar.pyzbar import decode
            
            # Read QR code
            decoded_objects = decode(image)
            if not decoded_objects:
                raise ValueError("No QR code found in the image")
                
            # Extract data from QR code
            qr_data = decoded_objects[0].data.decode('utf-8')
            key_data = json.loads(qr_data)
            
            # Validate key data
            if not all(k in key_data for k in ["name", "algorithm", "public_key"]):
                raise ValueError("Invalid key data in QR code")
                
            # Import the key
            name = key_data['name']
            # If the key already exists, add a suffix
            original_name = name
            counter = 1
            while name in self.keypairs:
                name = f"{original_name}_{counter}"
                counter += 1
                
            return self.import_public_key(name, key_data['public_key'])
            
        except Exception as e:
            raise ValueError(f"Error reading QR code: {str(e)}")
            
    def export_public_key_to_clipboard(self, keypair_name):
        """Copy public key to clipboard for easy sharing"""
        if keypair_name not in self.keypairs:
            raise ValueError(f"Keypair '{keypair_name}' not found")
            
        keypair = self.keypairs[keypair_name]
        if not keypair.get('public_key'):
            raise ValueError(f"Public key not available for '{keypair_name}'")
            
        # Copy the public key to clipboard
        pyperclip.copy(keypair['public_key'])
        return True
        
    def export_public_key_to_file(self, keypair_name, output_path=None):
        """Export public key to a standalone file"""
        if keypair_name not in self.keypairs:
            raise ValueError(f"Keypair '{keypair_name}' not found")
            
        keypair = self.keypairs[keypair_name]
        if not keypair.get('public_key'):
            raise ValueError(f"Public key not available for '{keypair_name}'")
            
        # Create a simplified object with just name and public key
        key_data = {
            'name': keypair['name'],
            'algorithm': keypair['algorithm'],
            'public_key': keypair['public_key']
        }
        
        # Determine output path
        if output_path is None:
            output_path = f"{keypair_name}_public_key.qkey"
            
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(key_data, f, indent=2)
            
        return output_path
        
    def import_public_key_from_file(self, file_path):
        """Import a public key from a file"""
        try:
            with open(file_path, 'r') as f:
                key_data = json.load(f)
                
            # Validate key data
            if not all(k in key_data for k in ["name", "algorithm", "public_key"]):
                raise ValueError("Invalid key data in file")
                
            # Import the key
            name = key_data['name']
            # If the key already exists, add a suffix
            original_name = name
            counter = 1
            while name in self.keypairs:
                name = f"{original_name}_{counter}"
                counter += 1
                
            return self.import_public_key(name, key_data['public_key'])
            
        except Exception as e:
            raise ValueError(f"Error importing key: {str(e)}") 