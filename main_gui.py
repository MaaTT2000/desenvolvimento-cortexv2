# Arquivo: main_gui.py (VERSÃO FINAL 2.0 - Identidade "CorteX")

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import os # Importado para ajudar a encontrar o ícone

import otimizador_core as core

class OtimizadorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("CorteX - Otimizador de Chapas v2.0")
        self.master.geometry("950x750")

        # --- Tenta definir o ícone da aplicação ---
        self._set_app_icon()
        
        # --- Configura o menu da aplicação ---
        self._create_menu()

        # --- Configura o estilo visual "CorteX" ---
        self._setup_styles()
        
        # --- Estrutura principal com padding ---
        main_frame = ttk.Frame(master, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Estrutura e Widgets ---
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        param_frame = ttk.LabelFrame(header_frame, text="Parâmetros de Corte", padding=10)
        param_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        file_actions_frame = ttk.LabelFrame(header_frame, text="Arquivo", padding=10)
        file_actions_frame.pack(side=tk.LEFT, padx=(10, 0))
        pecas_frame_container = ttk.LabelFrame(main_frame, text="Lista de Peças", padding=10)
        pecas_frame_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        canvas = tk.Canvas(pecas_frame_container, bg=self.colors['frame_bg'], borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(pecas_frame_container, orient="vertical", command=canvas.yview)
        self.pecas_frame = ttk.Frame(canvas, style='Dark.TFrame')
        self.pecas_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.pecas_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        result_frame = ttk.LabelFrame(main_frame, text="Plano de Otimização CorteX", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)
        self._create_param_widgets(param_frame)
        self._create_file_action_widgets(file_actions_frame)
        self._create_control_widgets(controls_frame)
        self._create_result_widgets(result_frame)
        self.pecas_entries = []
        for _ in range(5): self._adicionar_campo_peca()

    def _set_app_icon(self):
        """Tenta encontrar e definir o ícone da aplicação."""
        try:
            # O ícone 'cortex.ico' deve estar na mesma pasta que o script
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cortex.ico')
            if os.path.exists(icon_path):
                self.master.iconbitmap(icon_path)
        except Exception:
            # Se falhar (ex: não está no Windows), não quebra a aplicação
            print("Aviso: Ícone 'cortex.ico' não encontrado ou não foi possível defini-lo.")

    def _create_menu(self):
        """Cria o menu superior da aplicação."""
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre CorteX", command=self._show_about_dialog)

    def _show_about_dialog(self):
        """Exibe a janela 'Sobre' com a identidade da marca."""
        about_win = tk.Toplevel(self.master)
        about_win.title("Sobre CorteX")
        about_win.geometry("350x200")
        about_win.resizable(False, False)
        about_win.configure(bg=self.colors['bg'])
        about_win.transient(self.master)
        about_win.grab_set()

        ttk.Label(about_win, text="CorteX", font=('Segoe UI', 28, 'bold')).pack(pady=(15, 0))
        ttk.Label(about_win, text="Otimizador Inteligente de Chapas de Aço", font=('Segoe UI', 10)).pack()
        ttk.Label(about_win, text="Versão 2.0", font=('Segoe UI', 9), foreground=self.colors['disabled_fg']).pack(pady=(0, 20))
        
        ttk.Button(about_win, text="OK", command=about_win.destroy, style='Accent.TButton').pack(pady=10)


    def _setup_styles(self):
        """Configura o tema visual 'CorteX'."""
        self.colors = {
            'bg': '#2E2E2E',
            'frame_bg': '#3A3A3A',
            'text': '#F0F0F0',
            'steel_silver': '#8D99AE',
            'accent': '#2E8B57', # SeaGreen
            'accent_active': '#3CB371',
            'secondary': '#555555',
            'secondary_active': '#6A6A6A',
            'entry_bg': '#4A4A4A',
            'disabled_fg': '#999999'
        }
        self.master.configure(bg=self.colors['bg'])
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background=self.colors['bg'], foreground=self.colors['text'], font=('Segoe UI', 10))
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'])
        style.configure('TLabelFrame', background=self.colors['bg'], bordercolor=self.colors['steel_silver'])
        style.configure('TLabelFrame.Label', background=self.colors['bg'], foreground=self.colors['steel_silver'], font=('Segoe UI', 11, 'bold'))
        style.configure('TButton', padding=6, font=('Segoe UI', 10, 'bold'), borderwidth=0)
        style.map('TButton', foreground=[('active', self.colors['text'])], background=[('active', self.colors['secondary_active'])])
        style.configure('Accent.TButton', background=self.colors['accent'], foreground=self.colors['text'])
        style.map('Accent.TButton', background=[('active', self.colors['accent_active'])])
        style.configure('Secondary.TButton', background=self.colors['secondary'], foreground=self.colors['text'])
        style.map('Secondary.TButton', background=[('active', self.colors['secondary_active'])])
        style.configure('TEntry', fieldbackground=self.colors['entry_bg'], foreground=self.colors['text'], bordercolor=self.colors['secondary'], insertcolor=self.colors['text'])
        style.map('TEntry', background=[('focus', self.colors['entry_bg'])])
        style.configure('TCombobox', foreground='#000000', bordercolor=self.colors['secondary'], arrowcolor=self.colors['text'])
        style.map('TCombobox', selectbackground=[('readonly', self.colors['accent'])], selectforeground=[('readonly', self.colors['text'])])
        style.configure('Vertical.TScrollbar', background=self.colors['secondary'], troughcolor=self.colors['frame_bg'], bordercolor=self.colors['bg'], arrowcolor=self.colors['text'])
        style.map('Vertical.TScrollbar', background=[('active', self.colors['secondary_active'])])

    # ... O resto do código (lógica dos widgets e ações) permanece o mesmo, mas será colado aqui para garantir a integridade do arquivo.
    # A única mudança é nos títulos das caixas de diálogo.

    def _create_param_widgets(self, frame):
        ttk.Label(frame, text="Largura Chapa (mm):").grid(row=0, column=0, sticky="W")
        self.largura_chapa_var = tk.StringVar(value=core.LARGURA_CHAPA_PADRAO)
        ttk.Entry(frame, textvariable=self.largura_chapa_var, width=10).grid(row=0, column=1, padx=5, sticky="W")
        ttk.Label(frame, text="Meta Aprov. (%):").grid(row=1, column=0, sticky="W", pady=(5,0))
        self.excelencia_var = tk.StringVar(value=core.META_EXCELENCIA)
        ttk.Entry(frame, textvariable=self.excelencia_var, width=10).grid(row=1, column=1, padx=5, pady=(5,0), sticky="W")
        ttk.Label(frame, text="Algoritmo:").grid(row=0, column=2, sticky="W", padx=(20,5))
        self.algoritmo_var = tk.StringVar()
        algoritmo_combo = ttk.Combobox(frame, textvariable=self.algoritmo_var, values=["Primeiro Encaixe Decrescente (FFD)", "Melhor Encaixe (Múltiplas Tentativas)"], width=35, state='readonly')
        algoritmo_combo.grid(row=0, column=3, rowspan=2, sticky="W")
        algoritmo_combo.current(0)
        
    def _create_file_action_widgets(self, frame):
        ttk.Button(frame, text="Carregar Pedido", command=self._carregar_pedido, style='Secondary.TButton').pack(fill=tk.X, pady=2)
        ttk.Button(frame, text="Salvar Pedido", command=self._salvar_pedido, style='Secondary.TButton').pack(fill=tk.X, pady=2)

    def _create_control_widgets(self, frame):
        ttk.Button(frame, text="Adicionar Linha", command=self._adicionar_campo_peca, style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame, text="Limpar Lista", command=self._limpar_lista_pecas, style='Secondary.TButton').pack(side=tk.LEFT)
        ttk.Button(frame, text="OTIMIZAR", command=self._otimizar, style="Accent.TButton").pack(side=tk.LEFT, padx=50)
        ttk.Button(frame, text="Exportar Plano de Corte", command=self._exportar_relatorio, style='Secondary.TButton').pack(side=tk.RIGHT)

    def _create_result_widgets(self, frame):
        self.result_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, state="disabled", font=("Courier New", 10), bg=self.colors['entry_bg'], fg=self.colors['text'], relief=tk.FLAT)
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def _adicionar_campo_peca(self):
        row_frame = ttk.Frame(self.pecas_frame)
        row_frame.pack(fill=tk.X, pady=4, padx=5)
        ttk.Label(row_frame, text=f"Item {len(self.pecas_entries) + 1}:").pack(side=tk.LEFT, padx=5)
        ttk.Label(row_frame, text="Largura (mm):").pack(side=tk.LEFT)
        largura_entry = ttk.Entry(row_frame, width=10)
        largura_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(row_frame, text="Qtd:").pack(side=tk.LEFT)
        qtd_entry = ttk.Entry(row_frame, width=8)
        qtd_entry.pack(side=tk.LEFT, padx=5)
        self.pecas_entries.append((largura_entry, qtd_entry))
        
    def _limpar_lista_pecas(self, recriar_campos=True):
        for widgets in self.pecas_entries:
            widgets[0].master.destroy()
        self.pecas_entries = []
        if recriar_campos:
            for _ in range(5): self._adicionar_campo_peca()

    def _coletar_dados_de_entrada(self):
        try:
            largura_chapa = int(self.largura_chapa_var.get())
            excelencia = float(self.excelencia_var.get())
            algoritmo_map = {"Primeiro Encaixe Decrescente (FFD)": "ffd", "Melhor Encaixe (Múltiplas Tentativas)": "best_fit"}
            algoritmo_selecionado = algoritmo_map.get(self.algoritmo_var.get())
        except (ValueError, TypeError):
            messagebox.showerror("CorteX - Erro de Entrada", "A Largura da Chapa e a Meta de Aproveitamento devem ser números válidos.")
            return None, None, None, None
        pecas_dict = {}
        for largura_entry, qtd_entry in self.pecas_entries:
            largura_str = largura_entry.get()
            qtd_str = qtd_entry.get()
            if largura_str and qtd_str:
                try:
                    largura = int(largura_str)
                    qtd = int(qtd_str)
                    if largura > 0 and qtd > 0:
                        pecas_dict[largura] = pecas_dict.get(largura, 0) + qtd
                except ValueError:
                    messagebox.showerror("CorteX - Erro de Entrada", f"Os valores de peça '{largura_str}' e '{qtd_str}' devem ser números inteiros.")
                    return None, None, None, None
        if not pecas_dict:
            messagebox.showwarning("CorteX - Aviso", "Nenhuma peça foi inserida para otimização.")
            return None, None, None, None
        return pecas_dict, largura_chapa, excelencia, algoritmo_selecionado

    def _otimizar(self):
        pecas, largura_chapa, excelencia, algoritmo = self._coletar_dados_de_entrada()
        if pecas is None: return
        relatorio_texto = core.executar_otimizacao(pecas, largura_chapa, excelencia, algoritmo)
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, relatorio_texto)
        self.result_text.config(state="disabled")

    def _salvar_pedido(self):
        pecas_lista = []
        for largura_entry, qtd_entry in self.pecas_entries:
            largura = largura_entry.get()
            qtd = qtd_entry.get()
            if largura and qtd:
                pecas_lista.append({"largura": largura, "quantidade": qtd})
        if not pecas_lista:
            messagebox.showwarning("CorteX", "Não há peças para salvar.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")], title="Salvar Pedido Como...")
        if not filepath: return
        with open(filepath, 'w') as f:
            json.dump(pecas_lista, f, indent=4)
        messagebox.showinfo("CorteX", f"Pedido salvo com sucesso!")

    def _carregar_pedido(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")], title="Carregar Pedido")
        if not filepath: return
        with open(filepath, 'r') as f:
            try:
                pecas_lista = json.load(f)
            except json.JSONDecodeError:
                messagebox.showerror("CorteX", "Arquivo de pedido inválido ou corrompido.")
                return
        self._limpar_lista_pecas(recriar_campos=False)
        for peca in pecas_lista:
            self._adicionar_campo_peca()
            largura_entry, qtd_entry = self.pecas_entries[-1]
            largura_entry.insert(0, str(peca.get("largura", "")))
            qtd_entry.insert(0, str(peca.get("quantidade", "")))
        messagebox.showinfo("CorteX", f"Pedido carregado com sucesso!")

    def _exportar_relatorio(self):
        relatorio_texto = self.result_text.get(1.0, tk.END)
        if len(relatorio_texto.strip()) == 0:
            messagebox.showwarning("CorteX", "Não há plano de corte para exportar.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")], title="Exportar Plano de Corte Como...")
        if not filepath: return
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(relatorio_texto)
        messagebox.showinfo("CorteX", f"Plano de corte exportado com sucesso!")


if __name__ == "__main__":
    root = tk.Tk()
    app = OtimizadorApp(root)
    root.mainloop()