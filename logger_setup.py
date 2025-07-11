import logging

# Create logger object
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Capture all levels (even if file/console filters later)

# Formatter for both console and file
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# === File handler ===
file_handler = logging.FileHandler('all_event.log', mode='a', encoding='utf-8')
file_handler.setLevel(logging.INFO)  # Only INFO and above go to file
file_handler.setFormatter(formatter)

# === Console handler ===
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Print everything to console
console_handler.setFormatter(formatter)

# === Add handlers (avoid duplicates) ===
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
