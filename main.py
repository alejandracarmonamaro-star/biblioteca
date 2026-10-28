"""Programa principal: junta los tres componentes y ofrece un menú por consola."""
from datetime import date, timedelta

from catalogo import catalogo_de_ejemplo
from socios import Socios
from prestamos import Prestamos


def pedir_entero(texto):
    try:
        return int(input(texto).strip())
    except ValueError:
        raise ValueError("Tienes que escribir un número.")


def mostrar_libros(libros):
    if not libros:
        print("  (no se ha encontrado ningún libro)")
    for libro in libros:
        print("  " + str(libro))


def main():
    # Aquí (y solo aquí) se crean los componentes y se conectan entre sí.
    catalogo = catalogo_de_ejemplo()
    socios = Socios()
    prestamos = Prestamos(catalogo, socios)
    hoy = date.today()      # fecha "de la biblioteca"; se puede avanzar para probar caducidades

    while True:
        print(f"\n=== BIBLIOTECA DE BARRIO (hoy: {hoy}) ===")
        print("1. Buscar libro")
        print("2. Dar de alta un socio")
        print("3. Hacer un préstamo")
        print("4. Devolver un libro")
        print("5. Reservar un libro prestado")
        print("6. Ver préstamos y estado de un socio")
        print("7. Avanzar días (para probar la caducidad de 7 días)")
        print("0. Salir")
        opcion = input("Elige una opción: ").strip()

        try:
            if opcion == "1":
                texto = input("Título (o parte del título; vacío = todos): ")
                mostrar_libros(catalogo.buscar(texto))

            elif opcion == "2":
                socio = socios.alta(input("Nombre del socio: "))
                print(f"  Socio dado de alta: {socio}")

            elif opcion == "3":
                socio_id = pedir_entero("Id del socio: ")
                libro_id = pedir_entero("Id del libro: ")
                p = prestamos.prestar(socio_id, libro_id, hoy)
                print(f"  Préstamo {p.id} hecho (ejemplar {p.ejemplar_id}). Devolver antes del {p.vencimiento}.")

            elif opcion == "4":
                prestamo_id = pedir_entero("Id del préstamo: ")
                p, retraso = prestamos.devolver(prestamo_id, hoy)
                print(f"  Devuelto el ejemplar {p.ejemplar_id}.")
                if retraso:
                    print(f"  Retraso de {retraso} día(s): el socio queda sancionado hasta "
                          f"{socios.obtener(p.socio_id).sancionado_hasta}.")
                cola = prestamos.reservas_de(p.libro_id)
                if cola:
                    siguiente = socios.obtener(cola[0].socio_id)
                    print(f"  Aviso: hay {len(cola)} reserva(s). Le toca a {siguiente.nombre}.")

            elif opcion == "5":
                socio_id = pedir_entero("Id del socio: ")
                libro_id = pedir_entero("Id del libro: ")
                _, posicion = prestamos.reservar(socio_id, libro_id, hoy)
                print(f"  Reserva hecha. Posición en la cola: {posicion}.")

            elif opcion == "6":
                socio = socios.obtener(pedir_entero("Id del socio: "))
                print(f"  {socio}" + ("  <-- SANCIONADO" if socios.esta_sancionado(socio.id, hoy) else ""))
                activos = prestamos.prestamos_activos(socio.id)
                if not activos:
                    print("  No tiene préstamos activos.")
                for p in activos:
                    libro = catalogo.obtener(p.libro_id)
                    aviso = "  <-- CADUCADO" if p.esta_vencido(hoy) else ""
                    print(f"  Préstamo {p.id}: «{libro.titulo}» (ejemplar {p.ejemplar_id}), vence {p.vencimiento}{aviso}")

            elif opcion == "7":
                dias = pedir_entero("¿Cuántos días avanzas?: ")
                hoy = hoy + timedelta(days=dias)
                print(f"  Ahora es {hoy}.")

            elif opcion == "0":
                print("¡Hasta pronto!")
                break
            else:
                print("  Opción no válida.")
        except ValueError as error:
            print(f"  ✗ {error}")


if __name__ == "__main__":
    main()
