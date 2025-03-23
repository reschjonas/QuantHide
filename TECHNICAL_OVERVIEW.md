# Technical Overview of Kyber

This document provides a detailed technical explanation of the technologies, cryptographic methods, and implementation details used in the Kyber application.

## Table of Contents

1. [Post-Quantum Cryptography](#post-quantum-cryptography)
2. [MLKEM-1024 (Kyber)](#mlkem-1024-kyber)
3. [Steganography Implementation](#steganography-implementation)
4. [Krypton Cipher](#krypton-cipher)
5. [Key Management System](#key-management-system)
6. [Application Architecture](#application-architecture)
7. [Security Considerations](#security-considerations)

## Post-Quantum Cryptography

### The Quantum Threat

Traditional public-key cryptography systems (like RSA and ECC) rely on mathematical problems that are difficult for classical computers to solve, such as integer factorization and discrete logarithms. Quantum computers, which utilize quantum bits (qubits) and can exist in multiple states simultaneously, can solve these problems efficiently using algorithms like Shor's algorithm. This poses an existential threat to current cryptographic infrastructure.

A sufficiently powerful quantum computer could break most of the cryptography currently used to secure the internet and sensitive communications. While large-scale quantum computers don't exist yet, data encrypted today could be stored and decrypted later when quantum computers become available—a threat known as "harvest now, decrypt later."

### Post-Quantum Cryptography Standardization

To address this threat, the National Institute of Standards and Technology (NIST) initiated a process to develop and standardize quantum-resistant cryptographic algorithms. After several rounds of evaluation, NIST selected a set of algorithms considered resistant to attacks from both classical and quantum computers.

One of the selected algorithms is Kyber (officially known as ML-KEM or CRYSTALS-Kyber), which is implemented in this application as MLKEM-1024.

## MLKEM-1024 (Kyber)

### Overview

MLKEM-1024 is a Key Encapsulation Mechanism (KEM) based on the hardness of the Module Learning With Errors (MLWE) problem. Unlike traditional public-key encryption, a KEM is designed specifically for establishing shared secrets between parties, which can then be used with symmetric encryption.

The "1024" in MLKEM-1024 indicates the security level, with larger numbers providing stronger security (at the cost of larger keys and ciphertexts).

### How MLKEM-1024 Works

1. **Key Generation**: Creates a public and private key pair
   ```python
   public_key, secret_key = kem.keygen()
   ```

2. **Encapsulation**: Uses the recipient's public key to create a ciphertext and a shared secret
   ```python
   cipher_text, shared_secret = kem.encaps(public_key)
   ```

3. **Decapsulation**: Uses the recipient's private key and the ciphertext to recover the shared secret
   ```python
   shared_secret = kem.decaps(secret_key, cipher_text)
   ```

### Implementation in Kyber

In the Kyber application, we utilize the QuantCrypt library's implementation of MLKEM-1024:

```python
from quantcrypt.kem import MLKEM_1024

# Create an instance of the KEM algorithm
kem = MLKEM_1024()

# Generate keypair
public_key, secret_key = kem.keygen()

# Encrypt a message to a recipient (using their public key)
encryption_result = key_manager.encrypt_message(recipient_name, message_bytes)

# Decrypt a message (using your private key)
encryption_key = key_manager.decrypt_message(decryptor_name, cipher_data)
```

The application manages these operations through the `KeyManager` class, which provides a higher-level interface for generating, storing, and using keypairs.

## Steganography Implementation

### Least Significant Bit (LSB) Steganography

Kyber employs LSB steganography to hide encrypted messages within ordinary images. This technique works by replacing the least significant bits of pixel values in an image with bits from the message. Since modifying the least significant bit causes only minor changes to the pixel color, these modifications are imperceptible to the human eye.

### Implementation Details

The `Steganography` class handles the embedding and extraction of messages:

```python
def hide_message(self, image_path, message_bytes, output_path=None):
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
```

Key aspects of the implementation:

1. **Message Delimiter**: A special delimiter (`###END###`) is added to mark the end of the message.
2. **Capacity Check**: The application verifies that the image has sufficient capacity to hold the message.
3. **Bit Manipulation**: Each bit of the message is stored in the least significant bit of a pixel value.
4. **Original Format Preservation**: The modified image maintains the same dimensions and format as the original.

For extraction, the process is reversed:

```python
def retrieve_message(self, stego_image_path):
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
    delimiter_index = extracted_bytes.find(self.delimiter)
    if delimiter_index != -1:
        # Return only the message part
        return bytes(extracted_bytes[:delimiter_index])
    else:
        # If no delimiter found, it's probably not a valid steganographic image
        raise ValueError("No hidden message found in this image")
```

## Krypton Cipher

Before being hidden in images, messages are encrypted using the Krypton cipher from the QuantCrypt library. Krypton is a symmetric cipher based on AES-256 with additional security features.

### Architecture

Krypton employs a layered approach to encryption:

1. **Plaintext Masking**: Input is masked by XORing with a bytestream generated by a keyed cSHAKE256 hash function.
2. **AES-256 Encryption**: The masked data is then encrypted using AES-256 in EAX mode.
3. **Verification Data**: The nonce and authentication tag are encrypted with AES-256 in SIV mode.

### Key Derivation

The 64-byte master key used by Krypton is derived using Argon2, a memory-hard key derivation function:

```python
# Derive encryption key from shared secret using Argon2
argon = Argon2.Key(shared_secret)
encryption_key = argon.secret_key
```

This provides protection against brute-force attacks, even with quantum computing resources.

### Integration with MLKEM-1024

The complete encryption/decryption flow in the application is:

1. **Encryption**:
   - Generate ciphertext and shared secret using recipient's public key
   - Derive encryption key from shared secret using Argon2
   - Encrypt message using Krypton cipher with derived key
   - Hide encrypted message in image using LSB steganography

2. **Decryption**:
   - Extract encrypted message from image using LSB steganography
   - Recover shared secret using recipient's private key
   - Derive encryption key from shared secret using Argon2
   - Decrypt message using Krypton cipher with derived key

## Key Management System

The application includes a comprehensive key management system implemented in the `KeyManager` class. This system provides:

### Key Generation and Storage

```python
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
```

Keys are stored in JSON format with:
- Human-readable names for easy identification
- Base64-encoded "armored" format for both public and private keys
- Algorithm identification

### Key Import/Export

The system supports various ways to share public keys:

1. **File-based Import/Export**:
   ```python
   def export_public_key_to_file(self, keypair_name, output_path=None):
       # Export public key to a standalone file
       ...
   
   def import_public_key_from_file(self, file_path):
       # Import a public key from a file
       ...
   ```

2. **QR Code Generation**:
   ```python
   def generate_key_qr_code(self, keypair_name, size=400):
       # Generate a QR code containing the public key
       ...
   
   def read_key_from_qr_code(self, image):
       # Extract a public key from a QR code image
       ...
   ```

3. **Clipboard Support**:
   ```python
   def export_public_key_to_clipboard(self, keypair_name):
       # Copy public key to clipboard for easy sharing
       ...
   ```

### Message Encryption/Decryption

The `CryptoStego` class combines the key management, encryption, and steganography operations:

```python
def hide_encrypted_message(self, image_path, message, recipient_name, output_path=None):
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
```

## Application Architecture

The Kyber application is built with a modular architecture consisting of several main components:

### Core Components

1. **App**: The main application class that initializes the UI and handles user interactions.
2. **KeyManager**: Manages cryptographic keys (generation, storage, import/export).
3. **Steganography**: Handles hiding and retrieving data in images.
4. **CryptoStego**: Integrates cryptographic operations with steganography.

### User Interface

The application uses CustomTkinter to provide a modern, user-friendly interface with the following tabs:

1. **Hide**: For selecting images, entering messages, and encrypting them.
2. **Reveal**: For selecting steganographic images and decrypting hidden messages.
3. **Keys**: For generating and managing cryptographic keys.
4. **QR**: For sharing public keys via QR codes.
5. **Help**: For providing usage information and documentation.

### Workflows

#### Hide Message Workflow:
1. User selects an image and enters a message
2. User selects a recipient's public key
3. Application encrypts the message using MLKEM-1024 and Krypton
4. Encrypted message is hidden in the image using LSB steganography
5. Output image is saved

#### Reveal Message Workflow:
1. User selects a steganographic image
2. User selects their private key
3. Application extracts the hidden data from the image
4. Application decrypts the message using the private key
5. Decrypted message is displayed to the user

## Security Considerations

### Cryptographic Strength

1. **Post-Quantum Security**: MLKEM-1024 offers security equivalent to AES-256 against quantum attacks.
2. **Key Sizes**: Public keys are ~1.5KB, private keys ~3KB, and ciphertexts ~1.5KB.
3. **Shared Secret**: The KEM produces a 32-byte shared secret, which is expanded to 64 bytes using Argon2.

### Steganographic Security

1. **Visual Imperceptibility**: Changes to the image are not visible to the human eye.
2. **Statistical Analysis Resistance**: LSB steganography can be detected through statistical analysis of large image sets, but detecting a single steganographic image without a reference is difficult.
3. **Capacity Limitations**: Each pixel can only store 1 bit of the message, so large messages require large images.

### Implementation Security

1. **Secure Key Storage**: Keys are stored in separate files with clear ownership.
2. **Memory Management**: Sensitive data is not unnecessarily persisted in memory.
3. **Input Validation**: The application validates inputs to prevent attacks.

## Conclusion

Kyber combines post-quantum cryptography with steganography to provide a secure communication method resistant to both current and future threats. By leveraging the NIST-selected MLKEM-1024 algorithm, the Krypton cipher, and LSB steganography, it offers robust protection for sensitive communications.

This application demonstrates how post-quantum cryptographic primitives can be integrated into practical applications, providing a bridge to the post-quantum future of secure communications. 