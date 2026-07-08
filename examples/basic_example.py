"""
Basic example of using dixUIAuto framework.

This example demonstrates:
- Connecting to a device
- Opening an app
- Finding and clicking elements
- Filling forms
- Taking screenshots
"""

from lib.engine import DixEngine


def basic_automation():
    """Basic automation workflow example."""
    
    # Initialize engine
    engine = DixEngine()
    
    try:
        # Connect to device (auto-detects first available)
        print("Connecting to device...")
        engine.connect()
        
        # Get device info
        info = engine.get_device_info()
        print(f"Connected to: {info.get('model', 'Unknown')}")
        
        # Open application
        print("Opening app...")
        engine.open("com.example.app")
        
        # Wait for element to appear
        print("Waiting for login screen...")
        if engine.wait(text="Login", timeout=10):
            print("Login screen loaded!")
        
        # Find and click element by text
        print("Clicking 'Entrar' button...")
        engine.click(text="Entrar")
        
        # Fill form fields
        print("Filling form...")
        engine.form.fill(label="Username", value="user123")
        engine.form.fill(label="Password", value="secret123")
        
        # Click submit
        engine.click(text="Submit")
        
        # Take screenshot
        print("Taking screenshot...")
        screenshot_path = engine.take_screenshot()
        print(f"Screenshot saved: {screenshot_path}")
        
        # Swipe/scroll
        print("Scrolling down...")
        engine.swipe(direction="down", steps=2)
        
        # Wait for next screen
        engine.wait(text="Welcome", timeout=5)
        
        print("Automation completed successfully!")
        
    except Exception as e:
        print(f"Error during automation: {e}")
        
    finally:
        # Disconnect
        engine.disconnect()
        print("Disconnected from device")


if __name__ == "__main__":
    basic_automation()
