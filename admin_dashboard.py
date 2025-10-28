import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import math
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import pandas as pd
import os


class ScadaData:
    def __init__(self):
        self.potencia_total = 42.0
        self.voltaje = 220.5
        self.corriente = 185.0
        self.frecuencia = 60.0
        self.potencia_activa = 35.3
        self.potencia_reactiva = 18.7
        self.alarmas = [
            {
                "tipo": "⚠️",
                "mensaje": "Corriente cercana al límite (185A)",
                "nivel": "advertencia",
            },
            {
                "tipo": "🔧",
                "mensaje": "Mantenimiento programado para hoy",
                "nivel": "info",
            },
            {
                "tipo": "✅",
                "mensaje": "Sistema operando normalmente",
                "nivel": "normal",
            },
            {"tipo": "🔋", "mensaje": "Batería de respaldo al 85%", "nivel": "info"},
            {
                "tipo": "🌡️",
                "mensaje": "Temperatura del transformador estable",
                "nivel": "normal",
            },
            {
                "tipo": "📡",
                "mensaje": "Comunicación con subestación normal",
                "nivel": "normal",
            },
            {
                "tipo": "⚡",
                "mensaje": "Pico de voltaje detectado",
                "nivel": "advertencia",
            },
        ]
        # Nuevos atributos para el modo Excel
        self.excel_data = None
        self.excel_loaded = False
        self.original_data = None
        self.current_excel_index = 0  # Para simular variación en datos Excel


