"""Mesa interactiva, dibujo y reproducción de resultados independientes de la búsqueda."""
import math
import tkinter as tk
from tkinter import ttk, messagebox
from algorithms import search, compare, reconstruct_path, scenario, SCENARIOS

BG, PANEL, TABLE = "#0f172a", "#1e293b", "#17263d"
TEXT, MUTED, BLUE = "#f8fafc", "#94a3b8", "#3b82f6"


class DominoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Efecto Dominó · BFS y DFS")
        self.geometry("1180x800")
        self.minsize(1060, 760)
        self.configure(bg=BG)
        self.matrix = [[0]*12 for _ in range(8)]
        self.start = self.target = self.result = self.job = None
        self.running = self.paused = False
        self.groups, self.states = [], {}
        self.index = self.frame = 0
        self.mode = tk.StringVar(value="Colocar")
        self.algorithm = tk.StringVar(value="BFS")
        self.preset = tk.StringVar(value=SCENARIOS[2])
        self.speed = tk.DoubleVar(value=500)
        self.status = tk.StringVar(value="Coloca fichas adyacentes, selecciona el inicio y observa cómo se propaga la reacción")
        self.style_widgets()
        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.algorithm_changed()
        self.example()

    def style_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10), background=PANEL, foreground=TEXT)
        style.configure("TFrame", background=PANEL)
        style.configure("TLabel", background=PANEL, foreground=TEXT)
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure("TButton", background="#334155", foreground=TEXT, borderwidth=0, padding=(9, 7))
        style.map("TButton", background=[("disabled", "#253247"), ("active", "#475569")], foreground=[("disabled", "#64748b")])
        style.configure("Primary.TButton", background=BLUE)
        style.map("Primary.TButton", background=[("disabled", "#253247"), ("active", "#2563eb")])
        style.configure("Tool.TRadiobutton", padding=5, background=PANEL, foreground=MUTED)
        style.map("Tool.TRadiobutton", background=[("selected", "#254772"), ("active", "#334155")], foreground=[("selected", TEXT)])
        style.configure("TCombobox", fieldbackground=TABLE, background="#334155", foreground=TEXT, arrowcolor=TEXT, padding=4)
        style.map("TCombobox", fieldbackground=[("readonly", TABLE)], foreground=[("readonly", TEXT)])
        style.configure("Horizontal.TScale", background=PANEL, troughcolor=TABLE)
        style.configure("Treeview", background=TABLE, fieldbackground=TABLE, foreground=TEXT, rowheight=36, borderwidth=0)
        style.configure("Treeview.Heading", background="#334155", foreground=TEXT, padding=8)
        self.option_add("*TCombobox*Listbox.background", TABLE)
        self.option_add("*TCombobox*Listbox.foreground", TEXT)

    def build_ui(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(18, 12))
        tk.Label(header, text="EFECTO DOMINÓ", font=("Segoe UI", 24, "bold"), bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(header, text="Simulador de estrategias de búsqueda | BFS y DFS", bg=BG, fg=MUTED, font=("Segoe UI", 11)).pack(anchor="w")
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        left = ttk.Frame(body, padding=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(left, text="MESA DE PROPAGACIÓN   /   12 × 8", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        self.canvas = tk.Canvas(left, bg=TABLE, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw())
        self.canvas.bind("<Button-1>", self.click)
        ttk.Label(left, text="● De pie   ·   🟠 Cayendo   ·   Verde: caída   ·   Tenue: inaccesible", style="Muted.TLabel").pack(pady=(8, 2))
        ttk.Label(left, text="Azul: INICIO / ruta   ·   Rosa: META   ·   n: nivel BFS", style="Muted.TLabel").pack()
        self.log = tk.Text(left, height=4, bg=BG, fg=MUTED, relief="flat", padx=8, pady=6, font=("Consolas", 9), state="disabled")
        self.log.pack(fill="x", pady=(8, 0))
        right = ttk.Frame(body, padding=12, width=320)
        right.grid(row=0, column=1, sticky="ns")
        ttk.Label(right, text="01  EDITAR MESA", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tools = ttk.Frame(right)
        tools.pack(fill="x", pady=5)
        for i, mode in enumerate(("Colocar", "Quitar", "Inicio", "Objetivo")):
            ttk.Radiobutton(tools, text=mode, variable=self.mode, value=mode, style="Tool.TRadiobutton").grid(row=i//2, column=i%2, sticky="ew")
        for i in range(2): tools.columnconfigure(i, weight=1)
        ttk.Combobox(right, textvariable=self.preset, values=SCENARIOS, state="readonly", width=29).pack(fill="x")
        row = ttk.Frame(right)
        row.pack(fill="x", pady=5)
        ttk.Button(row, text="Cargar escenario", command=self.example).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Limpiar", command=self.clear).pack(side="left", padx=(5, 0))
        ttk.Label(right, text="02  REPRODUCIR", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(8, 5))
        self.selector = ttk.Combobox(right, textvariable=self.algorithm, values=("BFS", "DFS"), state="readonly")
        self.selector.pack(fill="x")
        self.selector.bind("<<ComboboxSelected>>", lambda e: self.algorithm_changed())
        self.info = ttk.Label(right, wraplength=290, style="Muted.TLabel")
        self.info.pack(anchor="w", pady=6)
        controls = ttk.Frame(right)
        controls.pack(fill="x")
        self.buttons = {}
        actions = [("Iniciar", self.run), ("Pausar", self.pause), ("Reanudar", self.resume), ("Reiniciar caída", self.reset), ("← Retroceder", lambda: self.step(-1)), ("Avanzar →", lambda: self.step(1))]
        for i, (label, command) in enumerate(actions):
            button = ttk.Button(controls, text=label, command=command, style="Primary.TButton" if i == 0 else "TButton")
            button.grid(row=i//2, column=i%2, sticky="ew", padx=2, pady=2)
            self.buttons[label] = button
        for i in range(2): controls.columnconfigure(i, weight=1)
        ttk.Label(right, text="Duración por nivel / paso · rápido → lento", style="Muted.TLabel").pack(pady=(6, 0))
        ttk.Scale(right, from_=160, to=1600, variable=self.speed).pack(fill="x")
        row = ttk.Frame(right)
        row.pack(fill="x", pady=5)
        ttk.Button(row, text="Comparar BFS / DFS", command=self.comparison).pack(side="left", expand=True, fill="x")
        ttk.Button(row, text="¿Cómo funciona?", command=self.help).pack(side="left", padx=(5, 0))
        ttk.Label(left, text="RESULTADOS · CÁLCULO Y REPRODUCCIÓN", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 4), before=self.log)
        cards = ttk.Frame(left)
        cards.pack(fill="x", before=self.log)
        self.metrics = {}
        for i, title in enumerate(("Total", "Alcanzables", "Sin caer", "Explorados", "Nivel / paso actual", "Niveles BFS", "Cálculo (ms)", "Tiempo meta", "Ruta (conexiones)", "Tiempo final BFS")):
            card = tk.Frame(cards, bg=TABLE, padx=7, pady=3)
            card.grid(row=i//5, column=i%5, sticky="nsew", padx=2, pady=2)
            tk.Label(card, text=title, bg=TABLE, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")
            value = tk.Label(card, text="—", bg=TABLE, fg=TEXT, font=("Segoe UI", 12, "bold"))
            value.pack(anchor="w")
            self.metrics[title] = value
        for i in range(5): cards.columnconfigure(i, weight=1)
        tk.Label(self, textvariable=self.status, bg=BG, fg=MUTED, anchor="w", font=("Segoe UI", 9)).pack(fill="x", padx=24, pady=10)

    def algorithm_changed(self):
        self.reset()
        self.info.config(text="BFS · Cola FIFO. Cada nivel inicia su caída al mismo tiempo." if self.algorithm.get() == "BFS" else "DFS · Pila LIFO. Solo exploración: no representa tiempos de caída mínimos.")

    def geometry_cell(self):
        return max(1, self.canvas.winfo_width())/12, max(1, self.canvas.winfo_height())/8

    def draw(self):
        self.canvas.delete("all")
        w, h = self.geometry_cell()
        for r in range(9): self.canvas.create_line(0, r*h, 12*w, r*h, fill="#263850")
        for c in range(13): self.canvas.create_line(c*w, 0, c*w, 8*h, fill="#263850")
        if self.result:
            # Conexiones debajo de las piezas: solo las ya activadas en la reproducción.
            for node, parent in self.result.parents.items():
                if parent is not None and node in self.states:
                    r,c = node
                    y,x = parent
                    self.canvas.create_line((x+.5)*w, (y+.5)*h, (c+.5)*w, (r+.5)*h, fill="#22c55e", width=2)
            path = reconstruct_path(self.result, self.target)
            for a,b in zip(path, path[1:]):
                self.canvas.create_line((a[1]+.5)*w, (a[0]+.5)*h, (b[1]+.5)*w, (b[0]+.5)*h, fill="#60a5fa", width=3, dash=(4, 3))
        for r in range(8):
            for c in range(12):
                if self.matrix[r][c]: self.draw_tile(r,c,w,h)

    def draw_tile(self, r, c, w, h):
        node = (r,c)
        progress = self.states.get(node, 0)
        inactive = self.result is not None and node not in self.result.parents
        color = "#64748b" if inactive else "#22c55e" if progress >= 1 else "#f59e0b" if progress > 0 else "#e2e8f0"
        outline = "#f472b6" if node == self.target else "#60a5fa" if node == self.start else "#94a3b8"
        # Rotar juntos la silueta, la separación y los puntos alrededor del centro.
        size = min(w, h)
        tw, th = size*.39, size*.72
        angle = progress*math.pi/2
        co, si = math.cos(angle), math.sin(angle)
        cx, cy = (c+.5)*w, (r+.5)*h
        def point(x,y): return cx+x*co-y*si, cy+x*si+y*co
        a,b,k = tw/2, th/2, size*.055
        local = [(-a+k,-b),(a-k,-b),(a,-b+k),(a,b-k),(a-k,b),(-a+k,b),(-a,b-k),(-a,-b+k)]
        points = [v for x,y in local for v in point(x,y)]
        self.canvas.create_polygon(*[v+3 for v in points], smooth=True, fill="#0b1220", outline="")
        self.canvas.create_polygon(*points, smooth=True, fill=color, outline=outline, width=2)
        self.canvas.create_line(*point(-a+3,0), *point(a-3,0), fill="#334155", width=1)
        for x,y in [(0,-th*.24),(-tw*.23,th*.16),(tw*.23,th*.32)]:
            px,py = point(x,y)
            radius = max(1.6,size*.035)
            self.canvas.create_oval(px-radius,py-radius,px+radius,py+radius,fill="#17263d",outline="")
        label = "INICIO · META" if node == self.start == self.target else "INICIO" if node == self.start else "META" if node == self.target else ""
        if label: self.canvas.create_text(cx, r*h+6, text=label, fill=outline, font=("Segoe UI", 7, "bold"))
        if self.result and self.result.algorithm == "BFS" and node in self.result.levels:
            self.canvas.create_text((c+1)*w-4,(r+1)*h-6,text=f"n{self.result.levels[node]}",fill=MUTED,font=("Segoe UI",7),anchor="e")

    def click(self, event):
        if self.running:
            self.status.set("Reinicia la caída para editar la mesa.")
            return
        w,h = self.geometry_cell()
        r,c = int(event.y/h),int(event.x/w)
        if not (0<=r<8 and 0<=c<12): return
        mode = self.mode.get()
        if mode in ("Inicio", "Objetivo") and not self.matrix[r][c]:
            self.status.set("El inicio y la meta deben estar sobre una ficha.")
            return
        self.reset()
        if mode == "Colocar": self.matrix[r][c] = 1
        elif mode == "Quitar":
            self.matrix[r][c] = 0
            if self.start == (r,c): self.start = None
            if self.target == (r,c): self.target = None
        elif mode == "Inicio": self.start = (r,c)
        else: self.target = None if self.target == (r,c) else (r,c)
        self.draw()
        self.update_stats()

    def cancel_timer(self):
        if self.job is not None: self.after_cancel(self.job)
        self.job = None

    def reset(self):
        self.cancel_timer()
        self.running = self.paused = False
        self.states, self.groups = {}, []
        self.result = None
        self.index = self.frame = 0
        self.selector.config(state="readonly")
        self.write_log("")
        self.draw()
        self.update_stats()
        self.status.set("Coloca fichas adyacentes, selecciona el inicio y observa cómo se propaga la reacción")

    def clear(self):
        self.reset()
        self.matrix = [[0]*12 for _ in range(8)]
        self.start = self.target = None
        self.draw()
        self.update_stats()

    def example(self):
        self.reset()
        self.matrix, self.start, self.target = scenario(self.preset.get())
        self.draw()
        self.update_stats()
        self.status.set(f"{self.preset.get()} · Listo para iniciar. Puedes editar las fichas.")

    def valid(self):
        if self.start is None:
            messagebox.showinfo("Falta el inicio", "Coloca fichas y selecciona una ficha inicial.")
            return False
        return True

    def prepare(self):
        if not self.valid(): return False
        self.reset()
        self.result = search(self.matrix, self.start, self.algorithm.get())
        if self.result.algorithm == "BFS":
            self.groups = [[] for _ in range(max(self.result.levels.values())+1)]
            for node in self.result.order: self.groups[self.result.levels[node]].append(node)
        else: self.groups = [[node] for node in self.result.order]
        self.running = True
        self.selector.config(state="disabled")
        self.write_log("Orden | (fila, columna) | " + ("nivel / tiempo" if self.result.algorithm == "BFS" else "profundidad DFS (no tiempo)") + "\n" + "\n".join(f"{i+1:>3} | ({r+1}, {c+1}) | {self.result.levels[(r,c)]}" for i,(r,c) in enumerate(self.result.order)))
        return True

    def run(self):
        if self.running: return
        if self.prepare(): self.tick()

    def tick(self):
        self.job = None
        if self.paused or not self.running: return
        if self.index >= len(self.groups):
            self.finish()
            return
        self.frame += 1
        for node in self.groups[self.index]: self.states[node] = min(1, self.frame/12)
        self.status.set(f"{self.result.algorithm} · {'Nivel' if self.result.algorithm == 'BFS' else 'Paso de exploración'} {self.index if self.result.algorithm == 'BFS' else self.index+1} en reproducción")
        self.draw()
        self.update_stats()
        if self.frame >= 12:
            self.index += 1
            self.frame = 0
        self.job = self.after(max(1, int(self.speed.get()/12)), self.tick)

    def finish(self):
        self.running = self.paused = False
        self.selector.config(state="readonly")
        self.status.set("Simulación finalizada · Puedes revisar los pasos o editar la mesa.")
        self.update_stats()

    def pause(self):
        if not self.running: return
        self.cancel_timer()
        self.paused = True
        self.status.set("En pausa · Reanuda o revisa la secuencia con las flechas.")
        self.update_stats()

    def resume(self):
        if not self.paused: return
        self.paused = False
        self.running = True
        self.tick()

    def step(self, direction):
        if self.result is None and not self.prepare(): return
        self.cancel_timer()
        self.running = self.paused = True
        # El índice cuenta grupos completos; se reconstruye desde los grupos precalculados.
        self.index = max(0, min(len(self.groups), self.index + direction))
        self.frame = 0
        self.states = {node: 1 for group in self.groups[:self.index] for node in group}
        self.selector.config(state="disabled")
        self.draw()
        self.update_stats()
        self.status.set(f"Revisión en pausa · {self.index} de {len(self.groups)} grupos completados")

    def update_stats(self):
        total = sum(map(sum,self.matrix))
        fallen = sum(value >= 1 for value in self.states.values())
        values = {key: "—" for key in self.metrics}
        values.update({"Total":total, "Sin caer":total-fallen})
        if self.result:
            result = self.result
            path = reconstruct_path(result,self.target)
            values.update({"Alcanzables":len(result.order), "Explorados":len(result.order), "Cálculo (ms)":f"{result.seconds*1000:.3f}", "Ruta (conexiones)":len(path)-1 if path else "Sin ruta"})
            if result.algorithm == "BFS":
                values.update({"Nivel / paso actual": min(self.index,len(self.groups)-1), "Niveles BFS":len(self.groups), "Tiempo meta":result.levels.get(self.target,"Sin ruta"), "Tiempo final BFS":len(self.groups)-1})
            else:
                values["Nivel / paso actual"] = min(self.index+1,len(self.groups))
                values["Tiempo meta"] = "No aplica"
        for key,value in values.items(): self.metrics[key].config(text=str(value))
        for label in ("Iniciar",): self.buttons[label].config(state="disabled" if self.running else "normal")
        self.buttons["Pausar"].config(state="normal" if self.running and not self.paused else "disabled")
        self.buttons["Reanudar"].config(state="normal" if self.paused else "disabled")

    def write_log(self, text):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.insert("end", text)
        self.log.config(state="disabled")

    def comparison(self):
        if not self.valid(): return
        results = compare(self.matrix,self.start,self.target)
        win = tk.Toplevel(self)
        win.title("Comparación BFS vs DFS")
        win.configure(bg=PANEL)
        ttk.Label(win, text="MISMA MESA · MISMA CONDICIÓN DE TERMINACIÓN", font=("Segoe UI", 14, "bold")).pack(padx=20,pady=15)
        columns = ("Algoritmo", "Estructura", "Explorados", "Ruta", "Cálculo (ms)", "¿Mínima?", "Resultado")
        table = ttk.Treeview(win, columns=columns, show="headings", height=2)
        for col in columns:
            table.heading(col,text=col)
            table.column(col,width=120,anchor="center")
        table.pack(padx=20,pady=10,fill="x")
        paths = [reconstruct_path(result,self.target) for result in results]
        for result,path in zip(results,paths):
            table.insert("","end",values=(result.algorithm,"Cola FIFO" if result.algorithm == "BFS" else "Pila LIFO",len(result.order),len(path)-1 if path else "Sin ruta",f"{result.seconds*1000:.4f}","Sí" if result.algorithm == "BFS" else "No garantiza", "Sin meta" if self.target is None else "Encontrada" if path else "Inalcanzable"))
        conclusion = "No se seleccionó meta: ambos recorrieron todo el componente alcanzable." if self.target is None else "La meta es inalcanzable desde el inicio. Ambos agotaron su frontera."
        if all(paths):
            a,b = (len(path)-1 for path in paths)
            conclusion = f"BFS encontró una ruta de {a} conexiones y DFS de {b}. " + ("BFS obtuvo la ruta más corta." if a<b else "En esta mesa las rutas tienen igual longitud; DFS no la garantiza en general.")
        ttk.Label(win,text="Explorados = nodos extraídos y procesados, incluida la meta.\nAmbos se detienen al extraer la meta; sin meta o si es inaccesible, agotan la frontera.\nRuta = número de conexiones. Cálculo excluye animación; BFS no siempre usa menos CPU.",style="Muted.TLabel").pack(padx=20,pady=10,anchor="w")
        ttk.Label(win,text=conclusion,wraplength=820).pack(padx=20,pady=(0,20),anchor="w")

    def help(self):
        win = tk.Toplevel(self)
        win.title("¿Cómo funciona?")
        win.configure(bg=PANEL)
        content = [
            ("Un grafo sobre la mesa", "Cada ficha es un nodo. Dos vecinas ortogonales forman una conexión de costo 1. Los huecos interrumpen la reacción."),
            ("BFS · Primero en entrar, primero en salir", "La cola FIFO procesa primero las fichas más cercanas. Por eso sus niveles son distancias mínimas: cada conexión añade una unidad. Un nivel inicia su animación al mismo tiempo."),
            ("DFS · Último en entrar, primero en salir", "La pila LIFO profundiza antes de explorar otras ramas. Su orden y su ruta pueden ser diferentes. No calcula tiempos mínimos de propagación."),
            ("Agente basado en metas", "Lee la mesa, inicio y meta; determina qué fichas se alcanzan y calcula niveles y una ruta mínima con BFS. Actualiza la visualización para mostrar el resultado."),
            ("Cómo leer los resultados", "Alcanzables y explorados describen el cálculo completo. Sin caer se actualiza durante la animación. Los niveles incluyen el 0. Ruta cuenta conexiones; tiempo meta solo aplica a BFS."),
            ("Modelo simplificado", "Entorno observable, determinista, estático durante la búsqueda y discreto. No representa fuerzas, gravedad ni colisiones reales. Costo g(n)=g(padre)+1; sin heurística. Tiempo O(V+E).")]
        for title,text in content:
            ttk.Label(win,text=title,font=("Segoe UI",11,"bold")).pack(anchor="w",padx=20,pady=(12,3))
            ttk.Label(win,text=text,wraplength=560,style="Muted.TLabel").pack(anchor="w",padx=20)
        ttk.Button(win,text="Entendido",command=win.destroy).pack(pady=16)

    def close(self):
        self.cancel_timer()
        self.destroy()
