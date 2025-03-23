#!/usr/bin/env python3

import sys
import os
import logging
from pathlib import Path

# Add the parent directory to the path to make qstego importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path('qstego.log')),
        logging.StreamHandler()
    ]
)

def main():
    try:
        from qstego import App
        app = App()
        app.mainloop()
    except Exception as e:
        logging.error(f"Error starting application: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 