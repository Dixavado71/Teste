"""
Demo Fluxo JSON - dixUIAuto

Este script demonstra a execução de fluxos definidos em JSON:
- Carregar fluxo de arquivo
- Executar sequência de ações automaticamente
- Tratamento de erros e retries
- Relatórios de execução
"""

import sys
import os
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import DixEngine
from config import (
    APP_PACKAGE,
    DEVICE_ID,
    DEBUG_MODE,
    FLOWS_DIR,
    MAX_RETRIES
)


class FlowReporter:
    """Gera relatórios de execução de fluxos."""
    
    def __init__(self, flow_name: str):
        self.flow_name = flow_name
        self.start_time = datetime.now()
        self.steps = []
        self.errors = []
        
    def log_step(self, step_index: int, action: str, status: str, details: str = ""):
        """Registra um passo executado."""
        self.steps.append({
            'index': step_index,
            'action': action,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
    def log_error(self, step_index: int, error: str):
        """Registra um erro."""
        self.errors.append({
            'step': step_index,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
        
    def generate_report(self) -> dict:
        """Gera relatório final."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        success_count = sum(1 for s in self.steps if s['status'] == 'SUCCESS')
        fail_count = sum(1 for s in self.steps if s['status'] == 'FAILED')
        skip_count = sum(1 for s in self.steps if s['status'] == 'SKIPPED')
        
        return {
            'flow_name': self.flow_name,
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'total_steps': len(self.steps),
            'success': success_count,
            'failed': fail_count,
            'skipped': skip_count,
            'errors': len(self.errors),
            'steps': self.steps,
            'error_details': self.errors
        }
        
    def print_summary(self, report: dict):
        """Imprime resumo do relatório."""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE EXECUÇÃO")
        print("="*60)
        print(f"Fluxo: {report['flow_name']}")
        print(f"Duração: {report['duration_seconds']:.2f} segundos")
        print(f"\nResultados:")
        print(f"  ✅ Sucesso: {report['success']}")
        print(f"  ❌ Falhas: {report['failed']}")
        print(f"  ⏭️  Pulados: {report['skipped']}")
        print(f"  📋 Total: {report['total_steps']}")
        
        if report['errors'] > 0:
            print(f"\n⚠️  Erros ({report['errors']}):")
            for err in report['error_details'][:5]:  # Mostra até 5 erros
                print(f"   Passo {err['step']}: {err['error']}")
        
        print("="*60)


def carregar_fluxo(caminho: str) -> list:
    """Carrega um fluxo JSON do arquivo."""
    print(f"\n📄 Carregando fluxo: {caminho}")
    
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            fluxo = json.load(f)
        
        print(f"✅ Fluxo carregado com {len(fluxo)} ações")
        return fluxo
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {caminho}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao parsear JSON: {str(e)}")
        return None


def executar_acao(engine: DixEngine, acao: dict) -> bool:
    """Executa uma única ação do fluxo."""
    action_type = acao.get('action', '')
    description = acao.get('description', 'Sem descrição')
    
    print(f"   → {action_type.upper()}: {description}")
    
    try:
        if action_type == 'click':
            params = {k: v for k, v in acao.items() if k not in ['action', 'description']}
            return engine.click(**params)
            
        elif action_type == 'wait':
            timeout = acao.get('timeout', 5)
            params = {k: v for k, v in acao.items() 
                     if k not in ['action', 'description', 'timeout'] and k != 'timeout'}
            if params:
                return engine.wait(**params, timeout=timeout)
            else:
                time.sleep(timeout)
                return True
                
        elif action_type == 'fill':
            params = {k: v for k, v in acao.items() if k not in ['action', 'description']}
            resultado = engine.form.fill(**params)
            return resultado.get('success', False)
            
        elif action_type == 'swipe':
            direction = acao.get('direction', 'up')
            percent = acao.get('percent', 0.5)
            return engine.gestures.swipe(direction=direction, percent=percent)
            
        elif action_type == 'scroll':
            direction = acao.get('direction', 'down')
            steps = acao.get('steps', 10)
            return engine.gestures.scroll(direction=direction, steps=steps)
            
        elif action_type == 'screenshot':
            name = acao.get('name', f'screenshot_{int(time.time())}')
            caminho = engine.screenshot(name)
            return caminho is not None
            
        elif action_type == 'validate':
            params = {k: v for k, v in acao.items() if k not in ['action', 'description']}
            resultado = engine.validator.validate(**params)
            return resultado.get('valid', False)
            
        elif action_type == 'open':
            package = acao.get('package', '')
            return engine.open(package)
            
        elif action_type == 'shell':
            command = acao.get('command', '')
            result = engine.device.shell(command)
            return result is not None
            
        elif action_type == 'back':
            engine.device.back()
            return True
            
        elif action_type == 'home':
            engine.device.home()
            return True
            
        else:
            print(f"   ⚠️ Ação desconhecida: {action_type}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        return False


def executar_fluxo(engine: DixEngine, fluxo: list, reporter: FlowReporter, 
                   max_retries: int = MAX_RETRIES) -> bool:
    """Executa todo o fluxo com tratamento de erros."""
    
    print("\n" + "="*60)
    print("▶️  INICIANDO EXECUÇÃO DO FLUXO")
    print("="*60)
    
    total_steps = len(fluxo)
    
    for index, acao in enumerate(fluxo, 1):
        print(f"\n[{index}/{total_steps}] ", end="")
        
        tentativas = 0
        sucesso = False
        
        while tentativas < max_retries and not sucesso:
            if tentativas > 0:
                print(f"   🔄 Tentativa {tentativas + 1}/{max_retries}")
            
            sucesso = executar_acao(engine, acao)
            
            if not sucesso:
                tentativas += 1
                if tentativas < max_retries:
                    time.sleep(1)  # Delay antes de retry
                    
        # Registra no reporter
        action_type = acao.get('action', 'unknown')
        description = acao.get('description', '')
        
        if sucesso:
            reporter.log_step(index, action_type, 'SUCCESS', description)
            print(f"   ✅ OK")
        else:
            reporter.log_step(index, action_type, 'FAILED', description)
            reporter.log_error(index, f"Falha na ação {action_type}: {description}")
            print(f"   ❌ FALHA")
            
            # Verifica se deve continuar ou parar
            stop_on_error = acao.get('stop_on_error', True)
            if stop_on_error:
                print(f"   ⚠️  Parando fluxo devido ao erro")
                return False
    
    return True


def demonstrar_tipos_acao():
    """Mostra todos os tipos de ação suportados."""
    print("\n" + "="*60)
    print("📋 TIPOS DE AÇÃO SUPORTADOS")
    print("="*60)
    
    acoes = {
        'click': 'Clica em elemento (text, desc, resourceId, etc.)',
        'wait': 'Espera por elemento ou tempo determinado',
        'fill': 'Preenche campo de formulário',
        'swipe': 'Desliza tela (up, down, left, right)',
        'scroll': 'Rola lista ou scrollview',
        'screenshot': 'Captura screenshot da tela',
        'validate': 'Valida elemento ou texto na tela',
        'open': 'Abre aplicativo pelo package',
        'shell': 'Executa comando ADB shell',
        'back': 'Volta tela anterior',
        'home': 'Vai para tela home',
        'long_click': 'Clique longo em elemento',
        'double_click': 'Duplo clique em elemento',
        'input': 'Digita texto em campo',
        'clear': 'Limpa campo de texto',
    }
    
    for acao, descricao in acoes.items():
        print(f"  • {acao:15} - {descricao}")


def main():
    """Função principal do demo de fluxo JSON."""
    print("\n" + "="*60)
    print("🤖 DIXUIAUTO - DEMO FLUXO JSON")
    print("="*60)
    print("Este demo mostra execução de fluxos definidos em JSON")
    
    # Inicializa a engine
    engine = DixEngine(debug=DEBUG_MODE)
    
    # Conecta ao dispositivo
    print("\n🔌 Conectando ao dispositivo...")
    try:
        if DEVICE_ID:
            engine.connect(device_id=DEVICE_ID)
        else:
            engine.connect()
        print("✅ Conexão estabelecida!")
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        print("\n⚠️  Para este demo, é necessário um dispositivo conectado.")
        return
    
    # Mostra tipos de ação
    demonstrar_tipos_acao()
    
    # Lista fluxos disponíveis
    print("\n" + "="*60)
    print("📁 FLUXOS DISPONÍVEIS")
    print("="*60)
    
    fluxos_disponiveis = []
    flows_dir = os.path.join(os.path.dirname(__file__), FLOWS_DIR)
    
    if os.path.exists(flows_dir):
        for arquivo in os.listdir(flows_dir):
            if arquivo.endswith('.json'):
                caminho_completo = os.path.join(flows_dir, arquivo)
                fluxos_disponiveis.append({
                    'nome': arquivo.replace('.json', ''),
                    'caminho': caminho_completo
                })
                print(f"  • {arquivo}")
    else:
        print(f"  ⚠️ Diretório de fluxos não encontrado: {flows_dir}")
    
    if not fluxos_disponiveis:
        print("\n⚠️  Nenhum fluxo JSON encontrado.")
        print("   Crie arquivos .json no diretório 'flows/'")
        return
    
    # Seleciona fluxo para executar
    print("\n" + "="*60)
    print("EXECUTANDO FLUXO DE EXEMPLO")
    print("="*60)
    
    # Usa o primeiro fluxo disponível
    fluxo_selecionado = fluxos_disponiveis[0]
    print(f"\n📋 Fluxo: {fluxo_selecionado['nome']}")
    
    # Carrega o fluxo
    fluxo = carregar_fluxo(fluxo_selecionado['caminho'])
    
    if not fluxo:
        print("❌ Não foi possível carregar o fluxo")
        return
    
    # Abre aplicativo (se especificado no config)
    if APP_PACKAGE and APP_PACKAGE != "com.example.app":
        print(f"\n🚀 Abrindo aplicativo: {APP_PACKAGE}")
        try:
            engine.open(APP_PACKAGE)
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Erro ao abrir app: {str(e)}")
    
    # Cria reporter
    reporter = FlowReporter(fluxo_selecionado['nome'])
    
    # Executa o fluxo
    sucesso = executar_fluxo(engine, fluxo, reporter)
    
    # Gera relatório
    report = reporter.generate_report()
    reporter.print_summary(report)
    
    # Salva relatório em arquivo
    relatorio_path = f"relatorio_{fluxo_selecionado['nome']}_{int(time.time())}.json"
    try:
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Relatório salvo em: {relatorio_path}")
    except Exception as e:
        print(f"\n⚠️ Não foi possível salvar relatório: {str(e)}")
    
    # Resumo final
    print("\n" + "="*60)
    print("✅ DEMO FLUXO JSON CONCLUÍDO")
    print("="*60)
    print("""
Para criar seus próprios fluxos:

1. Crie arquivo JSON em flows/
2. Defina sequência de ações
3. Execute com: engine.flow.execute('flows/seu_fluxo.json')

Ações disponíveis: click, wait, fill, swipe, scroll, 
                   screenshot, validate, open, shell, back, home
    """)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        import traceback
        traceback.print_exc()
