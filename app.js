// Programa principal de la versión web: crea los tres componentes, los conecta y pinta la pantalla.
import { catalogoDeEjemplo } from './catalogo.js';
import { Socios } from './socios.js';
import { Prestamos, MAX_LIBROS } from './prestamos.js';
import { hoyReal, sumarDias, formatoFecha } from './fechas.js';

const catalogo = catalogoDeEjemplo();
const socios = new Socios();
const prestamos = new Prestamos(catalogo, socios);
socios.alta('Ana López');   // socios de ejemplo para poder probar enseguida
socios.alta('Beto Ruiz');

let hoy = hoyReal();        // "fecha de la biblioteca": se puede avanzar para probar caducidades

const $ = (id) => document.getElementById(id);

// Crea un elemento con texto seguro (nunca se interpreta como HTML).
function el(etiqueta, props = {}, ...hijos) {
  const e = document.createElement(etiqueta);
  for (const [k, v] of Object.entries(props)) {
    if (k === 'class') e.className = v; else e.setAttribute(k, v);
  }
  for (const h of hijos) if (h !== null && h !== undefined) e.append(h);
  return e;
}

function mostrarMensaje(texto, ok = true) {
  const m = $('mensaje');
  m.textContent = texto;
  m.className = 'mensaje ' + (ok ? 'ok' : 'error');
  m.hidden = false;
}

// Ejecuta una acción; si falla (regla incumplida) muestra el error en vez de romper la página.
function accion(fn) {
  try {
    mostrarMensaje(fn(), true);
  } catch (error) {
    mostrarMensaje('✗ ' + error.message, false);
  }
  pintarTodo();
}

function nombreSocio(id) { return socios.obtener(id).nombre; }
function tituloLibro(id) { return catalogo.obtener(id).titulo; }

// ---------- pintar ----------
function pintarFecha() { $('fecha-hoy').textContent = formatoFecha(hoy); }

function pintarLibros() {
  const lista = $('lista-libros');
  lista.replaceChildren();
  const encontrados = catalogo.buscar($('buscador').value);
  if (encontrados.length === 0) lista.append(el('li', { class: 'vacio' }, 'No se ha encontrado ningún libro.'));
  for (const libro of encontrados) {
    const libres = libro.disponibles().length;
    const chips = libro.ejemplares.map((e) => el('span', { class: 'chip ' + e.estado }, `${e.id} · ${e.estado}`));
    const reservas = prestamos.reservasDe(libro.id).length;
    lista.append(el('li', {},
      el('strong', {}, libro.titulo),
      el('span', { class: 'autor' }, `${libro.autor} · id ${libro.id}`),
      el('div', { class: 'nota' }, `${libres} de ${libro.ejemplares.length} ejemplares disponibles` + (reservas ? ` · ${reservas} reserva(s)` : '')),
      el('div', { class: 'chips' }, ...chips)));
  }
}

function pintarSocios() {
  const tbody = $('tabla-socios');
  tbody.replaceChildren();
  for (const s of socios.listar()) {
    const n = prestamos.prestamosActivos(s.id).length;
    const sancionado = socios.estaSancionado(s.id, hoy);
    tbody.append(el('tr', {},
      el('td', {}, s.id), el('td', {}, s.nombre), el('td', {}, `${n} / ${MAX_LIBROS}`),
      el('td', { class: sancionado ? 'etiqueta-mal' : 'etiqueta-bien' },
        sancionado ? `Sancionado/a hasta ${formatoFecha(s.sancionadoHasta)}` : 'Al día')));
  }
}

function pintarSelectores() {
  const antesSocio = $('sel-socio').value;
  const antesLibro = $('sel-libro').value;
  $('sel-socio').replaceChildren(...socios.listar().map((s) => el('option', { value: s.id }, `${s.id} · ${s.nombre}`)));
  $('sel-libro').replaceChildren(...catalogo.listar().map((l) => el('option', { value: l.id }, `${l.titulo} (${l.disponibles().length} libres)`)));
  if (antesSocio) $('sel-socio').value = antesSocio;
  if (antesLibro) $('sel-libro').value = antesLibro;
}

