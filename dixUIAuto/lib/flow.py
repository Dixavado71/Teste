"""
Flow Engine - Execução de fluxos JSON
"""
import json
import time
from typing import List, Dict, Optional
from pathlib import Path
from lib.logs import logger
from lib.exceptions import FlowError
from lib.actions import create_action, ACTION_MAP


class FlowEngine:
    """Executa fluxos definidos em JSON."""
    
    def __init__(self, engine):
        self.engine = engine
        self.log = logger.get_logger("Flow")
        self._current_flow: List[Dict] = []
        self._step_count = 0
        self._success_count = 0
    
    def load(self, flow_path: str) -> List[Dict]:
        """Carrega fluxo de arquivo JSON."""
        path = Path(flow_path)
        if not path.exists():
            # Tentar no diretório de flows
            from config.settings import FLOWS_DIR
            path = Path(FLOWS_DIR) / flow_path
            if not path.exists():
                path = Path(FLOWS_DIR) / f"{flow_path}.json"
        
        if not path.exists():
            raise FileNotFoundError(f"Flow não encontrado: {flow_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            self._current_flow = json.load(f)
        
        self.log.info(f"Flow carregado: {path.name} ({len(self._current_flow)} passos)")
        return self._current_flow
    
    def load_from_dict(self, flow_data: List[Dict]) -> List[Dict]:
        """Carrega fluxo de dicionário."""
        self._current_flow = flow_data
        self.log.info(f"Flow carregado ({len(flow_data)} passos)")
        return flow_data
    
    def execute(self, flow: List[Dict] = None, 
                stop_on_error: bool = False) -> bool:
        """
        Executa fluxo completo.
        
        Args:
            flow: Lista de ações (opcional, usa flow carregado)
            stop_on_error: Para execução no primeiro erro
        """
        if flow:
            self._current_flow = flow
        
        if not self._current_flow:
            raise FlowError("Nenhum flow carregado")
        
        self._step_count = len(self._current_flow)
        self._success_count = 0
        
        self.log.info(f"Iniciando execução do flow ({self._step_count} passos)")
        
        for i, step in enumerate(self._current_flow, 1):
            action_type = step.get("action", "").lower()
            
            if not action_type:
                self.log.warning(f"Passo {i}: ação vazia, pulando")
                continue
            
            self.log.info(f"Passo {i}/{self._step_count}: {action_type}")
            
            try:
                action = create_action(action_type, **{
                    k: v for k, v in step.items() if k != "action"
                })
                
                if not action:
                    self.log.error(f"Ação desconhecida: {action_type}")
                    if stop_on_error:
                        return False
                    continue
                
                success = action.execute(self.engine)
                
                if success:
                    self._success_count += 1
                    self.log.success(f"Passo {i} concluído")
                else:
                    self.log.error(f"Passo {i} falhou")
                    if stop_on_error:
                        return False
                
                # Pequeno delay entre ações
                time.sleep(0.3)
                
            except Exception as e:
                self.log.error(f"Erro no passo {i}: {e}")
                if stop_on_error:
                    raise FlowError(f"Erro no passo {i}: {e}")
        
        all_success = self._success_count == self._step_count
        if all_success:
            self.log.success(f"Flow executado com sucesso ({self._success_count}/{self._step_count})")
        else:
            self.log.warning(f"Flow parcial ({self._success_count}/{self._step_count})")
        
        return all_success
    
    def run(self, flow_path: str, stop_on_error: bool = False) -> bool:
        """Carrega e executa fluxo."""
        self.load(flow_path)
        return self.execute(stop_on_error=stop_on_error)
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas da última execução."""
        return {
            "total_steps": self._step_count,
            "successful": self._success_count,
            "failed": self._step_count - self._success_count,
            "success_rate": self._success_count / self._step_count if self._step_count else 0
        }
