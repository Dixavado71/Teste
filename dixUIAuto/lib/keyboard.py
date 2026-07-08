"""
Keyboard Engine - Entrada de texto e controle de teclado
"""
import time
from typing import Optional
from lib.parser import UINode
from lib.adb_bridge import ADBBridge
from lib.logs import logger
from config.constants import KEY_CODES


class Keyboard:
    """Responsável pela entrada de texto e controle do teclado."""
    
    def __init__(self, adb: ADBBridge):
        self.adb = adb
        self.log = logger.get_logger("Keyboard")
    
    def send_keys(self, text: str, node: UINode = None) -> bool:
        """
        Digita texto no elemento ou foco atual.
        
        Args:
            text: Texto a ser digitado
            node: Elemento opcional para clicar antes de digitar
        """
        if node:
            from lib.clicker import Clicker
            clicker = Clicker(self.adb)
            clicker.click(node)
            time.sleep(0.3)
        
        self.log.info(f"Digitando: {text[:20]}{'...' if len(text) > 20 else ''}")
        return self.adb.input_text(text)
    
    def clear(self, node: UINode = None) -> bool:
        """
        Limpa campo de input.
        
        Args:
            node: Elemento EditText opcional
        """
        if node:
            from lib.clicker import Clicker
            clicker = Clicker(self.adb)
            clicker.click(node)
            time.sleep(0.3)
        
        self.log.info("Limpando campo...")
        
        # Selecionar todo o texto (Ctrl+A via keycode não funciona bem em Android)
        # Estratégia: long press + select all + delete
        if node:
            x, y = node.center
            # Long press para selecionar
            self.adb.input_swipe(x, y, x, y, 800)
            time.sleep(0.5)
        
        # Enviar múltiplos backspaces
        for _ in range(50):
            self.adb.input_keyevent(KEY_CODES["BACKSPACE"])
            time.sleep(0.02)
        
        return True
    
    def paste(self, text: str = None) -> bool:
        """
        Cola texto da área de transferência.
        Nota: Requer que o texto já esteja no clipboard do dispositivo.
        """
        self.log.info("Colando texto...")
        # Emular Ctrl+V (keycode 179 em alguns dispositivos)
        return self.adb.input_keyevent(179)
    
    def enter(self) -> bool:
        """Envia tecla Enter."""
        self.log.debug("Enviando Enter")
        return self.adb.input_keyevent(KEY_CODES["ENTER"])
    
    def backspace(self, count: int = 1) -> bool:
        """
        Envia tecla Backspace.
        
        Args:
            count: Número de vezes para pressionar
        """
        self.log.debug(f"Enviando {count}x Backspace")
        for _ in range(count):
            self.adb.input_keyevent(KEY_CODES["BACKSPACE"])
            time.sleep(0.05)
        return True
    
    def delete(self) -> bool:
        """Alias para backspace."""
        return self.backspace()
    
    def hide_keyboard(self) -> bool:
        """Tenta esconder o teclado virtual."""
        self.log.debug("Escondendo teclado")
        # Pressionar botão Back
        return self.adb.input_keyevent(KEY_CODES["BACK"])
    
    def press_key(self, key_name: str) -> bool:
        """
        Pressiona tecla especial por nome.
        
        Args:
            key_name: Nome da tecla (ENTER, BACKSPACE, TAB, etc.)
        """
        keycode = KEY_CODES.get(key_name.upper())
        if not keycode:
            raise ValueError(f"Tecla desconhecida: {key_name}")
        
        self.log.debug(f"Pressionando {key_name}")
        return self.adb.input_keyevent(keycode)
    
    def fill_and_submit(self, text: str, node: UINode = None, 
                        submit_with_enter: bool = True) -> bool:
        """
        Preenche campo e submete.
        
        Args:
            text: Texto a preencher
            node: Elemento para clicar antes
            submit_with_enter: Se True, usa Enter; se False, usa botão Back
        """
        self.send_keys(text, node)
        time.sleep(0.3)
        
        if submit_with_enter:
            return self.enter()
        else:
            return self.hide_keyboard()
