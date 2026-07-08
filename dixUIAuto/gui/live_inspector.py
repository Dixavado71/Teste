"""
Live Inspector - Ferramenta de Inspeção em Tempo Real
Permite inspecionar a árvore da UI, filtrar elementos e gerar seletores
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
import threading
import time
import sys
import os
from typing import List, Dict, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings
from lib.logs import get_logger

logger = get_logger(__name__)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class ThemeColors:
    BG_PRIMARY = "#1a1a2e"
    BG_SECONDARY = "#16213e"
    BG_TERTIARY = "#0f3460"
    ACCENT = "#e94560"
    SUCCESS = "#00d26a"
    WARNING = "#ffc107"
    ERROR = "#dc3545"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0a0"
    BORDER = "#2a2a4e"
    CARD_BG = "#1f2937"
    HIGHLIGHT = "#ffd700"


class UINode:
    """Representa um nó da árvore da UI"""
    
    def __init__(self, element: ET.Element, depth: int = 0):
        self.element = element
        self.depth = depth
        self.children: List[UINode] = []
        self.parent: Optional[UINode] = None
        
        # Extrair atributos
        self.text = element.get('text', '')
        self.resource_id = element.get('resource-id', '')
        self.content_desc = element.get('content-desc', '')
        self.class_name = element.get('class', '')
        self.bounds = element.get('bounds', '')
        self.checkable = element.get('checkable', 'false')
        self.checked = element.get('checked', 'false')
        self.clickable = element.get('clickable', 'false')
        self.enabled = element.get('enabled', 'true')
        self.focusable = element.get('focusable', 'false')
        self.focused = element.get('focused', 'false')
        self.scrollable = element.get('scrollable', 'false')
        self.selected = element.get('selected', 'false')
        
        # Calcular score de qualidade do seletor
        self.selector_score = self._calculate_selector_score()
    
    def _calculate_selector_score(self) -> float:
        """Calcula score de confiança para o seletor (0-1)"""
        score = 0.0
        max_score = 0.0
        
        # resource-id é o mais estável
        if self.resource_id:
            score += 0.4
        max_score += 0.4
        
        # content-desc é muito bom
        if self.content_desc:
            score += 0.3
        max_score += 0.3
        
        # texto único é bom
        if self.text and len(self.text.strip()) > 0:
            score += 0.2
        max_score += 0.2
        
        # classe específica ajuda
        if self.class_name and not self.class_name.startswith('android.widget'):
            score += 0.1
        max_score += 0.1
        
        return score / max_score if max_score > 0 else 0.0
    
    def get_best_selector(self) -> Dict[str, str]:
        """Retorna o melhor seletor para este elemento"""
        selectors = {}
        
        if self.resource_id:
            selectors['resource_id'] = self.resource_id
        
        if self.content_desc:
            selectors['desc'] = self.content_desc
        
        if self.text and len(self.text.strip()) > 0:
            selectors['text'] = self.text
        
        if self.class_name:
            selectors['class_name'] = self.class_name
        
        return selectors
    
    def to_dict(self) -> Dict:
        return {
            'text': self.text,
            'resource_id': self.resource_id,
            'content_desc': self.content_desc,
            'class_name': self.class_name,
            'bounds': self.bounds,
            'depth': self.depth,
            'clickable': self.clickable,
            'selector_score': self.selector_score
        }


class ElementTreeViewer(ctk.CTkFrame):
    """Visualizador da árvore de elementos da UI"""
    
    def __init__(self, parent, on_select_element=None):
        super().__init__(parent, fg_color=ThemeColors.CARD_BG,
                        corner_radius=12, border_width=1,
                        border_color=ThemeColors.BORDER)
        
        self.on_select_element = on_select_element
        self.nodes: List[UINode] = []
        self.selected_node: Optional[UINode] = None
        self._setup_ui()
    
    def _setup_ui(self):
        # Título
        title = ctk.CTkLabel(
            self, text="🌳 Árvore de Elementos",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ThemeColors.TEXT_PRIMARY
        )
        title.pack(pady=(15, 10), padx=15, anchor="w")
        
        # Filtros
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(
            filter_frame, text="Filtrar:",
            text_color=ThemeColors.TEXT_SECONDARY
        ).pack(side="left", padx=(0, 10))
        
        self.filter_entry = ctk.CTkEntry(
            filter_frame, placeholder_text="Texto, ID, classe...",
            fg_color=ThemeColors.BG_TERTIARY,
            border_color=ThemeColors.BORDER,
            text_color=ThemeColors.TEXT_PRIMARY,
            width=200
        )
        self.filter_entry.pack(side="left", padx=(0, 10))
        self.filter_entry.bind("<KeyRelease>", self._apply_filter)
        
        # Checkbox apenas clicáveis
        self.clickable_only = ctk.CTkCheckBox(
            filter_frame, text="Apenas Clicáveis",
            fg_color=ThemeColors.ACCENT,
            text_color=ThemeColors.TEXT_PRIMARY,
            command=self._apply_filter
        )
        self.clickable_only.pack(side="left", padx=(0, 10))
        
        # Treeview
        tree_frame = ctk.CTkFrame(self, fg_color=ThemeColors.BG_TERTIARY,
                                  corner_radius=8)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Criar treeview estilizada
        style = ttk.Style()
        style.theme_use('default')
        
        # Configurar cores da treeview
        style.configure("Custom.Treeview",
                       background=ThemeColors.BG_TERTIARY,
                       foreground=ThemeColors.TEXT_PRIMARY,
                       fieldbackground=ThemeColors.BG_TERTIARY,
                       rowheight=25,
                       font=('Arial', 10))
        
        style.map("Custom.Treeview",
                 background=[('selected', ThemeColors.ACCENT)],
                 foreground=[('selected', ThemeColors.TEXT_PRIMARY)])
        
        style.configure("Custom.Treeview.Heading",
                       background=ThemeColors.BG_SECONDARY,
                       foreground=ThemeColors.TEXT_PRIMARY,
                       font=('Arial', 11, 'bold'))
        
        self.tree = ttk.Treeview(
            tree_frame, style="Custom.Treeview",
            columns=('text', 'id', 'class', 'score'),
            show='tree headings'
        )
        
        self.tree.heading('#0', text='Elemento')
        self.tree.heading('text', text='Texto')
        self.tree.heading('id', text='Resource ID')
        self.tree.heading('class', text='Classe')
        self.tree.heading('score', text='Score')
        
        self.tree.column('#0', width=200, minwidth=150)
        self.tree.column('text', width=150, minwidth=100)
        self.tree.column('id', width=150, minwidth=100)
        self.tree.column('class', width=120, minwidth=80)
        self.tree.column('score', width=60, minwidth=50)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        vsb.grid(row=0, column=1, sticky="ns", pady=5)
        hsb.grid(row=1, column=0, sticky="ew", padx=5)
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind de seleção
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        # Contador
        self.counter_label = ctk.CTkLabel(
            self, text="0 elementos",
            text_color=ThemeColors.TEXT_SECONDARY,
            font=ctk.CTkFont(size=12)
        )
        self.counter_label.pack(pady=(0, 15))
    
    def load_xml(self, xml_content: str):
        """Carrega XML da UI"""
        try:
            root = ET.fromstring(xml_content)
            self.nodes = []
            
            # Limpar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Processar nós recursivamente
            self._process_node(root, '', 0)
            
            self.counter_label.configure(text=f"{len(self.nodes)} elementos")
            
        except Exception as e:
            logger.error(f"Erro ao carregar XML: {e}")
            messagebox.showerror("Erro", f"Falha ao carregar XML:\n{e}")
    
    def _process_node(self, element: ET.Element, parent_id: str, depth: int):
        """Processa nó e seus filhos"""
        node = UINode(element, depth)
        self.nodes.append(node)
        
        # Inserir na treeview
        values = (
            node.text[:30] + '...' if len(node.text) > 30 else node.text,
            node.resource_id.split('/')[-1] if '/' in node.resource_id else node.resource_id,
            node.class_name.split('.')[-1] if '.' in node.class_name else node.class_name,
            f"{node.selector_score:.2f}"
        )
        
        item_id = self.tree.insert(
            parent_id, 'end',
            text=f"[{depth}] {node.class_name.split('.')[-1]}",
            values=values
        )
        
        node.item_id = item_id
        
        # Processar filhos
        for child in element:
            self._process_node(child, item_id, depth + 1)
    
    def _apply_filter(self, event=None):
        """Aplica filtros na treeview"""
        filter_text = self.filter_entry.get().lower()
        clickable_only = self.clickable_only.get()
        
        visible_count = 0
        
        for item in self.tree.get_children():
            self._filter_item(item, filter_text, clickable_only)
            if self.tree.item(item, 'open'):
                visible_count += 1
        
        self.counter_label.configure(text=f"{visible_count}/{len(self.nodes)} elementos")
    
    def _filter_item(self, item_id: str, filter_text: str, clickable_only: bool):
        """Filtra item recursivamente"""
        should_show = True
        
        # Verificar filtro de texto
        if filter_text:
            values = self.tree.item(item_id, 'values')
            item_text = ' '.join(str(v) for v in values).lower()
            if filter_text not in item_text:
                should_show = False
        
        # Verificar filtro clicável
        if clickable_only:
            # Precisaríamos armazenar essa info nos valores
            pass
        
        # Mostrar/ocultar
        if should_show:
            self.tree.detach(item_id)  # Remove temporariamente
            # Lógica complexa de re-inserção seria necessária
        else:
            self.tree.detach(item_id)
    
    def _on_select(self, event):
        """Callback quando elemento é selecionado"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        
        # Encontrar nó correspondente
        for node in self.nodes:
            if hasattr(node, 'item_id') and node.item_id == item_id:
                self.selected_node = node
                if self.on_select_element:
                    self.on_select_element(node)
                break


