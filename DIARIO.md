# Diario de desarrollo – Biblioteca de barrio

## 28/10/2026 · Diseño inicial
Separo la aplicación en tres componentes (`catalogo.py`, `socios.py`, `prestamos.py`) que se juntan en `main.py`.
`Prestamos` recibe `Catalogo` y `Socios` al crearse y solo llama a sus funciones públicas.
Decisiones de las reglas extra:
- Cada título (`Libro`) tiene varios `Ejemplar`, y cada ejemplar tiene su propio estado (disponible/prestado).
- Máximo 2 libros a la vez por socio y préstamo de 7 días.
- Si se devuelve tarde, el socio queda sancionado tantos días como de retraso. Un socio sancionado no puede pedir ni reservar.
- Solo se puede reservar un libro cuando no queda ningún ejemplar libre para esa persona. Al devolverse un ejemplar, se guarda para el primero de la cola.

## 28/10/2026 · Petición del cliente: «que Prestamos lea directamente la lista de libros de Catalogo»
**Decisión: no lo hago.** Si `Prestamos` leyera directamente la lista de libros, quedaría atado a cómo `Catalogo` guarda sus datos (y se saltaría el estado de cada ejemplar), así que cualquier cambio interno lo rompería. Seguiré usando solo `buscar`, `obtener` y `marcar_prestado`, porque la ganancia de velocidad es mínima y el código se mantiene más seguro y fácil de cambiar.

## 28/10/2026 · Versión web
Hago la versión web con la misma estructura (`catalogo.js`, `socios.js`, `prestamos.js` y `app.js`) y la publico con GitHub Pages desde la carpeta `docs/`.
