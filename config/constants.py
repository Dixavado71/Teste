"""
Constant values used throughout the dixUIAuto framework.
"""

# ADB Commands
ADB_CMD_DEVICES = "devices"
ADB_CMD_SHELL = "shell"
ADB_CMD_INSTALL = "install"
ADB_CMD_UNINSTALL = "uninstall"
ADB_CMD_PULL = "pull"
ADB_CMD_PUSH = "push"
ADB_CMD_START = "am start"
ADB_CMD_STOP = "am force-stop"
ADB_CMD_SCREENCAP = "screencap"
ADB_CMD_DUMPSYS = "dumpsys"
ADB_CMD_INPUT = "input"

# UI Element Attributes
ATTR_TEXT = "text"
ATTR_RESOURCE_ID = "resource-id"
ATTR_CLASS = "class"
ATTR_CONTENT_DESC = "content-desc"
ATTR_BOUNDS = "bounds"
ATTR_CHECKABLE = "checkable"
ATTR_CHECKED = "checked"
ATTR_CLICKABLE = "clickable"
ATTR_ENABLED = "enabled"
ATTR_FOCUSABLE = "focusable"
ATTR_FOCUSED = "focused"
ATTR_LONG_CLICKABLE = "long-clickable"
ATTR_PASSWORD = "password"
ATTR_SCROLLABLE = "scrollable"
ATTR_SELECTED = "selected"

# Common Android Classes
CLASS_BUTTON = "android.widget.Button"
CLASS_TEXT_VIEW = "android.widget.TextView"
CLASS_EDIT_TEXT = "android.widget.EditText"
CLASS_IMAGE_VIEW = "android.widget.ImageView"
CLASS_LIST_VIEW = "android.widget.ListView"
CLASS_RECYCLER_VIEW = "androidx.recyclerview.widget.RecyclerView"
CLASS_SCROLL_VIEW = "android.widget.ScrollView"
CLASS_WEB_VIEW = "android.webkit.WebView"

# Input types
INPUT_TYPE_TEXT = "text"
INPUT_TYPE_PASSWORD = "password"
INPUT_TYPE_EMAIL = "email"
INPUT_TYPE_PHONE = "phone"
INPUT_TYPE_NUMBER = "number"

# Key codes
KEYCODE_ENTER = 66
KEYCODE_BACK = 4
KEYCODE_HOME = 3
KEYCODE_BACKSPACE = 67
KEYCODE_DEL = 67
KEYCODE_TAB = 61

# Swipe directions
DIRECTION_UP = "up"
DIRECTION_DOWN = "down"
DIRECTION_LEFT = "left"
DIRECTION_RIGHT = "right"

# XML Namespaces
XML_NAMESPACE = "{http://schemas.android.com/apk/res/android}"
