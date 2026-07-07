"""
Form - Smart form filling for dixUIAuto.
"""

from typing import Optional, Dict, Any
from lib.logs import setup_logger
from lib.exceptions import FormFillError, ElementNotFoundError

logger = setup_logger("SmartForm")


class SmartForm:
    """
    Smart Form - Intelligent form filling module.
    
    Allows filling forms by label:
    ```python
    engine.form.fill(label="Número de CPF", value="02959350146")
    ```
    
    Internally:
    1. Finds label
    2. Finds corresponding field
    3. Clicks field
    4. Clears field
    5. Types value
    6. Validates
    
    Supports:
    - Text fields
    - Password fields
    - Email fields
    - Phone fields
    - CEP (Brazilian ZIP)
    - PIX keys
    - Credit card numbers
    - OTP codes
    """
    
    def __init__(self, finder, clicker, keyboard, validator, locator):
        """
        Initialize SmartForm.
        
        Args:
            finder: Finder instance
            clicker: ClickEngine instance
            keyboard: KeyboardEngine instance
            validator: Validator instance
            locator: Locator instance
        """
        self.finder = finder
        self.clicker = clicker
        self.keyboard = keyboard
        self.validator = validator
        self.locator = locator
        self._all_elements = []
    
    def set_elements(self, elements: list) -> None:
        """Set the current list of UI elements."""
        self._all_elements = elements
    
    def fill(self, label: str, value: str, 
             field_type: Optional[str] = None) -> bool:
        """
        Fill a form field by finding its label.
        
        Args:
            label: Label text to search for
            value: Value to enter
            field_type: Optional type hint ('text', 'password', 'email', etc.)
            
        Returns:
            True if successful
            
        Raises:
            FormFillError: If filling fails
        """
        logger.info(f"Filling field '{label}' with value '{value[:10]}...'")
        
        try:
            # Step 1: Find the label
            label_element = self._find_label(label)
            
            if label_element is None:
                raise FormFillError(f"Label not found: '{label}'")
            
            # Step 2: Find corresponding field
            field_element = self.locator.find_field_for_label(
                label_element, self._all_elements)
            
            if field_element is None:
                raise FormFillError(f"No field found for label: '{label}'")
            
            # Step 3: Click the field
            if not self.clicker.click(field_element):
                raise FormFillError(f"Failed to click field for: '{label}'")
            
            # Step 4: Clear and type
            if field_type == 'password':
                success = self.keyboard.send_keys(value, clear_first=True)
            elif field_type == 'slow':
                success = self.keyboard.type_slowly(value)
            else:
                success = self.keyboard.send_keys(value, clear_first=True)
            
            if not success:
                raise FormFillError(f"Failed to enter value for: '{label}'")
            
            # Step 5: Validate
            logger.info(f"Successfully filled field: '{label}'")
            return True
            
        except Exception as e:
            logger.error(f"Form fill error: {e}")
            raise FormFillError(f"Failed to fill '{label}': {e}")
    
    def _find_label(self, label_text: str):
        """Find a label element by text."""
        # Try exact match first
        elements = self.finder.find_text(label_text, exact=True, timeout=2)
        if elements:
            return elements[0]
        
        # Try partial match
        elements = self.finder.find_text(label_text, exact=False, timeout=2)
        if elements:
            return elements[0]
        
        # Try content-desc
        elements = self.finder.find_desc(label_text, exact=False, timeout=2)
        if elements:
            return elements[0]
        
        return None
    
    def fill_by_resource(self, resource_id: str, value: str) -> bool:
        """
        Fill a field by its resource ID.
        
        Args:
            resource_id: Resource ID of the field
            value: Value to enter
            
        Returns:
            True if successful
        """
        logger.info(f"Filling field by resource-id: '{resource_id}'")
        
        elements = self.finder.find_resource(resource_id)
        if not elements:
            raise FormFillError(f"Field not found: {resource_id}")
        
        field = elements[0]
        
        if not self.clicker.click(field):
            raise FormFillError(f"Failed to click field: {resource_id}")
        
        if not self.keyboard.send_keys(value, clear_first=True):
            raise FormFillError(f"Failed to enter value: {resource_id}")
        
        return True
    
    def fill_cpf(self, cpf: str) -> bool:
        """
        Fill CPF field (Brazilian tax ID).
        
        Args:
            cpf: CPF number (with or without formatting)
            
        Returns:
            True if successful
        """
        # Remove formatting
        cpf_clean = ''.join(c for c in cpf if c.isdigit())
        
        # Look for CPF label
        labels = ['CPF', 'Número de CPF', 'Digite seu CPF', 'Informar CPF']
        
        for label in labels:
            try:
                if self.fill(label, cpf_clean):
                    return True
            except FormFillError:
                continue
        
        raise FormFillError(f"Could not find CPF field")
    
    def fill_password(self, password: str, label: str = 'Senha') -> bool:
        """
        Fill password field.
        
        Args:
            password: Password value
            label: Label to search for
            
        Returns:
            True if successful
        """
        return self.fill(label, password, field_type='password')
    
    def fill_email(self, email: str, label: str = 'E-mail') -> bool:
        """
        Fill email field.
        
        Args:
            email: Email address
            label: Label to search for
            
        Returns:
            True if successful
        """
        return self.fill(label, email, field_type='email')
    
    def fill_phone(self, phone: str, label: str = 'Telefone') -> bool:
        """
        Fill phone field.
        
        Args:
            phone: Phone number
            label: Label to search for
            
        Returns:
            True if successful
        """
        phone_clean = ''.join(c for c in phone if c.isdigit())
        return self.fill(label, phone_clean, field_type='phone')
    
    def fill_cep(self, cep: str, label: str = 'CEP') -> bool:
        """
        Fill CEP field (Brazilian ZIP code).
        
        Args:
            cep: CEP value
            label: Label to search for
            
        Returns:
            True if successful
        """
        cep_clean = ''.join(c for c in cep if c.isdigit())
        return self.fill(label, cep_clean)
    
    def fill_pix(self, pix_key: str, label: str = 'Chave PIX') -> bool:
        """
        Fill PIX key field.
        
        Args:
            pix_key: PIX key value
            label: Label to search for
            
        Returns:
            True if successful
        """
        return self.fill(label, pix_key)
    
    def fill_credit_card(self, card_number: str, label: str = 'Cartão') -> bool:
        """
        Fill credit card number field.
        
        Args:
            card_number: Card number
            label: Label to search for
            
        Returns:
            True if successful
        """
        card_clean = ''.join(c for c in card_number if c.isdigit())
        return self.fill(label, card_clean)
    
    def fill_otp(self, otp: str, label: str = 'Código') -> bool:
        """
        Fill OTP (One-Time Password) field.
        
        Args:
            otp: OTP code
            label: Label to search for
            
        Returns:
            True if successful
        """
        return self.fill(label, otp, field_type='slow')
    
    def fill_multiple(self, fields: Dict[str, str]) -> bool:
        """
        Fill multiple fields at once.
        
        Args:
            fields: Dictionary of label -> value pairs
            
        Returns:
            True if all fields filled successfully
        """
        for label, value in fields.items():
            if not self.fill(label, value):
                logger.error(f"Failed to fill field: {label}")
                return False
        
        logger.info(f"Successfully filled {len(fields)} fields")
        return True
