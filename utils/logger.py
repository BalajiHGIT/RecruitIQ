"""Simple application logging setup."""
import logging

def setup_logger():
    logging.basicConfig(
        filename="application.log",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    return logging.getLogger("recruitment_placement")
