"""
Utils - Utility functions for dixUIAuto.
"""

import re
from typing import Optional, List


def parse_bounds(bounds_str: str) -> Optional[tuple]:
    """
    Parse bounds string to tuple.
    
    Args:
        bounds_str: String like "[0,100][200,300]"
        
    Returns:
        Tuple (left, top, right, bottom) or None
    """
    try:
        match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
        if match:
            return tuple(map(int, match.groups()))
    except:
        pass
    return None


def calculate_center(bounds: tuple) -> tuple:
    """
    Calculate center point from bounds.
    
    Args:
        bounds: Tuple (left, top, right, bottom)
        
    Returns:
        Tuple (center_x, center_y)
    """
    left, top, right, bottom = bounds
    return ((left + right) // 2, (top + bottom) // 2)


def sanitize_text(text: str) -> str:
    """
    Sanitize text for comparison.
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text (trimmed, normalized whitespace)
    """
    if not text:
        return ""
    # Normalize whitespace
    text = ' '.join(text.split())
    return text.strip()


def mask_sensitive_data(data: str, data_type: str = 'default') -> str:
    """
    Mask sensitive data for logging.
    
    Args:
        data: Sensitive data
        data_type: Type of data ('cpf', 'password', 'card', etc.)
        
    Returns:
        Masked string
    """
    if not data:
        return ""
    
    if len(data) <= 4:
        return "*" * len(data)
    
    if data_type in ['cpf', 'cnpj']:
        # Show last 4 digits
        return "*" * (len(data) - 4) + data[-4:]
    
    if data_type == 'card':
        # Show last 4 digits with spacing
        return "**** **** **** " + data[-4:]
    
    if data_type == 'password':
        return "*" * len(data)
    
    # Default: show first 2 and last 2
    return data[:2] + "*" * (len(data) - 4) + data[-2:]


def format_phone(phone: str) -> str:
    """
    Format phone number to Brazilian format.
    
    Args:
        phone: Raw phone number
        
    Returns:
        Formatted phone
    """
    digits = ''.join(c for c in phone if c.isdigit())
    
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    elif len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    
    return digits


def format_cpf(cpf: str) -> str:
    """
    Format CPF to standard Brazilian format.
    
    Args:
        cpf: Raw CPF number
        
    Returns:
        Formatted CPF
    """
    digits = ''.join(c for c in cpf if c.isdigit())
    
    if len(digits) == 11:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    
    return digits


def format_cep(cep: str) -> str:
    """
    Format CEP to Brazilian format.
    
    Args:
        cep: Raw CEP
        
    Returns:
        Formatted CEP
    """
    digits = ''.join(c for c in cep if c.isdigit())
    
    if len(digits) == 8:
        return f"{digits[:5]}-{digits[5:]}"
    
    return digits


def validate_email(email: str) -> bool:
    """
    Basic email validation.
    
    Args:
        email: Email address
        
    Returns:
        True if valid format
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))


def validate_cpf(cpf: str) -> bool:
    """
    Validate CPF checksum.
    
    Args:
        cpf: CPF number
        
    Returns:
        True if valid CPF
    """
    digits = ''.join(c for c in cpf if c.isdigit())
    
    if len(digits) != 11:
        return False
    
    # Check for repeated digits
    if len(set(digits)) == 1:
        return False
    
    def calculate_digit(digit_count: int) -> int:
        total = sum(int(digits[i]) * (digit_count + 1 - i) 
                   for i in range(digit_count))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder
    
    digit1 = calculate_digit(9)
    digit2 = calculate_digit(10)
    
    return digits[9] == str(digit1) and digits[10] == str(digit2)


def truncate_string(s: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        s: Input string
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def find_common_prefix(strings: List[str]) -> str:
    """
    Find common prefix among strings.
    
    Args:
        strings: List of strings
        
    Returns:
        Common prefix
    """
    if not strings:
        return ""
    
    prefix = strings[0]
    for s in strings[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    
    return prefix
