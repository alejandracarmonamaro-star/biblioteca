// Utilidades de fechas. Las fechas se guardan como texto "AAAA-MM-DD".
// (Eso permite compararlas con < y > sin problemas.)

function dosDigitos(n) { return String(n).padStart(2, '0'); }

export function hoyReal() {
  const d = new Date();
  return `${d.getFullYear()}-${dosDigitos(d.getMonth() + 1)}-${dosDigitos(d.getDate())}`;
}

export function sumarDias(iso, dias) {
  const [a, m, d] = iso.split('-').map(Number);
  return new Date(Date.UTC(a, m - 1, d + dias)).toISOString().slice(0, 10);
}

// Días que hay de b a a (a - b).
export function diferenciaDias(a, b) {
  const ms = (iso) => { const [y, m, d] = iso.split('-').map(Number); return Date.UTC(y, m - 1, d); };
  return Math.round((ms(a) - ms(b)) / 86400000);
}

export function formatoFecha(iso) {
  const [a, m, d] = iso.split('-');
  return `${d}/${m}/${a}`;
}
