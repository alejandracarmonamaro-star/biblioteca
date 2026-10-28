"""Componente PRÉSTAMOS.

Gestiona préstamos, devoluciones y reservas.
IMPORTANTE: este componente NO conoce el interior de Catalogo ni de Socios.
Solo les pide cosas llamando a sus funciones públicas:
    catalogo.obtener / num_disponibles / marcar_prestado / marcar_devuelto
    socios.obtener / esta_sancionado / sancionar
"""
from datetime import date, timedelta

DIAS_PRESTAMO = 7       # cada préstamo caduca a los 7 días
MAX_LIBROS = 2          # un socio no puede tener más de 2 libros a la vez


class Prestamo:
    """Un préstamo concreto: tiene identidad (id) y estado (devuelto o no)."""

    def __init__(self, id, socio_id, libro_id, ejemplar_id, inicio):
        self.id = id
        self.socio_id = socio_id
        self.libro_id = libro_id
        self.ejemplar_id = ejemplar_id
        self.inicio = inicio
        self.vencimiento = inicio + timedelta(days=DIAS_PRESTAMO)
        self.devuelto_el = None

    @property
    def activo(self):
        return self.devuelto_el is None

    def esta_vencido(self, hoy):
        return self.activo and hoy > self.vencimiento


class Reserva:
    def __init__(self, socio_id, libro_id, fecha):
        self.socio_id = socio_id
        self.libro_id = libro_id
        self.fecha = fecha


class Prestamos:
    def __init__(self, catalogo, socios):
        # Guardamos los componentes que nos pasan; solo usaremos sus funciones públicas.
        self._catalogo = catalogo
        self._socios = socios
        self._prestamos = {}       # id -> Prestamo
        self._reservas = []        # cola de Reserva (por orden de llegada)
        self._siguiente_id = 1

    # ---------- consultas ----------
    def prestamos_activos(self, socio_id=None):
        return [p for p in self._prestamos.values()
                if p.activo and (socio_id is None or p.socio_id == socio_id)]

    def vencidos(self, hoy=None):
        hoy = hoy or date.today()
        return [p for p in self._prestamos.values() if p.esta_vencido(hoy)]

    def reservas_de(self, libro_id):
        return [r for r in self._reservas if r.libro_id == libro_id]

    def reservas_pendientes(self):
        return list(self._reservas)

    # ---------- préstamo ----------
    def prestar(self, socio_id, libro_id, hoy=None):
        hoy = hoy or date.today()
        socio = self._socios.obtener(socio_id)
        libro = self._catalogo.obtener(libro_id)

        if self._socios.esta_sancionado(socio_id, hoy):
            raise ValueError(f"{socio.nombre} está sancionado/a y no puede pedir libros.")
        if len(self.prestamos_activos(socio_id)) >= MAX_LIBROS:
            raise ValueError(f"{socio.nombre} ya tiene {MAX_LIBROS} libros prestados (máximo permitido).")
        if any(p.libro_id == libro_id for p in self.prestamos_activos(socio_id)):
            raise ValueError(f"{socio.nombre} ya tiene un ejemplar de «{libro.titulo}».")

        libres = self._catalogo.num_disponibles(libro_id)
        if libres == 0:
            raise ValueError(f"No quedan ejemplares de «{libro.titulo}». Puedes reservarlo.")

        # Los ejemplares libres se reservan primero para quienes están en la cola.
        cola = self.reservas_de(libro_id)
        posicion = next((i for i, r in enumerate(cola) if r.socio_id == socio_id), None)
        if posicion is not None:
            if posicion >= libres:
                raise ValueError("Tu reserva todavía no es la siguiente: espera tu turno.")
            self._reservas.remove(cola[posicion])      # se cumple su reserva
        elif libres <= len(cola):
            raise ValueError(f"Los ejemplares libres de «{libro.titulo}» están reservados para otros socios.")

        ejemplar_id = self._catalogo.marcar_prestado(libro_id)
        prestamo = Prestamo(self._siguiente_id, socio_id, libro_id, ejemplar_id, hoy)
        self._prestamos[prestamo.id] = prestamo
        self._siguiente_id += 1
        return prestamo

    # ---------- devolución ----------
    def devolver(self, prestamo_id, hoy=None):
        """Devuelve el libro. Si hay retraso, sanciona al socio tantos días como de retraso.
        Devuelve (prestamo, dias_de_retraso)."""
        hoy = hoy or date.today()
        if prestamo_id not in self._prestamos or not self._prestamos[prestamo_id].activo:
            raise ValueError(f"No hay ningún préstamo activo con id {prestamo_id}.")
        prestamo = self._prestamos[prestamo_id]
        self._catalogo.marcar_devuelto(prestamo.ejemplar_id)
        prestamo.devuelto_el = hoy

        retraso = max(0, (hoy - prestamo.vencimiento).days)
        if retraso > 0:
            self._socios.sancionar(prestamo.socio_id, hoy + timedelta(days=retraso))
        return prestamo, retraso

    # ---------- reservas ----------
    def reservar(self, socio_id, libro_id, hoy=None):
        hoy = hoy or date.today()
        socio = self._socios.obtener(socio_id)
        libro = self._catalogo.obtener(libro_id)

        if self._socios.esta_sancionado(socio_id, hoy):
            raise ValueError(f"{socio.nombre} está sancionado/a y no puede pedir libros.")
        if any(p.libro_id == libro_id for p in self.prestamos_activos(socio_id)):
            raise ValueError(f"{socio.nombre} ya tiene un ejemplar de «{libro.titulo}».")
        cola = self.reservas_de(libro_id)
        if any(r.socio_id == socio_id for r in cola):
            raise ValueError(f"{socio.nombre} ya tiene reservado «{libro.titulo}».")
        if self._catalogo.num_disponibles(libro_id) > len(cola):
            raise ValueError(f"Hay ejemplares libres de «{libro.titulo}»: pide el préstamo directamente.")

        reserva = Reserva(socio_id, libro_id, hoy)
        self._reservas.append(reserva)
        return reserva, len(cola) + 1      # posición en la cola
