"""
dixUIAuto GUI - Premium Dark Interface

A modern, elegant GUI for the dixUIAuto Android automation framework.
Features a dark theme with compact controls and comprehensive device management.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
from datetime import datetime
from pathlib import Path

# Import framework components
try:
    from lib.engine import DixEngine
    from lib.exceptions import DixUIAutoError
    FRAMEWORK_AVAILABLE = True
except ImportError:
    FRAMEWORK_AVAILABLE = False


class StyleConstants:
    """Premium dark theme color palette and style constants."""
    
    # Colors - Premium Dark Theme
    BG_PRIMARY = "#1a1a2e"        # Deep navy background
    BG_SECONDARY = "#16213e"      # Slightly lighter panel background
    BG_TERTIARY = "#0f3460"       # Accent panels
    FG_PRIMARY = "#eaeaea"        # Primary text
    FG_SECONDARY = "#b8b8b8"      # Secondary text
    ACCENT_COLOR = "#e94560"      # Pink accent
    ACCENT_HOVER = "#ff6b6b"      # Lighter pink on hover
    SUCCESS_COLOR = "#4ecca3"     # Green for success states
    WARNING_COLOR = "#ffc857"     # Yellow for warnings
    ERROR_COLOR = "#e94560"       # Red for errors
    
    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_SMALL = 9
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_LARGE = 12
    FONT_SIZE_TITLE = 14
    
    # Spacing
    PADDING_XS = 3
    PADDING_SM = 5
    PADDING_MD = 10
    PADDING_LG = 15
    
    # Sizes
    BUTTON_HEIGHT = 25
    INPUT_HEIGHT = 25
    PANEL_WIDTH = 200
    LOG_HEIGHT = 150


class Tooltip:
    """Tooltip widget for hover information."""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            tw, text=self.text,
            background="#0f3460",
            foreground="#eaeaea",
            font=(StyleConstants.FONT_FAMILY, StyleConstants.FONT_SIZE_SMALL),
            padding=StyleConstants.PADDING_SM,
            relief="solid",
            borderwidth=1
        )
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class DevicePanel(ttk.LabelFrame):
    """Device connection and status panel."""
    
    def __init__(self, parent, gui):
        super().__init__(parent, text="📱 Device", padding=StyleConstants.PADDING_MD)
        self.gui = gui
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Device selection
        device_frame = ttk.Frame(self)
        device_frame.pack(fill=tk.X, pady=(0, StyleConstants.PADDING_SM))
        
        ttk.Label(device_frame, text="Device:", width=8).pack(side=tk.LEFT)
        
        self.device_var = tk.StringVar(value="auto")
        self.device_combo = ttk.Combobox(
            device_frame,
            textvariable=self.device_var,
            values=["auto"],
            state="readonly",
            height=5
        )
        self.device_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(StyleConstants.PADDING_SM, 0))
        
        Tooltip(self.device_combo, "Select device ID or 'auto' for first available")
        
        # Connection buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X)
        
        self.connect_btn = ttk.Button(
            btn_frame, text="Connect",
            command=self.gui.on_connect,
            width=10
        )
        self.connect_btn.pack(side=tk.LEFT, padx=(0, StyleConstants.PADDING_SM))
        
        self.disconnect_btn = ttk.Button(
            btn_frame, text="Disconnect",
            command=self.gui.on_disconnect,
            state="disabled",
            width=10
        )
        self.disconnect_btn.pack(side=tk.LEFT)
        
        # Status indicator
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, pady=(StyleConstants.PADDING_SM, 0))
        
        self.status_indicator = tk.Canvas(
            self, width=12, height=12,
            background=StyleConstants.BG_TERTIARY,
            highlightthickness=0
        )
        self.status_indicator.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(
            status_frame, text="Disconnected",
            font=(StyleConstants.FONT_FAMILY, StyleConstants.FONT_SIZE_SMALL)
        )
        self.status_label.pack(side=tk.LEFT, padx=(StyleConstants.PADDING_SM, 0))
        
        # Device info
        self.info_label = ttk.Label(
            self, text="",
            font=(StyleConstants.FONT_FAMILY, StyleConstants.FONT_SIZE_SMALL),
            foreground=StyleConstants.FG_SECONDARY
        )
        self.info_label.pack(fill=tk.X, pady=(StyleConstants.PADDING_SM, 0))
    
    def set_connected(self, connected: bool, device_info: dict = None):
        """Update UI based on connection status."""
        if connected:
            self.status_indicator.itemconfig(
                self.status_indicator, background=StyleConstants.SUCCESS_COLOR
            )
            self.status_label.config(text="Connected")
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            
            if device_info:
                info_text = f"{device_info.get('model', 'Unknown')} | {device_info.get('android_version', 'N/A')}"
                self.info_label.config(text=info_text)
        else:
            self.status_indicator.itemconfig(
                self.status_indicator, background=StyleConstants.BG_TERTIARY
            )
            self.status_label.config(text="Disconnected")
            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")
            self.info_label.config(text="")
    
    def refresh_devices(self):
        """Refresh device list."""
        # This would call ADB to get devices
        pass


class AppControlPanel(ttk.LabelFrame):
    """Application control panel."""
    
    def __init__(self, parent, gui):
        super().__init__(parent, text="📲 App Control", padding=StyleConstants.PADDING_MD)
        self.gui = gui
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Package input
        pkg_frame = ttk.Frame(self)
        pkg_frame.pack(fill=tk.X, pady=(0, StyleConstants.PADDING_SM))
        
        ttk.Label(pkg_frame, text="Package:", width=8).pack(side=tk.LEFT)
        
        self.package_var = tk.StringVar()
        self.package_entry = ttk.Entry(pkg_frame, textvariable=self.package_var)
        self.package_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(StyleConstants.PADDING_SM, 0))
        
        Tooltip(self.package_entry, "Enter app package name (e.g., com.example.app)")
        
        # Action buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X)
        
        self.open_btn = ttk.Button(
            btn_frame, text="Open",
            command=self.gui.on_open_app,
            state="disabled",
            width=8
        )
        self.open_btn.pack(side=tk.LEFT, padx=(0, StyleConstants.PADDING_SM))
        
        self.close_btn = ttk.Button(
            btn_frame, text="Close",
            command=self.gui.on_close_app,
            state="disabled",
            width=8
        )
        self.close_btn.pack(side=tk.LEFT)
        
        # Current app display
        current_frame = ttk.Frame(self)
        current_frame.pack(fill=tk.X, pady=(StyleConstants.PADDING_SM, 0))
        
        ttk.Label(
            current_frame, text="Current:",
            font=(StyleConstants.FONT_FAMILY, StyleConstants.FONT_SIZE_SMALL)
        ).pack(side=tk.LEFT)
        
        self.current_app_label = ttk.Label(
            current_frame, text="-",
            font=(StyleConstants.FONT_FAMILY, StyleConstants.FONT_SIZE_SMALL),
            foreground=StyleConstants.ACCENT_COLOR
        )
        self.current_app_label.pack(side=tk.LEFT, padx=(StyleConstants.PADDING_SM, 0))
    
    def set_enabled(self, enabled: bool):
        """Enable/disable controls."""
        state = "normal" if enabled else "disabled"
        self.open_btn.config(state=state)
        self.close_btn.config(state=state)
    
    def set_current_app(self, package: str):
        """Update current app display."""
        self.current_app_label.config(text=package or "-")


class ActionPanel(ttk.LabelFrame):
    """Quick actions panel."""
    
    def __init__(self, parent, gui):
        super().__init__(parent, text="⚡ Actions", padding=StyleConstants.PADDING_MD)
        self.gui = gui
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Search criteria
        search_frame = ttk.LabelFrame(self, text="Find Element", padding=StyleConstants.PADDING_SM)
        search_frame.pack(fill=tk.X, pady=(0, StyleConstants.PADDING_SM))
        
        # Text search
        text_frame = ttk.Frame(search_frame)
        text_frame.pack(fill=tk.X, pady=(0, StyleConstants.PADDING_XS))
        
        ttk.Label(text_frame, text="Text:", width=6).pack(side=tk.LEFT)
        self.text_var = tk.StringVar()
        ttk.Entry(text_frame, textvariable=self.text_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(StyleConstants.PADDING_SM, 0)
        )
        
        # Resource ID search
        id_frame = ttk.Frame(search_frame)
        id_frame.pack(fill=tk.X, pady=(0, StyleConstants.PADDING_XS))
        
        ttk.Label(id_frame, text="ID:", width=6).pack(side=tk.LEFT)
        self.id_var = tk.StringVar()
        ttk.Entry(id_frame, textvariable=self.id_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(StyleConstants.PADDING_SM, 0)
        )
        
        # Content description search
        desc_frame = ttk.Frame(search_frame)
        desc_frame.pack(fill=tk.X)
        
        ttk.Label(desc_frame, text="Desc:", width=6).pack(side=tk.LEFT)
        self.desc_var = tk.StringVar()
        ttk.Entry(desc_frame, textvariable=self.desc_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(StyleConstants.PADDING_SM, 0)
        )
        
        # Find button
        self.find_btn = ttk.Button(
            search_frame, text="🔍 Find",
            command=self.gui.on_find_element,
            state="disabled"
        )
        self.find_btn.pack(fill=tk.X, pady=(StyleConstants.PADDING_SM, 0))
        
        # Quick actions grid
        actions_frame = ttk.Frame(self)
        actions_frame.pack(fill=tk.X)
        
        # Row 1
        self.click_btn = ttk.Button(
            actions_frame, text="Click",
            command=self.gui.on_click,
            state="disabled",
            width=8
        )
        self.click_btn.grid(row=0, column=0, padx=(0, StyleConstants.PADDING_SM), pady=(0, StyleConstants.PADDING_SM))
        
        self.swipe_btn = ttk.Button(
            actions_frame, text="Swipe ↓",
            command=lambda: self.gui.on_swipe("down"),
            state="disabled",
            width=8
        )
        self.swipe_btn.grid(row=0, column=1, pady=(0, StyleConstants.PADDING_SM))
        
        # Row 2
        self.back_btn = ttk.Button(
            actions_frame, text="Back",
            command=self.gui.on_back,
            state="disabled",
            width=8
        )
        self.back_btn.grid(row=1, column=0, padx=(0, StyleConstants.PADDING_SM))
        
        self.home_btn = ttk.Button(
            actions_frame, text="Home",
            command=self.gui.on_home,
            state="disabled",
            width=8
        )
        self.home_btn.grid(row=1, column=1)
        
        # Row 3
        self.screenshot_btn = ttk.Button(
            actions_frame, text="📷 Screenshot",
            command=self.gui.on_screenshot,
            state="disabled",
            width=8
        )
        self.screenshot_btn.grid(row=2, column=0, columnspan=2, pady=(StyleConstants.PADDING_SM, 0))
    
    def set_enabled(self, enabled: bool):
        """Enable/disable all action buttons."""
        state = "normal" if enabled else "disabled"
        for btn in [self.find_btn, self.click_btn, self.swipe_btn, 
                    self.back_btn, self.home_btn, self.screenshot_btn]:
            btn.config(state=state)


class FormPanel(ttk.LabelFrame):
    """Form filling panel."""
    
    def __init__(self, parent, gui):
        super().__init__(parent, text="📝 Form Filler", padding=StyleConstants.PADDING_MD)
        self.gui = gui
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Label field
        label_frame = ttk.Frame(self)
        label_frame.pack(fill=tk.X, pady=(0, StyleConstants.PADDING_SM))
        
        ttk.Label(label_frame, text="Label:", width=6).pack(side=tk.LEFT)
        
        self.label_var = tk.StringVar()
        self.label_entry = ttk.Entry(label_frame, textvariable=self.label_var)
        self.label_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(StyleConstants.PADDING_SM, 0))
        
        Tooltip(self.label_entry, "Field label (e.g., 'Username', 'CPF')")
        
        # Value field
        value_frame = ttk.Frame(self)
        value_frame.pack(fill=tk.X, pady=(0, StyleConstants.PADDING_SM))
        
        ttk.Label(value_frame, text="Value:", width=6).pack(side=tk.LEFT)
        
        self.value_var = tk.StringVar()
        self.value_entry = ttk.Entry(value_frame, textvariable=self.value_var)
        self.value_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(StyleConstants.PADDING_SM, 0))
        
        Tooltip(self.value_entry, "Value to enter")
        
        # Fill button
        self.fill_btn = ttk.Button(
            self, text="Fill Field",
            command=self.gui.on_fill_form,
            state="disabled"
        )
        self.fill_btn.pack(fill=tk.X)
    
    def set_enabled(self, enabled: bool):
        """Enable/disable controls."""
        state = "normal" if enabled else "disabled"
        self.fill_btn.config(state=state)
    
    def clear(self):
        """Clear input fields."""
        self.label_var.set("")
        self.value_var.set("")


class LogPanel(ttk.LabelFrame):
    """Console log panel."""
    
    def __init__(self, parent, gui):
        super().__init__(parent, text="📋 Log Console", padding=StyleConstants.PADDING_MD)
        self.gui = gui
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            self,
            height=12,
            font=("Consolas", StyleConstants.FONT_SIZE_SMALL),
            bg=StyleConstants.BG_PRIMARY,
            fg=StyleConstants.FG_PRIMARY,
            insertbackground=StyleConstants.FG_PRIMARY,
            selectbackground=StyleConstants.BG_TERTIARY,
            relief="flat",
            borderwidth=0,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for different log levels
        self.log_text.tag_config("INFO", foreground=StyleConstants.FG_PRIMARY)
        self.log_text.tag_config("SUCCESS", foreground=StyleConstants.SUCCESS_COLOR)
        self.log_text.tag_config("WARNING", foreground=StyleConstants.WARNING_COLOR)
        self.log_text.tag_config("ERROR", foreground=StyleConstants.ERROR_COLOR)
        self.log_text.tag_config("DEBUG", foreground=StyleConstants.FG_SECONDARY)
        
        # Button frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=(StyleConstants.PADDING_SM, 0))
        
        self.clear_btn = ttk.Button(
            btn_frame, text="Clear",
            command=self.clear,
            width=8
        )
        self.clear_btn.pack(side=tk.LEFT)
        
        self.save_btn = ttk.Button(
            btn_frame, text="Save",
            command=self.gui.on_save_log,
            width=8
        )
        self.save_btn.pack(side=tk.LEFT, padx=(StyleConstants.PADDING_SM, 0))
    
    def log(self, message: str, level: str = "INFO"):
        """Add a log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_msg, level)
        self.log_text.see(tk.END)
    
    def clear(self):
        """Clear the log."""
        self.log_text.delete(1.0, tk.END)


