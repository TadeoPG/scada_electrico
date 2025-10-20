import tkinter as tk
from tkinter import ttk, messagebox
from database import UserDatabase


class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.db = UserDatabase()
        self.logo_image = None

        self.setup_ui()

    def setup_ui(self):
        self.root.title("LOGIN - SCADA ELÉCTRICO")
        self.root.geometry("450x500")  # Ventana más compacta
        self.root.configure(bg="#1e3c72")
        self.root.resizable(False, False)

        self.center_window()

        main_frame = tk.Frame(self.root, bg="#1e3c72", padx=15, pady=15)
        main_frame.pack(expand=True, fill="both")

        # Logo MPC más compacto
        self.create_compact_mpc_logo(main_frame)

        title_label = tk.Label(
            main_frame,
            text="SISTEMA SCADA ELÉCTRICO\nControl y Monitoreo de Subestaciones",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#1e3c72",
        )
        title_label.pack(pady=8)

        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill="x", pady=12)

        form_frame = tk.Frame(main_frame, bg="#1e3c72")
        form_frame.pack(pady=12)

        tk.Label(
            form_frame,
            text="Usuario:",
            font=("Arial", 10, "bold"),
            fg="white",
            bg="#1e3c72",
        ).grid(row=0, column=0, sticky="w", pady=6)
        self.username_entry = tk.Entry(
            form_frame, font=("Arial", 10), width=20, relief="solid", bd=1
        )
        self.username_entry.grid(row=0, column=1, padx=8, pady=6)

        tk.Label(
            form_frame,
            text="Contraseña:",
            font=("Arial", 10, "bold"),
            fg="white",
            bg="#1e3c72",
        ).grid(row=1, column=0, sticky="w", pady=6)
        self.password_entry = tk.Entry(
            form_frame, show="•", font=("Arial", 10), width=20, relief="solid", bd=1
        )
        self.password_entry.grid(row=1, column=1, padx=8, pady=6)

        self.progress = ttk.Progressbar(
            main_frame, orient="horizontal", length=200, mode="determinate"
        )
        self.progress.pack(pady=12)

        button_frame = tk.Frame(main_frame, bg="#1e3c72")
        button_frame.pack(pady=12)

        ingresar_btn = tk.Button(
            button_frame,
            text="INGRESAR",
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            width=10,
            height=1,
            relief="raised",
            bd=2,
            command=self.authenticate,
        )
        ingresar_btn.pack(side="left", padx=6)

        salir_btn = tk.Button(
            button_frame,
            text="SALIR",
            font=("Arial", 10, "bold"),
            bg="#e74c3c",
            fg="white",
            width=10,
            height=1,
            relief="raised",
            bd=2,
            command=self.root.quit,
        )
        salir_btn.pack(side="left", padx=6)

        info_label = tk.Label(
            main_frame,
            text="Prueba con: admin/admin123 | operador/operador123 | supervisor/supervisor123",
            font=("Arial", 7),
            fg="#bdc3c7",
            bg="#1e3c72",
        )
        info_label.pack(pady=8)

        self.root.bind("<Return>", lambda event: self.authenticate())
        self.username_entry.focus()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_compact_mpc_logo(self, parent):
        """Logo MPC compacto y bien distribuido"""
        # Contenedor principal más pequeño
        logo_container = tk.Frame(parent, bg="#1e3c72")
        logo_container.pack(pady=15)

        # Frame del logo más compacto
        logo_frame = tk.Frame(
            logo_container, bg="#2c3e50", width=180, height=90, relief="solid", bd=2
        )
        logo_frame.pack()
        logo_frame.pack_propagate(False)

        # Contenido del logo optimizado
        content_frame = tk.Frame(logo_frame, bg="#2c3e50")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Icono más pequeño
        icon_label = tk.Label(
            content_frame,
            text="⚡",
            font=("Arial", 20, "bold"),
            fg="#f39c12",
            bg="#2c3e50",
        )
        icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 5))

        # Texto del logo en dos líneas compactas
        name_label1 = tk.Label(
            content_frame,
            text="MPC",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#2c3e50",
            anchor="w",
        )
        name_label1.grid(row=0, column=1, sticky="w")

        name_label2 = tk.Label(
            content_frame,
            text="INGENIEROS S.A.C",
            font=("Arial", 9, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50",
            anchor="w",
        )
        name_label2.grid(row=1, column=1, sticky="w")

        # Línea decorativa compacta
        line_frame = tk.Frame(logo_frame, bg="#f39c12", height=1, width=140)
        line_frame.place(relx=0.5, rely=0.85, anchor="center")

        # Eslogan más pequeño
        slogan_label = tk.Label(
            logo_frame,
            text="Sistemas SCADA",
            font=("Arial", 7),
            fg="#bdc3c7",
            bg="#2c3e50",
        )
        slogan_label.place(relx=0.5, rely=0.92, anchor="center")

    def authenticate(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return

        self.progress["value"] = 0
        self.root.update()

        for i in range(0, 101, 2):
            self.progress["value"] = i
            self.root.update_idletasks()
            self.root.after(10)

        user_data = self.db.verify_user(username, password)

        if user_data:
            messagebox.showinfo("Éxito", f"Bienvenido {user_data['nombre']}")
            self.root.withdraw()
            self.on_login_success(user_data)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            self.progress["value"] = 0
            self.password_entry.delete(0, tk.END)
            self.username_entry.focus()
