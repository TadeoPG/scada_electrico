import tkinter as tk
from login_window import LoginWindow
from admin_dashboard import AdminDashboard
from operador_dashboard import OperadorDashboard
from supervisor_dashboard import SupervisorDashboard


class ScadaElectrico:
    def __init__(self):
        self.root = tk.Tk()
        self.current_user = None
        self.show_login()

    def show_login(self):
        self.root.withdraw()
        login_window = tk.Toplevel(self.root)
        LoginWindow(login_window, self.on_login_success)

    def on_login_success(self, user_data):
        self.current_user = user_data
        self.show_dashboard()

    def show_dashboard(self):
        self.root.deiconify()
        for widget in self.root.winfo_children():
            widget.destroy()

        if self.current_user["role"] == "admin":
            AdminDashboard(self.root, self.current_user, self.logout)
        elif self.current_user["role"] == "operador":
            OperadorDashboard(self.root, self.current_user, self.logout)
        elif self.current_user["role"] == "supervisor":
            SupervisorDashboard(self.root, self.current_user, self.logout)

    def logout(self):
        self.current_user = None
        self.root.destroy()
        self.__init__()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ScadaElectrico()
    app.run()
