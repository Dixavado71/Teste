"""
dixUIAuto - Premium GUI Interface
Interface gráfica moderna e estilosa para automação Android.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Import settings
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import Settings, settings

# Configure appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class DevicePanel(ctk.CTkFrame):
    """Painel de gerenciamento de dispositivos."""
    
    def __init__(self, master, engine_callback=None):
        super().__init__(master)
        self.engine_callback = engine_callback
        
        self.grid_columnconfigure(0, weight=1)
        
        # Título
        self.title_label = ctk.CTkLabel(
            self, 
            text="📱 Dispositivos", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Lista de dispositivos
        self.device_list = ctk.CTkTextbox(self, height=150, state="disabled")
        self.device_list.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Botões
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        self.refresh_btn = ctk.CTkButton(
            btn_frame, 
            text="🔄 Atualizar", 
            command=self.refresh_devices,
            width=100
        )
        self.refresh_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.connect_btn = ctk.CTkButton(
            btn_frame, 
            text="🔗 Conectar", 
            command=self.connect_device,
            width=100
        )
        self.connect_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Status
        self.status_label = ctk.CTkLabel(
            self, 
            text="Status: Desconectado", 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
    
    def refresh_devices(self):
        """Atualiza lista de dispositivos."""
        self.device_list.configure(state="normal")
        self.device_list.delete("0.0", "end")
        self.device_list.insert("0.0", "Buscando dispositivos...\n")
        self.device_list.configure(state="disabled")
        
        if self.engine_callback:
            try:
                devices = self.engine_callback('list_devices')
                self.device_list.configure(state="normal")
                self.device_list.delete("0.0", "end")
                if devices:
                    for dev in devices:
                        self.device_list.insert("end", f"{dev}\n")
                else:
                    self.device_list.insert("0.0", "Nenhum dispositivo encontrado.\n")
                self.device_list.configure(state="disabled")
            except Exception as e:
                self.device_list.configure(state="normal")
                self.device_list.delete("0.0", "end")
                self.device_list.insert("0.0", f"Erro: {str(e)}\n")
                self.device_list.configure(state="disabled")
    
    def connect_device(self):
        """Conecta ao dispositivo selecionado."""
        messagebox.showinfo("Conectar", "Funcionalidade de conexão em desenvolvimento.")
    
    def update_status(self, status: str, connected: bool = False):
        """Atualiza status da conexão."""
        color = "#00ff00" if connected else "gray"
        self.status_label.configure(text=f"Status: {status}", text_color=color)


class DashboardPanel(ctk.CTkFrame):
    """Painel dashboard com status e métricas."""
    
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        # Título
        self.title_label = ctk.CTkLabel(
            self, 
            text="📊 Dashboard", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="w")
        
        # Cards de status
        self.connection_card = self._create_card(0, 0, "🔗 Conexão", "Desconectado")
        self.app_card = self._create_card(0, 1, "📱 App", "Nenhum")
        self.actions_card = self._create_card(0, 2, "⚡ Ações", "0")
        
        # Log de atividades recentes
        self.log_label = ctk.CTkLabel(
            self, 
            text="📝 Atividades Recentes", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.log_label.grid(row=1, column=0, columnspan=3, padx=10, pady=(20, 5), sticky="w")
        
        self.activity_log = ctk.CTkTextbox(self, height=150, state="disabled")
        self.activity_log.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
    
    def _create_card(self, row: int, col: int, title: str, value: str) -> ctk.CTkFrame:
        """Cria um card de status."""
        card = ctk.CTkFrame(self, corner_radius=10, fg_color="#2b2b2b")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            card, 
            text=title, 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        value_label = ctk.CTkLabel(
            card, 
            text=value, 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00ccff"
        )
        value_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")
        
        return card
    
    def update_connection(self, status: str):
        """Atualiza status de conexão."""
        widget = self.connection_card.winfo_children()[1]
        widget.configure(text=status)
        self._log_activity(f"Conexão: {status}")
    
    def update_app(self, app_name: str):
        """Atualiza nome do app."""
        widget = self.app_card.winfo_children()[1]
        widget.configure(text=app_name[:20])
        self._log_activity(f"App: {app_name}")
    
    def update_actions(self, count: int):
        """Atualiza contador de ações."""
        widget = self.actions_card.winfo_children()[1]
        widget.configure(text=str(count))
    
    def _log_activity(self, message: str):
        """Registra atividade no log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.configure(state="normal")
        self.activity_log.insert("end", f"[{timestamp}] {message}\n")
        self.activity_log.see("end")
        self.activity_log.configure(state="disabled")


