import tempfile
from pathlib import Path
import unittest
import views as v
from shared.json_manager import GestorJSON

class Pruebas(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        carpeta = Path(self.tmp.name)
        v.gestor_estudiantes = GestorJSON(carpeta/'estudiantes.json')
        v.gestor_materias = GestorJSON(carpeta/'materias.json')
        v.gestor_matriculas = GestorJSON(carpeta/'matriculas.json')
        self.assertTrue(v.crear_estudiante(dict(nombre='Ana',apellido='Pérez',email='ana@u.edu',carnet='EST2026001',carrera='Software'))[0])
        self.assertTrue(v.crear_materia(dict(nombre='Cálculo I',codigo='MAT101',creditos=4,cupos=30))[0])
    def tearDown(self): self.tmp.cleanup()
    def test_flujo(self):
        self.assertFalse(v.crear_estudiante(dict(nombre='Sol',apellido='Paz',email='sol@u.edu',carnet='EST2026001'))[0])
        self.assertFalse(v.crear_materia(dict(nombre='Otra',codigo='MAT101',creditos=3,cupos=20))[0])
        self.assertTrue(v.crear_matricula(dict(estudiante_id=1,materia_id=1,periodo='2026-1'))[0])
        self.assertEqual(v.obtener_materia(1).cupos,29)
        self.assertFalse(v.crear_matricula(dict(estudiante_id=1,materia_id=1,periodo='2026-1'))[0])
        self.assertFalse(v.registrar_nota(1,21)[0])
        self.assertTrue(v.registrar_nota(1,16.5)[0])
        self.assertIn('Aprobado',v.certificado(1))
        self.assertEqual(v.promedio_de_estudiante(1),16.5)
        self.assertFalse(v.eliminar_estudiante(1)[0])
        self.assertTrue(v.retirar_matricula(1)[0])
        self.assertEqual(v.obtener_materia(1).cupos,30)
        self.assertTrue(v.eliminar_estudiante(1)[0])
    def test_crud(self):
        self.assertTrue(v.actualizar_estudiante(1,{'carrera':'Informática'})[0])
        self.assertEqual(v.obtener_estudiante(1).carrera,'Informática')
        self.assertEqual(len(v.buscar_estudiantes('Informática')),1)
        self.assertTrue(v.actualizar_materia(1,{'creditos':5})[0])
        self.assertEqual(v.obtener_materia(1).creditos,5)
        self.assertTrue(v.eliminar_materia(1)[0])

if __name__ == '__main__': unittest.main()