class AdminDashboard:
    def __init__(self, root, user_data, on_logout):
        self.root = root
        self.user_data = user_data
        self.on_logout = on_logout
        self.scada_data = ScadaData()
        self.current_section = None
        self.content_container = None
        self.selected_parameter = "Potencia"
        self.setup_ui()
        self.start_animations()

    def setup_ui(self):
        self.root.title(f"SCADA ELÉCTRICO - {self.user_data['nombre']}")
        self.root.geometry("1600x900")
        self.root.configure(bg="#0f172a")

        # Configurar grid principal
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Frame principal
        main_container = tk.Frame(self.root, bg="#0f172a")
        main_container.grid(
            row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10
        )

        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        # Header
        self.create_header(main_container)

        # Contenido principal - Sidebar + Dashboard
        content_frame = tk.Frame(main_container, bg="#0f172a")
        content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)

        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.create_sidebar(content_frame)

        # Contenedor de contenido dinámico
        self.content_container = tk.Frame(content_frame, bg="#0f172a")
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        # Mostrar dashboard por defecto
        self.show_dashboard()

    def create_header(self, parent):
        """Header del sistema"""
        header_frame = tk.Frame(parent, bg="#1e293b", height=80, relief="flat")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        header_frame.grid_propagate(False)

        header_frame.grid_columnconfigure(0, weight=1)

        # Título principal
        title_frame = tk.Frame(header_frame, bg="#1e293b")
        title_frame.grid(row=0, column=0, sticky="w", padx=30)

        tk.Label(
            title_frame,
            text="⚡ SISTEMA SCADA ELÉCTRICO",
            font=("Arial", 18, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
        ).grid(row=0, column=0, sticky="w")

        # Indicador de modo
        self.mode_indicator = tk.Label(
            title_frame,
            text="🔴 MODO SCADA - DATOS EN TIEMPO REAL",
            font=("Arial", 11, "bold"),
            fg="#10b981",
            bg="#1e293b",
        )
        self.mode_indicator.grid(row=1, column=0, sticky="w")

        # Info usuario
        user_frame = tk.Frame(header_frame, bg="#1e293b")
        user_frame.grid(row=0, column=1, sticky="e", padx=30)

        tk.Label(
            user_frame,
            text=f"👑 {self.user_data['nombre']}",
            font=("Arial", 11, "bold"),
            fg="#e2e8f0",
            bg="#1e293b",
        ).grid(row=0, column=0, sticky="e")
        tk.Label(
            user_frame,
            text=self.user_data["role"],
            font=("Arial", 10),
            fg="#94a3b8",
            bg="#1e293b",
        ).grid(row=1, column=0, sticky="e")

    def update_mode_indicator(self):
        """Actualizar el indicador de modo"""
        if self.scada_data.excel_loaded:
            self.mode_indicator.config(
                text="📊 MODO EXCEL - DATOS ESTÁTICOS CARGADOS", fg="#f59e0b"
            )
        else:
            self.mode_indicator.config(
                text="🔴 MODO SCADA - DATOS EN TIEMPO REAL", fg="#10b981"
            )

    def create_sidebar(self, parent):
        """Panel de navegación lateral para Administrador"""
        sidebar_frame = tk.Frame(parent, bg="#1e293b", width=250, relief="flat")
        sidebar_frame.grid(row=0, column=0, sticky="ns", padx=(0, 15))
        sidebar_frame.grid_propagate(False)

        # Título navegación
        nav_title = tk.Frame(sidebar_frame, bg="#38bdf8", height=50)
        nav_title.pack(fill="x", pady=(0, 20))
        nav_title.pack_propagate(False)

        tk.Label(
            nav_title,
            text="ADMINISTRADOR",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#38bdf8",
        ).pack(expand=True)

        # Botones de navegación para Administrador
        nav_items = [
            ("📊", "Dashboard", "#3b82f6"),
            ("📋", "Historial", "#8b5cf6"),
            ("📁", "Cargar Excel", "#06b6d4"),
            ("⚙️", "Configuración", "#f59e0b"),
            ("📈", "Reportes", "#10b981"),
            ("👥", "Usuarios", "#ec4899"),
            ("🚪", "Salir", "#64748b"),
        ]

        for emoji, text, color in nav_items:
            btn = tk.Button(
                sidebar_frame,
                text=f"   {emoji} {text}",
                font=("Arial", 12),
                bg="#1e293b",
                fg="#e2e8f0",
                activebackground=color,
                activeforeground="#0f172a",
                relief="flat",
                bd=0,
                anchor="w",
                cursor="hand2",
                command=lambda cmd=text.lower(): self.navigate(cmd),
            )
            btn.pack(fill="x", padx=15, pady=8, ipady=12)

            # Efecto hover
            def on_enter(e, button=btn, color=color):
                button.config(bg=color, fg="#0f172a")

            def on_leave(e, button=btn):
                button.config(bg="#1e293b", fg="#e2e8f0")

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    def navigate(self, option):
        """Navegación entre secciones para Administrador"""
        if "salir" in option.lower():
            if messagebox.askyesno(
                "Cerrar Sesión", "¿Está seguro que desea cerrar la sesión?"
            ):
                self.root.destroy()
                self.on_logout()
        elif "historial" in option.lower():
            self.show_history()
        elif "dashboard" in option.lower():
            self.show_dashboard()
        elif "cargar excel" in option.lower():
            self.cargar_excel()
        elif "configuración" in option.lower():
            self.show_configuracion()
        elif "reportes" in option.lower():
            self.mostrar_reportes()
        elif "usuarios" in option.lower():
            self.gestionar_usuarios()
        else:
            messagebox.showinfo("Navegación", f"Accediendo a: {option.title()}")

    def create_dashboard(self, parent):
        """Panel principal del dashboard con scroll"""
        # Frame principal del dashboard
        dash_main = tk.Frame(parent, bg="#0f172a")
        dash_main.pack(fill="both", expand=True)

        dash_main.grid_columnconfigure(0, weight=1)
        dash_main.grid_rowconfigure(1, weight=1)

        # Métrica principal
        self.create_power_metric(dash_main)

        # Frame scrollable para el contenido
        canvas_container = tk.Frame(dash_main, bg="#0f172a")
        canvas_container.grid(row=1, column=0, sticky="nsew", pady=10)

        canvas_container.grid_columnconfigure(0, weight=1)
        canvas_container.grid_rowconfigure(0, weight=1)

        # Canvas y scrollbar
        self.canvas = tk.Canvas(canvas_container, bg="#0f172a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            canvas_container, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg="#0f172a")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            width=self.canvas.winfo_width(),
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Empaquetado
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Configurar scroll con rueda del mouse
        self.canvas.bind("<Enter>", self._bind_to_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_from_mousewheel)

        # Configurar redimensionamiento
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Contenido del dashboard
        self.create_dashboard_content(self.scrollable_frame)

        # Dibujar gráficos iniciales después de un breve delay
        self.root.after(100, self.draw_initial_charts)

    def draw_initial_charts(self):
        """Dibujar gráficos iniciales después de que los canvas tengan tamaño"""
        if self.current_section == "dashboard":
            self.draw_voltage_chart()
            self.draw_current_chart()
            self.draw_power_chart()
            self.draw_frequency_chart()

    def on_frame_configure(self, event):
        """Actualizar scrollregion cuando cambia el tamaño del frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Ajustar el ancho del frame interno cuando cambia el tamaño del canvas"""
        self.canvas.itemconfig("all", width=event.width)
        # Redibujar gráficos cuando el canvas cambia de tamaño
        if self.current_section == "dashboard":
            self.root.after(100, self.draw_initial_charts)

    def _bind_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_from_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_power_metric(self, parent):
        """Métrica de potencia principal - CORREGIDO: Formato de decimales"""
        power_frame = tk.Frame(parent, bg="#1e293b", relief="flat", bd=0, height=120)
        power_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        power_frame.grid_propagate(False)

        power_frame.grid_columnconfigure(0, weight=1)

        content = tk.Frame(power_frame, bg="#1e293b")
        content.grid(row=0, column=0, sticky="nsew", padx=30, pady=20)

        # Título y valor
        title_frame = tk.Frame(content, bg="#1e293b")
        title_frame.pack(anchor="w")

        tk.Label(
            title_frame,
            text="POTENCIA TOTAL DEL SISTEMA",
            font=("Arial", 16, "bold"),
            fg="#94a3b8",
            bg="#1e293b",
        ).pack(anchor="w")

        self.power_value = tk.Label(
            title_frame,
            text=f"{self.scada_data.potencia_total:.1f} MW",
            font=("Arial", 36, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
        )
        self.power_value.pack(anchor="w", pady=(10, 0))

        # Indicadores
        indicators_frame = tk.Frame(content, bg="#1e293b")
        indicators_frame.pack(anchor="w", pady=(15, 0))

        tk.Label(
            indicators_frame,
            text="↗️ TENDENCIA ESTABLE",
            font=("Arial", 10, "bold"),
            fg="#10b981",
            bg="#1e293b",
        ).pack(side="left")

        tk.Label(
            indicators_frame, text="•", font=("Arial", 12), fg="#64748b", bg="#1e293b"
        ).pack(side="left", padx=10)

        tk.Label(
            indicators_frame,
            text="🟢 SISTEMA OPERATIVO",
            font=("Arial", 10, "bold"),
            fg="#10b981",
            bg="#1e293b",
        ).pack(side="left")

    def create_dashboard_content(self, parent):
        """Contenido del dashboard"""
        parent.grid_columnconfigure(0, weight=1)

        # Grid de métricas (2x2)
        metrics_frame = tk.Frame(parent, bg="#0f172a")
        metrics_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        metrics_frame.grid_columnconfigure(0, weight=1)
        metrics_frame.grid_columnconfigure(1, weight=1)

        # Fila 1 - Voltaje y Corriente
        self.create_voltage_card(metrics_frame, 0, 0)
        self.create_current_card(metrics_frame, 0, 1)

        # Fila 2 - Potencia y Frecuencia
        self.create_power_card(metrics_frame, 1, 0)
        self.create_frequency_card(metrics_frame, 1, 1)

        # Panel de alarmas
        self.create_alarms_panel(parent)

        # Panel de estadísticas
        self.create_stats_panel(parent)

    def create_voltage_card(self, parent, row, col):
        """Tarjeta de voltaje mejorada"""
        card_frame = tk.Frame(parent, bg="#1e293b", relief="flat", bd=0)
        card_frame.grid(row=row, column=col, sticky="nsew", padx=7, pady=7)

        # Header con gradiente
        header = tk.Frame(card_frame, bg="#1e40af", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_content = tk.Frame(header, bg="#1e40af")
        header_content.pack(fill="both", expand=True, padx=20)

        tk.Label(
            header_content,
            text="⚡ VOLTAJE DEL SISTEMA",
            font=("Arial", 13, "bold"),
            fg="white",
            bg="#1e40af",
        ).pack(side="left")

        # Icono decorativo
        tk.Label(
            header_content, text="🔌", font=("Arial", 16), fg="white", bg="#1e40af"
        ).pack(side="right")

        # Contenido principal
        content = tk.Frame(card_frame, bg="#1e293b", padx=25, pady=25)
        content.pack(fill="both", expand=True)

        # Valor principal con icono
        value_frame = tk.Frame(content, bg="#1e293b")
        value_frame.pack(fill="x", pady=(0, 15))

        self.voltage_value_label = tk.Label(
            value_frame,
            text=f"{self.scada_data.voltaje:.1f} V",
            font=("Arial", 28, "bold"),
            fg="#60a5fa",
            bg="#1e293b",
        )
        self.voltage_value_label.pack(anchor="w")

        # Información adicional
        info_frame = tk.Frame(content, bg="#1e293b")
        info_frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            info_frame,
            text="Línea Principal • Fase A-B-C",
            font=("Arial", 10),
            fg="#94a3b8",
            bg="#1e293b",
        ).pack(anchor="w")

        # Estado y rango
        status_frame = tk.Frame(content, bg="#1e293b")
        status_frame.pack(fill="x")

        status = "ÓPTIMO" if 215 <= self.scada_data.voltaje <= 225 else "VARIABLE"
        status_color = "#10b981" if 215 <= self.scada_data.voltaje <= 225 else "#f59e0b"

        tk.Label(
            status_frame,
            text=f"🟢 {status}",
            font=("Arial", 11, "bold"),
            fg=status_color,
            bg="#1e293b",
        ).pack(side="left")

        tk.Label(
            status_frame,
            text=f"Rango: 215V - 225V",
            font=("Arial", 10),
            fg="#64748b",
            bg="#1e293b",
        ).pack(side="right")

        # Gráfico mejorado
        chart_frame = tk.Frame(content, bg="#0f172a", height=80)
        chart_frame.pack(fill="x", pady=(20, 0))
        chart_frame.pack_propagate(False)

        self.voltage_canvas = tk.Canvas(
            chart_frame, bg="#0f172a", highlightthickness=0, height=80
        )
        self.voltage_canvas.pack(fill="both", expand=True)

    def create_current_card(self, parent, row, col):
        """Tarjeta de corriente mejorada"""
        card_frame = tk.Frame(parent, bg="#1e293b", relief="flat", bd=0)
        card_frame.grid(row=row, column=col, sticky="nsew", padx=7, pady=7)

        # Header con gradiente
        header = tk.Frame(card_frame, bg="#059669", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_content = tk.Frame(header, bg="#059669")
        header_content.pack(fill="both", expand=True, padx=20)

        tk.Label(
            header_content,
            text="🔌 CORRIENTE DEL SISTEMA",
            font=("Arial", 13, "bold"),
            fg="white",
            bg="#059669",
        ).pack(side="left")

        # Icono decorativo
        tk.Label(
            header_content, text="📊", font=("Arial", 16), fg="white", bg="#059669"
        ).pack(side="right")

        # Contenido principal
        content = tk.Frame(card_frame, bg="#1e293b", padx=25, pady=25)
        content.pack(fill="both", expand=True)

        # Valor principal
        value_frame = tk.Frame(content, bg="#1e293b")
        value_frame.pack(fill="x", pady=(0, 15))

        self.current_value_label = tk.Label(
            value_frame,
            text=f"{self.scada_data.corriente:.1f} A",
            font=("Arial", 28, "bold"),
            fg="#34d399",
            bg="#1e293b",
        )
        self.current_value_label.pack(anchor="w")

        # Información adicional
        info_frame = tk.Frame(content, bg="#1e293b")
        info_frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            info_frame,
            text="Transformador Principal • Carga Activa",
            font=("Arial", 10),
            fg="#94a3b8",
            bg="#1e293b",
        ).pack(anchor="w")

        # Estado y límite
        status_frame = tk.Frame(content, bg="#1e293b")
        status_frame.pack(fill="x")

        status = "NORMAL" if self.scada_data.corriente <= 180 else "ALERTA"
        status_color = "#10b981" if self.scada_data.corriente <= 180 else "#f59e0b"
        icon = "🟢" if self.scada_data.corriente <= 180 else "⚠️"

        tk.Label(
            status_frame,
            text=f"{icon} {status}",
            font=("Arial", 11, "bold"),
            fg=status_color,
            bg="#1e293b",
        ).pack(side="left")

        tk.Label(
            status_frame,
            text=f"Límite: 200A",
            font=("Arial", 10),
            fg="#64748b",
            bg="#1e293b",
        ).pack(side="right")

        # Gráfico mejorado
        chart_frame = tk.Frame(content, bg="#0f172a", height=80)
        chart_frame.pack(fill="x", pady=(20, 0))
        chart_frame.pack_propagate(False)

        self.current_canvas = tk.Canvas(
            chart_frame, bg="#0f172a", highlightthickness=0, height=80
        )
        self.current_canvas.pack(fill="both", expand=True)

    def create_power_card(self, parent, row, col):
        """Tarjeta de potencia mejorada"""
        card_frame = tk.Frame(parent, bg="#1e293b", relief="flat", bd=0)
        card_frame.grid(row=row, column=col, sticky="nsew", padx=7, pady=7)

        # Header con gradiente mejorado
        header = tk.Frame(card_frame, bg="#d97706", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_content = tk.Frame(header, bg="#d97706")
        header_content.pack(fill="both", expand=True, padx=50)

        tk.Label(
            header_content,
            text="📊 DISTRIBUCIÓN DE POTENCIA",
            font=("Arial", 13, "bold"),
            fg="white",
            bg="#d97706",
        ).pack(side="left")

        # Icono decorativo
        tk.Label(
            header_content, text="⚡", font=("Arial", 16), fg="white", bg="#d97706"
        ).pack(side="right")

        # Contenido principal
        content = tk.Frame(card_frame, bg="#1e293b", padx=25, pady=20)
        content.pack(fill="both", expand=True)

        # Valores de potencia simplificados
        values_frame = tk.Frame(content, bg="#1e293b")
        values_frame.pack(fill="x", pady=(0, 10))

        # Solo mostrar valores sin barras de progreso
        active_frame = tk.Frame(values_frame, bg="#1e293b")
        active_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            active_frame,
            text="Potencia Activa:",
            font=("Arial", 11),
            fg="#94a3b8",
            bg="#1e293b",
        ).pack(side="left")

        self.power_active_label = tk.Label(
            active_frame,
            text=f"{self.scada_data.potencia_activa:.1f} MW",
            font=("Arial", 11, "bold"),
            fg="#fbbf24",
            bg="#1e293b",
        )
        self.power_active_label.pack(side="right")

        reactive_frame = tk.Frame(values_frame, bg="#1e293b")
        reactive_frame.pack(fill="x", pady=(5, 0))

        tk.Label(
            reactive_frame,
            text="Potencia Reactiva:",
            font=("Arial", 11),
            fg="#94a3b8",
            bg="#1e293b",
        ).pack(side="left")

        self.power_reactive_label = tk.Label(
            reactive_frame,
            text=f"{self.scada_data.potencia_reactiva:.1f} MVAR",
            font=("Arial", 11, "bold"),
            fg="#60a5fa",
            bg="#1e293b",
        )
        self.power_reactive_label.pack(side="right")

        # Factor de potencia simplificado
        pf_frame = tk.Frame(content, bg="#1e293b")
        pf_frame.pack(fill="x", pady=(10, 0))

        tk.Label(
            pf_frame,
            text="Factor de Potencia: 0.95",
            font=("Arial", 11),
            fg="#94a3b8",
            bg="#1e293b",
        ).pack(side="left")

        tk.Label(
            pf_frame,
            text="EXCELENTE",
            font=("Arial", 11, "bold"),
            fg="#10b981",
            bg="#1e293b",
        ).pack(side="right")

        # Gráfico circular MÁS GRANDE
        chart_frame = tk.Frame(content, bg="#0f172a", height=180)
        chart_frame.pack(fill="x", pady=(15, 0))
        chart_frame.pack_propagate(False)

        self.power_canvas = tk.Canvas(
            chart_frame, bg="#0f172a", highlightthickness=0, height=180
        )
        self.power_canvas.pack(fill="both", expand=True)

    def create_frequency_card(self, parent, row, col):
        """Tarjeta de frecuencia mejorada con círculo más grande y mejorado"""
        card_frame = tk.Frame(parent, bg="#1e293b", relief="flat", bd=0)
        card_frame.grid(row=row, column=col, sticky="nsew", padx=7, pady=7)

        # Header con gradiente mejorado
        header = tk.Frame(card_frame, bg="#7c3aed", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_content = tk.Frame(header, bg="#7c3aed")
        header_content.pack(fill="both", expand=True, padx=20)

        tk.Label(
            header_content,
            text="🔄 FRECUENCIA DEL SISTEMA",
            font=("Arial", 13, "bold"),
            fg="white",
            bg="#7c3aed",
        ).pack(side="left")

        # Icono decorativo
        tk.Label(
            header_content, text="🎛️", font=("Arial", 16), fg="white", bg="#7c3aed"
        ).pack(side="right")

        # Contenido principal
        content = tk.Frame(card_frame, bg="#1e293b", padx=25, pady=20)
        content.pack(fill="both", expand=True)

        # Valor principal con diseño mejorado
        value_frame = tk.Frame(content, bg="#1e293b")
        value_frame.pack(fill="x", pady=(0, 10))

        self.freq_value_label = tk.Label(
            value_frame,
            text=f"{self.scada_data.frecuencia:.2f} Hz",
            font=("Arial", 28, "bold"),
            fg="#a78bfa",
            bg="#1e293b",
        )
        self.freq_value_label.pack(anchor="w")

        # Información de red
        info_frame = tk.Frame(content, bg="#1e293b")
        info_frame.pack(fill="x", pady=(0, 15))

        tk.Label(
            info_frame,
            text="Red Nacional Interconectada • Estabilidad Garantizada",
            font=("Arial", 10),
            fg="#94a3b8",
            bg="#1e293b",
        ).pack(anchor="w")

        # Estado y calidad
        status_frame = tk.Frame(content, bg="#1e293b")
        status_frame.pack(fill="x", pady=(0, 15))

        # Estado
        status = "ESTABLE" if 59.8 <= self.scada_data.frecuencia <= 60.2 else "VARIABLE"
        status_color = (
            "#10b981" if 59.8 <= self.scada_data.frecuencia <= 60.2 else "#f59e0b"
        )

        status_left = tk.Frame(status_frame, bg="#1e293b")
        status_left.pack(side="left", fill="x", expand=True)

        tk.Label(
            status_left,
            text=f"🟢 {status}",
            font=("Arial", 11, "bold"),
            fg=status_color,
            bg="#1e293b",
        ).pack(anchor="w")

        tk.Label(
            status_left,
            text=f"Rango: 59.8 - 60.2 Hz",
            font=("Arial", 9),
            fg="#64748b",
            bg="#1e293b",
        ).pack(anchor="w", pady=(2, 0))

        # Calidad
        status_right = tk.Frame(status_frame, bg="#1e293b")
        status_right.pack(side="right")

        deviation = abs(self.scada_data.frecuencia - 60.0)
        quality = (
            "ÓPTIMA"
            if deviation <= 0.1
            else "ACEPTABLE" if deviation <= 0.2 else "CRÍTICA"
        )
        quality_color = (
            "#10b981"
            if deviation <= 0.1
            else "#f59e0b" if deviation <= 0.2 else "#ef4444"
        )

        tk.Label(
            status_right,
            text=f"Calidad: {quality}",
            font=("Arial", 10, "bold"),
            fg=quality_color,
            bg="#1e293b",
        ).pack(anchor="e")

        # Medidor MEJORADO Y MÁS GRANDE
        chart_frame = tk.Frame(content, bg="#0f172a", height=180)
        chart_frame.pack(fill="x", pady=(10, 0))
        chart_frame.pack_propagate(False)

        self.freq_canvas = tk.Canvas(
            chart_frame, bg="#0f172a", highlightthickness=0, height=180
        )
        self.freq_canvas.pack(fill="both", expand=True)

    def create_alarms_panel(self, parent):
        """Panel de alarmas mejorado"""
        alarms_frame = tk.Frame(parent, bg="#1e293b", relief="flat", bd=0)
        alarms_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        # Header con icono animado
        header = tk.Frame(alarms_frame, bg="#dc2626", height=55)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_content = tk.Frame(header, bg="#dc2626")
        header_content.pack(fill="both", expand=True, padx=25)

        tk.Label(
            header_content,
            text="🚨 ALARMAS Y NOTIFICACIONES",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#dc2626",
        ).pack(side="left")

        # Contador de alarmas
        alarm_count = len(
            [
                a
                for a in self.scada_data.alarmas
                if a["nivel"] in ["advertencia", "critico"]
            ]
        )
        tk.Label(
            header_content,
            text=f"{alarm_count} Activas",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#dc2626",
        ).pack(side="right")

        # Contenido con mejor diseño
        content = tk.Frame(alarms_frame, bg="#1e293b", padx=20, pady=25)
        content.pack(fill="both", expand=True)

        # Grid de alarmas en 2 columnas
        alarms_grid = tk.Frame(content, bg="#1e293b")
        alarms_grid.pack(fill="both", expand=True)

        alarms_grid.columnconfigure(0, weight=1)
        alarms_grid.columnconfigure(1, weight=1)

        for i, alarma in enumerate(self.scada_data.alarmas):
            row = i // 2
            col = i % 2
            self.create_alarm_item(alarms_grid, alarma, row, col)

    def create_alarm_item(self, parent, alarma, row, col):
        """Crear item de alarma individual mejorado"""
        color_map = {
            "advertencia": ("#f59e0b", "#fef3c7"),
            "normal": ("#10b981", "#d1fae5"),
            "info": ("#38bdf8", "#dbeafe"),
            "critico": ("#dc2626", "#fee2e2"),
        }

        bg_color, text_color = color_map.get(alarma["nivel"], ("#64748b", "#f1f5f9"))

        alarm_frame = tk.Frame(parent, bg=bg_color, relief="flat", bd=0)
        alarm_frame.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)

        content = tk.Frame(alarm_frame, bg=bg_color, padx=18, pady=15)
        content.pack(fill="both", expand=True)

        # Header de la alarma
        alarm_header = tk.Frame(content, bg=bg_color)
        alarm_header.pack(fill="x", pady=(0, 10))

        # Icono y tipo
        icon_frame = tk.Frame(alarm_header, bg=bg_color)
        icon_frame.pack(side="left")

        tk.Label(
            icon_frame,
            text=alarma["tipo"],
            font=("Arial", 16),
            bg=bg_color,
            fg=text_color,
        ).pack(side="left")

        # Badge de nivel
        level_bg = "#0f172a" if alarma["nivel"] != "critico" else "#7f1d1d"
        level_fg = text_color if alarma["nivel"] != "critico" else "#fecaca"

        level_frame = tk.Frame(alarm_header, bg=level_bg, relief="flat", bd=0)
        level_frame.pack(side="right", padx=(10, 0))

        tk.Label(
            level_frame,
            text=alarma["nivel"].upper(),
            font=("Arial", 8, "bold"),
            bg=level_bg,
            fg=level_fg,
            padx=8,
            pady=3,
        ).pack()

        # Mensaje de la alarma
        message_frame = tk.Frame(content, bg=bg_color)
        message_frame.pack(fill="x")

        tk.Label(
            message_frame,
            text=alarma["mensaje"],
            font=("Arial", 11, "bold"),
            bg=bg_color,
            fg=text_color,
            wraplength=250,
            justify="left",
        ).pack(anchor="w")

        # Footer con timestamp
        footer_frame = tk.Frame(content, bg=bg_color)
        footer_frame.pack(fill="x", pady=(10, 0))

        tk.Label(
            footer_frame,
            text="🕐 Hace 5 min",
            font=("Arial", 9),
            bg=bg_color,
            fg=text_color,
        ).pack(side="left")

        # Indicador de prioridad
        priority = "Alta" if alarma["nivel"] in ["advertencia", "critico"] else "Normal"
        tk.Label(
            footer_frame,
            text=f"Prioridad: {priority}",
            font=("Arial", 9),
            bg=bg_color,
            fg=text_color,
        ).pack(side="right")

    def create_stats_panel(self, parent):
        """Panel de estadísticas mejorado"""
        stats_frame = tk.Frame(parent, bg="#1e293b", relief="flat", bd=0)
        stats_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))

        # Header elegante
        header = tk.Frame(stats_frame, bg="#4f46e5", height=55)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_content = tk.Frame(header, bg="#4f46e5")
        header_content.pack(fill="both", expand=True, padx=25)

        tk.Label(
            header_content,
            text="📈 ESTADÍSTICAS DEL SISTEMA",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#4f46e5",
        ).pack(side="left")

        tk.Label(
            header_content,
            text="Actualizado en tiempo real",
            font=("Arial", 11),
            fg="#c7d2fe",
            bg="#4f46e5",
        ).pack(side="right")

        # Contenido con tarjetas de estadísticas
        content = tk.Frame(stats_frame, bg="#1e293b", padx=20, pady=25)
        content.pack(fill="both", expand=True)

        # Grid de estadísticas 2x2
        stats_grid = tk.Frame(content, bg="#1e293b")
        stats_grid.pack(fill="both", expand=True)

        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)
        stats_grid.rowconfigure(0, weight=1)
        stats_grid.rowconfigure(1, weight=1)

        stats_data = [
            {
                "icon": "⏱️",
                "title": "Uptime del Sistema",
                "value": "99.8%",
                "subtitle": "Disponibilidad mensual",
                "trend": "↗️ +0.2%",
                "color": "#10b981",
            },
            {
                "icon": "🔧",
                "title": "Próximo Mantenimiento",
                "value": "15 días",
                "subtitle": "Programado",
                "trend": "⏳ En progreso",
                "color": "#f59e0b",
            },
            {
                "icon": "📊",
                "title": "Eficiencia Energética",
                "value": "94.2%",
                "subtitle": "Factor de utilización",
                "trend": "↗️ +1.5%",
                "color": "#38bdf8",
            },
            {
                "icon": "🔋",
                "title": "Energía Total",
                "value": "1.2 GWh",
                "subtitle": "Generada este mes",
                "trend": "📈 +5.3%",
                "color": "#ef4444",
            },
        ]

        for i, stat in enumerate(stats_data):
            row = i // 2
            col = i % 2
            self.create_stat_card(stats_grid, stat, row, col)

    def create_stat_card(self, parent, stat, row, col):
        """Crear tarjeta de estadística individual"""
        card_frame = tk.Frame(parent, bg="#0f172a", relief="flat", bd=0)
        card_frame.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)

        content = tk.Frame(card_frame, bg="#0f172a", padx=20, pady=20)
        content.pack(fill="both", expand=True)

        # Header con icono
        header_frame = tk.Frame(content, bg="#0f172a")
        header_frame.pack(fill="x", pady=(0, 15))

        # Icono
        icon_frame = tk.Frame(header_frame, bg="#0f172a")
        icon_frame.pack(side="left")

        tk.Label(
            icon_frame,
            text=stat["icon"],
            font=("Arial", 20),
            bg="#0f172a",
            fg=stat["color"],
        ).pack(side="left")

        # Título y tendencia
        text_frame = tk.Frame(header_frame, bg="#0f172a")
        text_frame.pack(side="left", fill="x", expand=True, padx=(12, 0))

        tk.Label(
            text_frame,
            text=stat["title"],
            font=("Arial", 12, "bold"),
            bg="#0f172a",
            fg="#e2e8f0",
        ).pack(anchor="w")

        tk.Label(
            text_frame,
            text=stat["trend"],
            font=("Arial", 9),
            bg="#0f172a",
            fg=stat["color"],
        ).pack(anchor="w", pady=(2, 0))

        # Valor principal
        value_frame = tk.Frame(content, bg="#0f172a")
        value_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            value_frame,
            text=stat["value"],
            font=("Arial", 24, "bold"),
            bg="#0f172a",
            fg=stat["color"],
        ).pack(anchor="w")

        # Subtítulo
        subtitle_frame = tk.Frame(content, bg="#0f172a")
        subtitle_frame.pack(fill="x")

        tk.Label(
            subtitle_frame,
            text=stat["subtitle"],
            font=("Arial", 10),
            bg="#0f172a",
            fg="#94a3b8",
        ).pack(anchor="w")

        # Barra de progreso decorativa
        progress_frame = tk.Frame(content, bg="#1e293b", height=4)
        progress_frame.pack(fill="x", pady=(15, 0))
        progress_frame.pack_propagate(False)

        progress_bar = tk.Frame(progress_frame, bg=stat["color"], height=4)
        progress_percent = random.randint(75, 95)
        progress_bar.place(relx=0, rely=0, relwidth=progress_percent / 100, relheight=1)

    # MÉTODOS DE GRÁFICOS
    def draw_voltage_chart(self):
        """Dibujar gráfico de voltaje mejorado - CON VERIFICACIÓN MEJORADA"""
        try:
            if not (
                hasattr(self, "voltage_canvas") and self.voltage_canvas.winfo_exists()
            ):
                return

            self.voltage_canvas.delete("all")
            w, h = self.voltage_canvas.winfo_width(), self.voltage_canvas.winfo_height()
            if w < 10 or h < 10:
                return

            # Fondo del gráfico
            self.voltage_canvas.create_rectangle(0, 0, w, h, fill="#0f172a", outline="")

            # Línea de tendencia con efecto de gradiente
            points = []
            num_points = 12
            max_voltage = 230
            min_voltage = 210

            for i in range(num_points):
                x = 10 + i * ((w - 20) / (num_points - 1))
                # Valor simulado con variación realista basada en el voltaje actual
                base_value = self.scada_data.voltaje
                variation = math.sin(i * 0.8 + datetime.now().timestamp() * 0.01) * 2
                value = base_value + variation + random.uniform(-0.5, 0.5)
                # Normalizar a la altura del canvas
                normalized_value = (value - min_voltage) / (max_voltage - min_voltage)
                y = h - 20 - (normalized_value * (h - 40))
                points.append((x, y))

            # Dibujar área bajo la curva
            area_points = [(points[0][0], h - 20)] + points + [(points[-1][0], h - 20)]
            self.voltage_canvas.create_polygon(
                area_points, fill="#1e40af", outline="", stipple="gray50"
            )

            # Dibujar línea principal
            for i in range(1, len(points)):
                x1, y1 = points[i - 1]
                x2, y2 = points[i]
                self.voltage_canvas.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="#60a5fa",
                    width=3,
                    smooth=True,
                    capstyle=tk.ROUND,
                )

            # Puntos de datos con efecto glow
            for x, y in points:
                # Efecto glow
                self.voltage_canvas.create_oval(
                    x - 4,
                    y - 4,
                    x + 4,
                    y + 4,
                    fill="#93c5fd",
                    outline="#60a5fa",
                    width=2,
                )
                self.voltage_canvas.create_oval(
                    x - 2, y - 2, x + 2, y + 2, fill="#3b82f6", outline=""
                )

            # Línea de referencia (valor actual)
            current_y = (
                h
                - 20
                - (
                    (self.scada_data.voltaje - min_voltage)
                    / (max_voltage - min_voltage)
                )
                * (h - 40)
            )
            self.voltage_canvas.create_line(
                10, current_y, w - 10, current_y, fill="#38bdf8", width=1, dash=(4, 2)
            )

            # Etiqueta de referencia
            self.voltage_canvas.create_text(
                w - 15,
                current_y - 8,
                text=f"{self.scada_data.voltaje:.1f}V",
                fill="#38bdf8",
                font=("Arial", 7),
                anchor="e",
            )

        except tk.TclError:
            # El canvas ya no existe, salir silenciosamente
            return

    def draw_current_chart(self):
        """Dibujar gráfico de corriente mejorado - CON VERIFICACIÓN MEJORADA"""
        try:
            if not (
                hasattr(self, "current_canvas") and self.current_canvas.winfo_exists()
            ):
                return

            self.current_canvas.delete("all")
            w, h = self.current_canvas.winfo_width(), self.current_canvas.winfo_height()
            if w < 10 or h < 10:
                return

            # Fondo del gráfico
            self.current_canvas.create_rectangle(0, 0, w, h, fill="#0f172a", outline="")

            center_y = h // 2
            amplitude = 30
            frequency = 0.1
            time_offset = datetime.now().timestamp() * 0.02
            points = []

            # Generar onda sinusoidal con armónicos para mayor realismo
            for i in range(0, w, 2):
                x = i
                # Onda principal con armónicos y variación en tiempo real
                time_factor = time_offset + i * 0.01
                main_wave = math.sin(time_factor * frequency)
                harmonic1 = 0.3 * math.sin(time_factor * frequency * 3 + 0.5)
                harmonic2 = 0.2 * math.sin(time_factor * frequency * 5 + 1.2)
                noise = random.uniform(-0.1, 0.1)

                y = center_y + amplitude * (main_wave + harmonic1 + harmonic2 + noise)
                points.append((x, y))

            # Dibujar área bajo la curva
            area_points = [(points[0][0], h)] + points + [(points[-1][0], h)]
            self.current_canvas.create_polygon(
                area_points, fill="#065f46", outline="", stipple="gray50"
            )

            # Dibujar línea de la onda
            for i in range(1, len(points)):
                x1, y1 = points[i - 1]
                x2, y2 = points[i]
                # Cambiar color según la amplitud
                color_intensity = min(255, int(abs(y1 - center_y) * 3))
                color = f"#34d399"
                self.current_canvas.create_line(
                    x1, y1, x2, y2, fill=color, width=2, smooth=True
                )

            # Línea cero
            self.current_canvas.create_line(
                0, center_y, w, center_y, fill="#94a3b8", width=1, dash=(2, 2)
            )

            # Picos destacados
            for i in range(0, len(points), len(points) // 4):
                if i < len(points):
                    x, y = points[i]
                    if abs(y - center_y) > amplitude * 0.7:
                        self.current_canvas.create_oval(
                            x - 3,
                            y - 3,
                            x + 3,
                            y + 3,
                            fill="#10b981",
                            outline="#059669",
                            width=1,
                        )

        except tk.TclError:
            # El canvas ya no existe, salir silenciosamente
            return

    def draw_power_chart(self):
        """Dibujar gráfico de potencia MEJORADO - MÁS GRANDE Y DETALLADO - CON VERIFICACIÓN MEJORADA"""
        try:
            if not (hasattr(self, "power_canvas") and self.power_canvas.winfo_exists()):
                return

            self.power_canvas.delete("all")
            w, h = self.power_canvas.winfo_width(), self.power_canvas.winfo_height()
            if w < 10 or h < 10:
                return

            # Fondo del gráfico
            self.power_canvas.create_rectangle(0, 0, w, h, fill="#0f172a", outline="")

            center_x, center_y = w // 2, h // 2
            # RADIO SIGNIFICATIVAMENTE AUMENTADO
            outer_radius = min(center_x, center_y) - 10
            inner_radius = outer_radius - 35  # Más espacio para el interior

            total_power = (
                self.scada_data.potencia_activa + self.scada_data.potencia_reactiva
            )
            active_angle = (self.scada_data.potencia_activa / total_power) * 360
            reactive_angle = 360 - active_angle

            # Anillo de fondo
            self.power_canvas.create_oval(
                center_x - outer_radius,
                center_y - outer_radius,
                center_x + outer_radius,
                center_y + outer_radius,
                fill="#1e293b",
                outline="#334155",
                width=2,
            )

            # Potencia activa - anillo más grueso
            for i in range(8):  # Más capas para mayor grosor
                offset = i * 2.5
                color_shade = [
                    "#fef3c7",
                    "#fde68a",
                    "#fcd34d",
                    "#fbbf24",
                    "#f59e0b",
                    "#d97706",
                    "#b45309",
                    "#92400e",
                ][i]
                self.power_canvas.create_arc(
                    center_x - outer_radius + offset,
                    center_y - outer_radius + offset,
                    center_x + outer_radius - offset,
                    center_y + outer_radius - offset,
                    start=0,
                    extent=active_angle,
                    style="arc",
                    outline=color_shade,
                    width=4,
                )

            # Potencia reactiva - anillo más grueso
            for i in range(8):  # Más capas para mayor grosor
                offset = i * 2.5
                color_shade = [
                    "#dbeafe",
                    "#93c5fd",
                    "#60a5fa",
                    "#3b82f6",
                    "#1d4ed8",
                    "#1e40af",
                    "#1e3a8a",
                    "#172554",
                ][i]
                self.power_canvas.create_arc(
                    center_x - outer_radius + offset,
                    center_y - outer_radius + offset,
                    center_x + outer_radius - offset,
                    center_y + outer_radius - offset,
                    start=active_angle,
                    extent=reactive_angle,
                    style="arc",
                    outline=color_shade,
                    width=4,
                )

            # Anillo interior
            self.power_canvas.create_oval(
                center_x - inner_radius,
                center_y - inner_radius,
                center_x + inner_radius,
                center_y + inner_radius,
                fill="#0f172a",
                outline="#475569",
                width=1,
            )

            # Porcentajes
            active_percent = (self.scada_data.potencia_activa / total_power) * 100
            reactive_percent = (self.scada_data.potencia_reactiva / total_power) * 100

            # Texto principal - MÁS GRANDE
            self.power_canvas.create_text(
                center_x,
                center_y - 20,
                text=f"{active_percent:.1f}%",
                fill="#fbbf24",
                font=("Arial", 18, "bold"),
            )

            self.power_canvas.create_text(
                center_x,
                center_y,
                text="Activa",
                fill="#fbbf24",
                font=("Arial", 12, "bold"),
            )

            self.power_canvas.create_text(
                center_x,
                center_y + 25,
                text=f"{reactive_percent:.1f}%",
                fill="#60a5fa",
                font=("Arial", 16, "bold"),
            )

            self.power_canvas.create_text(
                center_x,
                center_y + 45,
                text="Reactiva",
                fill="#60a5fa",
                font=("Arial", 10),
            )

        except tk.TclError:
            # El canvas ya no existe, salir silenciosamente
            return

    def draw_frequency_chart(self):
        """Dibujar medidor de frecuencia MEJORADO - MÁS GRANDE Y DETALLADO - CON VERIFICACIÓN MEJORADA"""
        try:
            if not (hasattr(self, "freq_canvas") and self.freq_canvas.winfo_exists()):
                return

            self.freq_canvas.delete("all")
            w, h = self.freq_canvas.winfo_width(), self.freq_canvas.winfo_height()
            if w < 10 or h < 10:
                return

            # Fondo del gráfico
            self.freq_canvas.create_rectangle(0, 0, w, h, fill="#0f172a", outline="")

            center_x, center_y = w // 2, h // 2
            # RADIO MÁXIMO POSIBLE
            outer_radius = min(center_x, center_y) - 5
            inner_radius = outer_radius - 30

            # Calcular ángulo basado en frecuencia
            min_freq, max_freq = 59.0, 61.0
            freq_range = max_freq - min_freq
            normalized_freq = (self.scada_data.frecuencia - min_freq) / freq_range
            freq_angle = 120 + (normalized_freq * 300)

            # Base del medidor
            self.freq_canvas.create_oval(
                center_x - outer_radius,
                center_y - outer_radius,
                center_x + outer_radius,
                center_y + outer_radius,
                fill="#1e293b",
                outline="#334155",
                width=2,
            )

            # Zonas de color - MÁS GRUESAS
            optimal_start = 120 + ((59.8 - min_freq) / freq_range) * 300
            optimal_end = 120 + ((60.2 - min_freq) / freq_range) * 300

            # Zona óptima (verde)
            self.freq_canvas.create_arc(
                center_x - outer_radius,
                center_y - outer_radius,
                center_x + outer_radius,
                center_y + outer_radius,
                start=optimal_start,
                extent=optimal_end - optimal_start,
                style="arc",
                outline="#10b981",
                width=18,
            )

            # Zona de advertencia (amarilla)
            warning1_start = 120 + ((59.5 - min_freq) / freq_range) * 300
            warning1_end = optimal_start
            self.freq_canvas.create_arc(
                center_x - outer_radius,
                center_y - outer_radius,
                center_x + outer_radius,
                center_y + outer_radius,
                start=warning1_start,
                extent=warning1_end - warning1_start,
                style="arc",
                outline="#f59e0b",
                width=18,
            )

            warning2_start = optimal_end
            warning2_end = 120 + ((60.5 - min_freq) / freq_range) * 300
            self.freq_canvas.create_arc(
                center_x - outer_radius,
                center_y - outer_radius,
                center_x + outer_radius,
                center_y + outer_radius,
                start=warning2_start,
                extent=warning2_end - warning2_start,
                style="arc",
                outline="#f59e0b",
                width=18,
            )

            # Zona crítica (roja)
            critical1_start = 120
            critical1_end = warning1_start
            self.freq_canvas.create_arc(
                center_x - outer_radius,
                center_y - outer_radius,
                center_x + outer_radius,
                center_y + outer_radius,
                start=critical1_start,
                extent=critical1_end - critical1_start,
                style="arc",
                outline="#ef4444",
                width=18,
            )

            critical2_start = warning2_end
            critical2_end = 420
            self.freq_canvas.create_arc(
                center_x - outer_radius,
                center_y - outer_radius,
                center_x + outer_radius,
                center_y + outer_radius,
                start=critical2_start,
                extent=critical2_end - critical2_start,
                style="arc",
                outline="#ef4444",
                width=18,
            )

            # Escala del medidor
            self.draw_enhanced_gauge_scale(center_x, center_y, outer_radius)

            # Aguja principal
            angle_rad = math.radians(freq_angle)
            needle_length = outer_radius - 25
            needle_x = center_x + needle_length * math.cos(angle_rad)
            needle_y = center_y - needle_length * math.sin(angle_rad)

            # Aguja con diseño mejorado
            self.freq_canvas.create_line(
                center_x,
                center_y,
                needle_x,
                needle_y,
                fill="#e2e8f0",
                width=6,
                capstyle=tk.ROUND,
            )

            # Punta de la aguja
            self.freq_canvas.create_oval(
                needle_x - 8,
                needle_y - 8,
                needle_x + 8,
                needle_y + 8,
                fill="#ef4444",
                outline="#dc2626",
                width=2,
            )

            # Centro del medidor
            self.freq_canvas.create_oval(
                center_x - 18,
                center_y - 18,
                center_x + 18,
                center_y + 18,
                fill="#475569",
                outline="#64748b",
                width=2,
            )
            self.freq_canvas.create_oval(
                center_x - 12,
                center_y - 12,
                center_x + 12,
                center_y + 12,
                fill="#1e293b",
                outline="#94a3b8",
            )

            # Valor actual en el centro
            self.freq_canvas.create_text(
                center_x,
                center_y - 10,
                text=f"{self.scada_data.frecuencia:.2f}",
                fill="#e2e8f0",
                font=("Arial", 14, "bold"),
            )

            self.freq_canvas.create_text(
                center_x, center_y + 10, text="Hz", fill="#94a3b8", font=("Arial", 11)
            )

        except tk.TclError:
            # El canvas ya no existe, salir silenciosamente
            return

    def draw_enhanced_gauge_scale(self, center_x, center_y, radius):
        """Dibujar escala mejorada del medidor de frecuencia"""
        # Marcas principales
        main_marks = [59.0, 59.5, 60.0, 60.5, 61.0]

        for i, freq in enumerate(main_marks):
            angle = 120 + ((freq - 59.0) / 2.0) * 300
            rad = math.radians(angle)

            # Línea de marca principal
            inner_radius = radius - 25
            outer_radius = radius
            x1 = center_x + inner_radius * math.cos(rad)
            y1 = center_y - inner_radius * math.sin(rad)
            x2 = center_x + outer_radius * math.cos(rad)
            y2 = center_y - outer_radius * math.sin(rad)

            self.freq_canvas.create_line(x1, y1, x2, y2, fill="#e2e8f0", width=4)

            # Etiqueta de valor
            label_radius = radius - 35
            label_x = center_x + label_radius * math.cos(rad)
            label_y = center_y - label_radius * math.sin(rad)

            self.freq_canvas.create_text(
                label_x,
                label_y,
                text=f"{freq:.1f}",
                fill="#e2e8f0",
                font=("Arial", 10, "bold"),
            )

    # MÉTODOS DE ANIMACIONES Y ACTUALIZACIÓN - ACTUALIZADOS
    def start_animations(self):
        """Iniciar animaciones en tiempo real - MODIFICADO para modo Excel"""

        def update_data():
            if self.scada_data.excel_loaded:
                # En modo Excel: avanzar cíclicamente por los registros del Excel
                self.update_excel_data()
            else:
                # En modo SCADA: simular variación de datos en tiempo real
                self.scada_data.potencia_total = 42.0 + random.uniform(-0.2, 0.2)
                self.scada_data.voltaje = 220.0 + random.uniform(-0.8, 0.8)
                self.scada_data.corriente = 185.0 + random.uniform(-1.5, 1.5)
                self.scada_data.frecuencia = 60.02 + random.uniform(-0.02, 0.02)
                self.scada_data.potencia_activa = 35.3 + random.uniform(-0.15, 0.15)
                self.scada_data.potencia_reactiva = 18.7 + random.uniform(-0.1, 0.1)

            # Actualizar valores en UI
            self.update_displayed_data()

            # Programar próxima actualización
            self.root.after(1000, update_data)

        # Iniciar animaciones después de un breve delay
        self.root.after(500, update_data)

    def update_displayed_data(self):
        """Actualizar todos los datos mostrados en la interfaz"""
        # Actualizar métricas principales
        if hasattr(self, "power_value") and self.power_value.winfo_exists():
            self.power_value.config(text=f"{self.scada_data.potencia_total:.1f} MW")

        if (
            hasattr(self, "voltage_value_label")
            and self.voltage_value_label.winfo_exists()
        ):
            self.voltage_value_label.config(text=f"{self.scada_data.voltaje:.1f} V")

        if (
            hasattr(self, "current_value_label")
            and self.current_value_label.winfo_exists()
        ):
            self.current_value_label.config(text=f"{self.scada_data.corriente:.1f} A")

        if hasattr(self, "freq_value_label") and self.freq_value_label.winfo_exists():
            self.freq_value_label.config(text=f"{self.scada_data.frecuencia:.2f} Hz")

        if (
            hasattr(self, "power_active_label")
            and self.power_active_label.winfo_exists()
        ):
            self.power_active_label.config(
                text=f"{self.scada_data.potencia_activa:.1f} MW"
            )

        if (
            hasattr(self, "power_reactive_label")
            and self.power_reactive_label.winfo_exists()
        ):
            self.power_reactive_label.config(
                text=f"{self.scada_data.potencia_reactiva:.1f} MVAR"
            )

        # Redibujar gráficos si estamos en dashboard
        if self.current_section == "dashboard":
            # VERIFICAR QUE LOS CANVAS EXISTAN ANTES DE DIBUJAR
            try:
                if (
                    hasattr(self, "voltage_canvas")
                    and self.voltage_canvas.winfo_exists()
                ):
                    self.draw_voltage_chart()

                if (
                    hasattr(self, "current_canvas")
                    and self.current_canvas.winfo_exists()
                ):
                    self.draw_current_chart()

                if hasattr(self, "power_canvas") and self.power_canvas.winfo_exists():
                    self.draw_power_chart()

                if hasattr(self, "freq_canvas") and self.freq_canvas.winfo_exists():
                    self.draw_frequency_chart()
            except tk.TclError:
                # Si hay error con los canvas, esperar a la próxima actualización
                pass

    def cargar_excel(self):
        """Función para cargar archivos Excel con modo temporal"""
        # Limpiar contenido primero
        self.clear_content()
        self.current_section = "cargar_excel"

        # Frame principal para cargar Excel
        main_frame = tk.Frame(self.content_container, bg="#0f172a")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Título
        title_frame = tk.Frame(main_frame, bg="#1e293b", relief="flat", bd=0)
        title_frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            title_frame,
            text="📁 CARGAR ARCHIVO EXCEL",
            font=("Arial", 20, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
        ).pack(pady=20)

        # Panel de contenido
        content_frame = tk.Frame(main_frame, bg="#1e293b", relief="flat", bd=0)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Información sobre el modo Excel
        info_frame = tk.Frame(content_frame, bg="#1e293b")
        info_frame.pack(fill="x", pady=(0, 30))

        tk.Label(
            info_frame,
            text="MODO EXCEL TEMPORAL",
            font=("Arial", 16, "bold"),
            fg="#f59e0b",
            bg="#1e293b",
        ).pack(anchor="w")

        tk.Label(
            info_frame,
            text="• Al cargar un Excel: Los datos del SCADA serán reemplazados por los del archivo\n• Al quitar el Excel: El sistema volverá automáticamente a datos en tiempo real",
            font=("Arial", 11),
            fg="#94a3b8",
            bg="#1e293b",
            justify="left",
        ).pack(anchor="w", pady=(10, 0))

        # Panel de control de Excel (si hay archivo cargado)
        if self.scada_data.excel_loaded:
            self.show_excel_control_panel(content_frame)
        else:
            # Botón para cargar Excel
            btn_frame = tk.Frame(content_frame, bg="#1e293b")
            btn_frame.pack(fill="x", pady=20)

            load_btn = tk.Button(
                btn_frame,
                text="📂 Seleccionar Archivo Excel",
                font=("Arial", 12, "bold"),
                bg="#06b6d4",
                fg="white",
                command=self.seleccionar_excel,
                cursor="hand2",
                padx=30,
                pady=15,
            )
            load_btn.pack()

            # Información de formato esperado
            format_frame = tk.Frame(content_frame, bg="#1e293b")
            format_frame.pack(fill="x", pady=(30, 0))

            tk.Label(
                format_frame,
                text="Formato esperado del Excel:",
                font=("Arial", 12, "bold"),
                fg="#e2e8f0",
                bg="#1e293b",
            ).pack(anchor="w")

            format_text = """Columnas esperadas (pueden variar):
• Potencia_Total (MW)
• Voltaje (V) 
• Corriente (A)
• Frecuencia (Hz)
• Potencia_Activa (MW)
• Potencia_Reactiva (MVAR)"""

            tk.Label(
                format_frame,
                text=format_text,
                font=("Arial", 10),
                fg="#94a3b8",
                bg="#1e293b",
                justify="left",
            ).pack(anchor="w", pady=(10, 0))

    def seleccionar_excel(self):
        """Seleccionar archivo Excel"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
        )

        if file_path:
            try:
                # Leer el archivo Excel
                df = pd.read_excel(file_path)

                # Guardar datos originales
                self.scada_data.original_data = {
                    "potencia_total": self.scada_data.potencia_total,
                    "voltaje": self.scada_data.voltaje,
                    "corriente": self.scada_data.corriente,
                    "frecuencia": self.scada_data.frecuencia,
                    "potencia_activa": self.scada_data.potencia_activa,
                    "potencia_reactiva": self.scada_data.potencia_reactiva,
                }

                # Procesar datos del Excel
                self.process_excel_data(df)

                # Activar modo Excel
                self.scada_data.excel_data = df
                self.scada_data.excel_loaded = True
                self.scada_data.excel_file_name = os.path.basename(file_path)
                self.scada_data.current_excel_index = 0  # Iniciar índice

                # Actualizar interfaz
                self.update_mode_indicator()
                self.update_displayed_data()

                # Recargar la sección de cargar Excel para mostrar el panel de control
                self.cargar_excel()

                messagebox.showinfo(
                    "Éxito",
                    f"Archivo Excel cargado correctamente.\nModo Excel activado.",
                )

            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo cargar el archivo Excel:\n{str(e)}"
                )

    def process_excel_data(self, df):
        """Procesar datos del Excel y actualizar SCADA"""
        # Mapear columnas del Excel a los datos del SCADA
        column_mapping = {
            "Potencia_Total": "potencia_total",
            "Voltaje": "voltaje",
            "Corriente": "corriente",
            "Frecuencia": "frecuencia",
            "Potencia_Activa": "potencia_activa",
            "Potencia_Reactiva": "potencia_reactiva",
        }

        # Usar el primer registro para inicializar
        for excel_col, scada_attr in column_mapping.items():
            if excel_col in df.columns:
                value = df[excel_col].iloc[0]  # Primer registro
                if pd.notna(value):
                    setattr(self.scada_data, scada_attr, float(value))

    def update_excel_data(self):
        """Actualizar datos del Excel de forma cíclica para simular variación"""
        if not self.scada_data.excel_loaded or self.scada_data.excel_data is None:
            return

        df = self.scada_data.excel_data
        if len(df) == 0:
            return

        # Avanzar al siguiente registro (cíclico)
        self.scada_data.current_excel_index = (
            self.scada_data.current_excel_index + 1
        ) % len(df)
        current_index = self.scada_data.current_excel_index

        # Mapear columnas
        column_mapping = {
            "Potencia_Total": "potencia_total",
            "Voltaje": "voltaje",
            "Corriente": "corriente",
            "Frecuencia": "frecuencia",
            "Potencia_Activa": "potencia_activa",
            "Potencia_Reactiva": "potencia_reactiva",
        }

        # Actualizar datos con el registro actual
        for excel_col, scada_attr in column_mapping.items():
            if excel_col in df.columns:
                value = df[excel_col].iloc[current_index]
                if pd.notna(value):
                    # Agregar pequeña variación aleatoria para simular movimiento
                    variation = random.uniform(-0.1, 0.1)
                    if excel_col == "Frecuencia":
                        variation *= 0.01  # Menor variación para frecuencia

                    setattr(self.scada_data, scada_attr, float(value) + variation)

    def show_excel_control_panel(self, parent):
        """Mostrar panel de control para el modo Excel (SOLO en la sección Cargar Excel)"""
        control_frame = tk.Frame(parent, bg="#0f172a", relief="raised", bd=1)
        control_frame.pack(fill="x", pady=(0, 20))

        # Contenido del panel
        control_content = tk.Frame(control_frame, bg="#1e293b", padx=20, pady=15)
        control_content.pack(fill="x")

        # Información del archivo
        info_frame = tk.Frame(control_content, bg="#1e293b")
        info_frame.pack(fill="x", pady=(0, 15))

        tk.Label(
            info_frame,
            text="📊 ARCHIVO EXCEL CARGADO",
            font=("Arial", 14, "bold"),
            fg="#f59e0b",
            bg="#1e293b",
        ).pack(anchor="w")

        file_info = f"Archivo: {getattr(self.scada_data, 'excel_file_name', 'N/A')} | Registros: {len(self.scada_data.excel_data)}"
        tk.Label(
            info_frame, text=file_info, font=("Arial", 11), fg="#94a3b8", bg="#1e293b"
        ).pack(anchor="w", pady=(5, 0))

        # Datos cargados
        data_frame = tk.Frame(control_content, bg="#1e293b")
        data_frame.pack(fill="x", pady=(0, 15))

        tk.Label(
            data_frame,
            text="Datos cargados desde el Excel:",
            font=("Arial", 11, "bold"),
            fg="#e2e8f0",
            bg="#1e293b",
        ).pack(anchor="w")

        # Mostrar valores actuales
        values_text = f"""• Potencia Total: {self.scada_data.potencia_total:.1f} MW
• Voltaje: {self.scada_data.voltaje:.1f} V
• Corriente: {self.scada_data.corriente:.1f} A  
• Frecuencia: {self.scada_data.frecuencia:.2f} Hz
• Potencia Activa: {self.scada_data.potencia_activa:.1f} MW
• Potencia Reactiva: {self.scada_data.potencia_reactiva:.1f} MVAR"""

        tk.Label(
            data_frame,
            text=values_text,
            font=("Arial", 10),
            fg="#38bdf8",
            bg="#1e293b",
            justify="left",
        ).pack(anchor="w", pady=(10, 0))

        # Botón para quitar Excel
        btn_frame = tk.Frame(control_content, bg="#1e293b")
        btn_frame.pack(fill="x")

        quit_btn = tk.Button(
            btn_frame,
            text="❌ Quitar Excel y Volver a SCADA",
            font=("Arial", 11, "bold"),
            bg="#dc2626",
            fg="white",
            command=self.quitar_excel,
            cursor="hand2",
            padx=20,
            pady=10,
        )
        quit_btn.pack()

    def quitar_excel(self):
        """Quitar el archivo Excel y volver al modo SCADA"""
        if not self.scada_data.excel_loaded:
            messagebox.showinfo("Info", "No hay archivo Excel cargado.")
            return

        # Restaurar datos originales
        if self.scada_data.original_data:
            self.scada_data.potencia_total = self.scada_data.original_data[
                "potencia_total"
            ]
            self.scada_data.voltaje = self.scada_data.original_data["voltaje"]
            self.scada_data.corriente = self.scada_data.original_data["corriente"]
            self.scada_data.frecuencia = self.scada_data.original_data["frecuencia"]
            self.scada_data.potencia_activa = self.scada_data.original_data[
                "potencia_activa"
            ]
            self.scada_data.potencia_reactiva = self.scada_data.original_data[
                "potencia_reactiva"
            ]

        # Desactivar modo Excel
        self.scada_data.excel_data = None
        self.scada_data.excel_loaded = False
        self.scada_data.original_data = None
        self.scada_data.current_excel_index = 0

        # Actualizar interfaz
        self.update_mode_indicator()
        self.update_displayed_data()

        # Recargar la sección actual
        if self.current_section == "cargar_excel":
            self.cargar_excel()
        else:
            # Si estamos en otra sección, mostrar mensaje
            messagebox.showinfo(
                "Éxito", "Modo Excel desactivado. Volviendo a datos en tiempo real."
            )

    def show_history(self):
        """Mostrar la sección de historial"""
        self.clear_content()
        self.current_section = "historial"
        self.create_history_section()

    def create_history_section(self):
        """Crear la sección de historial (APARIENCIA ORIGINAL COMPLETA)"""
        # Frame principal del historial
        main_frame = tk.Frame(self.content_container, bg="#0f172a")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Título y controles de filtro
        header_frame = tk.Frame(main_frame, bg="#1e293b", relief="flat", bd=0)
        header_frame.pack(fill="x", pady=(0, 15))

        # Título HISTORIAL DE MEDICION
        title_frame = tk.Frame(header_frame, bg="#1e293b")
        title_frame.pack(fill="x", pady=(15, 10))

        tk.Label(
            title_frame,
            text="📊 HISTORIAL DE MEDICIONES",
            font=("Arial", 20, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
        ).pack()

        # Controles de filtro mejorados
        filter_frame = tk.Frame(header_frame, bg="#1e293b")
        filter_frame.pack(fill="x", pady=(10, 15))

        # Fechas con calendarios - EN ESPAÑOL
        dates_frame = tk.Frame(filter_frame, bg="#1e293b")
        dates_frame.pack(fill="x", pady=10)

        tk.Label(
            dates_frame,
            text="Selecciona Fecha:",
            font=("Arial", 12, "bold"),
            fg="#94a3b8",
            bg="#1e293b",
        ).pack(side="left")

        # Fecha desde - EN ESPAÑOL
        tk.Label(
            dates_frame, text="Desde:", font=("Arial", 11), fg="#e2e8f0", bg="#1e293b"
        ).pack(side="left", padx=(20, 5))

        # Usar fecha por defecto más reciente
        default_fecha_desde = datetime.now() - timedelta(days=7)
        self.fecha_desde = DateEntry(
            dates_frame,
            width=12,
            background="#1e293b",
            foreground="white",
            borderwidth=2,
            date_pattern="dd/mm/yyyy",
            font=("Arial", 11),
            mindate=datetime(2020, 1, 1),
            maxdate=datetime.now() + timedelta(days=365),
            locale="es_ES",
        )
        self.fecha_desde.set_date(default_fecha_desde)
        self.fecha_desde.pack(side="left", padx=5)

        # Fecha hasta - EN ESPAÑOL
        tk.Label(
            dates_frame, text="Hasta:", font=("Arial", 11), fg="#e2e8f0", bg="#1e293b"
        ).pack(side="left", padx=(20, 5))

        self.fecha_hasta = DateEntry(
            dates_frame,
            width=12,
            background="#1e293b",
            foreground="white",
            borderwidth=2,
            date_pattern="dd/mm/yyyy",
            font=("Arial", 11),
            mindate=datetime(2020, 1, 1),
            maxdate=datetime.now() + timedelta(days=365),
            locale="es_ES",
        )
        self.fecha_hasta.set_date(datetime.now())
        self.fecha_hasta.pack(side="left", padx=5)

        # Selector de parámetro mejorado
        param_frame = tk.Frame(filter_frame, bg="#1e293b")
        param_frame.pack(fill="x", pady=10)

        tk.Label(
            param_frame,
            text="Parámetro:",
            font=("Arial", 12, "bold"),
            fg="#94a3b8",
            bg="#1e293b",
        ).pack(side="left")

        self.param_var = tk.StringVar(value="Potencia")
        param_combo = ttk.Combobox(
            param_frame,
            textvariable=self.param_var,
            values=[
                "Potencia",
                "Frecuencia",
                "Voltaje",
                "Corriente",
                "Todos los parámetros",
            ],
            state="readonly",
            font=("Arial", 11),
            width=20,
        )
        param_combo.pack(side="left", padx=(20, 0))
        param_combo.bind("<<ComboboxSelected>>", self.on_parameter_change)

        # Botones de acción
        buttons_frame = tk.Frame(filter_frame, bg="#1e293b")
        buttons_frame.pack(fill="x", pady=10)

        # Botón de búsqueda MEJORADO
        search_btn = tk.Button(
            buttons_frame,
            text="🔍 Buscar Historial",
            font=("Arial", 11, "bold"),
            bg="#38bdf8",
            fg="white",
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.buscar_historial,
        )
        search_btn.pack(side="left", padx=(0, 10))

        # Botón para generar reporte Excel del historial mostrado
        reporte_btn = tk.Button(
            filter_frame,
            text="💾 Generar Reporte Excel",
            font=("Arial", 11, "bold"),
            bg="#38bdf8",
            fg="#0f172a",
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=6,
            command=self.generar_reporte_historial,
        )
        reporte_btn.pack(side="left", padx=(15, 0))

        # Resultados
        results_frame = tk.Frame(main_frame, bg="#0f172a")
        results_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Título Resultados con contador
        results_header = tk.Frame(results_frame, bg="#0f172a")
        results_header.pack(fill="x", pady=(0, 15))

        tk.Label(
            results_header,
            text="📋 Resultados del Historial",
            font=("Arial", 16, "bold"),
            fg="#e2e8f0",
            bg="#0f172a",
        ).pack(side="left")

        # Contador de registros y estadísticas
        stats_frame = tk.Frame(results_header, bg="#0f172a")
        stats_frame.pack(side="right")

        self.record_count_label = tk.Label(
            stats_frame,
            text="Cargando...",
            font=("Arial", 11),
            fg="#94a3b8",
            bg="#0f172a",
        )
        self.record_count_label.pack(side="top", anchor="e")

        self.stats_label = tk.Label(
            stats_frame, text="", font=("Arial", 10), fg="#64748b", bg="#0f172a"
        )
        self.stats_label.pack(side="top", anchor="e")

        # Crear tabla de resultados
        self.create_enhanced_history_table(results_frame)

    def create_enhanced_history_table(self, parent):
        """Crear tabla de historial MEJORADA con más funcionalidades"""
        # Frame de la tabla con scroll
        table_container = tk.Frame(parent, bg="#0f172a")
        table_container.pack(fill="both", expand=True)

        # Canvas y scrollbar para la tabla
        canvas = tk.Canvas(table_container, bg="#0f172a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            table_container, orient="vertical", command=canvas.yview
        )
        self.table_frame = tk.Frame(canvas, bg="#1e293b")

        self.table_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Empaquetado
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configurar scroll con mouse
        canvas.bind(
            "<Enter>",
            lambda e: canvas.bind_all(
                "<MouseWheel>",
                lambda event: canvas.yview_scroll(
                    int(-1 * (event.delta / 120)), "units"
                ),
            ),
        )
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Generar y mostrar datos iniciales
        self.actualizar_tabla_historial()

    def on_parameter_change(self, event=None):
        """Manejar cambio de parámetro"""
        self.selected_parameter = self.param_var.get()
        self.actualizar_tabla_historial()

    def buscar_historial(self):
        """Buscar en el historial según los filtros"""
        fecha_desde = self.fecha_desde.get_date()
        fecha_hasta = self.fecha_hasta.get_date()
        parametro = self.param_var.get()

        messagebox.showinfo(
            "Búsqueda",
            f"Buscando historial:\nDesde: {fecha_desde.strftime('%d/%m/%Y')}\nHasta: {fecha_hasta.strftime('%d/%m/%Y')}\nParámetro: {parametro}",
        )

        self.actualizar_tabla_historial()

    def actualizar_tabla_historial(self):
        """Actualizar la tabla de historial con nuevos datos"""
        # Limpiar tabla existente
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Encabezados de la tabla según el parámetro seleccionado
        headers = self.get_headers_for_parameter()

        # Crear encabezados MEJORADOS
        header_frame = tk.Frame(self.table_frame, bg="#334155")
        header_frame.pack(fill="x", padx=20, pady=(0, 10))

        for i, header in enumerate(headers):
            # Hacer los encabezados clickeables para ordenar
            btn = tk.Label(
                header_frame,
                text=header,
                font=("Arial", 12, "bold"),
                fg="#e2e8f0",
                bg="#334155",
                padx=15,
                pady=12,
                cursor="hand2",
            )
            btn.grid(row=0, column=i, sticky="ew", padx=2)
            btn.bind("<Button-1>", lambda e, col=i: self.ordenar_tabla(col))

            header_frame.grid_columnconfigure(i, weight=1)

        # Generar registros de historial
        history_data = self.generate_history_data()

        # Crear filas de datos MEJORADAS
        self.table_rows = []
        for i, record in enumerate(history_data):
            row_bg = "#1e293b" if i % 2 == 0 else "#0f172a"
            row_frame = tk.Frame(self.table_frame, bg=row_bg)
            row_frame.pack(fill="x", padx=20, pady=2)

            for col, value in enumerate(record):
                # Determinar color según el tipo de dato y valor
                text_color = self.get_color_for_value(value, col)

                label = tk.Label(
                    row_frame,
                    text=value,
                    font=("Arial", 11),
                    fg=text_color,
                    bg=row_bg,
                    padx=15,
                    pady=10,
                )
                label.grid(row=0, column=col, sticky="w")
                row_frame.grid_columnconfigure(col, weight=1)

            self.table_rows.append((row_frame, record))

        # Actualizar estadísticas
        self.actualizar_estadisticas(history_data)

    def get_headers_for_parameter(self):
        """Obtener encabezados según el parámetro seleccionado"""
        if self.selected_parameter == "Potencia":
            return [
                "Fecha",
                "Hora",
                "Potencia Total (MW)",
                "Potencia Activa (MW)",
                "Potencia Reactiva (MVAR)",
                "Estado",
            ]
        elif self.selected_parameter == "Frecuencia":
            return [
                "Fecha",
                "Hora",
                "Frecuencia (Hz)",
                "Desviación",
                "Calidad",
                "Estado",
            ]
        elif self.selected_parameter == "Voltaje":
            return [
                "Fecha",
                "Hora",
                "Voltaje (V)",
                "Fase A",
                "Fase B",
                "Fase C",
                "Estado",
            ]
        elif self.selected_parameter == "Corriente":
            return [
                "Fecha",
                "Hora",
                "Corriente (A)",
                "Fase A",
                "Fase B",
                "Fase C",
                "Estado",
            ]
        else:
            return ["Fecha", "Hora", "Parámetro", "Valor", "Unidad", "Límite", "Estado"]

    def generate_history_data(self):
        """Generar datos de historial de ejemplo"""
        # Si estamos en modo Excel, usar datos del Excel para el historial
        if self.scada_data.excel_loaded and self.scada_data.excel_data is not None:
            return self.generate_history_from_excel()
        else:
            return self.generate_simulated_history()

    def generate_history_from_excel(self):
        """Generar historial desde datos del Excel"""
        data = []
        df = self.scada_data.excel_data

        # Usar los datos del Excel para generar el historial
        for i in range(min(50, len(df))):
            date = datetime.now() - timedelta(hours=i)
            fecha_str = date.strftime("%d/%m/%Y")
            hora_str = date.strftime("%H:%M:%S")

            if self.selected_parameter == "Potencia":
                potencia_total = (
                    df["Potencia_Total"].iloc[i % len(df)]
                    if "Potencia_Total" in df.columns
                    else 40 + random.uniform(-2, 3)
                )
                potencia_activa = (
                    df["Potencia_Activa"].iloc[i % len(df)]
                    if "Potencia_Activa" in df.columns
                    else potencia_total * 0.85
                )
                potencia_reactiva = (
                    df["Potencia_Reactiva"].iloc[i % len(df)]
                    if "Potencia_Reactiva" in df.columns
                    else potencia_total * 0.15
                )

                data.append(
                    [
                        fecha_str,
                        hora_str,
                        f"{potencia_total:.1f} MW",
                        f"{potencia_activa:.1f} MW",
                        f"{potencia_reactiva:.1f} MVAR",
                        "Excel",
                    ]
                )

            elif self.selected_parameter == "Frecuencia":
                frecuencia = (
                    df["Frecuencia"].iloc[i % len(df)]
                    if "Frecuencia" in df.columns
                    else 60.0 + random.uniform(-0.1, 0.1)
                )
                data.append(
                    [
                        fecha_str,
                        hora_str,
                        f"{frecuencia:.2f} Hz",
                        f"{abs(frecuencia-60.0):.3f} Hz",
                        "Excel",
                        "Excel",
                    ]
                )

            elif self.selected_parameter == "Voltaje":
                voltaje = (
                    df["Voltaje"].iloc[i % len(df)]
                    if "Voltaje" in df.columns
                    else 220 + random.uniform(-5, 5)
                )
                data.append(
                    [
                        fecha_str,
                        hora_str,
                        f"{voltaje:.1f} V",
                        f"{voltaje:.1f} V",
                        f"{voltaje:.1f} V",
                        f"{voltaje:.1f} V",
                        "Excel",
                    ]
                )

            elif self.selected_parameter == "Corriente":
                corriente = (
                    df["Corriente"].iloc[i % len(df)]
                    if "Corriente" in df.columns
                    else 180 + random.uniform(-20, 25)
                )
                data.append(
                    [
                        fecha_str,
                        hora_str,
                        f"{corriente:.1f} A",
                        f"{corriente:.1f} A",
                        f"{corriente:.1f} A",
                        f"{corriente:.1f} A",
                        "Excel",
                    ]
                )

            else:
                # Todos los parámetros
                param = "Excel"
                valor = f"{df.iloc[i % len(df)].mean():.1f}"
                data.append(
                    [fecha_str, hora_str, param, valor, "Excel", "Excel", "Excel"]
                )

        return data

    def generate_simulated_history(self):
        """Generar datos de historial simulados (modo SCADA)"""
        data = []
        base_date = datetime.now() - timedelta(days=7)

        for i in range(50):
            date = base_date + timedelta(hours=i * 3)
            fecha_str = date.strftime("%d/%m/%Y")
            hora_str = date.strftime("%H:%M:%S")

            if self.selected_parameter == "Potencia":
                potencia_total = round(40 + random.uniform(-2, 3), 1)
                potencia_activa = round(potencia_total * 0.85, 1)
                potencia_reactiva = round(potencia_total * 0.15, 1)
                estado = "Óptimo" if potencia_total > 41 else "Normal"

                data.append(
                    [
                        fecha_str,
                        hora_str,
                        f"{potencia_total} MW",
                        f"{potencia_activa} MW",
                        f"{potencia_reactiva} MVAR",
                        estado,
                    ]
                )

            elif self.selected_parameter == "Frecuencia":
                frecuencia = round(60.0 + random.uniform(-0.1, 0.1), 2)
                desviacion = round(abs(frecuencia - 60.0), 3)
                calidad = (
                    "Óptima"
                    if desviacion <= 0.05
                    else "Aceptable" if desviacion <= 0.1 else "Crítica"
                )
                estado = "Estable" if calidad == "Óptima" else "Variable"

                data.append(
                    [
                        fecha_str,
                        hora_str,
                        f"{frecuencia} Hz",
                        f"{desviacion} Hz",
                        calidad,
                        estado,
                    ]
                )

            elif self.selected_parameter == "Voltaje":
                voltaje = round(220 + random.uniform(-5, 5), 1)
                fase_a = round(voltaje + random.uniform(-2, 2), 1)
                fase_b = round(voltaje + random.uniform(-2, 2), 1)
                fase_c = round(voltaje + random.uniform(-2, 2), 1)
                estado = "Óptimo" if 215 <= voltaje <= 225 else "Variable"

                data.append(
                    [
                        fecha_str,
                        hora_str,
                        f"{voltaje} V",
                        f"{fase_a} V",
                        f"{fase_b} V",
                        f"{fase_c} V",
                        estado,
                    ]
                )

            elif self.selected_parameter == "Corriente":
                corriente = round(180 + random.uniform(-20, 25), 1)
                fase_a = round(corriente + random.uniform(-10, 10), 1)
                fase_b = round(corriente + random.uniform(-10, 10), 1)
                fase_c = round(corriente + random.uniform(-10, 10), 1)
                estado = (
                    "Normal"
                    if corriente <= 190
                    else "Alerta" if corriente <= 200 else "Crítico"
                )

                data.append(
                    [
                        fecha_str,
                        hora_str,
                        f"{corriente} A",
                        f"{fase_a} A",
                        f"{fase_b} A",
                        f"{fase_c} A",
                        estado,
                    ]
                )

            else:
                # Todos los parámetros
                parametros = ["Potencia", "Frecuencia", "Voltaje", "Corriente"]
                param = random.choice(parametros)
                if param == "Potencia":
                    valor = f"{round(40 + random.uniform(-2, 3), 1)} MW"
                    unidad = "MW"
                    limite = "45 MW"
                elif param == "Frecuencia":
                    valor = f"{round(60.0 + random.uniform(-0.1, 0.1), 2)} Hz"
                    unidad = "Hz"
                    limite = "59.5-60.5 Hz"
                elif param == "Voltaje":
                    valor = f"{round(220 + random.uniform(-5, 5), 1)} V"
                    unidad = "V"
                    limite = "215-225 V"
                else:
                    valor = f"{round(180 + random.uniform(-20, 25), 1)} A"
                    unidad = "A"
                    limite = "200 A"

                estado = random.choice(["Óptimo", "Normal", "Alerta", "Crítico"])
                data.append([fecha_str, hora_str, param, valor, unidad, limite, estado])

        return data

    def get_color_for_value(self, value, column_index):
        """Determinar color del texto según el valor y columna"""
        if isinstance(value, str):
            value_lower = value.lower()

            # Colores para estados
            if any(
                estado in value_lower
                for estado in ["óptimo", "excelente", "normal", "estable"]
            ):
                return "#10b981"
            elif any(
                estado in value_lower
                for estado in ["alerta", "variable", "regular", "bajo"]
            ):
                return "#f59e0b"
            elif any(estado in value_lower for estado in ["crítico", "fuera de rango"]):
                return "#ef4444"

            # Colores para unidades de medida
            if "mw" in value_lower or "mvar" in value_lower:
                return "#fbbf24"
            elif "hz" in value_lower:
                return "#a78bfa"
            elif "v" in value_lower:
                return "#60a5fa"
            elif "a" in value_lower:
                return "#34d399"

        return "#e2e8f0"

    def ordenar_tabla(self, columna):
        """Ordenar tabla por columna clickeada"""
        messagebox.showinfo("Ordenar", f"Ordenando por columna {columna + 1}")

    def actualizar_estadisticas(self, datos):
        """Actualizar estadísticas en la interfaz"""
        if not datos:
            self.record_count_label.config(text="0 registros encontrados")
            self.stats_label.config(text="")
            return

        total_registros = len(datos)

        if self.selected_parameter == "Potencia":
            valores = []
            for fila in datos:
                for valor in fila:
                    if "MW" in str(valor) and not "MVAR" in str(valor):
                        try:
                            num = float(str(valor).replace(" MW", "").strip())
                            valores.append(num)
                        except:
                            pass

            if valores:
                promedio = sum(valores) / len(valores)
                self.stats_label.config(
                    text=f"Promedio: {promedio:.1f} MW | Mín: {min(valores):.1f} | Máx: {max(valores):.1f}"
                )

        self.record_count_label.config(text=f"{total_registros} registros encontrados")

    def generar_reporte_historial(self):
        """Generar y guardar reporte Excel del historial actual con formato profesional y logo"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
            from openpyxl.utils import get_column_letter
            from openpyxl.drawing.image import Image
            from openpyxl.worksheet.page import PageMargins
            import os

            # Obtener datos actuales mostrados
            datos = []
            for _, record in getattr(self, "table_rows", []):
                datos.append(record)

            if not datos:
                messagebox.showwarning("Advertencia", "No hay datos para exportar.")
                return

            headers = self.get_headers_for_parameter()

            # Diálogo para guardar
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Guardar Reporte de Historial",
                initialfile=f"Historial_{self.selected_parameter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            )
            if not file_path:
                return

            # Crear libro
            wb = Workbook()
            ws = wb.active
            ws.title = "Historial de Mediciones"

            # Márgenes de página más amplios
            ws.page_margins = PageMargins(left=0.4, right=0.4, top=0.5, bottom=0.5)

            # ===========================
            #  ENCABEZADO CON LOGO Y TÍTULO
            # ===========================
            logo_path = os.path.join("assets", "logo.jpg")
            if os.path.exists(logo_path):
                img = Image(logo_path)
                img.height = 80
                img.width = 100
                ws.add_image(img, "A1")

            # Título general
            ws.merge_cells("B1:{}2".format(get_column_letter(len(headers))))
            titulo_cell = ws["B1"]
            titulo_cell.value = f"Reporte de {self.selected_parameter}"
            titulo_cell.font = Font(bold=True, size=16, color="FFFFFF")
            titulo_cell.alignment = Alignment(horizontal="center", vertical="center")
            titulo_cell.fill = PatternFill(
                start_color="1E40AF", end_color="1E3A8A", fill_type="solid"
            )
            ws.row_dimensions[1].height = 30

            # Subtítulo con fecha
            ws.merge_cells("B3:{}3".format(get_column_letter(len(headers))))
            ws["B3"].value = (
                f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            ws["B3"].alignment = Alignment(horizontal="center", vertical="center")
            ws["B3"].font = Font(italic=True, color="4B5563")

            # ===========================
            #  ENCABEZADOS DE TABLA
            # ===========================
            header_row = 5
            header_fill = PatternFill(
                start_color="0F172A", end_color="0F172A", fill_type="solid"
            )
            header_font = Font(bold=True, color="FFFFFF")
            thin_border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )

            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=header_row, column=col_num, value=header)
                cell.fill = header_fill
                cell.font = header_font
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # ===========================
            #  DATOS CON FORMATO ZEBRA
            # ===========================
            even_fill = PatternFill(
                start_color="F8FAFC", end_color="F8FAFC", fill_type="solid"
            )
            odd_fill = PatternFill(
                start_color="E2E8F0", end_color="E2E8F0", fill_type="solid"
            )

            start_row = header_row + 1
            for row_num, row_data in enumerate(datos, start=start_row):
                for col_num, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num, value=value)
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = thin_border
                    # Fondo alternado
                    cell.fill = even_fill if row_num % 2 == 0 else odd_fill

            # ===========================
            #  AUTOAJUSTE DE COLUMNAS
            # ===========================
            for col_num in range(1, len(headers) + 1):
                col_letter = get_column_letter(col_num)
                max_length = max(
                    (len(str(cell.value)) if cell.value else 0)
                    for cell in ws[col_letter]
                )
                ws.column_dimensions[col_letter].width = max(max_length + 3, 14)

            # ===========================
            #  PIE DE FIRMA
            # ===========================
            footer_row = ws.max_row + 2
            ws.merge_cells(
                f"A{footer_row}:{get_column_letter(len(headers))}{footer_row}"
            )
            ws[f"A{footer_row}"].value = (
                "Sistema SCADA Eléctrico © 2025 - Todos los derechos reservados"
            )
            ws[f"A{footer_row}"].alignment = Alignment(
                horizontal="center", vertical="center"
            )
            ws[f"A{footer_row}"].font = Font(italic=True, size=10, color="6B7280")

            # ===========================
            #  GUARDAR ARCHIVO
            # ===========================
            wb.save(file_path)
            messagebox.showinfo(
                "Éxito",
                f"✅ Reporte profesional generado correctamente.\n\nArchivo: {file_path}",
            )

        except Exception as e:
            messagebox.showerror(
                "Error", f"Ocurrió un error al generar el reporte:\n{str(e)}"
            )

    def clear_content(self):
        """Limpiar el contenido actual"""
        if self.content_container:
            for widget in self.content_container.winfo_children():
                widget.destroy()

    def show_dashboard(self):
        """Mostrar el dashboard principal"""
        self.clear_content()
        self.current_section = "dashboard"
        self.create_dashboard(self.content_container)

    def show_configuracion(self):
        """Mostrar panel de configuración"""
        self.clear_content()
        self.current_section = "configuracion"
        messagebox.showinfo("Configuración", "Panel de configuración del sistema")

    def gestionar_usuarios(self):
        """Gestión de usuarios"""
        self.clear_content()
        self.current_section = "usuarios"
        messagebox.showinfo("Usuarios", "Panel de gestión de usuarios")

    def mostrar_reportes(self):
        """Función para mostrar reportes"""
        messagebox.showinfo("Reportes", "Generando reportes del sistema")


if __name__ == "__main__":

    def dummy_logout():
        print("Saliendo del sistema...")

    root = tk.Tk()
    user_data = {
        "nombre": "ADMINISTRADOR PRINCIPAL",
        "role": "Administrador del Sistema",
    }
    app = AdminDashboard(root, user_data, dummy_logout)
    root.mainloop()