class ElementDetails(ctk.CTkFrame):
    """Painel de detalhes do elemento selecionado"""
    
    def __init__(self, parent, on_generate_code=None):
        super().__init__(parent, fg_color=ThemeColors.CARD_BG,
                        corner_radius=12, border_width=1,
                        border_color=ThemeColors.BORDER)
        
        self.on_generate_code = on_generate_code
        self.current_node: Optional[UINode] = None
        self._setup_ui()
    
    def _setup_ui(self):
        # Título
        title = ctk.CTkLabel(
            self, text="📋 Detalhes do Elemento",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ThemeColors.TEXT_PRIMARY
        )
        title.pack(pady=(15, 10), padx=15, anchor="w")
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            label_text=""
        )
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Campos de informação
        self.info_labels = {}
        fields = [
            ('text', 'Texto'),
            ('resource_id', 'Resource ID'),
            ('content_desc', 'Content Desc'),
            ('class_name', 'Classe'),
            ('bounds', 'Bounds'),
            ('depth', 'Profundidade'),
            ('clickable', 'Clicável'),
            ('checkable', 'Checkable'),
            ('scrollable', 'Scrollable'),
            ('selector_score', 'Score do Seletor')
        ]
        
        for field, label_text in fields:
            frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                frame, text=f"{label_text}:",
                text_color=ThemeColors.TEXT_SECONDARY,
                width=120, anchor="w"
            ).pack(side="left", padx=(0, 10))
            
            value_label = ctk.CTkLabel(
                frame, text="-",
                text_color=ThemeColors.TEXT_PRIMARY,
                anchor="w"
            )
            value_label.pack(side="left", fill="x", expand=True)
            
            self.info_labels[field] = value_label
        
        # Separador
        sep = ctk.CTkFrame(self, height=2, fg_color=ThemeColors.BORDER)
        sep.pack(fill="x", padx=15, pady=15)
        
        # Geradores de código
        code_title = ctk.CTkLabel(
            self, text="💻 Gerar Código",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ThemeColors.TEXT_PRIMARY
        )
        code_title.pack(pady=(0, 10), padx=15, anchor="w")
        
        # Botões de geração
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        gen_python = ctk.CTkButton(
            btn_frame, text="🐍 Python",
            fg_color=ThemeColors.ACCENT,
            hover_color=ThemeColors.ACCENT_HOVER,
            command=lambda: self._generate_code('python')
        )
        gen_python.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        gen_json = ctk.CTkButton(
            btn_frame, text="📄 JSON Flow",
            fg_color=ThemeColors.SUCCESS,
            hover_color="#00b359",
            command=lambda: self._generate_code('json')
        )
        gen_json.pack(side="right", fill="x", expand=True)
        
        # Área de código gerado
        self.code_text = ctk.CTkTextbox(
            self, height=150,
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=ThemeColors.TEXT_PRIMARY,
            fg_color=ThemeColors.BG_TERTIARY,
            border_color=ThemeColors.BORDER
        )
        self.code_text.pack(fill="x", padx=15, pady=(0, 15))
    
    def set_element(self, node: UINode):
        """Define elemento selecionado"""
        self.current_node = node
        
        # Atualizar labels
        self.info_labels['text'].configure(text=node.text or '-')
        self.info_labels['resource_id'].configure(text=node.resource_id or '-')
        self.info_labels['content_desc'].configure(text=node.content_desc or '-')
        self.info_labels['class_name'].configure(text=node.class_name or '-')
        self.info_labels['bounds'].configure(text=node.bounds or '-')
        self.info_labels['depth'].configure(text=str(node.depth))
        self.info_labels['clickable'].configure(text=node.clickable)
        self.info_labels['checkable'].configure(text=node.checkable)
        self.info_labels['scrollable'].configure(text=node.scrollable)
        
        score_color = ThemeColors.SUCCESS if node.selector_score > 0.7 else \
                     ThemeColors.WARNING if node.selector_score > 0.4 else \
                     ThemeColors.ERROR
        self.info_labels['selector_score'].configure(
            text=f"{node.selector_score:.2f}",
            text_color=score_color
        )
        
        # Limpar código
        self.code_text.delete("1.0", "end")
        self.code_text.insert("end", "Selecione um elemento para gerar código...")
    
    def _generate_code(self, format_type: str):
        """Gera código para o elemento"""
        if not self.current_node:
            return
        
        selectors = self.current_node.get_best_selector()
        
        if format_type == 'python':
            code_lines = ["# Código Python generado"]
            
            if 'resource_id' in selectors:
                code_lines.append(f"engine.click(resource_id=\"{selectors['resource_id']}\")")
            elif 'desc' in selectors:
                code_lines.append(f"engine.click(desc=\"{selectors['desc']}\")")
            elif 'text' in selectors:
                code_lines.append(f"engine.click(text=\"{selectors['text']}\")")
            
            code = '\n'.join(code_lines)
        
        else:  # json
            action = {"action": "click"}
            action.update(selectors)
            code = json.dumps([action], indent=4, ensure_ascii=False)
        
        self.code_text.delete("1.0", "end")
        self.code_text.insert("end", code)
        
        if self.on_generate_code:
            self.on_generate_code(code, format_type)


