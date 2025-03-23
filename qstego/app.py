import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path
import pyperclip
import webbrowser
from tkinter import ttk

from .crypto_stego import CryptoStego

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set window title and size
        self.title("QuantumStego - Quantum-Safe Steganography")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Create directories if needed
        self.home_dir = os.path.dirname(os.path.abspath(__file__))
        self.keys_dir = os.path.join(self.home_dir, "keys")
        self.images_dir = os.path.join(self.home_dir, "images")
        
        os.makedirs(self.keys_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Initialize the steganography and crypto components
        self.crypto_stego = CryptoStego(self.keys_dir)
        
        # Create main container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Create tabs
        self.tabview.add("Hide")
        self.tabview.add("Reveal")
        self.tabview.add("QR Codes")
        self.tabview.add("Keys")
        self.tabview.add("Help")
        
        # Setup each tab
        self.setup_hide_tab()
        self.setup_reveal_tab()
        self.setup_qr_tab()
        self.setup_keys_tab()
        self.setup_help_tab()
        
        # Setup tooltips
        self.setup_tooltips()
        
        # Loading indicator label
        self.loading_label = ctk.CTkLabel(
            self, 
            text="Processing, please wait...",
            font=("Helvetica", 14, "bold"),
            fg_color=("light blue", "dark blue"),
            corner_radius=10,
            padx=20,
            pady=10
        )
        
        # Setup simplified drag and drop support
        self.setup_drag_and_drop()

    def setup_drag_and_drop(self):
        """Setup basic drop functionality for images"""
        # On Windows, we can use built-in drag and drop functionality
        # We'll connect this to our image drop zones when they're clicked
        
        # Define custom drop handlers instead of using DND_FILES
        def drop_on_hide_image(event):
            # This is just a simplified version - actual implementation would parse file path
            # and handle drops, but for now we'll just show a messagebox
            messagebox.showinfo("Drag and Drop", 
                               "Drag and drop is not fully implemented in this version.\n"
                               "Please use the 'Select Image' button instead.")
            
        def drop_on_reveal_image(event):
            messagebox.showinfo("Drag and Drop", 
                               "Drag and drop is not fully implemented in this version.\n"
                               "Please use the 'Select Image' button instead.")
            
        def drop_on_qr_image(event):
            messagebox.showinfo("Drag and Drop", 
                               "Drag and drop is not fully implemented in this version.\n"
                               "Please use the 'Select QR Code Image' button instead.")
        
        # These would be connected to the appropriate drop events in a full implementation
        # For now, we'll just note that drag and drop will be implemented in a future version
    
    def setup_hide_tab(self):
        """Setup UI for hiding encrypted messages in images"""
        hide_tab = self.tabview.tab("Hide")
        
        # Left side - Image selection and preview
        left_frame = ctk.CTkFrame(hide_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Image selection
        image_frame = ctk.CTkFrame(left_frame)
        image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(image_frame, text="Carrier Image", font=("Helvetica", 16, "bold")).pack(pady=(10, 5))
        
        self.hide_image_preview = ctk.CTkLabel(image_frame, text="Drop image here\nor click to select", width=300, height=300)
        self.hide_image_preview.pack(pady=10, padx=10)
        self.hide_image_preview.bind("<Button-1>", lambda e: self.select_hide_image())
        
        # Support drag and drop
        self.hide_image_preview.bind("<Enter>", lambda e: self.hide_image_preview.configure(cursor="hand2"))
        self.hide_image_preview.bind("<Leave>", lambda e: self.hide_image_preview.configure(cursor=""))
        
        # Add a small instruction below the image area
        ctk.CTkLabel(image_frame, text="You can drag and drop an image here", 
                    font=("Helvetica", 10, "italic"), text_color="gray").pack()
        
        select_image_btn = ctk.CTkButton(image_frame, text="Select Image", command=self.select_hide_image)
        select_image_btn.pack(pady=10)
        
        self.hide_image_path_var = tk.StringVar()
        ctk.CTkLabel(image_frame, textvariable=self.hide_image_path_var, 
                    wraplength=300, font=("Helvetica", 10)).pack(pady=5)
        
        # Right side - Message and recipient selection
        right_frame = ctk.CTkFrame(hide_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Message entry
        message_frame = ctk.CTkFrame(right_frame)
        message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(message_frame, text="Message to Hide", font=("Helvetica", 16, "bold")).pack(pady=(10, 5))
        
        self.hide_message_text = ctk.CTkTextbox(message_frame, width=300, height=200)
        self.hide_message_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Character count label
        self.hide_char_count_var = tk.StringVar(value="Characters: 0")
        ctk.CTkLabel(message_frame, textvariable=self.hide_char_count_var, 
                    font=("Helvetica", 10), anchor="e").pack(padx=10, fill=tk.X)
        
        # Update character count when text changes
        self.hide_message_text.bind("<<Modified>>", self.update_hide_char_count)
        
        # Recipient selection
        recipient_frame = ctk.CTkFrame(right_frame)
        recipient_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(recipient_frame, text="Recipient Key", font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
        
        self.hide_recipient_var = tk.StringVar()
        self.hide_recipient_combobox = ctk.CTkComboBox(
            recipient_frame, 
            values=self.crypto_stego.key_manager.get_keypair_names(),
            variable=self.hide_recipient_var,
            width=250,
            height=30
        )
        self.hide_recipient_combobox.pack(pady=10)
        
        refresh_keys_btn = ctk.CTkButton(
            recipient_frame, 
            text="Refresh Keys", 
            command=self.refresh_keys,
            width=100,
            height=30
        )
        refresh_keys_btn.pack(pady=10)
        
        # Hide action button
        hide_btn = ctk.CTkButton(
            right_frame, 
            text="Hide Message", 
            command=self.hide_message,
            fg_color=("green", "dark green"),
            hover_color=("dark green", "forest green"),
            font=("Helvetica", 14, "bold"),
            height=40
        )
        hide_btn.pack(pady=20)
        
        # Quick access buttons
        quick_frame = ctk.CTkFrame(right_frame)
        quick_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkButton(
            quick_frame,
            text="Clear Message",
            command=lambda: self.hide_message_text.delete("1.0", tk.END),
            width=120
        ).pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(
            quick_frame,
            text="Paste from Clipboard",
            command=self.paste_to_hide_message,
            width=170
        ).pack(side=tk.LEFT, padx=5)

    def setup_reveal_tab(self):
        """Setup UI for revealing hidden messages"""
        reveal_tab = self.tabview.tab("Reveal")
        
        # Left side - Image selection and preview
        left_frame = ctk.CTkFrame(reveal_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Image selection
        image_frame = ctk.CTkFrame(left_frame)
        image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(image_frame, text="Steganographic Image", font=("Helvetica", 16, "bold")).pack(pady=(10, 5))
        
        self.reveal_image_preview = ctk.CTkLabel(image_frame, text="Drop image here\nor click to select", width=300, height=300)
        self.reveal_image_preview.pack(pady=10, padx=10)
        self.reveal_image_preview.bind("<Button-1>", lambda e: self.select_reveal_image())
        
        # Support drag and drop
        self.reveal_image_preview.bind("<Enter>", lambda e: self.reveal_image_preview.configure(cursor="hand2"))
        self.reveal_image_preview.bind("<Leave>", lambda e: self.reveal_image_preview.configure(cursor=""))
        
        # Add a small instruction below the image area
        ctk.CTkLabel(image_frame, text="You can drag and drop an image here", 
                    font=("Helvetica", 10, "italic"), text_color="gray").pack()
        
        select_image_btn = ctk.CTkButton(image_frame, text="Select Image", command=self.select_reveal_image)
        select_image_btn.pack(pady=10)
        
        self.reveal_image_path_var = tk.StringVar()
        ctk.CTkLabel(image_frame, textvariable=self.reveal_image_path_var, 
                    wraplength=300, font=("Helvetica", 10)).pack(pady=5)
        
        # Right side - Decryption key selection and revealed message
        right_frame = ctk.CTkFrame(reveal_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Key selection
        key_frame = ctk.CTkFrame(right_frame)
        key_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(key_frame, text="Decryption Key", font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
        
        self.reveal_key_var = tk.StringVar()
        self.reveal_key_combobox = ctk.CTkComboBox(
            key_frame, 
            values=self.crypto_stego.key_manager.get_keypair_names(),
            variable=self.reveal_key_var,
            width=250,
            height=30
        )
        self.reveal_key_combobox.pack(pady=10)
        
        key_button_frame = ctk.CTkFrame(key_frame)
        key_button_frame.pack(fill=tk.X, pady=5)
        
        refresh_keys_btn = ctk.CTkButton(
            key_button_frame, 
            text="Refresh Keys", 
            command=self.refresh_keys,
            width=120
        )
        refresh_keys_btn.pack(side=tk.LEFT, padx=5)
        
        # Reveal action button
        reveal_btn = ctk.CTkButton(
            key_frame, 
            text="Reveal Message", 
            command=self.reveal_message,
            fg_color=("blue", "dark blue"),
            hover_color=("dark blue", "navy"),
            font=("Helvetica", 14, "bold"),
            height=40
        )
        reveal_btn.pack(pady=10)
        
        # Revealed message display
        message_frame = ctk.CTkFrame(right_frame)
        message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(message_frame, text="Revealed Message", font=("Helvetica", 16, "bold")).pack(pady=(10, 5))
        
        self.revealed_message_text = ctk.CTkTextbox(message_frame, width=300, height=200)
        self.revealed_message_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Action buttons
        action_frame = ctk.CTkFrame(message_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ctk.CTkButton(
            action_frame, 
            text="Copy to Clipboard", 
            command=self.copy_revealed_message,
            width=150
        ).pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(
            action_frame, 
            text="Save to File",
            command=self.save_revealed_message,
            width=150
        ).pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(
            action_frame,
            text="Clear",
            command=lambda: self.revealed_message_text.delete("1.0", tk.END),
            width=100
        ).pack(side=tk.LEFT, padx=5)
        
    def setup_qr_tab(self):
        """Setup UI for QR code generation and scanning"""
        qr_tab = self.tabview.tab("QR Codes")
        
        # Create left and right frames
        left_frame = ctk.CTkFrame(qr_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right_frame = ctk.CTkFrame(qr_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Generate QR code
        ctk.CTkLabel(left_frame, text="Generate QR Code for Key Sharing", 
                   font=("Helvetica", 16, "bold")).pack(pady=(10, 20))
        
        # Key selection for QR generation
        key_frame = ctk.CTkFrame(left_frame)
        key_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(key_frame, text="Select Key:").pack(side=tk.LEFT, padx=5)
        
        self.qr_gen_key_var = tk.StringVar()
        self.qr_gen_combobox = ctk.CTkComboBox(
            key_frame, 
            values=self.crypto_stego.key_manager.get_keypair_names(),
            variable=self.qr_gen_key_var,
            width=200
        )
        self.qr_gen_combobox.pack(side=tk.LEFT, padx=5)
        
        # QR code display
        self.qr_image_label = ctk.CTkLabel(left_frame, text="QR Code will appear here", width=300, height=300)
        self.qr_image_label.pack(pady=20)
        
        # Generate button
        gen_qr_btn = ctk.CTkButton(
            left_frame, 
            text="Generate QR Code", 
            command=self.generate_qr_code,
            fg_color=("green", "dark green"),
            hover_color=("dark green", "forest green")
        )
        gen_qr_btn.pack(pady=10)
        
        # Save QR code button
        save_qr_btn = ctk.CTkButton(
            left_frame, 
            text="Save QR Code as Image", 
            command=self.save_qr_code
        )
        save_qr_btn.pack(pady=10)
        
        # Right side - Scan QR code
        ctk.CTkLabel(right_frame, text="Scan QR Code to Import Key", 
                    font=("Helvetica", 16, "bold")).pack(pady=(10, 20))
        
        # QR code import
        qr_import_frame = ctk.CTkFrame(right_frame)
        qr_import_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.qr_scan_preview = ctk.CTkLabel(qr_import_frame, text="Drop QR code image here\nor click to select", 
                                          width=300, height=300)
        self.qr_scan_preview.pack(pady=20)
        self.qr_scan_preview.bind("<Button-1>", lambda e: self.select_qr_image())
        
        # Support drag and drop
        self.qr_scan_preview.bind("<Enter>", lambda e: self.qr_scan_preview.configure(cursor="hand2"))
        self.qr_scan_preview.bind("<Leave>", lambda e: self.qr_scan_preview.configure(cursor=""))
        
        # Scan button
        scan_qr_btn = ctk.CTkButton(
            qr_import_frame, 
            text="Select QR Code Image", 
            command=self.select_qr_image
        )
        scan_qr_btn.pack(pady=10)
        
        # Scan status
        self.qr_scan_status_var = tk.StringVar(value="No QR code scanned yet")
        ctk.CTkLabel(qr_import_frame, textvariable=self.qr_scan_status_var).pack(pady=10)

    def setup_keys_tab(self):
        """Setup UI for key management with improved user experience"""
        keys_tab = self.tabview.tab("Keys")
        
        # Left side - Key list and management
        left_frame = ctk.CTkFrame(keys_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Key generation
        gen_frame = ctk.CTkFrame(left_frame)
        gen_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(gen_frame, text="Generate New Keypair", 
                    font=("Helvetica", 16, "bold")).pack(pady=(10, 5))
        
        key_name_frame = ctk.CTkFrame(gen_frame)
        key_name_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(key_name_frame, text="Key Name:").pack(side=tk.LEFT, padx=5)
        
        self.new_key_name_var = tk.StringVar()
        key_name_entry = ctk.CTkEntry(key_name_frame, textvariable=self.new_key_name_var, width=200)
        key_name_entry.pack(side=tk.LEFT, padx=5)
        
        generate_btn = ctk.CTkButton(
            gen_frame, 
            text="Generate Keypair", 
            command=self.generate_keypair,
            fg_color=("green", "dark green"),
            hover_color=("dark green", "forest green"),
            font=("Helvetica", 12, "bold")
        )
        generate_btn.pack(pady=10)
        
        # Key list
        list_frame = ctk.CTkFrame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(list_frame, text="Available Keys", 
                    font=("Helvetica", 16, "bold")).pack(pady=5)
        
        self.keys_listbox_frame = ctk.CTkFrame(list_frame)
        self.keys_listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.update_keys_listbox()
        
        # Key management buttons
        btn_frame = ctk.CTkFrame(list_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        delete_btn = ctk.CTkButton(
            btn_frame, 
            text="Delete Selected", 
            command=self.delete_selected_key,
            fg_color=("red", "dark red"),
            hover_color=("dark red", "firebrick")
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ctk.CTkButton(
            btn_frame, 
            text="Refresh List", 
            command=self.refresh_keys
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Right side - Key import and export with more options
        right_frame = ctk.CTkFrame(keys_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tabview for import/export methods
        key_io_tabview = ctk.CTkTabview(right_frame)
        key_io_tabview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        key_io_tabview.add("Text Import/Export")
        key_io_tabview.add("File Import/Export")
        
        # Text Import/Export Tab
        text_tab = key_io_tabview.tab("Text Import/Export")
        
        # Import public key section
        import_frame = ctk.CTkFrame(text_tab)
        import_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(import_frame, text="Import Public Key from Text", 
                    font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
        
        key_name_frame = ctk.CTkFrame(import_frame)
        key_name_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(key_name_frame, text="Key Name:").pack(side=tk.LEFT, padx=5)
        
        self.import_key_name_var = tk.StringVar()
        import_key_name_entry = ctk.CTkEntry(key_name_frame, textvariable=self.import_key_name_var, width=200)
        import_key_name_entry.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(import_frame, text="Public Key (Base64):").pack(pady=5)
        
        self.import_key_text = ctk.CTkTextbox(import_frame, width=300, height=100)
        self.import_key_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Improved import buttons
        import_buttons_frame = ctk.CTkFrame(import_frame)
        import_buttons_frame.pack(fill=tk.X, pady=10)
        
        import_btn = ctk.CTkButton(
            import_buttons_frame, 
            text="Import Key", 
            command=self.import_public_key
        )
        import_btn.pack(side=tk.LEFT, padx=5)
        
        paste_btn = ctk.CTkButton(
            import_buttons_frame,
            text="Paste from Clipboard",
            command=lambda: self.import_key_text.insert("1.0", pyperclip.paste())
        )
        paste_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ctk.CTkButton(
            import_buttons_frame,
            text="Clear",
            command=lambda: self.import_key_text.delete("1.0", tk.END)
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Export public key section
        export_frame = ctk.CTkFrame(text_tab)
        export_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(export_frame, text="Export Public Key to Text", 
                    font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
        
        key_select_frame = ctk.CTkFrame(export_frame)
        key_select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(key_select_frame, text="Select Key:").pack(side=tk.LEFT, padx=5)
        
        self.export_key_var = tk.StringVar()
        self.export_key_combobox = ctk.CTkComboBox(
            key_select_frame, 
            values=self.crypto_stego.key_manager.get_keypair_names(),
            variable=self.export_key_var,
            width=200
        )
        self.export_key_combobox.pack(side=tk.LEFT, padx=5)
        
        export_btn = ctk.CTkButton(
            export_frame, 
            text="Export Public Key", 
            command=self.export_public_key
        )
        export_btn.pack(pady=10)
        
        ctk.CTkLabel(export_frame, text="Public Key:").pack(pady=5)
        
        self.export_key_text = ctk.CTkTextbox(export_frame, width=300, height=100)
        self.export_key_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        copy_export_btn = ctk.CTkButton(
            export_frame, 
            text="Copy to Clipboard", 
            command=self.copy_exported_key,
            width=150
        )
        copy_export_btn.pack(pady=10)
        
        # File Import/Export Tab
        file_tab = key_io_tabview.tab("File Import/Export")
        
        # File import section
        file_import_frame = ctk.CTkFrame(file_tab)
        file_import_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(file_import_frame, text="Import Key from File", 
                    font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
        
        import_file_btn = ctk.CTkButton(
            file_import_frame,
            text="Select Key File (.qkey)",
            command=self.import_key_from_file
        )
        import_file_btn.pack(pady=20)
        
        self.import_file_status_var = tk.StringVar(value="No file imported yet")
        ctk.CTkLabel(file_import_frame, textvariable=self.import_file_status_var,
                   wraplength=300).pack(pady=10)
        
        # File export section
        file_export_frame = ctk.CTkFrame(file_tab)
        file_export_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(file_export_frame, text="Export Key to File", 
                    font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
        
        key_select_frame2 = ctk.CTkFrame(file_export_frame)
        key_select_frame2.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(key_select_frame2, text="Select Key:").pack(side=tk.LEFT, padx=5)
        
        self.export_file_key_var = tk.StringVar()
        self.export_file_combobox = ctk.CTkComboBox(
            key_select_frame2, 
            values=self.crypto_stego.key_manager.get_keypair_names(),
            variable=self.export_file_key_var,
            width=200
        )
        self.export_file_combobox.pack(side=tk.LEFT, padx=5)
        
        export_file_btn = ctk.CTkButton(
            file_export_frame,
            text="Export Key to File",
            command=self.export_key_to_file
        )
        export_file_btn.pack(pady=20)
        
        self.export_file_status_var = tk.StringVar(value="No key exported yet")
        ctk.CTkLabel(file_export_frame, textvariable=self.export_file_status_var,
                    wraplength=300).pack(pady=10)
        
    def setup_help_tab(self):
        """Setup help and about information"""
        help_tab = self.tabview.tab("Help")
        
        # Create a scrollable frame
        help_scroll = ctk.CTkScrollableFrame(help_tab)
        help_scroll.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Add app title and description
        ctk.CTkLabel(help_scroll, text="QuantumStego", 
                   font=("Helvetica", 24, "bold")).pack(pady=(10, 5))
        
        ctk.CTkLabel(help_scroll, text="Quantum-Safe Steganography Tool", 
                   font=("Helvetica", 16)).pack(pady=(0, 20))
        
        # About section
        ctk.CTkLabel(help_scroll, text="About", 
                   font=("Helvetica", 18, "bold")).pack(pady=(10, 5), anchor="w")
        
        about_text = (
            "QuantumStego allows you to hide messages in images with quantum-safe encryption. "
            "It uses the MLKEM-1024 (Kyber) algorithm for post-quantum cryptography, "
            "ensuring your messages remain secure even against quantum computers."
        )
        
        ctk.CTkLabel(help_scroll, text=about_text, 
                   wraplength=800, justify="left").pack(pady=5, anchor="w")
        
        # Features section
        ctk.CTkLabel(help_scroll, text="Features", 
                   font=("Helvetica", 18, "bold")).pack(pady=(20, 5), anchor="w")
        
        features = [
            "• Hide messages in images with quantum-safe encryption",
            "• Reveal hidden messages with your private key",
            "• Generate and manage quantum-safe keys",
            "• Share public keys via text, file, or QR code",
            "• Drag-and-drop support for images",
            "• Modern, easy-to-use interface"
        ]
        
        for feature in features:
            ctk.CTkLabel(help_scroll, text=feature, 
                       justify="left").pack(pady=2, anchor="w")
        
        # Usage section
        ctk.CTkLabel(help_scroll, text="How to Use", 
                   font=("Helvetica", 18, "bold")).pack(pady=(20, 5), anchor="w")
        
        # Hide tab instructions
        ctk.CTkLabel(help_scroll, text="Hiding a Message:", 
                   font=("Helvetica", 14, "bold")).pack(pady=(10, 5), anchor="w")
        
        hide_steps = [
            "1. Go to the 'Hide' tab",
            "2. Select or drag an image to use as the carrier",
            "3. Enter the message you want to hide",
            "4. Select a recipient's public key from the dropdown",
            "5. Click 'Hide Message' to create the steganographic image"
        ]
        
        for step in hide_steps:
            ctk.CTkLabel(help_scroll, text=step, 
                       justify="left").pack(pady=2, anchor="w")
        
        # Reveal tab instructions
        ctk.CTkLabel(help_scroll, text="Revealing a Message:", 
                   font=("Helvetica", 14, "bold")).pack(pady=(10, 5), anchor="w")
        
        reveal_steps = [
            "1. Go to the 'Reveal' tab",
            "2. Select or drag the steganographic image",
            "3. Select your private key from the dropdown",
            "4. Click 'Reveal Message' to decrypt and show the hidden message",
            "5. Use the 'Copy to Clipboard' or 'Save to File' buttons as needed"
        ]
        
        for step in reveal_steps:
            ctk.CTkLabel(help_scroll, text=step, 
                       justify="left").pack(pady=2, anchor="w")
        
        # Keys tab instructions
        ctk.CTkLabel(help_scroll, text="Managing Keys:", 
                   font=("Helvetica", 14, "bold")).pack(pady=(10, 5), anchor="w")
        
        keys_steps = [
            "1. Go to the 'Keys' tab",
            "2. Generate a new keypair by entering a name and clicking 'Generate Keypair'",
            "3. Import someone's public key using text, file, or QR code",
            "4. Export your public key to share with others",
            "5. 🔑 indicates a full keypair (public+private), 🔒 indicates a public key only"
        ]
        
        for step in keys_steps:
            ctk.CTkLabel(help_scroll, text=step, 
                       justify="left").pack(pady=2, anchor="w")
        
        # QR tab instructions
        ctk.CTkLabel(help_scroll, text="Using QR Codes:", 
                   font=("Helvetica", 14, "bold")).pack(pady=(10, 5), anchor="w")
        
        qr_steps = [
            "1. Go to the 'QR Codes' tab",
            "2. Select a key from the dropdown and click 'Generate QR Code'",
            "3. Save the QR code as an image or show it directly to someone",
            "4. To import a key via QR code, select or drag a QR code image",
            "5. The app will automatically read and import the public key"
        ]
        
        for step in qr_steps:
            ctk.CTkLabel(help_scroll, text=step, 
                       justify="left").pack(pady=2, anchor="w")
        
        # Links section
        ctk.CTkLabel(help_scroll, text="Links", 
                   font=("Helvetica", 18, "bold")).pack(pady=(20, 5), anchor="w")
        
        # GitHub link
        github_btn = ctk.CTkButton(
            help_scroll,
            text="GitHub Repository",
            command=lambda: webbrowser.open("https://github.com/yourusername/quantumstego")
        )
        github_btn.pack(pady=5, anchor="w")
        
        # About post-quantum cryptography link
        pqc_btn = ctk.CTkButton(
            help_scroll,
            text="Learn About Post-Quantum Cryptography",
            command=lambda: webbrowser.open("https://csrc.nist.gov/Projects/post-quantum-cryptography")
        )
        pqc_btn.pack(pady=5, anchor="w")
        
        # Version information
        ctk.CTkLabel(help_scroll, text="Version: 1.1.0", 
                   font=("Helvetica", 10)).pack(pady=(20, 5))
        
    def setup_tooltips(self):
        """Setup tooltips for various UI elements"""
        # This could be expanded with a proper tooltip system
        pass
        
    def update_keys_listbox(self):
        """Update the keys listbox with current keys"""
        # Clear existing listbox frame contents
        for widget in self.keys_listbox_frame.winfo_children():
            widget.destroy()
        
        # Create scrollable frame for keys
        scrollable_frame = ctk.CTkScrollableFrame(self.keys_listbox_frame)
        scrollable_frame.pack(fill=tk.BOTH, expand=True)
        
        # Get key names
        key_names = self.crypto_stego.key_manager.get_keypair_names()
        
        if not key_names:
            # Show message if no keys
            ctk.CTkLabel(scrollable_frame, text="No keys found. Generate or import a key.",
                       font=("Helvetica", 12, "italic"), text_color="gray").pack(pady=20)
            self.key_var = tk.StringVar(value="")
            return
            
        # Create a label for each key
        self.key_var = tk.StringVar(value="")
        
        for i, name in enumerate(key_names):
            key = self.crypto_stego.key_manager.get_keypair(name)
            
            # Create a frame for each key entry
            key_entry_frame = ctk.CTkFrame(scrollable_frame)
            key_entry_frame.pack(fill=tk.X, padx=5, pady=3)
            
            # Create a colored indicator for full keypair vs public-only
            has_secret = key.get('secret_key') is not None
            indicator = "🔑" if has_secret else "🔒"
            indicator_color = "green" if has_secret else "blue"
            label_text = f"{indicator} {name}"
            
            radio_btn = ctk.CTkRadioButton(
                key_entry_frame,
                text=label_text,
                variable=self.key_var,
                value=name,
                fg_color=indicator_color
            )
            radio_btn.pack(side=tk.LEFT, padx=10, pady=5)
            
            # Add a text label showing the type of key
            key_type_text = "Full Keypair" if has_secret else "Public Key Only"
            ctk.CTkLabel(
                key_entry_frame,
                text=key_type_text,
                font=("Helvetica", 10),
                text_color="gray"
            ).pack(side=tk.RIGHT, padx=10, pady=5)
    
    def refresh_keys(self):
        """Refresh key lists in UI"""
        self.crypto_stego.key_manager.load_keypairs()
        self.update_keys_listbox()
        
        # Update comboboxes
        key_names = self.crypto_stego.key_manager.get_keypair_names()
        self.hide_recipient_combobox.configure(values=key_names)
        self.reveal_key_combobox.configure(values=key_names)
        self.export_key_combobox.configure(values=key_names)
        self.export_file_combobox.configure(values=key_names)
        self.qr_gen_combobox.configure(values=key_names)
    
    def update_hide_char_count(self, event=None):
        """Update character count for hide message textbox"""
        # Get text content
        message = self.hide_message_text.get("1.0", tk.END).strip()
        # Update count label
        self.hide_char_count_var.set(f"Characters: {len(message)}")
        # Reset modified flag
        self.hide_message_text.edit_modified(False)
    
    def paste_to_hide_message(self):
        """Paste clipboard content to hide message textbox"""
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                self.hide_message_text.delete("1.0", tk.END)
                self.hide_message_text.insert("1.0", clipboard_text)
                self.update_hide_char_count()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste from clipboard: {str(e)}")
    
    def select_hide_image(self):
        """Select an image for hiding a message"""
        image_path = filedialog.askopenfilename(
            title="Select Carrier Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if image_path:
            self.hide_image_path_var.set(image_path)
            self.update_image_preview(image_path, self.hide_image_preview)
    
    def select_reveal_image(self):
        """Select an image to reveal a hidden message"""
        image_path = filedialog.askopenfilename(
            title="Select Steganographic Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if image_path:
            self.reveal_image_path_var.set(image_path)
            self.update_image_preview(image_path, self.reveal_image_preview)
    
    def update_image_preview(self, image_path, preview_label):
        """Update image preview for the given label"""
        try:
            # Open and resize image for preview
            image = Image.open(image_path)
            image.thumbnail((300, 300))
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update label
            preview_label.configure(image=photo, text="")
            preview_label.image = photo  # Keep a reference
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def hide_message(self):
        """Hide an encrypted message in the selected image"""
        image_path = self.hide_image_path_var.get()
        recipient = self.hide_recipient_var.get()
        message = self.hide_message_text.get("1.0", tk.END).strip()
        
        if not image_path:
            messagebox.showerror("Error", "Please select a carrier image.")
            return
        
        if not recipient:
            messagebox.showerror("Error", "Please select a recipient key.")
            return
        
        if not message:
            messagebox.showerror("Error", "Please enter a message to hide.")
            return
        
        # Ask user where to save the output image
        file_path = filedialog.asksaveasfilename(
            title="Save Steganographic Image",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
            initialdir=self.images_dir,
            initialfile=os.path.basename(image_path).split('.')[0] + "_stego.png"
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Show loading indicator
            self.loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.update()  # Force UI update
            
            # Hide the message
            result_path = self.crypto_stego.hide_encrypted_message(
                image_path,
                message,
                recipient,
                file_path
            )
            
            # Update preview with the stego image
            self.update_image_preview(result_path, self.hide_image_preview)
            
            # Hide loading indicator
            self.loading_label.place_forget()
            
            messagebox.showinfo(
                "Success", 
                f"Message hidden successfully!\nSaved to: {result_path}"
            )
        except Exception as e:
            # Hide loading indicator
            self.loading_label.place_forget()
            messagebox.showerror("Error", f"Failed to hide message: {str(e)}")
    
    def reveal_message(self):
        """Reveal a hidden message from the selected image"""
        image_path = self.reveal_image_path_var.get()
        key_name = self.reveal_key_var.get()
        
        if not image_path:
            messagebox.showerror("Error", "Please select a steganographic image.")
            return
        
        if not key_name:
            messagebox.showerror("Error", "Please select a decryption key.")
            return
        
        try:
            # Show loading indicator
            self.loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.update()  # Force UI update
            
            # Reveal the message
            decrypted_message = self.crypto_stego.retrieve_encrypted_message(
                image_path,
                key_name
            )
            
            # Display the revealed message
            self.revealed_message_text.delete("1.0", tk.END)
            self.revealed_message_text.insert("1.0", decrypted_message.decode('utf-8'))
            
            # Hide loading indicator
            self.loading_label.place_forget()
            
            messagebox.showinfo("Success", "Message revealed successfully!")
        except Exception as e:
            # Hide loading indicator
            self.loading_label.place_forget()
            messagebox.showerror("Error", f"Failed to reveal message: {str(e)}")
    
    def save_revealed_message(self):
        """Save revealed message to a text file"""
        message = self.revealed_message_text.get("1.0", tk.END).strip()
        
        if not message:
            messagebox.showerror("Error", "No message to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Message",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(message)
                messagebox.showinfo("Success", f"Message saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save message: {str(e)}")
    
    def generate_keypair(self):
        """Generate a new quantum-safe keypair"""
        key_name = self.new_key_name_var.get().strip()
        
        if not key_name:
            messagebox.showerror("Error", "Please enter a name for the keypair.")
            return
        
        try:
            # Check if key already exists
            if key_name in self.crypto_stego.key_manager.get_keypair_names():
                answer = messagebox.askyesno(
                    "Key Exists", 
                    f"A key named '{key_name}' already exists. Overwrite it?"
                )
                if not answer:
                    return
            
            # Generate keypair
            self.crypto_stego.key_manager.generate_keypair(key_name)
            
            # Refresh key lists
            self.refresh_keys()
            
            # Clear key name field
            self.new_key_name_var.set("")
            
            messagebox.showinfo("Success", f"Keypair '{key_name}' generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate keypair: {str(e)}")
    
    def import_public_key(self):
        """Import a public key from text"""
        key_name = self.import_key_name_var.get().strip()
        key_text = self.import_key_text.get("1.0", tk.END).strip()
        
        if not key_name:
            messagebox.showerror("Error", "Please enter a name for the key.")
            return
        
        if not key_text:
            messagebox.showerror("Error", "Please enter the public key text.")
            return
        
        try:
            # Check if key already exists
            if key_name in self.crypto_stego.key_manager.get_keypair_names():
                answer = messagebox.askyesno(
                    "Key Exists", 
                    f"A key named '{key_name}' already exists. Overwrite it?"
                )
                if not answer:
                    return
            
            # Import public key
            self.crypto_stego.key_manager.import_public_key(key_name, key_text)
            
            # Refresh key lists
            self.refresh_keys()
            
            # Clear fields
            self.import_key_name_var.set("")
            self.import_key_text.delete("1.0", tk.END)
            
            messagebox.showinfo("Success", f"Public key '{key_name}' imported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import public key: {str(e)}")
    
    def export_public_key(self):
        """Export public key to text"""
        key_name = self.export_key_var.get()
        
        if not key_name:
            messagebox.showerror("Error", "Please select a key to export.")
            return
        
        try:
            # Get public key
            keypair = self.crypto_stego.key_manager.get_keypair(key_name)
            if not keypair or not keypair.get('public_key'):
                raise ValueError(f"Public key not available for '{key_name}'")
                
            public_key = keypair['public_key']
            
            # Display in text box
            self.export_key_text.delete("1.0", tk.END)
            self.export_key_text.insert("1.0", public_key)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export public key: {str(e)}")
    
    def import_key_from_file(self):
        """Import a key from a file"""
        file_path = filedialog.askopenfilename(
            title="Select Key File",
            filetypes=[("Key files", "*.qkey"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            keypair = self.crypto_stego.key_manager.import_public_key_from_file(file_path)
            self.import_file_status_var.set(f"Successfully imported key: {keypair['name']}")
            self.refresh_keys()
        except Exception as e:
            self.import_file_status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to import key: {str(e)}")
    
    def export_key_to_file(self):
        """Export a key to a file"""
        key_name = self.export_file_key_var.get()
        
        if not key_name:
            messagebox.showerror("Error", "Please select a key to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Key File",
            defaultextension=".qkey",
            filetypes=[("Key files", "*.qkey"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            output_path = self.crypto_stego.key_manager.export_public_key_to_file(key_name, file_path)
            self.export_file_status_var.set(f"Key exported to: {output_path}")
        except Exception as e:
            self.export_file_status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to export key: {str(e)}")
    
    def generate_qr_code(self):
        """Generate QR code for selected key"""
        key_name = self.qr_gen_key_var.get()
        
        if not key_name:
            messagebox.showerror("Error", "Please select a key.")
            return
            
        try:
            # Generate QR code
            qr_image = self.crypto_stego.key_manager.generate_key_qr_code(key_name)
            
            # Convert to PhotoImage for display
            photo = ImageTk.PhotoImage(qr_image)
            
            # Store QR image for saving
            self.current_qr_image = qr_image
            
            # Update label
            self.qr_image_label.configure(image=photo, text="")
            self.qr_image_label.image = photo  # Keep a reference
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code: {str(e)}")
    
    def save_qr_code(self):
        """Save the generated QR code as an image"""
        if not hasattr(self, 'current_qr_image') or self.current_qr_image is None:
            messagebox.showerror("Error", "Please generate a QR code first.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save QR Code",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_qr_image.save(file_path)
                messagebox.showinfo("Success", f"QR code saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save QR code: {str(e)}")
    
    def select_qr_image(self):
        """Select a QR code image for key import"""
        image_path = filedialog.askopenfilename(
            title="Select QR Code Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if image_path:
            try:
                # Load the image
                image = Image.open(image_path)
                
                # Display preview
                image_preview = image.copy()
                image_preview.thumbnail((300, 300))
                photo = ImageTk.PhotoImage(image_preview)
                self.qr_scan_preview.configure(image=photo, text="")
                self.qr_scan_preview.image = photo
                
                # Try to read the QR code
                keypair = self.crypto_stego.key_manager.read_key_from_qr_code(image)
                
                self.qr_scan_status_var.set(f"Successfully imported key: {keypair['name']}")
                self.refresh_keys()
                
            except Exception as e:
                self.qr_scan_status_var.set(f"Error: {str(e)}")
                messagebox.showerror("Error", f"Failed to read QR code: {str(e)}")
    
    def delete_selected_key(self):
        """Delete the selected key from the list"""
        key_name = self.key_var.get()
        
        if not key_name:
            messagebox.showerror("Error", "Please select a key to delete.")
            return
        
        answer = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete the key '{key_name}'? This cannot be undone."
        )
        
        if answer:
            try:
                # Delete key
                self.crypto_stego.key_manager.delete_keypair(key_name)
                
                # Refresh key lists
                self.refresh_keys()
                
                messagebox.showinfo("Success", f"Key '{key_name}' deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete key: {str(e)}")
    
    def copy_revealed_message(self):
        """Copy revealed message to clipboard"""
        message = self.revealed_message_text.get("1.0", tk.END).strip()
        
        if message:
            pyperclip.copy(message)
            messagebox.showinfo("Success", "Message copied to clipboard!")
    
    def copy_exported_key(self):
        """Copy exported key to clipboard"""
        key = self.export_key_text.get("1.0", tk.END).strip()
        
        if key:
            pyperclip.copy(key)
            messagebox.showinfo("Success", "Public key copied to clipboard!")