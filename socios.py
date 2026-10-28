"""Componente SOCIOS.

Guarda a las personas socias de la biblioteca y si están sancionadas.
"""


class Socio:
    """Una persona socia. Tiene identidad (id) y estado (sanción)."""

    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.sancionado_hasta = None    # fecha (date) o None si no está sancionado

    def esta_sancionado(self, hoy):
        return self.sancionado_hasta is not None and hoy < self.sancionado_hasta

    def __str__(self):
        extra = f" - sancionado hasta {self.sancionado_hasta}" if self.sancionado_hasta else ""
        return f"[{self.id}] {self.nombre}{extra}"


class Socios:
    def __init__(self):
        self._socios = {}          # id -> Socio  (privado por convención)
        self._siguiente_id = 1

    # ---------- funciones públicas ----------
    def alta(self, nombre):
        """Da de alta un socio nuevo y devuelve el Socio."""
        if not nombre.strip():
            raise ValueError("El nombre no puede estar vacío.")
        socio = Socio(self._siguiente_id, nombre.strip())
        self._socios[socio.id] = socio
        self._siguiente_id += 1
        return socio

    def obtener(self, id):
        """Devuelve el Socio con ese id, o lanza ValueError si no existe."""
        if id not in self._socios:
            raise ValueError(f"No existe ningún socio con id {id}.")
        return self._socios[id]

    def esta_sancionado(self, id, hoy):
        """True si el socio no puede pedir libros en la fecha `hoy`."""
        return self.obtener(id).esta_sancionado(hoy)

    def sancionar(self, id, hasta):
        """Sanciona al socio hasta la fecha indicada (si ya tenía una mayor, se mantiene)."""
        socio = self.obtener(id)
        if socio.sancionado_hasta is None or hasta > socio.sancionado_hasta:
            socio.sancionado_hasta = hasta

    def listar(self):
        return list(self._socios.values())
