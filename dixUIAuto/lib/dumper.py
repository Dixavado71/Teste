"""
XML Dumper - Obtém e gerencia dumps da interface
"""
import os
import time
from typing import Optional, Tuple
from lib.adb_bridge import ADBBridge
from lib.parser import XMLParser, UINode
from lib.cache import UICache
from lib.logs import logger
from config.settings import DUMPS_DIR


class Dumper:
    """Responsável por obter e gerenciar dumps da UI."""
    
    def __init__(self, adb: ADBBridge):
        self.adb = adb
        self.log = logger.get_logger("Dumper")
        self.parser = XMLParser()
        self.cache = UICache()
        self._current_xml: Optional[str] = None
        self._current_root: Optional[UINode] = None
        self._last_dump_time: float = 0
    
    def dump(self, use_cache: bool = True) -> Tuple[bool, UINode]:
        """
        Realiza dump da interface atual.
        
        Args:
            use_cache: Se True, usa cache se UI não mudou
        
        Returns:
            Tuple de (mudou_ui, root_node)
        """
        remote_path = "/sdcard/ui_dump.xml"
        
        # Realizar dump no dispositivo
        if not self.adb.dump_ui(remote_path):
            raise Exception("Falha ao realizar dump da UI")
        
        # Baixar conteúdo do dump
        local_path = os.path.join(DUMPS_DIR, "current.xml")
        if not self.adb.pull(remote_path, local_path):
            raise Exception("Falha ao baixar dump da UI")
        
        # Ler conteúdo XML
        with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
            xml_content = f.read()
        
        # Verificar se UI mudou (usando cache)
        ui_changed = self.cache.has_changed(xml_content)
        
        if use_cache and not ui_changed and self._current_root:
            self.log.debug("UI inalterada, usando root do cache")
            return False, self._current_root
        
        # Parsear novo XML
        self._current_xml = xml_content
        self._current_root = self.parser.parse(xml_content)
        self._last_dump_time = time.time()
        
        # Salvar em cache
        self.cache.set("current_ui", {
            "xml": xml_content,
            "timestamp": self._last_dump_time,
            "summary": self.parser.get_tree_summary()
        })
        
        self.log.success(f"Dump realizado{'(UI mudou)' if ui_changed else '(cache)'}")
        return ui_changed, self._current_root
    
    def refresh(self) -> UINode:
        """Força refresh do dump da UI."""
        _, root = self.dump(use_cache=False)
        return root
    
    def get_current_tree(self) -> Optional[UINode]:
        """Retorna árvore UI atual (pode estar em cache)."""
        return self._current_root
    
    def save_dump(self, filename: str = None) -> str:
        """Salva dump atual em arquivo."""
        if not self._current_xml:
            raise Exception("Nenhum dump disponível")
        
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"dump_{timestamp}.xml"
        
        filepath = os.path.join(DUMPS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self._current_xml)
        
        self.log.info(f"Dump salvo em: {filepath}")
        return filepath
    
    def load_dump(self, filepath: str) -> UINode:
        """Carrega dump de arquivo."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        self._current_xml = xml_content
        self._current_root = self.parser.parse(xml_content)
        
        self.log.info(f"Dump carregado de: {filepath}")
        return self._current_root
    
    def get_summary(self) -> dict:
        """Retorna resumo da UI atual."""
        if not self._current_root:
            return {}
        return self.parser.get_tree_summary()
    
    @property
    def last_update(self) -> float:
        """Retorna timestamp da última atualização."""
        return self._last_dump_time
