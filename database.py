class UserDatabase:
    def __init__(self):
        self.users = {
            "admin": {
                "password": "admin123",
                "role": "admin",
                "nombre": "Administrador Principal",
            },
            "operador": {
                "password": "operador123",
                "role": "operador",
                "nombre": "Operador de Turno",
            },
            "supervisor": {
                "password": "supervisor123",
                "role": "supervisor",
                "nombre": "Supervisor de Planta",
            },
        }

    def verify_user(self, username, password):
        if username in self.users and self.users[username]["password"] == password:
            return self.users[username]
        return None


class ScadaData:
    def __init__(self):
        self.potencia_total = 45
        self.subestaciones = {
            "Subestación 1": {"potencia": 10, "max": 15},
            "Subestación 2": {"potencia": 12, "max": 20},
            "Subestación 3": {"potencia": 23, "max": 25},
        }
        self.frecuencia = 60
        self.voltaje = 220
