// Componente PRÉSTAMOS: gestiona préstamos, devoluciones y reservas.
// NO conoce el interior de Catalogo ni de Socios: solo llama a sus funciones públicas:
//   catalogo.obtener / numDisponibles / marcarPrestado / marcarDevuelto
//   socios.obtener / estaSancionado / sancionar
import { sumarDias, diferenciaDias } from './fechas.js';

export const DIAS_PRESTAMO = 7;  // cada préstamo caduca a los 7 días
export const MAX_LIBROS = 2;     // máximo de libros a la vez por socio

export class Prestamo {
  constructor(id, socioId, libroId, ejemplarId, inicio) {
    this.id = id;
    this.socioId = socioId;
    this.libroId = libroId;
    this.ejemplarId = ejemplarId;
    this.inicio = inicio;
    this.vencimiento = sumarDias(inicio, DIAS_PRESTAMO);
    this.devueltoEl = null;
  }
  get activo() { return this.devueltoEl === null; }
  estaVencido(hoy) { return this.activo && hoy > this.vencimiento; }
}

export class Reserva {
  constructor(socioId, libroId, fecha) {
    this.socioId = socioId;
    this.libroId = libroId;
    this.fecha = fecha;
  }
}

export class Prestamos {
  #catalogo;
  #socios;
  #prestamos = new Map();
  #reservas = [];
  #siguienteId = 1;

  constructor(catalogo, socios) {
    this.#catalogo = catalogo;
    this.#socios = socios;
  }

  // ---------- consultas ----------
  prestamosActivos(socioId = null) {
    return [...this.#prestamos.values()].filter((p) => p.activo && (socioId === null || p.socioId === socioId));
  }
  vencidos(hoy) { return [...this.#prestamos.values()].filter((p) => p.estaVencido(hoy)); }
  reservasDe(libroId) { return this.#reservas.filter((r) => r.libroId === libroId); }
  reservasPendientes() { return [...this.#reservas]; }

  // ---------- préstamo ----------
  prestar(socioId, libroId, hoy) {
    const socio = this.#socios.obtener(socioId);
    const libro = this.#catalogo.obtener(libroId);

    if (this.#socios.estaSancionado(socioId, hoy)) throw new Error(`${socio.nombre} está sancionado/a y no puede pedir libros.`);
    const activos = this.prestamosActivos(socioId);
    if (activos.length >= MAX_LIBROS) throw new Error(`${socio.nombre} ya tiene ${MAX_LIBROS} libros prestados (máximo permitido).`);
    if (activos.some((p) => p.libroId === libroId)) throw new Error(`${socio.nombre} ya tiene un ejemplar de «${libro.titulo}».`);

    const libres = this.#catalogo.numDisponibles(libroId);
    if (libres === 0) throw new Error(`No quedan ejemplares de «${libro.titulo}». Puedes reservarlo.`);

    // Los ejemplares libres se guardan primero para quienes están en la cola de reservas.
    const cola = this.reservasDe(libroId);
    const posicion = cola.findIndex((r) => r.socioId === socioId);
    if (posicion !== -1) {
      if (posicion >= libres) throw new Error('Tu reserva todavía no es la siguiente: espera tu turno.');
      this.#reservas.splice(this.#reservas.indexOf(cola[posicion]), 1); // se cumple su reserva
    } else if (libres <= cola.length) {
      throw new Error(`Los ejemplares libres de «${libro.titulo}» están reservados para otros socios.`);
    }

    const ejemplarId = this.#catalogo.marcarPrestado(libroId);
    const prestamo = new Prestamo(this.#siguienteId++, socioId, libroId, ejemplarId, hoy);
    this.#prestamos.set(prestamo.id, prestamo);
    return prestamo;
  }

  // ---------- devolución ----------
  // Si hay retraso, sanciona al socio tantos días como de retraso.
  devolver(prestamoId, hoy) {
    const prestamo = this.#prestamos.get(prestamoId);
    if (!prestamo || !prestamo.activo) throw new Error(`No hay ningún préstamo activo con id ${prestamoId}.`);
    this.#catalogo.marcarDevuelto(prestamo.ejemplarId);
    prestamo.devueltoEl = hoy;

    const retraso = Math.max(0, diferenciaDias(hoy, prestamo.vencimiento));
    if (retraso > 0) this.#socios.sancionar(prestamo.socioId, sumarDias(hoy, retraso));
    return { prestamo, retraso };
  }

  // ---------- reservas ----------
  reservar(socioId, libroId, hoy) {
    const socio = this.#socios.obtener(socioId);
    const libro = this.#catalogo.obtener(libroId);

    if (this.#socios.estaSancionado(socioId, hoy)) throw new Error(`${socio.nombre} está sancionado/a y no puede pedir libros.`);
    if (this.prestamosActivos(socioId).some((p) => p.libroId === libroId)) throw new Error(`${socio.nombre} ya tiene un ejemplar de «${libro.titulo}».`);
    const cola = this.reservasDe(libroId);
    if (cola.some((r) => r.socioId === socioId)) throw new Error(`${socio.nombre} ya tiene reservado «${libro.titulo}».`);
    if (this.#catalogo.numDisponibles(libroId) > cola.length) throw new Error(`Hay ejemplares libres de «${libro.titulo}»: pide el préstamo directamente.`);

    const reserva = new Reserva(socioId, libroId, hoy);
    this.#reservas.push(reserva);
    return { reserva, posicion: cola.length + 1 };
  }
}
