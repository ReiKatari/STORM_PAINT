import sys
import os
import json
import math
import ctypes
import re
import requests
from datetime import datetime, timedelta
from fractions import Fraction
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QPushButton, QLabel, QTextEdit, QFrame, QMenu, 
    QSizePolicy, QDialog, QTabWidget, QComboBox, QLineEdit, QListWidget,
    QMessageBox, QFileDialog, QGraphicsOpacityEffect, 
    QAbstractItemView, QStyledItemDelegate, QDateEdit, QCheckBox
)
from PyQt6.QtCore import Qt, QSize, QEvent, QTimer, QPoint, QEasingCurve, QPropertyAnimation, QRect, QDate
from PyQt6.QtGui import (
    QAction, QIcon, QFont, QColor, QPalette, QClipboard, 
    QCursor, QKeySequence, QFontDatabase
)

# --- CONFIG & CONSTANTS ---
CONFIG_FILE = "storm_config_ultimate.json"
CURRENT_VERSION = "2.1.3" 

# --- THEMES ---
THEMES = {
    "Темная (По умолч.)": { "bg": "#121212", "fg": "#e0e0e0", "input_bg": "#252525", "input_fg": "#ffffff", "input_border": "#444", "btn_bg": "#2d2d2d", "btn_fg": "#ffffff", "accent": "#FE9F0A" },
    "Полярная белая": { "bg": "#ffffff", "fg": "#333333", "input_bg": "#f7f7f7", "input_fg": "#000000", "input_border": "#ccc", "btn_bg": "#f0f0f0", "btn_fg": "#000000", "accent": "#FF9500" },
    "Дракула": { "bg": "#282a36", "fg": "#f8f8f2", "input_bg": "#44475a", "input_fg": "#f8f8f2", "input_border": "#6272a4", "btn_bg": "#44475a", "btn_fg": "#f8f8f2", "accent": "#ff79c6" },
    "Солярис Темная": { "bg": "#002b36", "fg": "#839496", "input_bg": "#073642", "input_fg": "#ffffff", "input_border": "#586e75", "btn_bg": "#073642", "btn_fg": "#ffffff", "accent": "#b58900" },
    "Киберпанк": { "bg": "#0b0c15", "fg": "#00ff9f", "input_bg": "#1c1c2e", "input_fg": "#ffffff", "input_border": "#ff003c", "btn_bg": "#1c1c2e", "btn_fg": "#00ff9f", "accent": "#ff003c" },
    "Мятная": { "bg": "#212121", "fg": "#00ffcc", "input_bg": "#333333", "input_fg": "#00ffcc", "input_border": "#009688", "btn_bg": "#333333", "btn_fg": "#00ffcc", "accent": "#009688" },
    "Неон Сити (Ультра)": { 
        "bg": "#050505", "fg": "#00f3ff", "input_bg": "#0a0a0a", "input_fg": "#ff0099", 
        "input_border": "#00f3ff", "btn_bg": "#111111", "btn_fg": "#00f3ff", "accent": "#ff0099"
    },
    "Радиоактивная (Ультра)": { 
        "bg": "#0a0f00", "fg": "#ccff00", "input_bg": "#141f00", "input_fg": "#ffffff", 
        "input_border": "#66ff00", "btn_bg": "#1f3300", "btn_fg": "#ccff00", "accent": "#66ff00"
    },
    "Вейпорвейв 80 (Ультра)": { 
        "bg": "#240046", "fg": "#ff9e00", "input_bg": "#3c096c", "input_fg": "#ff9e00", 
        "input_border": "#9d4edd", "btn_bg": "#5a189a", "btn_fg": "#e0aaff", "accent": "#9d4edd"
    },
    "Обсидиан (Ультра)": { 
        "bg": "#000000", "fg": "#e0e0e0", "input_bg": "#1a1a1a", "input_fg": "#ffffff", 
        "input_border": "#333333", "btn_bg": "#1a1a1a", "btn_fg": "#ffffff", "accent": "#ffffff"
    },
    "Глубокий космос (Ультра)": { 
        "bg": "#020c1b", "fg": "#64ffda", "input_bg": "#112240", "input_fg": "#e6f1ff", 
        "input_border": "#233554", "btn_bg": "#0a192f", "btn_fg": "#64ffda", "accent": "#64ffda"
    },
    "Черная (Консоль)": {
        "bg": "#000000", "fg": "#00FF41", "input_bg": "#000000", "input_fg": "#00FF41", 
        "input_border": "#005515", "btn_bg": "#111111", "btn_fg": "#E0E0E0", "accent": "#333333"
    },
    "Матрица": {
        "bg": "#000000", "fg": "#00FF00", "input_bg": "#0D0D0D", "input_fg": "#00FF00", 
        "input_border": "#003300", "btn_bg": "#001100", "btn_fg": "#00FF00", "accent": "#00FF00"
    },
    "Океан": {
        "bg": "#E0F7FA", "fg": "#006064", "input_bg": "#B2EBF2", "input_fg": "#006064", 
        "input_border": "#0097A7", "btn_bg": "#80DEEA", "btn_fg": "#006064", "accent": "#00BCD4"
    },
    "Закат": {
        "bg": "#2D1B2E", "fg": "#FFD700", "input_bg": "#4A2C4C", "input_fg": "#FFD700", 
        "input_border": "#B565A7", "btn_bg": "#6A4C93", "btn_fg": "#FFD700", "accent": "#F77F00"
    },
    "Лес": {
        "bg": "#1B261D", "fg": "#A8D5BA", "input_bg": "#2D3E30", "input_fg": "#A8D5BA", 
        "input_border": "#4E7356", "btn_bg": "#384D3D", "btn_fg": "#A8D5BA", "accent": "#6DA378"
    }
}

APP_FONT = "Century Gothic"

def format_number(val):
    if not val: return "0"
    try:
        f = float(val)
        if f.is_integer():
            return "{:,.0f}".format(int(f))
        else:
            return "{:,.8f}".format(f).rstrip('0').rstrip('.')
    except:
        return val

class StormCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"STORM CALCULATOR v{CURRENT_VERSION}")
        
        # Set Window Icon for Taskbar
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stormcalculator.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Windows: Set AppUserModelID for taskbar grouping
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Storm.Calculator.App")
        except: pass
        
        # State
        self.current_theme = "Темная (По умолч.)"
        self.current_mode = "Обычный"
        self.expression = ""
        self.history = []
        self.memory_val = 0
        self.result_shown = False
        self.opacity_val = 1.0
        self.is_pinned = False
        self.is_mini = False
        self.auto_update = True # Default
        self.saved_geometry = None
        
        # Load Config
        self.load_config()
        
        # UI Setup
        self.init_ui()
        self.apply_theme()
        
        # Events
        self.setAcceptDrops(True)
        
        # Initial Resize
        self.set_mode(self.current_mode)
        
        # Auto-Update Check
        if self.auto_update:
            QTimer.singleShot(2000, self.check_for_updates)

    def check_for_updates(self):
        try:
            url = "https://api.github.com/repos/ReiKatari/STORM_CALCULATOR/releases/latest"
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                data = r.json()
                tag = data.get("tag_name", "").strip().lstrip("v")
                
                # Simple version compare
                if tag != CURRENT_VERSION:
                    # Found update
                    reply = QMessageBox.question(
                        self, "Доступно обновление", 
                        f"Текущая версия: {CURRENT_VERSION}\nНовая версия: {tag}\n\nХотите обновить сейчас?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        self.download_and_install_update(data)
        except: 
            pass # Silent fail on auto-check

    def download_and_install_update(self, release_data):
        try:
            # Find asset (prefer .exe if running frozen, or .py if script)
            assets = release_data.get("assets", [])
            download_url = None
            target_name = "update_temp.exe" # Default temp name
            
            is_script = sys.argv[0].endswith(".py")
            current_file = os.path.abspath(sys.argv[0])
            
            # Simple logic: pick the first asset that matches 'exe' if we are exe, or 'py' if py
            # Or just grab the first asset if user didn't specify strict rules
            if not assets:
                QMessageBox.warning(self, "Ошибка", "В релизе нет файлов для скачивания.")
                return

            # Try to find specific matching asset
            for asset in assets:
                name = asset["name"].lower()
                if is_script and name.endswith(".py"):
                    download_url = asset["browser_download_url"]
                    target_name = "update_temp.py"
                    break
                elif not is_script and name.endswith(".exe"):
                    download_url = asset["browser_download_url"]
                    target_name = "update_temp.exe"
                    break
            
            # Fallback: just take the first one
            if not download_url:
                download_url = assets[0]["browser_download_url"]
                target_name = assets[0]["name"]

            # Download
            r = requests.get(download_url, stream=True)
            if r.status_code == 200:
                with open(target_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Create Batch Updater
                bat_script = f"""@echo off
timeout /t 2 /nobreak > NUL
move /y "{target_name}" "{current_file}"
start "" "{current_file}"
del "%~f0"
"""
                with open("updater.bat", "w") as b:
                    b.write(bat_script)
                    
                # Launch bat and exit
                os.startfile("updater.bat")
                sys.exit(0)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось скачать обновление.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка обновления", str(e))

    def init_ui(self):
        self.setWindowTitle(f"STORM CALCULATOR v{CURRENT_VERSION}")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main Layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        
        # --- Top Bar ---
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon
        icon_lbl = QLabel()
        # Assuming icon_path is defined elsewhere or not needed for this change
        # For now, let's just make it an empty pixmap or remove if not critical
        icon_lbl.setPixmap(QIcon().pixmap(20, 20)) # Placeholder for icon
        top_layout.addWidget(icon_lbl)
        
        # Title (Smaller)
        title = QLabel(f"STORM CALCULATOR v{CURRENT_VERSION}")
        title.setFont(QFont(APP_FONT, 9, QFont.Weight.Bold))
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        # Controls (No maximize button)
        min_btn = self.create_top_btn("─", self.showMinimized, QFont(APP_FONT, 9))
        close_btn = self.create_top_btn("✕", self.close, QFont(APP_FONT, 9))
        close_btn.setStyleSheet("QPushButton:hover { background-color: #ff5f56; color: white; }")
        
        top_layout.addWidget(min_btn)
        top_layout.addWidget(close_btn)
        
        self.layout.addWidget(top_bar)
        
        # Window Drag
        # Assuming moveWindow and mousePressEvent methods exist for custom title bar drag
        top_bar.mouseMoveEvent = self.moveWindow # Placeholder
        top_bar.mousePressEvent = self.mousePressEvent # Placeholder
        
        # --- Toolbar (Settings & Tools) ---
        tools_row = QHBoxLayout()
        
        # Pin
        self.pin_btn = self.create_top_btn("📌", self.toggle_pin, QFont(APP_FONT, 9))
        self.pin_btn.setCheckable(True)
        tools_row.addWidget(self.pin_btn)
        
        # Mode (Expanding to fill space)
        self.mode_selector = QPushButton("Обычный")
        self.mode_selector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.mode_selector.setMenu(self.create_mode_menu())
        tools_row.addWidget(self.mode_selector)
        
        # No stretch - mode selector fills the gap

        # Settings Button
        self.settings_btn = self.create_top_btn("⚙", self.show_settings, QFont(APP_FONT, 10))
        tools_row.addWidget(self.settings_btn)

        # Tools Button
        tools_btn = self.create_top_btn("📋", self.show_tools_dialog, QFont(APP_FONT, 10))
        tools_row.addWidget(tools_btn)
        
        self.layout.addLayout(tools_row)
        
        # --- Display ---
        self.formula_lbl = QLabel("")
        self.formula_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.formula_lbl.setStyleSheet("color: #888; font-size: 10pt;")
        self.layout.addWidget(self.formula_lbl)
        
        self.display = QLineEdit("0")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        self.display.setStyleSheet("background: transparent; border: none; font-size: 28pt; font-weight: bold;")
        self.layout.addWidget(self.display)
        
        # --- Keypad ---
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)
        self.layout.addLayout(self.grid_layout)
        
        self.current_mode = "Обычный"
        self.setup_keypad("Обычный")
        
        # Enable keyboard input focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        
        # Initial Resize for Consistency
        self.set_mode(self.current_mode) # Call set_mode to apply initial size and keypad

    def create_top_btn(self, text, slot, font):
        btn = QPushButton(text)
        btn.setFont(font)
        btn.setFixedSize(26, 26)
        btn.clicked.connect(slot)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return btn

    def create_mode_menu(self):
        menu = QMenu(self)
        for m in ["Обычный", "Инженерный", "Программист", "Финансовый", "Конвертер"]:
            action = QAction(m, self)
            action.triggered.connect(lambda checked, mode=m: self.set_mode(mode))
            menu.addAction(action)
        return menu

    def set_mode(self, mode):
        if self.current_mode == mode:
            return
        self.current_mode = mode
        self.mode_selector.setText(mode)
        self.setup_keypad(mode)
        self.apply_theme()
        
        # Resize Logic for Consistent Buttons
        if mode == "Обычный":
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            self.resize(400, 600)
            self.setFixedSize(400, 600)
            QTimer.singleShot(100, lambda: self.setMinimumSize(400, 600))
            QTimer.singleShot(100, lambda: self.setMaximumSize(16777215, 16777215))
        elif mode == "Конвертер":
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            self.resize(420, 580)
            self.setFixedSize(420, 580)
            QTimer.singleShot(100, lambda: self.setMinimumSize(420, 580))
            QTimer.singleShot(100, lambda: self.setMaximumSize(16777215, 16777215))
        else:  # Инженерный, Программист, Финансовый
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            self.resize(500, 700)
            self.setFixedSize(500, 700)
            QTimer.singleShot(100, lambda: self.setMinimumSize(500, 700))
            QTimer.singleShot(100, lambda: self.setMaximumSize(16777215, 16777215))

    def setup_keypad(self, mode):
        # Clear existing items
        for i in reversed(range(self.grid_layout.count())): 
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)
            
        # RESET STRETCHES - Critical for switching modes
        for r in range(self.grid_layout.rowCount()): self.grid_layout.setRowStretch(r, 0)
        for c in range(self.grid_layout.columnCount()): self.grid_layout.setColumnStretch(c, 0)

        if mode == "Инженерный":
            layout = [
                ['MC', 'MR', 'M+', 'M-', 'C'],
                ['sin', 'cos', 'tan', '(', ')'],
                ['x²', '√', 'log', 'Mod', '÷'],
                ['7', '8', '9', '×', '^'],
                ['4', '5', '6', '-', 'π'],
                ['1', '2', '3', '+', 'e'],
                ['+/-', '0', '.', '=', 'x!']
            ]
        elif mode == "Программист":
            layout = [
                ['HEX', 'DEC', 'OCT', 'BIN', 'C'],
                ['A', 'B', '<<', '>>', '÷'],
                ['C', 'D', 'AND', 'OR', '×'],
                ['E', 'F', 'XOR', 'NOT', '-'],
                ['7', '8', '9', '(', '+'],
                ['4', '5', '6', ')', 'Mod'],
                ['1', '2', '3', '0', '=']
            ]
        elif mode == "Финансовый":
            # Financial calculator: PMT, PV, FV, Rate, Nper
            layout = [
                ['PMT', 'PV', 'FV', 'Rate', 'C'],
                ['Nper', '%', '±', '(', ')'],
                ['7', '8', '9', '÷', 'Tax+'],
                ['4', '5', '6', '×', 'Tax-'],
                ['1', '2', '3', '-', 'Margin'],
                ['+/-', '0', '.', '+', '=']
            ]
        elif mode == "Конвертер":
            # Unit converter mode
            layout = [
                ['km↔mi', 'm↔ft', 'cm↔in', 'C'],
                ['kg↔lb', 'g↔oz', 'L↔gal', '←'],
                ['7', '8', '9', '°C↔°F'],
                ['4', '5', '6', 'ha↔ac'],
                ['1', '2', '3', 'm²↔ft²'],
                ['+/-', '0', '.', '=']
            ]
        else: # Обычный
            layout = [
                ['MC', 'MR', 'M+', 'M-'],
                ['C', '←', '%', '÷'],
                ['7', '8', '9', '×'],
                ['4', '5', '6', '-'],
                ['1', '2', '3', '+'],
                ['+/-', '0', '.', '=']
            ]
        
        for r, row_keys in enumerate(layout):
            self.grid_layout.setRowStretch(r, 1)
            for c, key in enumerate(row_keys):
                self.grid_layout.setColumnStretch(c, 1)
                btn = QPushButton(key)
                
                # FIX: Force buttons to fill space and not shrink too much
                btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                btn.setMinimumSize(50, 50) 
                
                btn.setFont(QFont(APP_FONT, 14, QFont.Weight.Bold))
                btn.clicked.connect(lambda _, k=key: self.on_btn_click(k))
                btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                self.grid_layout.addWidget(btn, r, c)
                
                # Apply special styles
                if key == '=': btn.setProperty("class", "accent")
                elif key in ['C', 'MC', 'MR', 'M+', 'M-']: btn.setProperty("class", "danger")
                elif key in ['÷', '×', '-', '+']: btn.setProperty("class", "operator")
                else: btn.setProperty("class", "digit")

    def apply_theme(self):
        t = THEMES.get(self.current_theme, THEMES["Темная (По умолч.)"])
        if self.current_theme not in THEMES:
            self.current_theme = "Темная (По умолч.)"
            # self.theme_combo.setCurrentText(self.current_theme) # Removed combo
        
        qss = f"""
            * {{ font-family: "{APP_FONT}"; }}
            QMainWindow {{ background-color: {t['bg']}; }}
            QWidget {{ background-color: {t['bg']}; color: {t['fg']}; }}
            QLabel {{ color: {t['fg']}; border: none; }}
            QDialog {{ background-color: {t['bg']}; }}
            
            /* Modern Button Style from STORM SENDER */
            QPushButton {{
                background-color: {t['btn_bg']};
                color: {t['btn_fg']};
                border: 1px solid {t['input_border']};
                border-radius: 4px; /* Slightly sharper radius like sender */
                padding: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {t['input_bg']};
                border-color: {t['accent']};
            }}
            QPushButton:pressed {{
                background-color: {t['accent']};
                color: {t['bg']};
            }}
            
            /* Accent Buttons */
            QPushButton[class="accent"] {{
                background-color: {t['accent']};
                color: #ffffff;
                border: 1px solid {t['accent']};
            }}
            QPushButton[class="accent"]:hover {{
                background-color: {t['input_fg']}; /* Lighter on hover */
                color: {t['bg']};
            }}
            
            /* Special Keys */
            QPushButton[class="danger"], QPushButton[class="operator"] {{
                color: {t['accent']};
                font-size: 16pt;
                background-color: {t['btn_bg']};
            }}
            QPushButton[class="danger"]:hover, QPushButton[class="operator"]:hover {{
                background-color: {t['input_bg']};
            }}
            
            /* Inputs & Lists */
            QLineEdit, QListWidget {{
                background-color: {t['input_bg']};
                color: {t['input_fg']};
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 6px;
                font-size: 11pt;
            }}
            
            /* Combo Box - Centered */
            QComboBox {{
                background-color: {t['btn_bg']};
                color: {t['btn_fg']};
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 4px 10px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 0px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {t['input_bg']};
                color: {t['input_fg']};
                selection-background-color: {t['accent']};
                selection-color: white;
                outline: 0px;
                padding: 4px;
            }}
            
            /* Tabs */
            QTabWidget::pane {{ border: 0px; margin-top: 5px; }}
            QTabBar::tab {{ 
                background: {t['btn_bg']}; 
                color: {t['fg']}; 
                padding: 8px 16px; 
                border: 1px solid {t['input_border']};
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{ 
                background: {t['accent']}; 
                color: white; 
                border-color: {t['accent']};
            }}
        """
        self.setStyleSheet(qss)
        self.set_title_bar_color_dark(t.get("bg", "#000") not in ["#ffffff", "#f0f2f5", "#fdf6e3"])

    def set_title_bar_color_dark(self, is_dark):
        try:
            hwnd = self.winId().__int__()
            value = 1 if is_dark else 0
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(value)), 4)
        except: pass

    # --- Actions & Logic ---
    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()
        
        # Arrow keys for mode switching
        modes = ["Обычный", "Инженерный", "Программист", "Финансовый", "Конвертер"]
        if key == Qt.Key.Key_Left:
            idx = modes.index(self.current_mode) if self.current_mode in modes else 0
            self.set_mode(modes[(idx - 1) % len(modes)])
            return
        elif key == Qt.Key.Key_Right:
            idx = modes.index(self.current_mode) if self.current_mode in modes else 0
            self.set_mode(modes[(idx + 1) % len(modes)])
            return
        
        # Number keys
        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9: self.on_btn_click(text)
        elif text == ".": self.on_btn_click(".")
        elif text in "+-*/": 
            mapping = {'*': '×', '/': '÷', '-': '-'}
            self.on_btn_click(mapping.get(text, text))
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter: self.on_btn_click("=")
        elif key == Qt.Key.Key_Backspace: self.on_btn_click("←")
        elif key == Qt.Key.Key_Escape: self.on_btn_click("C")
        elif key == Qt.Key.Key_Delete: self.on_btn_click("C")
        
        if event.matches(QKeySequence.StandardKey.Copy):
            QApplication.clipboard().setText(self.expression if self.expression else "0")
        elif event.matches(QKeySequence.StandardKey.Paste):
            txt = QApplication.clipboard().text()
            if re.match(r'^[0-9+\-*/.()]+$', txt):
                self.expression = txt
                self.update_display()

    def on_btn_click(self, key):
        if key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            if self.result_shown:
                self.expression = str(key)
                self.result_shown = False
            else:
                self.expression += str(key)
        elif key == '.':
            if self.result_shown:
                self.expression = "0."
                self.result_shown = False
            elif "." not in self.expression.split(' ')[-1]: 
                 self.expression += "."
        elif key in ['+', '-', '×', '÷', '^', 'Mod']:
            self.result_shown = False
            self.expression += f" {key} "
        elif key == 'C':
            self.expression = ""
            self.result_shown = False
            self.update_display()
            return
        elif key == '←':
            self.expression = self.expression[:-1]
        elif key == '=':
            self.calculate()
        elif key == "HEX": self.convert_base(16)
        elif key == "DEC": self.convert_base(10)
        elif key == "OCT": self.convert_base(8)
        elif key == "BIN": self.convert_base(2)
        elif key == 'π': self.expression += str(math.pi)
        elif key == 'e': self.expression += str(math.e)
        elif key == 'x²': self.expression += "**2"
        elif key == '√': self.expression = f"math.sqrt({self.expression})"
        elif key == '+/-':
            try:
                val = float(self.expression) if self.expression else 0
                self.expression = str(-val)
            except: pass
        
        # --- Unit Conversions ---
        elif key == 'km↔mi': self.convert_unit(1.60934, "km", "mi")
        elif key == 'm↔ft': self.convert_unit(0.3048, "m", "ft")
        elif key == 'cm↔in': self.convert_unit(2.54, "cm", "in")
        elif key == 'kg↔lb': self.convert_unit(0.453592, "kg", "lb")
        elif key == 'g↔oz': self.convert_unit(28.3495, "g", "oz")
        elif key == 'L↔gal': self.convert_unit(3.78541, "L", "gal")
        elif key == '°C↔°F': self.convert_temp()
        elif key == 'ha↔ac': self.convert_unit(0.404686, "ha", "ac")
        elif key == 'm²↔ft²': self.convert_unit(0.092903, "m²", "ft²")
        
        # --- Financial ---
        elif key == 'Tax+':
            try:
                val = float(self.expression) if self.expression else 0
                self.expression = str(round(val * 1.12, 2))  # +12% tax
                self.formula_lbl.setText(f"{val} + 12% =")
            except: pass
        elif key == 'Tax-':
            try:
                val = float(self.expression) if self.expression else 0
                self.expression = str(round(val / 1.12, 2))  # Remove 12% tax
                self.formula_lbl.setText(f"{val} / 1.12 =")
            except: pass
        elif key == 'Margin':
            try:
                val = float(self.expression) if self.expression else 0
                # Assume 20% margin calculation
                self.expression = str(round(val * 1.20, 2))
                self.formula_lbl.setText(f"{val} + 20% margin =")
            except: pass
        elif key == '%':
            try:
                val = float(self.expression) if self.expression else 0
                self.expression = str(round(val / 100, 6))
            except: pass
        elif key == '±':
            try:
                val = float(self.expression) if self.expression else 0
                self.expression = str(-val)
            except: pass
        
        # Trig and Eng functions
        elif key == 'sin':
            try:
                val = float(self.expression) if self.expression else 0
                self.expression = str(round(math.sin(math.radians(val)), 8))
            except: pass
        elif key == 'cos':
            try:
                val = float(self.expression) if self.expression else 0
                self.expression = str(round(math.cos(math.radians(val)), 8))
            except: pass
        elif key == 'tan':
            try:
                val = float(self.expression) if self.expression else 0
                self.expression = str(round(math.tan(math.radians(val)), 8))
            except: pass
        elif key == 'log':
            try:
                val = float(self.expression) if self.expression else 0
                self.expression = str(round(math.log10(val), 8))
            except: pass
        elif key == 'x!':
            try:
                val = int(float(self.expression)) if self.expression else 0
                self.expression = str(math.factorial(val))
            except: pass
        
        # Memory
        elif key == 'MC': self.memory_val = 0
        elif key == 'MR': self.expression = str(self.memory_val)
        elif key == 'M+':
            try: self.memory_val += float(self.expression) if self.expression else 0
            except: pass
        elif key == 'M-':
            try: self.memory_val -= float(self.expression) if self.expression else 0
            except: pass
        
        self.update_display()

    def convert_unit(self, factor, unit1, unit2):
        """Toggle conversion between two units using a factor."""
        try:
            val = float(self.expression) if self.expression else 0
            # Simple toggle: if formula contains unit1, convert to unit2, else reverse
            if unit1 in self.formula_lbl.text():
                result = val / factor
                self.formula_lbl.setText(f"{val} {unit2} → {unit1}")
            else:
                result = val * factor
                self.formula_lbl.setText(f"{val} {unit1} → {unit2}")
            self.expression = str(round(result, 4))
            self.result_shown = True
        except: pass

    def convert_temp(self):
        """Toggle between Celsius and Fahrenheit."""
        try:
            val = float(self.expression) if self.expression else 0
            if "°F" in self.formula_lbl.text():
                result = (val - 32) * 5/9
                self.formula_lbl.setText(f"{val}°F → °C")
            else:
                result = val * 9/5 + 32
                self.formula_lbl.setText(f"{val}°C → °F")
            self.expression = str(round(result, 2))
            self.result_shown = True
        except: pass

    def update_display(self):
        disp_txt = self.expression if self.expression else "0"
        try:
            parts = re.split(r'([+\-×÷^Mod\(\)])', disp_txt)
            formatted_parts = []
            for p in parts:
                if p.strip() and p.strip() not in "+-×÷^Mod()":
                    formatted_parts.append(format_number(p))
                else:
                    formatted_parts.append(p)
            self.display.setText("".join(formatted_parts))
        except:
             self.display.setText(disp_txt)

    def calculate(self):
        try:
            raw_expr = self.expression.replace("×", "*").replace("÷", "/").replace("^", "**").replace("Mod", "%")
            res = eval(raw_expr)
            
            if isinstance(res, float) and res.is_integer():
                res = int(res)
            else:
                res = round(res, 8)
            
            self.history.append(f"{self.expression} = {res}")
            
            self.formula_lbl.setText(f"{self.expression} =")
            
            self.expression = str(res)
            self.display.setText(format_number(str(res)))
            self.result_shown = True
        except:
            self.display.setText("Ошибка")
            self.expression = ""

    def convert_base(self, base):
        try:
            val = int(float(self.expression))
            if base == 16: res = hex(val).upper().replace("0X", "")
            elif base == 8: res = oct(val).replace("0o", "")
            elif base == 2: res = bin(val).replace("0b", "")
            else: res = str(val)
            self.display.setText(res)
            self.expression = str(val)
            self.result_shown = True
        except: pass

    def cycle_mode(self):
        modes = ["Обычный", "Инженерный", "Программист"]
        idx = modes.index(self.current_mode)
        self.current_mode = modes[(idx + 1) % len(modes)]
        self.mode_selector.setText(self.current_mode)
        self.setup_keypad(self.current_mode)
        
        # FIX: Reset minimum size        # FIX: Force strict resize by setting FixedSize momentarily
        if self.current_mode == "Обычный":
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            # Increased size to make buttons match Engineering (approx 100x100)
            self.resize(400, 650) 
            self.setFixedSize(400, 650)
            QTimer.singleShot(100, lambda: self.setMinimumSize(400, 650))
            QTimer.singleShot(100, lambda: self.setMaximumSize(16777215, 16777215))
        else:
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            self.resize(500, 700)
            self.setFixedSize(500, 700)
            QTimer.singleShot(100, lambda: self.setMinimumSize(500, 700))
            QTimer.singleShot(100, lambda: self.setMaximumSize(16777215, 16777215))
        self.show()

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def moveWindow(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.isMaximized():
                 self.showNormal()
            if hasattr(self, 'drag_pos'):
                self.move(event.globalPosition().toPoint() - self.drag_pos)
                event.accept()

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.is_pinned)
        self.pin_btn.setText("📍" if self.is_pinned else "📌")
        self.show()
        self.save_config()

    def change_opacity_list(self, index):
        val = 1.0 - (index * 0.1)
        self.setWindowOpacity(val)

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.apply_theme()

    def toggle_mini_mode(self):
        if not self.is_mini:
            self.saved_geometry = self.geometry()
            self.setMinimumSize(0, 0)
            self.grid_frame.hide()
            self.mode_selector.hide()
            self.btn_history.hide()
            self.btn_tools.hide()
            # self.theme_combo.hide() # Keep settings? No, hide everything for mini
            self.settings_bar.setParent(None) # Temporarily remove layout items? Easier to just hide widgets
            
            # Re-implementation for hiding rows
            self.clear_layout(self.settings_bar)
            self.clear_layout(self.controls_bar)
            
            # Minimal header
            self.btn_mini.setParent(self.central_widget)
            self.btn_mini.move(5, 5)
            self.btn_mini.show()
            self.btn_mini.setText("🔼")
            
            self.formula_lbl.hide()
            self.display.setFixedHeight(50)
            self.display.setFont(QFont(APP_FONT, 20))
            self.resize(250, 80)
            self.is_mini = True
        else:
            # Restore... this is getting complex with layout rebuilding. 
            # Easier approach: Hide the widgets inside the layouts, not destroyed.
            # But the user asked for logic fix. 
            # Let's restart the app (simulate) or just rebuild UI?
            # Rebuilding UI is safer.
            self.is_mini = False
            self.init_ui() # Full rebuild
            self.apply_theme()
            self.cycle_mode() # Trigger resize
            if self.saved_geometry: self.setGeometry(self.saved_geometry)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.hide()
                else:
                    self.clear_layout(item.layout())

    def show_settings(self):
        d = QDialog(self)
        d.setWindowTitle("Настройки")
        d.setFixedWidth(320)
        d.setStyleSheet(self.styleSheet())
        
        layout = QVBoxLayout(d)
        
        # Theme
        layout.addWidget(QLabel("Тема:"))
        t_combo = QComboBox()
        t_combo.addItems(list(THEMES.keys()))
        t_combo.setCurrentText(self.current_theme)
        def on_theme(t):
            self.current_theme = t
            self.apply_theme()
            d.setStyleSheet(self.styleSheet())
            self.save_config()
        t_combo.currentTextChanged.connect(on_theme)
        layout.addWidget(t_combo)
        
        # Opacity
        layout.addWidget(QLabel("Прозрачность:"))
        o_combo = QComboBox()
        o_combo.addItems(["100%", "95%", "90%", "85%", "80%", "75%", "50%"])
        current_op_str = f"{int(self.windowOpacity() * 100)}%"
        o_combo.setCurrentText(current_op_str)
        def on_opacity(t):
            op = float(t.strip('%')) / 100.0
            self.setWindowOpacity(op)
            self.opacity_val = op
            self.save_config()
        o_combo.currentTextChanged.connect(on_opacity)
        layout.addWidget(o_combo)
        
        # Auto Update Checkbox
        layout.addWidget(QLabel("Обновления:"))
        chk = QCheckBox("Авто-обновление")
        chk.setChecked(self.auto_update)
        chk_style = """
            QCheckBox::indicator { width: 18px; height: 18px; border-radius: 3px; border: 1px solid #555; background: #333; }
            QCheckBox::indicator:checked { background-color: #28a745; border-color: #28a745; }
            QCheckBox { spacing: 8px; }
        """
        chk.setStyleSheet(chk_style)
        def on_auto_update(state):
            self.auto_update = (state == 2)
            self.save_config()
        chk.stateChanged.connect(on_auto_update)
        layout.addWidget(chk)
        
        layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(d.accept)
        layout.addWidget(ok_btn)
        
        d.exec()

    def show_history_dialog(self):
        d = QDialog(self)
        d.setWindowTitle("История")
        d.resize(400, 500)
        layout = QVBoxLayout(d)
        lst = QListWidget()
        lst.setFont(QFont(APP_FONT, 12))
        lst.addItems(reversed(self.history))
        layout.addWidget(lst)
        btn_export = QPushButton("💾 Сохранить в TXT")
        def export_history():
            path, _ = QFileDialog.getSaveFileName(d, "Сохранить историю", "history.txt", "Text Files (*.txt)")
            if path:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write("\n".join(self.history))
                    QMessageBox.information(d, "Успех", "История сохранена!")
                except: pass
        btn_export.clicked.connect(export_history)
        layout.addWidget(btn_export)
        d.exec()

    def show_tools_dialog(self):
        d = QDialog(self)
        d.setWindowTitle(f"STORM INSTRUMENTS v{CURRENT_VERSION}")
        d.resize(750, 550)
        
        # Compact Font for Tools
        tool_font = QFont(APP_FONT, 9)
        d.setFont(tool_font)
        
        # Force styles for tools
        d.setStyleSheet(f"""
            QWidget {{ font-size: 9pt; font-family: "{APP_FONT}"; }}
            QLabel {{ font-size: 9pt; }}
            QLineEdit, QDateEdit {{ font-size: 9pt; padding: 4px; }}
            QPushButton {{ font-size: 9pt; padding: 4px; }}
            QComboBox {{ font-size: 9pt; }}
            QLabel.header {{ font-weight: bold; color: {THEMES[self.current_theme]['accent']}; margin-top: 10px; }}
        """)
        
        layout = QVBoxLayout(d)
        
        anim = QPropertyAnimation(d, b"windowOpacity")
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.start()
        
        tabs = QTabWidget()
        
        def create_tab(title):
            w = QWidget()
            l = QVBoxLayout(w)
            l.setAlignment(Qt.AlignmentFlag.AlignTop)
            tabs.addTab(w, title)
            return l

        # 1. BMI
        bl = create_tab("ИМТ")
        bl.addWidget(QLabel("Вес (кг):")); w_in = QLineEdit(); bl.addWidget(w_in)
        bl.addWidget(QLabel("Рост (см):")); h_in = QLineEdit(); bl.addWidget(h_in)
        res_bmi = QLabel("Результат: -"); res_bmi.setStyleSheet("color:#FE9F0A;font-weight:bold;font-size:11pt;"); bl.addWidget(res_bmi)
        def calc_bmi():
            try:
                w = float(w_in.text())
                h = float(h_in.text())/100
                res_bmi.setText(f"ИМТ: {w/(h*h):.2f}")
            except: pass
        bb = QPushButton("Рассчитать"); bb.clicked.connect(calc_bmi); bl.addWidget(bb)

        # 2. Discount
        dl = create_tab("Скидка")
        dl.addWidget(QLabel("Цена:")); p_in = QLineEdit(); dl.addWidget(p_in)
        dl.addWidget(QLabel("Скидка (%):")); d_in = QLineEdit(); dl.addWidget(d_in)
        res_disc = QLabel("Результат: -"); res_disc.setStyleSheet("color:#FE9F0A;font-weight:bold;font-size:11pt;"); dl.addWidget(res_disc)
        def calc_disc():
            try:
                p=float(p_in.text());off=float(d_in.text()); v=p*(1-off/100)
                res_disc.setText(f"Итого: {v:,.2f} (Экон.: {p-v:,.2f})")
            except: pass
        db = QPushButton("Рассчитать"); db.clicked.connect(calc_disc); dl.addWidget(db)

        # 3. Loan
        ll = create_tab("Кредит")
        ll.addWidget(QLabel("Сумма:")); l_amt=QLineEdit(); ll.addWidget(l_amt)
        ll.addWidget(QLabel("Ставка (%):")); l_rate=QLineEdit(); ll.addWidget(l_rate)
        ll.addWidget(QLabel("Месяцев:")); l_m=QLineEdit(); ll.addWidget(l_m)
        res_loan = QLabel("Результат: -"); res_loan.setStyleSheet("color:#FE9F0A;font-weight:bold;font-size:11pt;"); ll.addWidget(res_loan)
        def calc_loan():
            try:
                P=float(l_amt.text()); r=float(l_rate.text())/1200; n=float(l_m.text())
                if r==0: m=P/n
                else: m=P*r*((1+r)**n)/(((1+r)**n)-1)
                res_loan.setText(f"Платеж: {m:,.2f}")
            except: pass
        lb = QPushButton("Рассчитать"); lb.clicked.connect(calc_loan); ll.addWidget(lb)

        # 4. Currency (Live/History)
        cl = create_tab("Валюта")
        
        c_row1 = QHBoxLayout()
        c_row1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_row1.addWidget(QLabel("Сумма:")); c_in=QLineEdit("1"); c_row1.addWidget(c_in)
        cl.addLayout(c_row1)
        
        c_row2 = QHBoxLayout()
        c_row2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Removed KZT/RUB from supported API list visually or handle them manually
        c_from = QComboBox(); c_from.setEditable(True); c_from.lineEdit().setReadOnly(True); c_from.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_from.addItems(["USD", "EUR", "GBP", "JPY", "CNY", "RUB", "KZT"])
        c_row2.addWidget(QLabel("Из:")); c_row2.addWidget(c_from)
        
        c_to = QComboBox(); c_to.setEditable(True); c_to.lineEdit().setReadOnly(True); c_to.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_to.addItems(["EUR", "USD", "GBP", "JPY", "CNY", "RUB", "KZT"])
        c_row2.addWidget(QLabel("В:")); c_row2.addWidget(c_to)
        cl.addLayout(c_row2)
        
        cl.addWidget(QLabel("Дата курса:")); c_date = QDateEdit(); c_date.setDate(QDate.currentDate()); c_date.setCalendarPopup(True); cl.addWidget(c_date)
        c_res = QLabel("Результат: -"); c_res.setStyleSheet("color:#FE9F0A;font-weight:bold;font-size:11pt;"); cl.addWidget(c_res)
        
        def calc_curr():
            try:
                amt=float(c_in.text())
                cur_from = c_from.currentText()
                cur_to = c_to.currentText()
                dt_obj = c_date.date().toPyDate()
                today = datetime.now().date()
                
                # Use 'latest' if today, else YYYY-MM-DD
                dt_str = "latest" if dt_obj >= today else dt_obj.strftime("%Y-%m-%d")
                dt_disp = "Сегодня" if dt_obj >= today else dt_obj.strftime("%d.%m.%Y")
                
                # Default rates fallback (Approximate)
                static_rates = {
                    "USD": 1.0, "EUR": 0.92, "GBP": 0.79, "JPY": 148.0, 
                    "CNY": 7.2, "RUB": 91.0, "KZT": 450.0
                }
                
                # Conversion logic
                rate = 1.0
                
                if cur_from == cur_to:
                    c_res.setText(f"{amt:,.2f} {cur_to}")
                    return

                # Check if currencies are supported by Frankfurter (major ones only)
                # Frankfurter NO longer supports RUB. KZT is not supported.
                unsupported = ["RUB", "KZT"]
                
                if cur_from in unsupported or cur_to in unsupported:
                    # Use static math
                    val_usd = amt / static_rates.get(cur_from, 1.0)
                    total = val_usd * static_rates.get(cur_to, 1.0)
                    rate = static_rates.get(cur_to, 1.0) / static_rates.get(cur_from, 1.0)
                    c_res.setText(f"{amt:,.2f} {cur_from} = {total:,.2f} {cur_to}\n(Прим. курс: 1 {cur_from} ~ {rate:,.4f} {cur_to})")
                    return

                try:
                    # Try fetch
                    url = f"https://api.frankfurter.app/{dt_str}?from={cur_from}&to={cur_to}"
                    r = requests.get(url, timeout=2)
                    if r.status_code == 200:
                        data = r.json()
                        rate = data.get("rates", {}).get(cur_to, 1.0)
                        total = amt * rate
                        c_res.setText(f"{amt:,.2f} {cur_from} = {total:,.2f} {cur_to}\n(1 {cur_from} = {rate:,.4f} {cur_to})\nДанные: {dt_disp}")
                    else:
                        raise Exception(f"HTTP {r.status_code}")
                except Exception as e:
                    # Fallback to static
                    val_usd = amt / static_rates.get(cur_from, 1.0)
                    total = val_usd * static_rates.get(cur_to, 1.0)
                    rate = static_rates.get(cur_to, 1.0) / static_rates.get(cur_from, 1.0)
                    c_res.setText(f"{amt:,.2f} {cur_from} = {total:,.2f} {cur_to}\n(Ошибка API. Резервный курс)")
                    
            except Exception as e: 
                c_res.setText(f"Ошибка: {e}")
                
        cb = QPushButton("Обновить и Перевести"); cb.clicked.connect(calc_curr); cl.addWidget(cb)
        
        # 5. Stopwatch
        sl = create_tab("Секундомер")
        st_lbl = QLabel("00:00:00"); 
        st_lbl.setFont(QFont(APP_FONT, 36, QFont.Weight.Bold))
        st_lbl.setStyleSheet(f"font-size: 36pt; font-weight: bold; font-family: '{APP_FONT}';")
        st_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        sl.addWidget(st_lbl)
        
        self.st_seconds = 0
        self.st_timer = QTimer(d)
        def st_tick(): 
            self.st_seconds += 1
            m, s = divmod(self.st_seconds, 60)
            h, m = divmod(m, 60)
            st_lbl.setText(f"{h:02d}:{m:02d}:{s:02d}")
            
        self.st_timer.timeout.connect(st_tick)
        b_box = QHBoxLayout()
        b1=QPushButton("Старт"); b1.clicked.connect(lambda: self.st_timer.start(1000)); b_box.addWidget(b1)
        b2=QPushButton("Стоп"); b2.clicked.connect(self.st_timer.stop); b_box.addWidget(b2)
        b3=QPushButton("Сброс"); 
        def st_reset(): self.st_timer.stop(); self.st_seconds=0; st_lbl.setText("00:00:00")
        b3.clicked.connect(st_reset); b_box.addWidget(b3)
        sl.addLayout(b_box)

        # 6. Timer
        tl = create_tab("Таймер")
        tm_row = QHBoxLayout()
        tm_row.addStretch()
        tm_row.addWidget(QLabel("Сек:"))
        t_in=QLineEdit(); t_in.setFixedWidth(100); tm_row.addWidget(t_in)
        tm_row.addStretch()
        tl.addLayout(tm_row)
        
        t_lbl = QLabel("0"); 
        t_lbl.setFont(QFont(APP_FONT, 36, QFont.Weight.Bold))
        t_lbl.setStyleSheet(f"font-size: 36pt; font-weight: bold; font-family: '{APP_FONT}';")
        t_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tl.addWidget(t_lbl)
        
        self.tm_val = 0; self.tm_timer=QTimer(d)
        def tm_tick():
            self.tm_val-=1; t_lbl.setText(str(self.tm_val))
            if self.tm_val<=0: self.tm_timer.stop(); QMessageBox.information(d, "Таймер", "Готово!")
        self.tm_timer.timeout.connect(tm_tick)
        
        def tm_start():
            try: self.tm_val=int(t_in.text()); t_lbl.setText(str(self.tm_val)); self.tm_timer.start(1000)
            except: pass
            
        tm_box = QHBoxLayout()
        tb1=QPushButton("Пуск"); tb1.clicked.connect(tm_start); tm_box.addWidget(tb1)
        tb2=QPushButton("Стоп"); tb2.clicked.connect(self.tm_timer.stop); tm_box.addWidget(tb2)
        tl.addLayout(tm_box)

        # 7. Date (Add & Diff)
        dtl = create_tab("Дата")
        
        l_add = QLabel("Добавить дни к текущей дате"); l_add.setProperty("class", "header"); l_add.setStyleSheet("font-weight:bold; font-size:10pt; margin-top:10px;"); dtl.addWidget(l_add)
        
        dt_add_box = QHBoxLayout()
        dt_add_box.addWidget(QLabel("Дней:")); d_in=QLineEdit(); dt_add_box.addWidget(d_in)
        dtl.addLayout(dt_add_box)
        
        d_res = QLabel("Результат: -"); d_res.setStyleSheet("color:#FE9F0A;font-weight:bold;font-size:11pt;"); dtl.addWidget(d_res)
        def calc_date():
            try: d=int(d_in.text()); dt=datetime.now()+timedelta(days=d); d_res.setText(dt.strftime("%d.%m.%Y"))
            except: pass
        dtb=QPushButton("Рассчитать дату"); dtb.clicked.connect(calc_date); dtl.addWidget(dtb)
        
        l_diff = QLabel("Разница дат"); l_diff.setProperty("class", "header"); l_diff.setStyleSheet("font-weight:bold; font-size:10pt; margin-top:15px;"); dtl.addWidget(l_diff)
        
        dt_start = QDateEdit(); dt_start.setCalendarPopup(True); dt_start.setDate(QDate.currentDate())
        dt_end = QDateEdit(); dt_end.setCalendarPopup(True); dt_end.setDate(QDate.currentDate().addDays(1))
        dtl.addWidget(QLabel("От:")); dtl.addWidget(dt_start)
        dtl.addWidget(QLabel("До:")); dtl.addWidget(dt_end)
        d_diff_res = QLabel("Разница: -"); d_diff_res.setStyleSheet("color:#FE9F0A;font-weight:bold;font-size:11pt;"); dtl.addWidget(d_diff_res)
        def calc_diff():
            d1 = dt_start.date().toPyDate()
            d2 = dt_end.date().toPyDate()
            delta = abs((d2 - d1).days)
            d_diff_res.setText(f"Разница: {delta} дн.")
        dtb2=QPushButton("Рассчитать разницу"); dtb2.clicked.connect(calc_diff); dtl.addWidget(dtb2)

        # 8. Age (Masked Input)
        al = create_tab("Возраст")
        al.addWidget(QLabel("Дата рождения (дд.мм.гггг):"))
        y_in=QLineEdit(); 
        y_in.setInputMask("00.00.0000;_") 
        al.addWidget(y_in)
        a_res = QLabel("Результат: -"); a_res.setStyleSheet("color:#FE9F0A;font-weight:bold;font-size:11pt;"); al.addWidget(a_res)
        
        def get_age_suffix(age):
            if age % 10 == 1 and age % 100 != 11: return "год"
            elif age % 10 in [2, 3, 4] and not (age % 100 in [12, 13, 14]): return "года"
            else: return "лет"
            
        def calc_age():
            try: 
                txt = y_in.text()
                bdate = datetime.strptime(txt, "%d.%m.%Y")
                today = datetime.now()
                age = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
                a_res.setText(f"Вам {age} {get_age_suffix(age)}")
            except: a_res.setText("Ошибка даты")
        ab=QPushButton("Расчет"); ab.clicked.connect(calc_age); al.addWidget(ab)

        layout.addWidget(tabs)
        d.exec()

    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.current_theme = data.get("theme", "Темная (По умолч.)")
                    self.current_mode = data.get("mode", "Обычный")
                    self.opacity_val = data.get("opacity", 1.0)
                    self.is_pinned = data.get("pinned", False)
                    self.auto_update = data.get("auto_update", True)
                    # Restore geometry if saved
                    # self.saved_geometry = data.get("geometry") 
        except: pass

    def save_config(self):
        data = {
            "theme": self.current_theme,
            "mode": self.current_mode,
            "opacity": self.opacity_val,
            "pinned": self.is_pinned,
            "auto_update": self.auto_update,
            "geometry": self.saveGeometry().data().hex()
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f)
        except: pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    font = QFont(APP_FONT)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)
    
    window = StormCalculator()
    window.show()
    sys.exit(app.exec())