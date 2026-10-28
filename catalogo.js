// Componente CATÁLOGO: guarda los libros (títulos) y los ejemplares de cada uno.
// Los datos internos son privados (#libros): los demás componentes usan solo las funciones públicas.

export const DISPONIBLE = 'disponible';
export const PRESTADO = 'prestado';

export class Ejemplar {
  constructor(id) {
    this.id = id;             // p. ej. "3-2" = ejemplar 2 del libro 3
    this.estado = DISPONIBLE; // cada ejemplar tiene su propio estado
  }
}

export class Libro {
  constructor(id, titulo, autor, numEjemplares = 1) {
    this.id = id;
    this.titulo = titulo;
    this.autor = autor;
    this.ejemplares = [];
    for (let n = 1; n <= numEjemplares; n++) this.ejemplares.push(new Ejemplar(`${id}-${n}`));
  }
  disponibles() { return this.ejemplares.filter((e) => e.estado === DISPONIBLE); }
}

export class Catalogo {
  #libros = new Map();
  #siguienteId = 1;

  agregar(titulo, autor, numEjemplares = 1) {
    if (!titulo.trim()) throw new Error('El título no puede estar vacío.');
    if (numEjemplares < 1) throw new Error('Debe haber al menos un ejemplar.');
    const libro = new Libro(this.#siguienteId++, titulo.trim(), autor.trim(), numEjemplares);
    this.#libros.set(libro.id, libro);
    return libro;
  }

  buscar(titulo) {
    const texto = titulo.trim().toLowerCase();
    return [...this.#libros.values()].filter((l) => l.titulo.toLowerCase().includes(texto));
  }

  obtener(id) {
    if (!this.#libros.has(id)) throw new Error(`No existe ningún libro con id ${id}.`);
    return this.#libros.get(id);
  }

  numDisponibles(id) { return this.obtener(id).disponibles().length; }

  // Marca como prestado un ejemplar libre y devuelve su id.
  marcarPrestado(id) {
    const libro = this.obtener(id);
    const libres = libro.disponibles();
    if (libres.length === 0) throw new Error(`No quedan ejemplares disponibles de «${libro.titulo}».`);
    libres[0].estado = PRESTADO;
    return libres[0].id;
  }

  marcarDevuelto(idEjemplar) {
    for (const libro of this.#libros.values()) {
      for (const ejemplar of libro.ejemplares) {
        if (ejemplar.id === idEjemplar) {
          if (ejemplar.estado !== PRESTADO) throw new Error(`El ejemplar ${idEjemplar} no estaba prestado.`);
          ejemplar.estado = DISPONIBLE;
          return;
        }
      }
    }
    throw new Error(`No existe el ejemplar ${idEjemplar}.`);
  }

  listar() { return [...this.#libros.values()]; }
}

export function catalogoDeEjemplo() {
  const c = new Catalogo();
  c.agregar('Don Quijote de la Mancha', 'Miguel de Cervantes', 2);
  c.agregar('Cien años de soledad', 'Gabriel García Márquez', 1);
  c.agregar('La sombra del viento', 'Carlos Ruiz Zafón', 3);
  c.agregar('El principito', 'Antoine de Saint-Exupéry', 2);
  c.agregar('Rayuela', 'Julio Cortázar', 1);
  return c;
}
