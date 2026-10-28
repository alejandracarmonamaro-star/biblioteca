// Componente SOCIOS: guarda a las personas socias y si están sancionadas.

export class Socio {
  constructor(id, nombre) {
    this.id = id;
    this.nombre = nombre;
    this.sancionadoHasta = null; // fecha "AAAA-MM-DD" o null
  }
  estaSancionado(hoy) { return this.sancionadoHasta !== null && hoy < this.sancionadoHasta; }
}

export class Socios {
  #socios = new Map();
  #siguienteId = 1;

  alta(nombre) {
    if (!nombre.trim()) throw new Error('El nombre no puede estar vacío.');
    const socio = new Socio(this.#siguienteId++, nombre.trim());
    this.#socios.set(socio.id, socio);
    return socio;
  }

  obtener(id) {
    if (!this.#socios.has(id)) throw new Error(`No existe ningún socio con id ${id}.`);
    return this.#socios.get(id);
  }

  estaSancionado(id, hoy) { return this.obtener(id).estaSancionado(hoy); }

  sancionar(id, hasta) {
    const socio = this.obtener(id);
    if (socio.sancionadoHasta === null || hasta > socio.sancionadoHasta) socio.sancionadoHasta = hasta;
  }

  listar() { return [...this.#socios.values()]; }
}