class FlowBuilderPanel(ctk.CTkFrame):
    """Construtor visual de flows."""
    
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Título
        self.title_label = ctk.CTkLabel(
            self, 
            text="🔧 Construtor de Flows", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Lista de ações
        self.actions_listbox = ctk.CTkTextbox(self, state="disabled")
        self.actions_listbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # Formulário de nova ação
        form_frame = ctk.CTkFrame(self)
        form_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Tipo de ação
        ctk.CTkLabel(form_frame, text="Ação:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.action_type = ctk.CTkComboBox(
            form_frame, 
            values=["click", "fill", "wait", "swipe", "scroll", "screenshot", "open_app", "press_back", "press_home"],
            width=150
        )
        self.action_type.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.action_type.set("click")
        
        # Parâmetro texto
        ctk.CTkLabel(form_frame, text="Texto:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.text_param = ctk.CTkEntry(form_frame, placeholder_text="Texto do elemento")
        self.text_param.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Parâmetro description
        ctk.CTkLabel(form_frame, text="Desc:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.desc_param = ctk.CTkEntry(form_frame, placeholder_text="Content description")
        self.desc_param.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Parâmetro resource-id
        ctk.CTkLabel(form_frame, text="Resource ID:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.resource_param = ctk.CTkEntry(form_frame, placeholder_text="resource-id")
        self.resource_param.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # Parâmetro valor (para fill)
        ctk.CTkLabel(form_frame, text="Valor:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.value_param = ctk.CTkEntry(form_frame, placeholder_text="Valor para preencher")
        self.value_param.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        
        # Botões
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        self.add_btn = ctk.CTkButton(
            btn_frame, 
            text="➕ Adicionar Ação", 
            command=self.add_action,
            width=150
        )
        self.add_btn.pack(side="left", padx=5)
        
        self.remove_btn = ctk.CTkButton(
            btn_frame, 
            text="🗑️ Remover Selecionada", 
            command=self.remove_action,
            width=150
        )
        self.remove_btn.pack(side="left", padx=5)
        
        self.export_btn = ctk.CTkButton(
            btn_frame, 
            text="💾 Exportar JSON", 
            command=self.export_flow,
            width=150,
            fg_color="#00cc66"
        )
        self.export_btn.pack(side="right", padx=5)
        
        self.clear_btn = ctk.CTkButton(
            btn_frame, 
            text="🧹 Limpar Tudo", 
            command=self.clear_actions,
            width=150,
            fg_color="#cc3300"
        )
        self.clear_btn.pack(side="right", padx=5)
        
        # Lista de ações
        self.actions: List[Dict[str, Any]] = []
    
    def add_action(self):
        """Adiciona uma ação à lista."""
        action_type = self.action_type.get()
        action = {"action": action_type}
        
        if text := self.text_param.get():
            action["text"] = text
        if desc := self.desc_param.get():
            action["desc"] = desc
        if resource := self.resource_param.get():
            action["resourceId"] = resource
        if value := self.value_param.get():
            action["value"] = value
        
        self.actions.append(action)
        self._update_listbox()
        
        # Limpar campos
        self.text_param.delete(0, 'end')
        self.desc_param.delete(0, 'end')
        self.resource_param.delete(0, 'end')
        self.value_param.delete(0, 'end')
    
    def remove_action(self):
        """Remove ação selecionada."""
        # Implementação simplificada - remove última
        if self.actions:
            self.actions.pop()
            self._update_listbox()
    
    def clear_actions(self):
        """Limpa todas as ações."""
        self.actions = []
        self._update_listbox()
    
    def export_flow(self):
        """Exporta flow para JSON."""
        if not self.actions:
            messagebox.showwarning("Aviso", "Nenhuma ação para exportar!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialdir=settings.FLOWS_DIR
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.actions, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Sucesso", f"Flow exportado para:\n{file_path}")
    
    def _update_listbox(self):
        """Atualiza lista de ações."""
        self.actions_listbox.configure(state="normal")
        self.actions_listbox.delete("0.0", "end")
        
        for i, action in enumerate(self.actions):
            action_str = f"{i+1}. {action['action']}"
            if 'text' in action:
                action_str += f" (text='{action['text']}')"
            if 'desc' in action:
                action_str += f" (desc='{action['desc']}')"
            if 'value' in action:
                action_str += f" (value='{action['value']}')"
            
            self.actions_listbox.insert("end", action_str + "\n")
        
        self.actions_listbox.configure(state="disabled")


class QuickActionsPanel(ctk.CTkFrame):
    """Painel de ações rápidas."""
    
    def __init__(self, master, action_callback=None):
        super().__init__(master)
        self.action_callback = action_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        # Título
        self.title_label = ctk.CTkLabel(
            self, 
            text="⚡ Ações Rápidas", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="w")
        
        # Botões de ações
        actions = [
            ("🏠 Home", "home"),
            ("↩️ Back", "back"),
            ("📷 Screenshot", "screenshot"),
            ("🔄 Refresh UI", "refresh"),
            ("📋 Clipboard", "clipboard"),
            ("🔍 Inspector", "inspector"),
        ]
        
        for i, (text, action_name) in enumerate(actions):
            row = i // 3
            col = i % 3
            
            btn = ctk.CTkButton(
                self, 
                text=text, 
                command=lambda a=action_name: self._execute_action(a),
                height=40
            )
            btn.grid(row=row+1, column=col, padx=5, pady=5, sticky="ew")
    
    def _execute_action(self, action_name: str):
        """Executa ação rápida."""
        if self.action_callback:
            try:
                self.action_callback(action_name)
            except Exception as e:
                messagebox.showerror("Erro", f"Falha na ação: {str(e)}")


class PremiumGUI(ctk.CTk):
    """Interface gráfica principal premium."""
    
    def __init__(self):
        super().__init__()
        
        self.title("dixUIAuto - Premium GUI")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Frame principal com scroll
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        
        # Coluna esquerda
        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)
        
        self.device_panel = DevicePanel(left_frame)
        self.device_panel.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.quick_actions = QuickActionsPanel(left_frame)
        self.quick_actions.grid(row=1, column=0, sticky="ew")
        
        # Coluna direita
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=2)
        
        self.dashboard = DashboardPanel(right_frame)
        self.dashboard.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.flow_builder = FlowBuilderPanel(right_frame)
        self.flow_builder.grid(row=1, column=0, sticky="nsew")
        
        # Menu
        self._create_menu()
        
        # Status bar
        self.status_bar = ctk.CTkLabel(
            self, 
            text="dixUIAuto v2.0 | Pronto para usar", 
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
    
    def _create_menu(self):
        """Cria menu principal."""
        menubar = ctk.CTkFrame(self, height=40)
        menubar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        
        # Botões do menu
        buttons = [
            ("📁 Abrir Flow", self._open_flow),
            ("▶️ Executar", self._execute_flow),
            ("⚙️ Configurações", self._show_settings),
            ("❓ Ajuda", self._show_help),
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(
                menubar, 
                text=text, 
                command=command,
                width=120,
                height=30
            )
            btn.pack(side="left", padx=5, pady=5)
    
    def _open_flow(self):
        """Abre arquivo de flow."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            initialdir=settings.FLOWS_DIR
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    flow = json.load(f)
                messagebox.showinfo("Sucesso", f"Flow carregado: {len(flow)} ações")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar flow: {str(e)}")
    
    def _execute_flow(self):
        """Executa flow atual."""
        messagebox.showinfo("Executar", "Funcionalidade de execução em desenvolvimento.")
    
    def _show_settings(self):
        """Mostra configurações."""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Configurações")
        settings_window.geometry("600x400")
        
        label = ctk.CTkLabel(
            settings_window, 
            text="Configurações do dixUIAuto\n\nEm desenvolvimento...", 
            font=ctk.CTkFont(size=16)
        )
        label.pack(pady=50)
    
    def _show_help(self):
        """Mostra ajuda."""
        help_window = ctk.CTkToplevel(self)
        help_window.title("Ajuda")
        help_window.geometry("700x500")
        
        help_text = """
        dixUIAuto - Guia Rápido
        
        1. Conecte seu dispositivo Android via USB
        2. Habilite a depuração USB no dispositivo
        3. Clique em "🔄 Atualizar" para listar dispositivos
        4. Selecione e conecte ao dispositivo
        5. Use o Construtor de Flows para criar automações
        6. Exporte o flow como JSON
        7. Execute com a engine do dixUIAuto
        
        Ações Suportadas:
        - click: Clica em elemento por texto/desc/resourceId
        - fill: Preenche campo com valor
        - wait: Aguarda elemento aparecer
        - swipe: Desliza tela
        - scroll: Rola lista
        - screenshot: Captura tela
        - open_app: Abre aplicativo
        - press_back: Volta tela
        - press_home: Vai para home
        
        Para mais informações, consulte a documentação.
        """
        
        text_box = ctk.CTkTextbox(help_window)
        text_box.pack(fill="both", expand=True, padx=20, pady=20)
        text_box.insert("0.0", help_text)
        text_box.configure(state="disabled")


def main():
    """Função principal."""
    try:
        app = PremiumGUI()
        app.mainloop()
    except Exception as e:
        print(f"❌ Erro ao iniciar GUI: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
