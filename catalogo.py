"""Componente CATÁLOGO.

Guarda los libros (títulos) y los ejemplares físicos de cada uno.
Nadie fuera de este fichero debe tocar la estructura interna (_libros):
los demás componentes solo usan las funciones públicas.
"""

DISPONIBLE = "disponible"
PRESTADO = "prestado"


class Ejemplar:
    """Una copia física de un libro. Tiene identidad (id) y estado propio."""

    def __init__(self, id, estado=DISPONIBLE):
        self.id = id            # p. ej. "3-2" = ejemplar 2 del libro 3
        self.estado = estado    # DISPONIBLE o PRESTADO

    def __str__(self):
        return f"{self.id} ({self.estado})"


class Libro:
    """Un título del catálogo. Tiene identidad (id) y varios ejemplares."""

    def __init__(self, id, titulo, autor, num_ejemplares=1):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.ejemplares = [Ejemplar(f"{id}-{n}") for n in range(1, num_ejemplares + 1)]

    def disponibles(self):
        return [e for e in self.ejemplares if e.estado == DISPONIBLE]

    def __str__(self):
        libres = len(self.disponibles())
        return (f"[{self.id}] {self.titulo} - {self.autor} "
                f"({libres} de {len(self.ejemplares)} ejemplares disponibles)")


class Catalogo:
    def __init__(self):
        self._libros = {}          # id -> Libro  (privado por convención)
        self._siguiente_id = 1

    # ---------- funciones públicas ----------
    def agregar(self, titulo, autor, num_ejemplares=1):
        """Da de alta un título nuevo con sus ejemplares y devuelve el Libro."""
        if not titulo.strip():
            raise ValueError("El título no puede estar vacío.")
        if num_ejemplares < 1:
            raise ValueError("Debe haber al menos un ejemplar.")
        libro = Libro(self._siguiente_id, titulo.strip(), autor.strip(), num_ejemplares)
        self._libros[libro.id] = libro
        self._siguiente_id += 1
        return libro

    def buscar(self, titulo):
        """Devuelve la lista de libros cuyo título contiene el texto (sin mayúsculas)."""
        texto = titulo.strip().lower()
        return [l for l in self._libros.values() if texto in l.titulo.lower()]

    def obtener(self, id):
        """Devuelve el Libro con ese id, o lanza ValueError si no existe."""
        if id not in self._libros:
            raise ValueError(f"No existe ningún libro con id {id}.")
        return self._libros[id]

    def num_disponibles(self, id):
        """Cuántos ejemplares de ese libro están libres ahora mismo."""
        return len(self.obtener(id).disponibles())

    def marcar_prestado(self, id):
        """Marca como prestado un ejemplar libre del libro y devuelve su id."""
        libro = self.obtener(id)
        libres = libro.disponibles()
        if not libres:
            raise ValueError(f"No quedan ejemplares disponibles de «{libro.titulo}».")
        ejemplar = libres[0]
        ejemplar.estado = PRESTADO
        return ejemplar.id

    def marcar_devuelto(self, id_ejemplar):
        """Vuelve a dejar disponible un ejemplar que estaba prestado."""
        for libro in self._libros.values():
            for ejemplar in libro.ejemplares:
                if ejemplar.id == id_ejemplar:
                    if ejemplar.estado != PRESTADO:
                        raise ValueError(f"El ejemplar {id_ejemplar} no estaba prestado.")
                    ejemplar.estado = DISPONIBLE
                    return
        raise ValueError(f"No existe el ejemplar {id_ejemplar}.")

    def listar(self):
        return list(self._libros.values())


def catalogo_de_ejemplo():
    """Catálogo con algunos libros para poder probar la aplicación."""
    c = Catalogo()
    c.agregar("Don Quijote de la Mancha", "Miguel de Cervantes", 2)
    c.agregar("Cien años de soledad", "Gabriel García Márquez", 1)
    c.agregar("La sombra del viento", "Carlos Ruiz Zafón", 3)
    c.agregar("El principito", "Antoine de Saint-Exupéry", 2)
    c.agregar("Rayuela", "Julio Cortázar", 1)
    return c
