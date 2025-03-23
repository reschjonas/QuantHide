
# Kyber

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![Status](https://img.shields.io/badge/status-beta-yellow)

A quantum-resistant steganography tool that hides messages in images using post-quantum cryptography. Protects your communications against future quantum computers.

![Kyber Preview](https://i.imgur.com/example.png)

## ✨ Features

- **Quantum-Safe Encryption** - Uses MLKEM-1024 (Kyber) algorithm selected by NIST for standardization
- **Steganography** - Conceals encrypted messages within ordinary images using LSB technique
- **Key Management** - Generate, import, export, and manage quantum-resistant keys
- **QR Code Support** - Share public keys via QR codes
- **Modern Interface** - Clean, intuitive UI built with CustomTkinter
- **Drag & Drop** - Easy file handling with drag and drop support

## 🔒 Security

Kyber employs the following security measures:

- **Post-Quantum Protection** - Resistant to attacks from quantum computers
- **Krypton Cipher** - Advanced symmetric encryption alongside Kyber KEM
- **Argon2 KDF** - Secure key derivation with high memory cost parameters
- **LSB Steganography** - Visually undetectable message hiding

## 📥 Installation

### Prerequisites

- Python 3.8 or higher

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/kyber.git
cd kyber
```

2. Install dependencies:
```bash
pip install quantcrypt customtkinter pillow numpy pyperclip qrcode
```

3. Run the application:
```bash
python main.py
```

## 📚 Usage

### Hide a Message

1. Go to the **Hide** tab
2. Select a carrier image
3. Enter your message
4. Choose a recipient's public key
5. Click "Hide Message"

### Reveal a Message

1. Go to the **Reveal** tab
2. Select a stego image
3. Select your private key
4. Click "Reveal Message"

### Manage Keys

1. Go to the **Keys** tab
2. Generate a new keypair with a unique name
3. Export your public key to share with others
4. Import public keys received from your contacts

## 💡 How It Works

Kyber combines post-quantum cryptography with steganography:

1. **Key Encapsulation** - The recipient's public key is used to encapsulate a shared secret
2. **Symmetric Encryption** - The message is encrypted using the Krypton cipher
3. **Steganography** - The encrypted data is hidden in the least significant bits of image pixels
4. **Decryption** - Only the recipient with the matching private key can extract and decrypt the message

## 🔧 Advanced Features

- **QR Code Key Sharing** - Generate QR codes from public keys for easy sharing
- **Clipboard Support** - Copy/paste keys and revealed messages
- **Drag and Drop** - Easily load images by dragging them onto the application

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [QuantCrypt](https://github.com/aabmets/quantcrypt) - Post-quantum cryptography library
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern UI library for Tkinter
- [NIST](https://www.nist.gov/pqcrypto) - For their work on post-quantum cryptography standardization