class DixUIAutoGUI:
    """Main GUI application class."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("dixUIAuto - Android Automation")
        self.root.geometry("900x650")
        self.root.minsize(800, 550)
        
        # Set dark theme colors
        self.root.configure(bg=StyleConstants.BG_PRIMARY)
        
        # Engine instance
        self.engine = None
        self.connected = False
        
        # Message queue for thread-safe logging
        self.message_queue = queue.Queue()
        
        # Setup UI
        self._setup_styles()
        self._setup_ui()
        
        # Start message processing
        self._process_messages()
    
    def _setup_styles(self):
        """Configure ttk styles for dark theme."""
        style = ttk.Style()
        
        # Configure colors
        style.configure(
            "TFrame", background=StyleConstants.BG_PRIMARY
        )
        style.configure(
            "TLabel",
            background=StyleConstants.BG_PRIMARY,
            foreground=StyleConstants.FG_PRIMARY,
            font=(StyleConstants.FONT_FAMILY, StyleConstants.FONT_SIZE_NORMAL)
        )
        style.configure(
            "TLabelframe",
            background=StyleConstants.BG_SECONDARY,
            foreground=StyleConstants.FG_PRIMARY,
            font=(StyleConstants.FONT_FAMILY, StyleConstants.FONT_SIZE_TITLE, "bold")
        )
        style.configure(
            "TLabelframe.Label",
            background=StyleConstants.BG_SECONDARY,
            foreground=StyleConstants.FG_PRIMARY,
            font=(StyleConstants.FONT_FAMILY, StyleConstants.FONT_SIZE_TITLE, "bold")
        )
        style.configure(
            "TButton",
            font=(StyleConstants.FONT_FAMILY, StyleConstants.FONT_SIZE_NORMAL)
        )
        style.configure(
            "TEntry",
            fieldbackground=StyleConstants.BG_PRIMARY,
            foreground=StyleConstants.FG_PRIMARY,
            insertcolor=StyleConstants.FG_PRIMARY
        )
        style.configure(
            "TCombobox",
            fieldbackground=StyleConstants.BG_PRIMARY,
            foreground=StyleConstants.FG_PRIMARY
        )
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        # Main container
        main_container = ttk.Frame(self.root, padding=StyleConstants.PADDING_LG)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (controls)
        left_panel = ttk.Frame(main_container, width=StyleConstants.PANEL_WIDTH)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, StyleConstants.PADDING_MD))
        left_panel.pack_propagate(False)
        
        # Create panels in left column
        self.device_panel = DevicePanel(left_panel, self)
        self.device_panel.pack(fill=tk.X, pady=(0, StyleConstants.PADDING_MD))
        
        self.app_panel = AppControlPanel(left_panel, self)
        self.app_panel.pack(fill=tk.X, pady=(0, StyleConstants.PADDING_MD))
        
        self.action_panel = ActionPanel(left_panel, self)
        self.action_panel.pack(fill=tk.X, pady=(0, StyleConstants.PADDING_MD))
        
        self.form_panel = FormPanel(left_panel, self)
        self.form_panel.pack(fill=tk.X)
        
        # Right panel (log)
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.log_panel = LogPanel(right_panel, self)
        self.log_panel.pack(fill=tk.BOTH, expand=True)
        
        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _log_message(self, message: str, level: str = "INFO"):
        """Thread-safe logging."""
        self.message_queue.put((message, level))
    
    def _process_messages(self):
        """Process queued messages."""
        try:
            while True:
                message, level = self.message_queue.get_nowait()
                self.log_panel.log(message, level)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self._process_messages)
    
    def _run_in_thread(self, func, *args, **kwargs):
        """Run a function in a background thread."""
        def wrapper():
            try:
                result = func(*args, **kwargs)
                if result:
                    self._log_message(f"Operation completed successfully", "SUCCESS")
            except Exception as e:
                self._log_message(f"Error: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
    
    # Event handlers
    
    def on_connect(self):
        """Handle connect button click."""
        self._log_message("Connecting to device...")
        
        def connect_task():
            try:
                if not FRAMEWORK_AVAILABLE:
                    raise RuntimeError("Framework not available. Please install dependencies.")
                
                device_id = self.device_panel.device_var.get()
                device_id = None if device_id == "auto" else device_id
                
                self.engine = DixEngine()
                self.engine.connect(device_id)
                
                self.connected = True
                device_info = self.engine.get_device_info()
                
                self.root.after(0, lambda: self.device_panel.set_connected(True, device_info))
                self.root.after(0, lambda: self.app_panel.set_enabled(True))
                self.root.after(0, lambda: self.action_panel.set_enabled(True))
                self.root.after(0, lambda: self.form_panel.set_enabled(True))
                
                self._log_message("Device connected successfully", "SUCCESS")
                
            except Exception as e:
                self.root.after(0, lambda: self._log_message(f"Connection failed: {str(e)}", "ERROR"))
        
        self._run_in_thread(connect_task)
    
    def on_disconnect(self):
        """Handle disconnect button click."""
        try:
            if self.engine:
                self.engine.disconnect()
            
            self.connected = False
            self.device_panel.set_connected(False)
            self.app_panel.set_enabled(False)
            self.action_panel.set_enabled(False)
            self.form_panel.set_enabled(False)
            
            self._log_message("Device disconnected", "WARNING")
            
        except Exception as e:
            self._log_message(f"Disconnect error: {str(e)}", "ERROR")
    
    def on_open_app(self):
        """Handle open app button click."""
        package = self.app_panel.package_var.get().strip()
        
        if not package:
            messagebox.showwarning("Warning", "Please enter a package name")
            return
        
        self._log_message(f"Opening app: {package}")
        
        def open_task():
            try:
                success = self.engine.open(package)
                if success:
                    current_pkg = self.engine.get_current_package()
                    self.root.after(0, lambda: self.app_panel.set_current_app(current_pkg))
                    self._log_message(f"App opened: {package}", "SUCCESS")
                else:
                    self.root.after(0, lambda: self._log_message("Failed to open app", "ERROR"))
            except Exception as e:
                self.root.after(0, lambda: self._log_message(f"Open app error: {str(e)}", "ERROR"))
        
        self._run_in_thread(open_task)
    
    def on_close_app(self):
        """Handle close app button click."""
        package = self.app_panel.package_var.get().strip()
        
        if not package:
            package = self.app_panel.current_app_label.cget("text")
            if package == "-":
                messagebox.showwarning("Warning", "No app specified")
                return
        
        self._log_message(f"Closing app: {package}")
        
        def close_task():
            try:
                success = self.engine.close(package)
                if success:
                    self.root.after(0, lambda: self.app_panel.set_current_app(None))
                    self._log_message(f"App closed: {package}", "SUCCESS")
                else:
                    self.root.after(0, lambda: self._log_message("Failed to close app", "ERROR"))
            except Exception as e:
                self.root.after(0, lambda: self._log_message(f"Close app error: {str(e)}", "ERROR"))
        
        self._run_in_thread(close_task)
    
    def on_find_element(self):
        """Handle find element button click."""
        text = self.action_panel.text_var.get().strip()
        resource_id = self.action_panel.id_var.get().strip()
        content_desc = self.action_panel.desc_var.get().strip()
        
        if not any([text, resource_id, content_desc]):
            messagebox.showwarning("Warning", "Please enter at least one search criterion")
            return
        
        criteria = {}
        if text:
            criteria['text'] = text
        if resource_id:
            criteria['resource_id'] = resource_id
        if content_desc:
            criteria['content_desc'] = content_desc
        
        self._log_message(f"Finding element: {criteria}")
        
        try:
            self.engine.refresh()
            element = self.engine.finder.find_first(**criteria)
            
            if element:
                self._log_message(f"Element found: {element}", "SUCCESS")
            else:
                self._log_message("Element not found", "WARNING")
                
        except Exception as e:
            self._log_message(f"Find error: {str(e)}", "ERROR")
    
    def on_click(self):
        """Handle click button click."""
        text = self.action_panel.text_var.get().strip()
        resource_id = self.action_panel.id_var.get().strip()
        content_desc = self.action_panel.desc_var.get().strip()
        
        if not any([text, resource_id, content_desc]):
            messagebox.showwarning("Warning", "Please specify an element to click")
            return
        
        self._log_message("Performing click...")
        
        def click_task():
            try:
                success = self.engine.click(
                    text=text if text else None,
                    resource_id=resource_id if resource_id else None,
                    content_desc=content_desc if content_desc else None
                )
                
                if success:
                    self.root.after(0, lambda: self._log_message("Click successful", "SUCCESS"))
                else:
                    self.root.after(0, lambda: self._log_message("Click failed", "ERROR"))
                    
            except Exception as e:
                self.root.after(0, lambda: self._log_message(f"Click error: {str(e)}", "ERROR"))
        
        self._run_in_thread(click_task)
    
    def on_swipe(self, direction: str):
        """Handle swipe button click."""
        self._log_message(f"Swiping {direction}...")
        
        def swipe_task():
            try:
                success = self.engine.swipe(direction)
                if success:
                    self.root.after(0, lambda: self._log_message(f"Swipe {direction} successful", "SUCCESS"))
                else:
                    self.root.after(0, lambda: self._log_message("Swipe failed", "ERROR"))
            except Exception as e:
                self.root.after(0, lambda: self._log_message(f"Swipe error: {str(e)}", "ERROR"))
        
        self._run_in_thread(swipe_task)
    
    def on_back(self):
        """Handle back button click."""
        self._log_message("Sending BACK key...")
        
        try:
            if self.engine and self.engine.adb:
                self.engine.adb.input_key("KEYCODE_BACK")
                self._log_message("Back key sent", "SUCCESS")
        except Exception as e:
            self._log_message(f"Back error: {str(e)}", "ERROR")
    
    def on_home(self):
        """Handle home button click."""
        self._log_message("Sending HOME key...")
        
        try:
            if self.engine and self.engine.adb:
                self.engine.adb.input_key("KEYCODE_HOME")
                self._log_message("Home key sent", "SUCCESS")
        except Exception as e:
            self._log_message(f"Home error: {str(e)}", "ERROR")
    
    def on_screenshot(self):
        """Handle screenshot button click."""
        self._log_message("Taking screenshot...")
        
        def screenshot_task():
            try:
                path = self.engine.take_screenshot()
                self.root.after(0, lambda: self._log_message(f"Screenshot saved: {path}", "SUCCESS"))
            except Exception as e:
                self.root.after(0, lambda: self._log_message(f"Screenshot error: {str(e)}", "ERROR"))
        
        self._run_in_thread(screenshot_task)
    
    def on_fill_form(self):
        """Handle form fill button click."""
        label = self.form_panel.label_var.get().strip()
        value = self.form_panel.value_var.get().strip()
        
        if not label or not value:
            messagebox.showwarning("Warning", "Please enter both label and value")
            return
        
        self._log_message(f"Filling form: {label} = {value}")
        
        def fill_task():
            try:
                success = self.engine.form.fill(label=label, value=value)
                if success:
                    self.root.after(0, lambda: self._log_message("Form filled successfully", "SUCCESS"))
                    self.root.after(0, lambda: self.form_panel.clear())
                else:
                    self.root.after(0, lambda: self._log_message("Form fill failed", "ERROR"))
            except Exception as e:
                self.root.after(0, lambda: self._log_message(f"Form fill error: {str(e)}", "ERROR"))
        
        self._run_in_thread(fill_task)
    
    def on_save_log(self):
        """Handle save log button click."""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Log As"
        )
        
        if file_path:
            try:
                log_content = self.log_panel.log_text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                self._log_message(f"Log saved to: {file_path}", "SUCCESS")
            except Exception as e:
                self._log_message(f"Save error: {str(e)}", "ERROR")
    
    def on_closing(self):
        """Handle window close event."""
        if self.connected:
            if messagebox.askokcancel("Quit", "Device is connected. Disconnect and quit?"):
                self.on_disconnect()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Start the GUI application."""
        self._log_message("dixUIAuto GUI started", "SUCCESS")
        self._log_message("Connect to a device to begin automation")
        self.root.mainloop()


def main():
    """Entry point for the GUI application."""
    app = DixUIAutoGUI()
    app.run()


if __name__ == "__main__":
    main()