function pintarPrestamos() {
  const tbody = $('tabla-prestamos');
  tbody.replaceChildren();
  const activos = prestamos.prestamosActivos();
  if (activos.length === 0) {
    tbody.append(el('tr', {}, el('td', { colspan: '7', class: 'vacio' }, 'No hay préstamos activos.')));
  }
  for (const p of activos) {
    const vencido = p.estaVencido(hoy);
    const boton = el('button', { type: 'button', 'data-id': p.id, class: 'secundario' }, 'Devolver');
    tbody.append(el('tr', {},
      el('td', {}, p.id), el('td', {}, nombreSocio(p.socioId)), el('td', {}, tituloLibro(p.libroId)),
      el('td', {}, p.ejemplarId), el('td', {}, formatoFecha(p.vencimiento)),
      el('td', { class: vencido ? 'etiqueta-mal' : 'etiqueta-bien' }, vencido ? 'CADUCADO' : 'En plazo'),
      el('td', {}, boton)));
  }
}

function pintarReservas() {
  const lista = $('lista-reservas');
  lista.replaceChildren();
  const reservas = prestamos.reservasPendientes();
  if (reservas.length === 0) lista.append(el('li', { class: 'vacio' }, 'No hay reservas.'));
  for (const r of reservas) {
    lista.append(el('li', {}, `${nombreSocio(r.socioId)} espera «${tituloLibro(r.libroId)}» (desde ${formatoFecha(r.fecha)})`));
  }
}

function pintarTodo() {
  pintarFecha(); pintarLibros(); pintarSocios(); pintarSelectores(); pintarPrestamos(); pintarReservas();
}

// ---------- eventos ----------
$('buscador').addEventListener('input', pintarLibros);

$('form-socio').addEventListener('submit', (ev) => {
  ev.preventDefault();
  accion(() => {
    const socio = socios.alta($('nombre-socio').value);
    $('nombre-socio').value = '';
    return `Socio dado de alta: ${socio.nombre} (id ${socio.id}).`;
  });
});

function idSeleccionado(selectId, nombre) {
  const valor = $(selectId).value;
  if (!valor) throw new Error(`Elige ${nombre}.`);
  return Number(valor);
}

$('btn-prestar').addEventListener('click', () => accion(() => {
  const p = prestamos.prestar(idSeleccionado('sel-socio', 'un socio'), idSeleccionado('sel-libro', 'un libro'), hoy);
  return `Préstamo ${p.id} hecho (ejemplar ${p.ejemplarId}). Devolver antes del ${formatoFecha(p.vencimiento)}.`;
}));

$('btn-reservar').addEventListener('click', () => accion(() => {
  const { posicion } = prestamos.reservar(idSeleccionado('sel-socio', 'un socio'), idSeleccionado('sel-libro', 'un libro'), hoy);
  return `Reserva hecha. Posición en la cola: ${posicion}.`;
}));

$('tabla-prestamos').addEventListener('click', (ev) => {
  const boton = ev.target.closest('button[data-id]');
  if (!boton) return;
  accion(() => {
    const { prestamo, retraso } = prestamos.devolver(Number(boton.dataset.id), hoy);
    let texto = `Devuelto el ejemplar ${prestamo.ejemplarId}.`;
    if (retraso > 0) {
      const hasta = socios.obtener(prestamo.socioId).sancionadoHasta;
      texto += ` Retraso de ${retraso} día(s): ${nombreSocio(prestamo.socioId)} queda sancionado/a hasta ${formatoFecha(hasta)}.`;
    }
    const cola = prestamos.reservasDe(prestamo.libroId);
    if (cola.length > 0) texto += ` Hay ${cola.length} reserva(s): le toca a ${nombreSocio(cola[0].socioId)}.`;
    return texto;
  });
});

function avanzar(dias) {
  hoy = sumarDias(hoy, dias);
  pintarTodo();
  mostrarMensaje(`Ahora es ${formatoFecha(hoy)}.`, true);
}
$('btn-mas1').addEventListener('click', () => avanzar(1));
$('btn-mas7').addEventListener('click', () => avanzar(7));
$('btn-real').addEventListener('click', () => { hoy = hoyReal(); pintarTodo(); mostrarMensaje('Fecha real restaurada.', true); });

pintarTodo();
