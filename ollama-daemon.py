import subprocess
import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_ollama_serve() -> None:
    try:
        # Set the environmental variable
        os.environ['OLLAMA_HOST'] = '0.0.0.0:11434'

        # Open os.devnull for stdout and stderr to suppress output
        with open(os.devnull, 'w') as devnull:
            # Start 'ollama serve' as a daemon process
            process = subprocess.Popen(
                ['ollama', 'serve'],
                stdout=devnull,
                stderr=devnull,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
            logging.info(f"Started 'ollama serve' with PID: {process.pid}")

    except Exception as e:
        # Handle any specific error or logging here
        logging.error(f"Error while starting 'ollama serve': {e}")

if __name__ == "__main__":
    run_ollama_serve()
