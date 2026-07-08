"""
dixUIAuto - Live Inspector
Ferramenta de inspeção em tempo real da UI Android.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import re

# Import settings
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import Settings, settings

# Configure appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class UINode:
    """Representa um nó da árvore da UI."""
    
    def __init__(self, element: ET.Element, parent: Optional['UINode'] = None, depth: int = 0):
        self.element = element
        self.parent = parent
        self.depth = depth
        self.children: List[UINode] = []
        
        # Extrair atributos
        self.text = element.get('text', '')
        self.resource_id = element.get('resource-id', '')
        self.content_desc = element.get('content-desc', '')
        self.class_name = element.get('class', '')
        self.bounds = element.get('bounds', '')
        self.checkable = element.get('checkable', 'false') == 'true'
        self.checked = element.get('checked', 'false') == 'true'
        self.clickable = element.get('clickable', 'false') == 'true'
        self.enabled = element.get('enabled', 'false') == 'true'
        self.focusable = element.get('focusable', 'false') == 'true'
        self.focused = element.get('focused', 'false') == 'true'
        self.scrollable = element.get('scrollable', 'false') == 'true'
        self.selected = element.get('selected', 'false') == 'true'
        self.index = element.get('index', '0')
        
        # Calcular score do seletor
        self.selector_score = self._calculate_selector_score()
    
    def _calculate_selector_score(self) -> float:
        """Calcula score de confiança do seletor (0.0 - 1.0)."""
        score = 0.0
        factors = 0
        
        # Resource ID é o melhor seletor
        if self.resource_id and not self.resource_id.startswith('android:'):
            score += 0.4
            factors += 1
        
        # Content description é muito bom
        if self.content_desc and len(self.content_desc) > 3:
            score += 0.3
            factors += 1
        
        # Texto único é bom
        if self.text and len(self.text) > 2:
            score += 0.2
            factors += 1
        
        # Classe específica ajuda
        if self.class_name and not any(x in self.class_name for x in ['Layout', 'View']):
            score += 0.1
            factors += 1
        
        # É clicável
        if self.clickable:
            score += 0.05
            factors += 1
        
        # Normalizar para 0-1
        return min(1.0, score) if factors > 0 else 0.0
    
    def get_best_selector(self) -> Tuple[str, str]:
        """Retorna melhor estratégia de seleção e o valor."""
        if self.resource_id and not self.resource_id.startswith('android:'):
            return ('resourceId', self.resource_id)
        elif self.content_desc and len(self.content_desc) > 3:
            return ('desc', self.content_desc)
        elif self.text and len(self.text) > 2:
            return ('text', self.text)
        elif self.class_name:
            return ('className', self.class_name)
        else:
            return ('text', self.text or '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'text': self.text,
            'resourceId': self.resource_id,
            'contentDesc': self.content_desc,
            'className': self.class_name,
            'bounds': self.bounds,
            'clickable': self.clickable,
            'checkable': self.checkable,
            'checked': self.checked,
            'enabled': self.enabled,
            'focusable': self.focusable,
            'focused': self.focused,
            'scrollable': self.scrollable,
            'selected': self.selected,
            'index': self.index,
            'depth': self.depth,
            'selectorScore': round(self.selector_score, 2),
        }
    
    def generate_code(self, language: str = 'python') -> str:
        """Gera código para selecionar este elemento."""
        strategy, value = self.get_best_selector()
        
        if language == 'python':
            if strategy == 'resourceId':
                return f'engine.click(resourceId="{value}")'
            elif strategy == 'desc':
                return f'engine.click(desc="{value}")'
            elif strategy == 'text':
                return f'engine.click(text="{value}")'
            else:
                return f'engine.click(className="{value}")'
        
        elif language == 'json':
            action = {"action": "click"}
            if strategy == 'resourceId':
                action["resourceId"] = value
            elif strategy == 'desc':
                action["desc"] = value
            elif strategy == 'text':
                action["text"] = value
            else:
                action["className"] = value
            return json.dumps(action, indent=4)
        
        return ""


class TreeView(ctk.CTkFrame):
    """Visualização em árvore dos elementos."""
    
    def __init__(self, master, on_select_callback=None):
        super().__init__(master)
        self.on_select_callback = on_select_callback
        self.nodes: List[UINode] = []
        self.selected_node: Optional[UINode] = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Treebox com scroll
        self.tree_text = ctk.CTkTextbox(self, state="disabled")
        self.tree_text.grid(row=0, column=0, sticky="nsew")
        
        # Configurar tags para cores
        self.tree_text.tag_config("root", foreground="#00ccff", font=("Consolas", 10, "bold"))
        self.tree_text.tag_config("level1", foreground="#0099cc")
        self.tree_text.tag_config("level2", foreground="#006699")
        self.tree_text.tag_config("level3", foreground="#003366")
        self.tree_text.tag_config("leaf", foreground="#999999")
        self.tree_text.tag_config("clickable", foreground="#00ff00")
        self.tree_text.tag_config("selected", background="#333333")
    
    def load_xml(self, xml_content: str):
        """Carrega XML na árvore."""
        try:
            root = ET.fromstring(xml_content)
            self.nodes = []
            self._parse_node(root, None, 0)
            self._render_tree()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao parsear XML: {str(e)}")
    
    def _parse_node(self, element: ET.Element, parent: Optional[UINode], depth: int):
        """Parseia nó XML recursivamente."""
        node = UINode(element, parent, depth)
        self.nodes.append(node)
        
        for child in element:
            self._parse_node(child, node, depth + 1)
    
    def _render_tree(self):
        """Renderiza árvore no textbox."""
        self.tree_text.configure(state="normal")
        self.tree_text.delete("0.0", "end")
        
        for node in self.nodes:
            indent = "  " * node.depth
            icon = "📱" if node.depth == 0 else ("📦" if node.children else "🔹")
            
            # Destaque para elementos clicáveis
            clickable_mark = "✅" if node.clickable else "  "
            
            # Nome do elemento
            name = node.class_name.split('.')[-1] if '.' in node.class_name else node.class_name
            if node.text:
                name += f' "{node.text[:30]}"'
            
            line = f"{indent}{icon} {name} {clickable_mark}\n"
            
            # Determinar tag baseada no depth
            if node.depth == 0:
                tag = "root"
            elif node.depth == 1:
                tag = "level1"
            elif node.depth == 2:
                tag = "level2"
            else:
                tag = "leaf"
            
            if node.clickable:
                tag = "clickable"
            
            self.tree_text.insert("end", line, tag)
        
        self.tree_text.configure(state="disabled")
    
    def get_filtered_nodes(self, filters: Dict[str, str]) -> List[UINode]:
        """Filtra nós baseado nos critérios."""
        filtered = []
        
        for node in self.nodes:
            match = True
            
            if filters.get('text') and filters['text'] not in node.text:
                match = False
            if filters.get('resource_id') and filters['resource_id'] not in node.resource_id:
                match = False
            if filters.get('content_desc') and filters['content_desc'] not in node.content_desc:
                match = False
            if filters.get('class_name') and filters['class_name'] not in node.class_name:
                match = False
            if filters.get('clickable_only') and not node.clickable:
                match = False
            
            if match:
                filtered.append(node)
        
        return filtered


class DetailPanel(ctk.CTkFrame):
    """Painel de detalhes do elemento selecionado."""
    
    def __init__(self, master):
        super().__init__(master)
        self.current_node: Optional[UINode] = None
        
        self.grid_columnconfigure(0, weight=1)
        
        # Título
        self.title_label = ctk.CTkLabel(
            self, 
            text="📋 Detalhes do Elemento", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Score do seletor
        self.score_frame = ctk.CTkFrame(self)
        self.score_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.score_frame, text="🎯 Score do Seletor:").pack(side="left", padx=5)
        self.score_label = ctk.CTkLabel(
            self.score_frame, 
            text="0.00", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00ccff"
        )
        self.score_label.pack(side="left", padx=5)
        
        # Propriedades
        props_frame = ctk.CTkScrollableFrame(self, height=300)
        props_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        props_frame.grid_columnconfigure(1, weight=1)
        
        self.prop_labels = []
        self.prop_values = []
        
        properties = [
            "Text", "Resource ID", "Content Desc", "Class Name",
            "Bounds", "Index", "Depth", "Clickable", "Checkable",
            "Checked", "Enabled", "Focusable", "Focused",
            "Scrollable", "Selected"
        ]
        
        for i, prop in enumerate(properties):
            label = ctk.CTkLabel(props_frame, text=f"{prop}:", font=ctk.CTkFont(weight="bold"))
            label.grid(row=i, column=0, padx=5, pady=2, sticky="e")
            
            value = ctk.CTkLabel(props_frame, text="-", width=300, anchor="w")
            value.grid(row=i, column=1, padx=5, pady=2, sticky="w")
            
            self.prop_labels.append(label)
            self.prop_values.append(value)
        
        # Geração de código
        code_frame = ctk.CTkFrame(self)
        code_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        code_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(code_frame, text="💻 Código Gerado:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.code_type = ctk.CTkSegmentedButton(
            code_frame, 
            values=["Python", "JSON"],
            command=self._update_code
        )
        self.code_type.grid(row=0, column=1, padx=5, pady=5)
        self.code_type.set("Python")
        
        self.code_box = ctk.CTkTextbox(code_frame, height=80, state="disabled")
        self.code_box.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Botões de ação
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        self.copy_btn = ctk.CTkButton(
            btn_frame, 
            text="📋 Copiar Código", 
            command=self._copy_code,
            width=150
        )
        self.copy_btn.pack(side="left", padx=5)
        
        self.export_btn = ctk.CTkButton(
            btn_frame, 
            text="💾 Exportar JSON", 
            command=self._export_json,
            width=150
        )
        self.export_btn.pack(side="left", padx=5)
    
    def set_node(self, node: UINode):
        """Define nó atual e atualiza display."""
        self.current_node = node
        
        # Atualizar score
        score = node.selector_score
        self.score_label.configure(text=f"{score:.2f}")
        
        if score >= 0.7:
            self.score_label.configure(text_color="#00ff00")
        elif score >= 0.4:
            self.score_label.configure(text_color="#ffcc00")
        else:
            self.score_label.configure(text_color="#ff3300")
        
        # Atualizar propriedades
        data = node.to_dict()
        prop_mapping = [
            "text", "resourceId", "contentDesc", "className",
            "bounds", "index", "depth", "clickable", "checkable",
            "checked", "enabled", "focusable", "focused",
            "scrollable", "selected"
        ]
        
        for i, prop in enumerate(prop_mapping):
            value = data.get(prop, "-")
            if isinstance(value, bool):
                value = "✅ Sim" if value else "❌ Não"
            self.prop_values[i].configure(text=str(value))
        
        # Atualizar código
        self._update_code(self.code_type.get())
    
    def _update_code(self, code_type: str):
        """Atualiza caixa de código."""
        if not self.current_node:
            return
        
        lang = "python" if code_type == "Python" else "json"
        code = self.current_node.generate_code(lang)
        
        self.code_box.configure(state="normal")
        self.code_box.delete("0.0", "end")
        self.code_box.insert("0.0", code)
        self.code_box.configure(state="disabled")
    
    def _copy_code(self):
        """Copia código para clipboard."""
        # Implementação simplificada
        messagebox.showinfo("Copiar", "Código copiado para clipboard (simulação)")
    
    def _export_json(self):
        """Exporta elemento como JSON."""
        if not self.current_node:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_node.to_dict(), f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Sucesso", f"Elemento exportado para:\n{file_path}")


class FilterPanel(ctk.CTkFrame):
    """Painel de filtros."""
    
    def __init__(self, master, on_filter_callback=None):
        super().__init__(master)
        self.on_filter_callback = on_filter_callback
        
        self.grid_columnconfigure(1, weight=1)
        
        # Título
        ctk.CTkLabel(
            self, 
            text="🔍 Filtros", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Filtro por texto
        ctk.CTkLabel(self, text="Texto:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.text_filter = ctk.CTkEntry(self, placeholder_text="Filtrar por texto")
        self.text_filter.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        # Filtro por resource-id
        ctk.CTkLabel(self, text="Resource ID:").grid(row=2, column=0, padx=5, pady=2, sticky="e")
        self.resource_filter = ctk.CTkEntry(self, placeholder_text="Filtrar por resource-id")
        self.resource_filter.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # Filtro por content-desc
        ctk.CTkLabel(self, text="Content Desc:").grid(row=3, column=0, padx=5, pady=2, sticky="e")
        self.desc_filter = ctk.CTkEntry(self, placeholder_text="Filtrar por content-desc")
        self.desc_filter.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        
        # Filtro por classe
        ctk.CTkLabel(self, text="Classe:").grid(row=4, column=0, padx=5, pady=2, sticky="e")
        self.class_filter = ctk.CTkEntry(self, placeholder_text="Filtrar por classe")
        self.class_filter.grid(row=4, column=1, padx=5, pady=2, sticky="ew")
        
        # Checkbox clicáveis apenas
        self.clickable_only = ctk.CTkCheckBox(self, text="Apenas Clicáveis ✅")
        self.clickable_only.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Botão aplicar
        self.apply_btn = ctk.CTkButton(
            self, 
            text="🔍 Aplicar Filtros", 
            command=self._apply_filters,
            width=200
        )
        self.apply_btn.grid(row=6, column=0, columnspan=2, padx=5, pady=10)
        
        # Botão limpar
        self.clear_btn = ctk.CTkButton(
            self, 
            text="🧹 Limpar", 
            command=self._clear_filters,
            width=200,
            fg_color="#666666"
        )
        self.clear_btn.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
    
    def _apply_filters(self):
        """Aplica filtros."""
        filters = {
            'text': self.text_filter.get(),
            'resource_id': self.resource_filter.get(),
            'content_desc': self.desc_filter.get(),
            'class_name': self.class_filter.get(),
            'clickable_only': self.clickable_only.get(),
        }
        
        if self.on_filter_callback:
            self.on_filter_callback(filters)
    
    def _clear_filters(self):
        """Limpa filtros."""
        self.text_filter.delete(0, 'end')
        self.resource_filter.delete(0, 'end')
        self.desc_filter.delete(0, 'end')
        self.class_filter.delete(0, 'end')
        self.clickable_only.deselect()
        
        if self.on_filter_callback:
            self.on_filter_callback({})


class LiveInspectorGUI(ctk.CTk):
    """Interface principal do Live Inspector."""
    
    def __init__(self):
        super().__init__()
        
        self.title("dixUIAuto - Live Inspector")
        self.geometry("1600x1000")
        self.minsize(1400, 900)
        
        # Configurar grid principal
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # Painel esquerdo - Árvore
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_rowconfigure(1, weight=1)
        
        # Toolbar superior
        toolbar = ctk.CTkFrame(left_frame, fg_color="transparent")
        toolbar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.refresh_btn = ctk.CTkButton(
            toolbar, 
            text="🔄 Atualizar UI", 
            command=self._refresh_ui,
            width=150
        )
        self.refresh_btn.pack(side="left", padx=5)
        
        self.load_btn = ctk.CTkButton(
            toolbar, 
            text="📁 Carregar XML", 
            command=self._load_xml_file,
            width=150
        )
        self.load_btn.pack(side="left", padx=5)
        
        self.auto_refresh_var = ctk.BooleanVar(value=False)
        self.auto_refresh_cb = ctk.CTkCheckBox(
            toolbar, 
            text="Auto Refresh (5s)", 
            variable=self.auto_refresh_var,
            command=self._toggle_auto_refresh
        )
        self.auto_refresh_cb.pack(side="right", padx=5)
        
        # Filtros
        self.filter_panel = FilterPanel(left_frame, on_filter_callback=self._apply_filters)
        self.filter_panel.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # Árvore
        self.tree_view = TreeView(left_frame)
        self.tree_view.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Painel direito - Detalhes
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_rowconfigure(1, weight=1)
        
        self.detail_panel = DetailPanel(right_frame)
        self.detail_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Stats
        stats_frame = ctk.CTkFrame(right_frame)
        stats_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        
        self.total_label = ctk.CTkLabel(stats_frame, text="Total: 0 elementos")
        self.total_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.clickable_label = ctk.CTkLabel(stats_frame, text="Clicáveis: 0")
        self.clickable_label.grid(row=0, column=1, padx=5, pady=5)
        
        # Status bar
        self.status_bar = ctk.CTkLabel(
            self, 
            text="Live Inspector v2.0 | Aguardando XML", 
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Auto refresh thread
        self.auto_refresh_thread = None
        self.running = True
    
    def _refresh_ui(self):
        """Atualiza UI (simulado)."""
        messagebox.showinfo(
            "Atualizar", 
            "Para inspecionar em tempo real:\n\n"
            "1. Conecte seu dispositivo Android\n"
            "2. Execute: adb shell uiautomator dump /sdcard/window_dump.xml\n"
            "3. Execute: adb pull /sdcard/window_dump.xml\n"
            "4. Clique em '📁 Carregar XML' e selecione o arquivo\n\n"
            "Ou use a engine do dixUIAuto para dump automático."
        )
    
    def _load_xml_file(self):
        """Carrega arquivo XML."""
        file_path = filedialog.askopenfilename(
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                
                self.tree_view.load_xml(xml_content)
                self._update_stats()
                self.status_bar.configure(text=f"XML carregado: {Path(file_path).name}")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar XML: {str(e)}")
    
    def _apply_filters(self, filters: Dict[str, str]):
        """Aplica filtros à árvore."""
        # Implementação simplificada
        pass
    
    def _update_stats(self):
        """Atualiza estatísticas."""
        nodes = self.tree_view.nodes
        total = len(nodes)
        clickable = sum(1 for n in nodes if n.clickable)
        
        self.total_label.configure(text=f"Total: {total} elementos")
        self.clickable_label.configure(text=f"Clicáveis: {clickable}")
    
    def _toggle_auto_refresh(self):
        """Alterna auto refresh."""
        if self.auto_refresh_var.get():
            # Iniciar thread de auto refresh
            pass
        else:
            # Parar thread
            pass
    
    def load_xml_content(self, xml_content: str):
        """Carrega conteúdo XML diretamente."""
        self.tree_view.load_xml(xml_content)
        self._update_stats()
        self.status_bar.configure(text="XML carregado com sucesso")


def main():
    """Função principal."""
    try:
        app = LiveInspectorGUI()
        app.mainloop()
    except Exception as e:
        print(f"❌ Erro ao iniciar Live Inspector: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
