#!/usr/bin/env python3
"""
HomeNet - Parental Network Controller
Proudly developed in UAE, Al Ain
Author: AbduF
Contact: abdalfaqeeh@gmail.com

A comprehensive parental control application for home networks.
Features: Time-based blocking, traffic monitoring, host management,
          bilingual UI (Arabic/English), and system alerts.
"""

import sys
import os
import logging
from pathlib import Path

# Add app directory to path
APP_DIR = Path(__file__).parent
sys.path.insert(0, str(APP_DIR))

from app import HomeNetApp


def setup_logging():
    """Configure application logging."""
    log_dir = APP_DIR / "logs"
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "homenet.log"),
            logging.StreamHandler()
        ]
    )


def main():
    """Main entry point for HomeNet application."""
    setup_logging()
    logger = logging.getLogger("HomeNet")
    logger.info("Starting HomeNet - Parental Network Controller")
    logger.info(f"Application directory: {APP_DIR}")

    try:
        app = HomeNetApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