class LiveInspector(ctk.CTk):
    """Janela principal do Live Inspector"""
    
    def __init__(self, engine=None):
        super().__init__()
        
        self.title("dixUIAuto - Live Inspector")
        self.geometry("1600x1000")
        self.minsize(1400, 900)
        
        self.engine = engine
        self.is_inspecting = False
        self.inspect_thread = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Layout principal
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Painel esquerdo - Árvore
        self.tree_viewer = ElementTreeViewer(
            self, on_select_element=self._on_element_selected
        )
        self.tree_viewer.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Painel direito - Detalhes
        self.details_panel = ElementDetails(
            self, on_generate_code=self._on_code_generated
        )
        self.details_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        
        # Barra inferior de controles
        self._create_control_bar()
    
    def _create_control_bar(self):
        control_frame = ctk.CTkFrame(
            self, height=60, fg_color=ThemeColors.BG_SECONDARY,
            corner_radius=8
        )
        control_frame.grid(row=1, column=0, columnspan=2, sticky="ew",
                          padx=10, pady=(0, 10))
        
        # Botão capturar
        self.capture_btn = ctk.CTkButton(
            control_frame, text="📸 Capturar UI",
            fg_color=ThemeColors.ACCENT,
            hover_color=ThemeColors.ACCENT_HOVER,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._capture_ui
        )
        self.capture_btn.pack(side="left", padx=20, pady=10)
        
        # Auto refresh
        self.auto_refresh_var = ctk.BooleanVar(value=False)
        auto_refresh_cb = ctk.CTkCheckBox(
            control_frame, text="Auto Refresh (5s)",
            variable=self.auto_refresh_var,
            fg_color=ThemeColors.ACCENT,
            text_color=ThemeColors.TEXT_PRIMARY,
            command=self._toggle_auto_refresh
        )
        auto_refresh_cb.pack(side="left", padx=20)
        
        # Status
        status_label = ctk.CTkLabel(
            control_frame, text="● Pronto",
            text_color=ThemeColors.SUCCESS,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        status_label.pack(side="right", padx=20)
    
    def _capture_ui(self):
        """Captura UI atual"""
        if not self.engine:
            messagebox.showwarning("Atenção", "Engine não inicializada!")
            return
        
        try:
            self.capture_btn.configure(text="⏳ Capturando...", state="disabled")
            
            # Obter dump da UI
            xml_content = self.engine.dump()
            
            # Carregar na treeview
            self.tree_viewer.load_xml(xml_content)
            
            self.capture_btn.configure(text="✅ Capturado!", state="normal")
            self.after(2000, lambda: self.capture_btn.configure(text="📸 Capturar UI"))
            
        except Exception as e:
            logger.error(f"Erro ao capturar UI: {e}")
            self.capture_btn.configure(text="❌ Erro", state="normal")
            messagebox.showerror("Erro", f"Falha ao capturar UI:\n{e}")
    
    def _toggle_auto_refresh(self):
        """Alterna auto refresh"""
        if self.auto_refresh_var.get():
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()
    
    def _start_auto_refresh(self):
        """Inicia auto refresh"""
        def refresh_loop():
            while self.auto_refresh_var.get():
                try:
                    self._capture_ui()
                except:
                    pass
                time.sleep(5)
        
        self.inspect_thread = threading.Thread(target=refresh_loop, daemon=True)
        self.inspect_thread.start()
    
    def _stop_auto_refresh(self):
        """Para auto refresh"""
        self.auto_refresh_var.set(False)
    
    def _on_element_selected(self, node: UINode):
        """Callback quando elemento é selecionado"""
        self.details_panel.set_element(node)
    
    def _on_code_generated(self, code: str, format_type: str):
        """Callback quando código é gerado"""
        logger.info(f"Código {format_type} generado")


def main():
    """Ponto de entrada do inspector"""
    try:
        from main import DixEngine
        engine = DixEngine()
        engine.connect()
        
        app = LiveInspector(engine)
        app.mainloop()
        
    except Exception as e:
        print(f"Erro ao iniciar inspector: {e}")
        # Fallback sem engine
        app = LiveInspector()
        app.mainloop()


if __name__ == "__main__":
    main()
