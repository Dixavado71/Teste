"""
Cache Engine - Gerenciamento inteligente de cache de UI
"""
import hashlib
import json
import os
import time
from typing import Optional, Dict, Any
from lib.logs import logger
from lib.exceptions import CacheError
from config.settings import CACHE_ENABLED, CACHE_TTL, CACHE_MAX_SIZE, CACHE_DIR


class UICache:
    """Gerencia cache da interface para evitar dumps desnecessários."""
    
    def __init__(self):
        self.log = logger.get_logger("Cache")
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._current_hash: Optional[str] = None
        self.enabled = CACHE_ENABLED
        
        # Garantir diretório de cache
        os.makedirs(CACHE_DIR, exist_ok=True)
    
    def _compute_hash(self, xml_content: str) -> str:
        """Computa hash SHA256 do conteúdo XML."""
        return hashlib.sha256(xml_content.encode('utf-8')).hexdigest()
    
    def _is_expired(self, key: str) -> bool:
        """Verifica se entrada do cache expirou."""
        if key not in self._timestamps:
            return True
        age = time.time() - self._timestamps[key]
        return age > CACHE_TTL
    
    def _cleanup(self):
        """Remove entradas expiradas e excedentes."""
        now = time.time()
        expired_keys = [
            k for k, ts in self._timestamps.items()
            if now - ts > CACHE_TTL
        ]
        
        for key in expired_keys:
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
        
        # Limitar tamanho máximo
        while len(self._cache) > CACHE_MAX_SIZE:
            oldest_key = min(self._timestamps, key=self._timestamps.get)
            self._cache.pop(oldest_key, None)
            self._timestamps.pop(oldest_key, None)
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache."""
        if not self.enabled:
            return None
        
        if key not in self._cache:
            return None
        
        if self._is_expired(key):
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any):
        """Armazena valor no cache."""
        if not self.enabled:
            return
        
        self._cleanup()
        self._cache[key] = value
        self._timestamps[key] = time.time()
        self.log.debug(f"Cache set: {key}")
    
    def invalidate(self, key: str = None):
        """Invalida cache específico ou todo o cache."""
        if key:
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
            self.log.debug(f"Cache invalidado: {key}")
        else:
            self._cache.clear()
            self._timestamps.clear()
            self._current_hash = None
            self.log.info("Cache completo invalidado")
    
    def has_changed(self, xml_content: str) -> bool:
        """Verifica se a UI mudou comparando hashes."""
        if not self.enabled:
            return True
        
        new_hash = self._compute_hash(xml_content)
        has_changed = self._current_hash != new_hash
        
        if has_changed:
            self._current_hash = new_hash
            self.log.debug("UI mudou - novo hash detectado")
        else:
            self.log.debug("UI inalterada - usando cache")
        
        return has_changed
    
    def save_to_file(self, filename: str, data: Dict):
        """Salva dados em arquivo de cache."""
        filepath = os.path.join(CACHE_DIR, f"{filename}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.log.debug(f"Cache salvo em: {filepath}")
        except Exception as e:
            raise CacheError(f"Falha ao salvar cache: {e}")
    
    def load_from_file(self, filename: str) -> Optional[Dict]:
        """Carrega dados de arquivo de cache."""
        filepath = os.path.join(CACHE_DIR, f"{filename}.json")
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.log.debug(f"Cache carregado de: {filepath}")
            return data
        except Exception as e:
            self.log.warning(f"Falha ao carregar cache: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do cache."""
        return {
            "entries": len(self._cache),
            "enabled": self.enabled,
            "ttl": CACHE_TTL,
            "max_size": CACHE_MAX_SIZE,
            "current_hash": self._current_hash[:8] + "..." if self._current_hash else None
        }
