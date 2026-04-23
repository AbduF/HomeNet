"""
HomeNet - Main Application Class
Parental Network Controller with bilingual support
"""

import os
import sys
import customtkinter as ctk
from pathlib import Path
import logging

from core.database import Database
from core.config import Config
from gui.login import LoginWindow
from gui.main_window import MainWindow


class HomeNetApp(ctk.CTk):
    """Main application class for HomeNet."""

    def __init__(self):
        super().__init__()

        # Configuration
        self.app_dir = Path(__file__).parent
        self.config = Config(self.app_dir / "config.json")
        self.db = Database(self.app_dir / "homenet.db")

        # Setup logging
        self.logger = logging.getLogger("HomeNet.App")

        # Window configuration
        self.title("HomeNet - Parental Network Controller")
        self.geometry("1400x900")
        self.minsize(1200, 700)

        # Set theme
        self.setup_theme()

        # Initialize user session
        self.current_user = None

        # Start with login
        self.show_login()

    def setup_theme(self):
        """Configure application theme."""
        # Color scheme
        ctk.set_default_color_theme("blue")
        ctk.set_appearance_mode("dark")

        # Configure colors
        self.colors = {
            'primary': '#1E88E5',
            'secondary': '#43A047',
            'accent': '#FF7043',
            'danger': '#E53935',
            'bg_dark': '#1A1A2E',
            'bg_light': '#16213E',
            'surface': '#0F3460',
            'text_primary': '#FFFFFF',
            'text_secondary': '#B0B0B0'
        }

    def show_login(self):
        """Display login window."""
        self.logger.info("Showing login window")

        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Create login window
        login = LoginWindow(self, self.db, self.config)
        login.pack(fill="both", expand=True)

        # Bind login success
        self.bind("<LoginSuccess>", lambda e: self.on_login_success())

    def on_login_success(self):
        """Handle successful login."""
        self.logger.info("Login successful, showing main window")

        # Clear widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Create main window
        main = MainWindow(self, self.db, self.config)
        main.pack(fill="both", expand=True)


def main():
    """Entry point for HomeNet."""
    app = HomeNetApp()
    app.mainloop()


if __name__ == "__main__":
    main()
