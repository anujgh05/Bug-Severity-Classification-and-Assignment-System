import logging
import os
from datetime import datetime

# 1. Create a clean timestamp (e.g., 05_12_2026_11_30_PM)
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%p')}.log"

# 2. Define the directory path ONLY
logs_dir = os.path.join(os.getcwd(), "logs")

# 3. Create the directory if it doesn't exist
os.makedirs(logs_dir, exist_ok=True)

# 4. Join the directory and the filename
LOG_FILE_PATH = os.path.join(logs_dir, LOG_FILE)

logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

