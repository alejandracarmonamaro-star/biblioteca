"""Pruebas automáticas de las reglas. Se ejecutan con:  python -m unittest -v"""
import unittest
from datetime import date, timedelta

from catalogo import Catalogo
from socios import Socios
from prestamos import Prestamos

HOY = date(2026, 1, 10)


class PruebasBiblioteca(unittest.TestCase):
    def setUp(self):
        self.catalogo = Catalogo()
        self.socios = Socios()
        self.prestamos = Prestamos(self.catalogo, self.socios)
        self.l1 = self.catalogo.agregar("Libro uno", "A", 2)
        self.l2 = self.catalogo.agregar("Libro dos", "B", 1)
        self.l3 = self.catalogo.agregar("Libro tres", "C", 1)
        self.ana = self.socios.alta("Ana")
        self.beto = self.socios.alta("Beto")
        self.cris = self.socios.alta("Cris")

    def test_buscar_ignora_mayusculas(self):
        self.assertEqual([l.id for l in self.catalogo.buscar("UNO")], [self.l1.id])

    def test_cada_ejemplar_tiene_su_estado(self):
        self.prestamos.prestar(self.ana.id, self.l1.id, HOY)
        estados = [e.estado for e in self.catalogo.obtener(self.l1.id).ejemplares]
        self.assertEqual(sorted(estados), ["disponible", "prestado"])

    def test_maximo_dos_libros(self):
        self.prestamos.prestar(self.ana.id, self.l1.id, HOY)
        self.prestamos.prestar(self.ana.id, self.l2.id, HOY)
        with self.assertRaises(ValueError):
            self.prestamos.prestar(self.ana.id, self.l3.id, HOY)

    def test_prestamo_caduca_a_los_7_dias(self):
        p = self.prestamos.prestar(self.ana.id, self.l1.id, HOY)
        self.assertEqual(p.vencimiento, HOY + timedelta(days=7))
        self.assertFalse(p.esta_vencido(HOY + timedelta(days=7)))
        self.assertTrue(p.esta_vencido(HOY + timedelta(days=8)))

    def test_devolver_tarde_sanciona_y_bloquea_prestamos(self):
        p = self.prestamos.prestar(self.ana.id, self.l1.id, HOY)
        tarde = HOY + timedelta(days=10)          # 3 días de retraso
        _, retraso = self.prestamos.devolver(p.id, tarde)
        self.assertEqual(retraso, 3)
        with self.assertRaises(ValueError):
            self.prestamos.prestar(self.ana.id, self.l2.id, tarde)
        # pasada la sanción vuelve a poder pedir
        self.prestamos.prestar(self.ana.id, self.l2.id, tarde + timedelta(days=3))

    def test_devolver_a_tiempo_no_sanciona(self):
        p = self.prestamos.prestar(self.ana.id, self.l1.id, HOY)
        self.prestamos.devolver(p.id, HOY + timedelta(days=7))
        self.assertFalse(self.socios.esta_sancionado(self.ana.id, HOY + timedelta(days=7)))

    def test_reservar_solo_si_esta_todo_prestado(self):
        with self.assertRaises(ValueError):                     # hay libres
            self.prestamos.reservar(self.beto.id, self.l2.id, HOY)
        self.prestamos.prestar(self.ana.id, self.l2.id, HOY)    # ya no quedan
        _, pos = self.prestamos.reservar(self.beto.id, self.l2.id, HOY)
        self.assertEqual(pos, 1)

    def test_el_ejemplar_devuelto_se_guarda_para_el_que_reservo(self):
        p = self.prestamos.prestar(self.ana.id, self.l2.id, HOY)
        self.prestamos.reservar(self.beto.id, self.l2.id, HOY)
        self.prestamos.devolver(p.id, HOY + timedelta(days=1))
        with self.assertRaises(ValueError):                     # Cris se cuela: no puede
            self.prestamos.prestar(self.cris.id, self.l2.id, HOY + timedelta(days=1))
        self.prestamos.prestar(self.beto.id, self.l2.id, HOY + timedelta(days=1))
        self.assertEqual(self.prestamos.reservas_de(self.l2.id), [])

    def test_socio_sancionado_no_puede_reservar(self):
        self.prestamos.prestar(self.beto.id, self.l2.id, HOY)
        p = self.prestamos.prestar(self.ana.id, self.l1.id, HOY)
        self.prestamos.devolver(p.id, HOY + timedelta(days=9))
        with self.assertRaises(ValueError):
            self.prestamos.reservar(self.ana.id, self.l2.id, HOY + timedelta(days=9))


if __name__ == "__main__":
    unittest.main()
