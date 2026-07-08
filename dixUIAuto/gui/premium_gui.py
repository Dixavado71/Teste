"""
dixUIAuto GUI - Interface Gráfica Premium Dark
Interface moderna e estilosa para automação Android
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import json
import os
from datetime import datetime
from typing import Optional, List, Dict
import sys

# Adiciona o path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings
from lib.logs import get_logger

logger = get_logger(__name__)

# Configuração do tema premium dark
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class ThemeColors:
    """Cores premium para a interface"""
    BG_PRIMARY = "#1a1a2e"
    BG_SECONDARY = "#16213e"
    BG_TERTIARY = "#0f3460"
    ACCENT = "#e94560"
    ACCENT_HOVER = "#ff6b81"
    SUCCESS = "#00d26a"
    WARNING = "#ffc107"
    ERROR = "#dc3545"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0a0"
    BORDER = "#2a2a4e"
    CARD_BG = "#1f2937"


class DeviceCard(ctk.CTkFrame):
    """Card estiloso para exibição de dispositivo"""
    
    def __init__(self, parent, device_info: dict, on_select=None):
        super().__init__(parent, fg_color=ThemeColors.CARD_BG, 
                        corner_radius=12, border_width=2,
                        border_color=ThemeColors.BORDER)
        
        self.device_info = device_info
        self.on_select = on_select
        self.selected = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Layout grid
        self.grid_columnconfigure(1, weight=1)
        
        # Ícone do dispositivo
        icon_label = ctk.CTkLabel(
            self, text="📱", font=ctk.CTkFont(size=24),
            width=50
        )
        icon_label.grid(row=0, column=0, padx=(15, 10), pady=15, rowspan=2)
        
        # Nome do dispositivo
        name_label = ctk.CTkLabel(
            self, text=self.device_info.get('name', 'Unknown'),
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ThemeColors.TEXT_PRIMARY,
            anchor="w"
        )
        name_label.grid(row=0, column=1, sticky="w", pady=(15, 5))
        
        # Status
        status = self.device_info.get('status', 'unknown')
        status_color = ThemeColors.SUCCESS if status == 'device' else ThemeColors.WARNING
        status_label = ctk.CTkLabel(
            self, text=f"● {status}",
            font=ctk.CTkFont(size=12),
            text_color=status_color,
            anchor="w"
        )
        status_label.grid(row=1, column=1, sticky="w", pady=(0, 15))
        
        # Botão de seleção
        self.select_btn = ctk.CTkButton(
            self, text="Selecionar", width=100, height=28,
            fg_color=ThemeColors.BG_TERTIARY,
            hover_color=ThemeColors.ACCENT,
            command=self._on_select
        )
        self.select_btn.grid(row=0, column=2, rowspan=2, padx=15, pady=15)
    
    def _on_select(self):
        if self.on_select:
            self.on_select(self.device_info)
    
    def set_selected(self, selected: bool):
        self.selected = selected
        if selected:
            self.configure(border_color=ThemeColors.ACCENT)
            self.select_btn.configure(text="Selecionado", fg_color=ThemeColors.ACCENT)
        else:
            self.configure(border_color=ThemeColors.BORDER)
            self.select_btn.configure(text="Selecionar", fg_color=ThemeColors.BG_TERTIARY)


class ActionBuilder(ctk.CTkFrame):
    """Construtor visual de ações para flows"""
    
    ACTION_TYPES = [
        "click", "long_click", "double_click",
        "fill", "swipe", "scroll", "wait",
        "assert_exists", "assert_text", "screenshot"
    ]
    
    LOCATOR_TYPES = ["text", "desc", "resource_id", "class_name", "xpath", "regex"]
    
    def __init__(self, parent, on_add_action=None):
        super().__init__(parent, fg_color=ThemeColors.CARD_BG,
                        corner_radius=12, border_width=1,
                        border_color=ThemeColors.BORDER)
        
        self.on_add_action = on_add_action
        self._setup_ui()
    
    def _setup_ui(self):
        # Título
        title = ctk.CTkLabel(
            self, text="🛠️ Construtor de Ações",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ThemeColors.TEXT_PRIMARY
        )
        title.pack(pady=(15, 10), padx=15, anchor="w")
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Tipo de ação
        ctk.CTkLabel(
            main_frame, text="Ação:",
            text_color=ThemeColors.TEXT_SECONDARY
        ).grid(row=0, column=0, padx=(0, 10), pady=10, sticky="w")
        
        self.action_type = ctk.CTkComboBox(
            main_frame, values=self.ACTION_TYPES,
            fg_color=ThemeColors.BG_TERTIARY,
            border_color=ThemeColors.BORDER,
            dropdown_fg_color=ThemeColors.BG_SECONDARY
        )
        self.action_type.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")
        self.action_type.set("click")
        
        # Localizador
        ctk.CTkLabel(
            main_frame, text="Localizar por:",
            text_color=ThemeColors.TEXT_SECONDARY
        ).grid(row=1, column=0, padx=(0, 10), pady=10, sticky="w")
        
        self.locator_type = ctk.CTkComboBox(
            main_frame, values=self.LOCATOR_TYPES,
            fg_color=ThemeColors.BG_TERTIARY,
            border_color=ThemeColors.BORDER,
            dropdown_fg_color=ThemeColors.BG_SECONDARY
        )
        self.locator_type.grid(row=1, column=1, padx=(0, 10), pady=10, sticky="ew")
        self.locator_type.set("text")
        
        # Valor do localizador
        ctk.CTkLabel(
            main_frame, text="Valor:",
            text_color=ThemeColors.TEXT_SECONDARY
        ).grid(row=2, column=0, padx=(0, 10), pady=10, sticky="w")
        
        self.locator_value = ctk.CTkEntry(
            main_frame, placeholder_text="Ex: Entrar, CPF, etc.",
            fg_color=ThemeColors.BG_TERTIARY,
            border_color=ThemeColors.BORDER,
            text_color=ThemeColors.TEXT_PRIMARY
        )
        self.locator_value.grid(row=2, column=1, padx=(0, 10), pady=10, sticky="ew")
        
        # Campo extra (para fill)
        ctk.CTkLabel(
            main_frame, text="Valor extra:",
            text_color=ThemeColors.TEXT_SECONDARY
        ).grid(row=3, column=0, padx=(0, 10), pady=10, sticky="w")
        
        self.extra_value = ctk.CTkEntry(
            main_frame, placeholder_text="Texto para preencher (fill)",
            fg_color=ThemeColors.BG_TERTIARY,
            border_color=ThemeColors.BORDER,
            text_color=ThemeColors.TEXT_PRIMARY
        )
        self.extra_value.grid(row=3, column=1, padx=(0, 10), pady=10, sticky="ew")
        
        # Tempo de espera
        ctk.CTkLabel(
            main_frame, text="Timeout (s):",
            text_color=ThemeColors.TEXT_SECONDARY
        ).grid(row=4, column=0, padx=(0, 10), pady=10, sticky="w")
        
        self.timeout = ctk.CTkEntry(
            main_frame, placeholder_text="10",
            fg_color=ThemeColors.BG_TERTIARY,
            border_color=ThemeColors.BORDER,
            text_color=ThemeColors.TEXT_PRIMARY,
            width=100
        )
        self.timeout.grid(row=4, column=1, padx=(0, 10), pady=10, sticky="w")
        self.timeout.insert(0, "10")
        
        # Botão adicionar
        add_btn = ctk.CTkButton(
            self, text="➕ Adicionar Ação",
            fg_color=ThemeColors.ACCENT,
            hover_color=ThemeColors.ACCENT_HOVER,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._add_action
        )
        add_btn.pack(pady=15, padx=15, fill="x")
    
    def _add_action(self):
        action_data = {
            "action": self.action_type.get(),
            "timeout": int(self.timeout.get() or 10)
        }
        
        locator_type = self.locator_type.get()
        locator_value = self.locator_value.get()
        
        if locator_value:
            action_data[locator_type] = locator_value
        
        if self.action_type.get() == "fill":
            action_data["value"] = self.extra_value.get()
        
        if self.on_add_action:
            self.on_add_action(action_data)
        
        # Limpar campos
        self.locator_value.delete(0, 'end')
        self.extra_value.delete(0, 'end')


class FlowEditor(ctk.CTkFrame):
    """Editor visual de flows com lista de ações"""
    
    def __init__(self, parent, on_export=None):
        super().__init__(parent, fg_color=ThemeColors.CARD_BG,
                        corner_radius=12, border_width=1,
                        border_color=ThemeColors.BORDER)
        
        self.actions: List[Dict] = []
        self.on_export = on_export
        self._setup_ui()
    
    def _setup_ui(self):
        # Título
        title = ctk.CTkLabel(
            self, text="📋 Editor de Flow",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ThemeColors.TEXT_PRIMARY
        )
        title.pack(pady=(15, 10), padx=15, anchor="w")
        
        # Lista de ações
        list_frame = ctk.CTkFrame(self, fg_color=ThemeColors.BG_TERTIARY,
                                  corner_radius=8)
        list_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.actions_listbox = ctk.CTkTextbox(
            list_frame, font=ctk.CTkFont(family="Consolas", size=11),
            text_color=ThemeColors.TEXT_PRIMARY,
            fg_color=ThemeColors.BG_TERTIARY,
            border_color=ThemeColors.BORDER
        )
        self.actions_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Contador
        self.counter_label = ctk.CTkLabel(
            self, text="0 ações",
            text_color=ThemeColors.TEXT_SECONDARY,
            font=ctk.CTkFont(size=12)
        )
        self.counter_label.pack(pady=(0, 10))
        
        # Botões de ação
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        clear_btn = ctk.CTkButton(
            btn_frame, text="🗑️ Limpar",
            fg_color=ThemeColors.ERROR,
            hover_color="#c82333",
            command=self._clear_actions
        )
        clear_btn.pack(side="left", padx=(0, 10))
        
        export_btn = ctk.CTkButton(
            btn_frame, text="💾 Exportar JSON",
            fg_color=ThemeColors.SUCCESS,
            hover_color="#00b359",
            command=self._export_flow
        )
        export_btn.pack(side="right")
    
    def add_action(self, action_data: Dict):
        self.actions.append(action_data)
        self._update_display()
    
    def _update_display(self):
        self.actions_listbox.delete("1.0", "end")
        
        for i, action in enumerate(self.actions, 1):
            action_str = f"{i}. {action['action']}"
            if 'text' in action:
                action_str += f" (text='{action['text']}')"
            elif 'desc' in action:
                action_str += f" (desc='{action['desc']}')"
            elif 'resource_id' in action:
                action_str += f" (id='{action['resource_id']}')"
            
            if action['action'] == 'fill' and 'value' in action:
                action_str += f" → '{action['value']}'"
            
            self.actions_listbox.insert("end", action_str + "\n")
        
        self.counter_label.configure(text=f"{len(self.actions)} ações")
    
    def _clear_actions(self):
        self.actions.clear()
        self._update_display()
    
    def _export_flow(self):
        if not self.actions:
            messagebox.showwarning("Atenção", "Nenhuma ação para exportar!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.actions, f, indent=4, ensure_ascii=False)
            
            messagebox.showinfo("Sucesso", f"Flow exportado com sucesso!\n{filename}")
            
            if self.on_export:
                self.on_export(filename)


class DixUIGUI(ctk.CTk):
    """Interface principal do dixUIAuto"""
    
    def __init__(self):
        super().__init__()
        
        self.title("dixUIAuto - Android Automation Studio")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.engine = None
        self.current_device = None
        
        self._setup_ui()
        self._load_engine()
    
    def _setup_ui(self):
        # Frame principal
        main_container = ctk.CTkFrame(self, fg_color=ThemeColors.BG_PRIMARY)
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self._create_sidebar(main_container)
        
        # Área principal
        self._create_main_area(main_container)
        
        # Status bar
        self._create_status_bar(main_container)
    
    def _create_sidebar(self, parent):
        sidebar = ctk.CTkFrame(
            parent, width=280, fg_color=ThemeColors.BG_SECONDARY,
            corner_radius=12
        )
        sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 10), pady=0)
        sidebar.grid_propagate(False)
        
        # Logo
        logo_label = ctk.CTkLabel(
            sidebar, text="🤖 dixUIAuto",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=ThemeColors.ACCENT
        )
        logo_label.pack(pady=20)
        
        subtitle = ctk.CTkLabel(
            sidebar, text="Android Automation Studio",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.TEXT_SECONDARY
        )
        subtitle.pack(pady=(0, 20))
        
        # Separador
        sep = ctk.CTkFrame(sidebar, height=2, fg_color=ThemeColors.BORDER)
        sep.pack(fill="x", padx=20, pady=10)
        
        # Seção Dispositivos
        devices_title = ctk.CTkLabel(
            sidebar, text="📱 Dispositivos",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ThemeColors.TEXT_PRIMARY
        )
        devices_title.pack(pady=(10, 10), padx=20, anchor="w")
        
        # Scrollable frame para dispositivos
        self.devices_frame = ctk.CTkScrollableFrame(
            sidebar, fg_color="transparent",
            label_text=""
        )
        self.devices_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botão refresh
        refresh_btn = ctk.CTkButton(
            sidebar, text="🔄 Atualizar",
            fg_color=ThemeColors.BG_TERTIARY,
            hover_color=ThemeColors.ACCENT,
            command=self._refresh_devices
        )
        refresh_btn.pack(pady=10, padx=20, fill="x")
    
    def _create_main_area(self, parent):
        main_area = ctk.CTkFrame(parent, fg_color="transparent")
        main_area.grid(row=0, column=1, sticky="nsew")
        main_area.grid_rowconfigure(0, weight=1)
        main_area.grid_columnconfigure(0, weight=1)
        
        # Notebook (abas)
        self.notebook = ctk.CTkTabview(main_area, fg_color=ThemeColors.CARD_BG,
                                       border_color=ThemeColors.BORDER)
        self.notebook.pack(fill="both", expand=True)
        
        # Aba Dashboard
        self.dashboard_tab = self.notebook.add("Dashboard")
        self._setup_dashboard_tab(self.dashboard_tab)
        
        # Aba Construtor
        self.builder_tab = self.notebook.add("Construtor de Flows")
        self._setup_builder_tab(self.builder_tab)
        
        # Aba Inspector
        self.inspector_tab = self.notebook.add("Inspector")
        self._setup_inspector_tab(self.inspector_tab)
        
        # Aba Logs
        self.logs_tab = self.notebook.add("Logs")
        self._setup_logs_tab(self.logs_tab)
    
    def _setup_dashboard_tab(self, tab):
        # Header
        header = ctk.CTkLabel(
            tab, text="🎯 Dashboard",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ThemeColors.TEXT_PRIMARY
        )
        header.pack(pady=20, padx=20, anchor="w")
        
        # Cards de status
        cards_frame = ctk.CTkFrame(tab, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=10)
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Card Conexão
        conn_card = self._create_status_card(
            cards_frame, "🔌 Conexão", "Desconectado", ThemeColors.WARNING
        )
        conn_card.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Card App
        app_card = self._create_status_card(
            cards_frame, "📲 Aplicativo", "Nenhum", ThemeColors.TEXT_SECONDARY
        )
        app_card.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Card Ações
        actions_card = self._create_status_card(
            cards_frame, "⚡ Ações Executadas", "0", ThemeColors.ACCENT
        )
        actions_card.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        # Controles principais
        controls_frame = ctk.CTkFrame(tab, fg_color=ThemeColors.CARD_BG,
                                      corner_radius=12)
        controls_frame.pack(fill="x", padx=20, pady=20)
        
        # Package input
        pkg_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        pkg_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            pkg_frame, text="Package do App:",
            text_color=ThemeColors.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 10))
        
        self.package_entry = ctk.CTkEntry(
            pkg_frame, placeholder_text="com.example.app",
            fg_color=ThemeColors.BG_TERTIARY,
            border_color=ThemeColors.BORDER,
            text_color=ThemeColors.TEXT_PRIMARY,
            width=400
        )
        self.package_entry.pack(side="left", padx=(0, 10))
        
        open_btn = ctk.CTkButton(
            pkg_frame, text="🚀 Abrir App",
            fg_color=ThemeColors.ACCENT,
            hover_color=ThemeColors.ACCENT_HOVER,
            command=self._open_app
        )
        open_btn.pack(side="left")
        
        # Botões de ação rápida
        actions_grid = ctk.CTkFrame(controls_frame, fg_color="transparent")
        actions_grid.pack(fill="x", padx=20, pady=(0, 20))
        
        actions = [
            ("🏠 Home", self._go_home),
            ("↩️ Back", self._go_back),
            ("📸 Screenshot", self._screenshot),
            ("🔄 Refresh UI", self._refresh_ui)
        ]
        
        for i, (text, command) in enumerate(actions):
            btn = ctk.CTkButton(
                actions_grid, text=text,
                fg_color=ThemeColors.BG_TERTIARY,
                hover_color=ThemeColors.ACCENT,
                width=150,
                command=command
            )
            btn.grid(row=0, column=i, padx=10, pady=10)
        
        actions_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
    
    def _create_status_card(self, parent, title: str, value: str, color: str):
        card = ctk.CTkFrame(parent, fg_color=ThemeColors.CARD_BG,
                           corner_radius=12, height=100)
        
        title_label = ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.TEXT_SECONDARY
        )
        title_label.pack(pady=(15, 5))
        
        value_label = ctk.CTkLabel(
            card, text=value,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=color
        )
        value_label.pack(pady=(0, 15))
        
        return card
    
    def _setup_builder_tab(self, tab):
        # Layout horizontal
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Construtor de ações
        self.action_builder = ActionBuilder(
            tab, on_add_action=self._on_action_added
        )
        self.action_builder.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Editor de flow
        self.flow_editor = FlowEditor(
            tab, on_export=self._on_flow_exported
        )
        self.flow_editor.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    
    def _setup_inspector_tab(self, tab):
        # Placeholder para inspector
        placeholder = ctk.CTkLabel(
            tab, text="🔍 Inspector de UI\n\nEm desenvolvimento...\n\nPermitirá inspecionar elementos em tempo real",
            font=ctk.CTkFont(size=16),
            text_color=ThemeColors.TEXT_SECONDARY
        )
        placeholder.place(relx=0.5, rely=0.5, anchor="center")
    
    def _setup_logs_tab(self, tab):
        # Área de logs
        self.logs_text = ctk.CTkTextbox(
            tab, font=ctk.CTkFont(family="Consolas", size=11),
            text_color=ThemeColors.TEXT_PRIMARY,
            fg_color=ThemeColors.BG_TERTIARY,
            border_color=ThemeColors.BORDER
        )
        self.logs_text.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Botão limpar logs
        clear_btn = ctk.CTkButton(
            tab, text="🗑️ Limpar Logs",
            fg_color=ThemeColors.ERROR,
            hover_color="#c82333",
            width=150,
            command=lambda: self.logs_text.delete("1.0", "end")
        )
        clear_btn.pack(pady=(0, 20))
    
    def _create_status_bar(self, parent):
        status_bar = ctk.CTkFrame(
            parent, height=40, fg_color=ThemeColors.BG_SECONDARY,
            corner_radius=8
        )
        status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", 
                       padx=0, pady=(10, 0))
        
        status_label = ctk.CTkLabel(
            status_bar, text="✅ Pronto | dixUIAuto v1.0",
            text_color=ThemeColors.TEXT_SECONDARY,
            font=ctk.CTkFont(size=12)
        )
        status_label.pack(side="left", padx=20)
    
    def _load_engine(self):
        """Carrega a engine do dixUIAuto"""
        try:
            from main import DixEngine
            self.engine = DixEngine()
            self._log("Engine carregada com sucesso!")
            self._refresh_devices()
        except Exception as e:
            self._log(f"Erro ao carregar engine: {e}", level="error")
            messagebox.showerror("Erro", f"Falha ao inicializar engine:\n{e}")
    
    def _refresh_devices(self):
        """Atualiza lista de dispositivos"""
        if not self.engine:
            return
        
        try:
            devices = self.engine.list_devices()
            
            # Limpar frame
            for widget in self.devices_frame.winfo_children():
                widget.destroy()
            
            if not devices:
                no_devices = ctk.CTkLabel(
                    self.devices_frame, text="Nenhum dispositivo encontrado",
                    text_color=ThemeColors.TEXT_SECONDARY
                )
                no_devices.pack(pady=20)
                return
            
            for device in devices:
                card = DeviceCard(
                    self.devices_frame, device,
                    on_select=self._on_device_selected
                )
                card.pack(fill="x", padx=10, pady=5)
            
            self._log(f"{len(devices)} dispositivo(s) encontrado(s)")
        except Exception as e:
            self._log(f"Erro ao listar dispositivos: {e}", level="error")
    
    def _on_device_selected(self, device_info: dict):
        """Callback quando dispositivo é selecionado"""
        try:
            if self.engine:
                self.engine.connect(device_info.get('id'))
                self.current_device = device_info
                self._log(f"Dispositivo conectado: {device_info.get('name')}")
                messagebox.showinfo("Sucesso", f"Conectado a {device_info.get('name')}")
        except Exception as e:
            self._log(f"Erro ao conectar: {e}", level="error")
            messagebox.showerror("Erro", f"Falha na conexão:\n{e}")
    
    def _on_action_added(self, action_data: Dict):
        """Callback quando ação é adicionada"""
        self.flow_editor.add_action(action_data)
        self._log(f"Ação adicionada: {action_data['action']}")
    
    def _on_flow_exported(self, filename: str):
        """Callback quando flow é exportado"""
        self._log(f"Flow exportado: {filename}")
    
    def _open_app(self):
        """Abre aplicativo no dispositivo"""
        package = self.package_entry.get()
        if not package:
            messagebox.showwarning("Atenção", "Informe o package do aplicativo!")
            return
        
        if not self.engine or not self.current_device:
            messagebox.showwarning("Atenção", "Conecte um dispositivo primeiro!")
            return
        
        try:
            self._log(f"Abrindo aplicativo: {package}")
            self.engine.open(package)
            self._log("Aplicativo aberto com sucesso!")
        except Exception as e:
            self._log(f"Erro ao abrir app: {e}", level="error")
            messagebox.showerror("Erro", f"Falha ao abrir aplicativo:\n{e}")
    
    def _go_home(self):
        """Volta para home"""
        if self.engine:
            try:
                self.engine.device.press("home")
                self._log("Indo para home")
            except Exception as e:
                self._log(f"Erro: {e}", level="error")
    
    def _go_back(self):
        """Volta tela anterior"""
        if self.engine:
            try:
                self.engine.device.press("back")
                self._log("Voltando tela anterior")
            except Exception as e:
                self._log(f"Erro: {e}", level="error")
    
    def _screenshot(self):
        """Captura screenshot"""
        if self.engine:
            try:
                filename = f"screenshots/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.engine.screenshot(filename)
                self._log(f"Screenshot salva: {filename}")
                messagebox.showinfo("Sucesso", f"Screenshot salva em:\n{filename}")
            except Exception as e:
                self._log(f"Erro ao capturar screenshot: {e}", level="error")
    
    def _refresh_ui(self):
        """Atualiza UI"""
        if self.engine:
            try:
                self.engine.refresh()
                self._log("UI atualizada")
            except Exception as e:
                self._log(f"Erro ao atualizar UI: {e}", level="error")
    
    def _log(self, message: str, level: str = "info"):
        """Adiciona log na interface"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "info": "#00d26a",
            "warning": "#ffc107",
            "error": "#dc3545"
        }
        color = color_map.get(level, "#ffffff")
        
        log_entry = f"[{timestamp}] {message}\n"
        
        if hasattr(self, 'logs_text'):
            self.logs_text.insert("end", log_entry)
            self.logs_text.see("end")
        
        logger.info(message)
    
    def run(self):
        """Inicia a aplicação"""
        self.mainloop()


def main():
    """Ponto de entrada da GUI"""
    app = DixUIGUI()
    app.run()


if __name__ == "__main__":
    main()
