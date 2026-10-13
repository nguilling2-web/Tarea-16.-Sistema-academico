from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# =====================================================================
# CLASE BASE (ABSTRACTA)
# =====================================================================
# Solo dice QUÉ métodos debe tener todo controlador.
# CÓMO se hace cada uno lo escribe cada controlador, de la forma más simple.
class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


# =====================================================================
# CONTROLADOR DE ESTUDIANTES
# =====================================================================
class EstudianteController(CrudBase):

    def __init__(self, archivo="data/estudiantes.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for estudiante in self.lista:
            datos.append(estudiante.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "apellido", "email", "carnet"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"
        for campo in ("nombre", "apellido", "email", "carnet"):
            if campo in datos and str(datos[campo]).strip() == "":
                return f"El campo {campo} no puede quedar vacío"
        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            # CONJUNTO: impide emails repetidos.
            usados = {e.email.lower() for e in self.lista if e.id != id_actual}
            if email in usados:
                return "Ese email ya está registrado"
        if "carnet" in datos:
            carnet = str(datos["carnet"]).strip().upper()
            # CONJUNTO: permite comprobar carnets únicos rápidamente.
            usados = {e.carnet.upper() for e in self.lista if e.id != id_actual}
            if carnet in usados:
                return "Ese carnet ya está registrado"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_estudiante):
        for estudiante in self.lista:
            if estudiante.id == id_estudiante:
                return estudiante
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados
        # TUPLA: campos fijos que se consultan en cada búsqueda.
        campos = ("nombre", "apellido", "email", "carnet", "carrera")
        for estudiante in self.lista:
            if any(texto in str(getattr(estudiante, campo)).lower() for campo in campos):
                encontrados.append(estudiante)
        return encontrados

    def siguiente(self):
        mayor = 0
        for estudiante in self.lista:
            if estudiante.id > mayor:
                mayor = estudiante.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error
        estudiante = Estudiante(self.siguiente(),
                                str(datos["nombre"]).strip().title(),
                                str(datos["apellido"]).strip().title(),
                                str(datos["email"]).strip().lower(),
                                str(datos["carnet"]).strip().upper(),
                                str(datos.get("carrera", "")).strip().title())
        self.lista.append(estudiante)
        self.guardar()
        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_estudiante, datos):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if not datos:
            return False, "No se indicó ningún cambio"
        permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"
        error = self.validar(datos, id_estudiante)
        if error:
            return False, error
        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            setattr(estudiante, campo, valor)
        self.guardar()
        return True, f"Estudiante {id_estudiante} actualizado"

    def eliminar(self, id_estudiante):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if hasattr(self, "matriculas") and any(m.estudiante_id == id_estudiante for m in self.matriculas.leer()):
            return False, "No se puede eliminar: tiene matrículas registradas"
        self.lista.remove(estudiante)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"

    def carreras(self):
        """CONJUNTO: carreras sin repetidos, ordenadas para el resumen."""
        return sorted({e.carrera for e in self.lista if e.carrera != ""})


# =====================================================================
# CONTROLADOR DE MATERIAS
# =====================================================================
class MateriaController(CrudBase):

    def __init__(self, archivo="data/materias.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for materia in self.lista:
            datos.append(materia.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "codigo", "creditos", "cupos"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"
        for campo in ("nombre", "codigo"):
            if campo in datos and not str(datos[campo]).strip():
                return f"El campo {campo} no puede quedar vacío"
        if "creditos" in datos:
            try:
                creditos = int(datos["creditos"])
                if str(datos["creditos"]).strip() != str(creditos) or not 1 <= creditos <= 10:
                    return "Los créditos deben ser un entero entre 1 y 10"
            except (TypeError, ValueError):
                return "Los créditos deben ser un entero entre 1 y 10"
        if "cupos" in datos:
            try:
                cupos = int(datos["cupos"])
                if str(datos["cupos"]).strip() != str(cupos) or not 0 <= cupos <= Materia.CUPOS_MAXIMOS:
                    return f"Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}"
            except (TypeError, ValueError):
                return "Los cupos deben ser un número entero"
        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            # CONJUNTO: los códigos de materia no se pueden repetir.
            usados = {m.codigo.upper() for m in self.lista if m.id != id_actual}
            if codigo in usados:
                return "Ese código ya está registrado"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_materia):
        for materia in self.lista:
            if materia.id == id_materia:
                return materia
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados
        # TUPLA: campos buscables que no cambian.
        campos = ("nombre", "codigo")
        for materia in self.lista:
            if any(texto in str(getattr(materia, campo)).lower() for campo in campos):
                encontrados.append(materia)
        return encontrados

    def siguiente(self):
        mayor = 0
        for materia in self.lista:
            if materia.id > mayor:
                mayor = materia.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error
        materia = Materia(self.siguiente(),
                          str(datos["nombre"]).strip().title(),
                          str(datos["codigo"]).strip().upper(),
                          int(datos["creditos"]), int(datos["cupos"]))
        self.lista.append(materia)
        self.guardar()
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_materia, datos):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"
        if not datos:
            return False, "No se indicó ningún cambio"
        desconocidos = set(datos) - {"nombre", "codigo", "creditos", "cupos"}
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"
        error = self.validar(datos, id_materia)
        if error:
            return False, error
        if "cupos" in datos and hasattr(self, "matriculas"):
            ocupados = sum(m.materia_id == id_materia for m in self.matriculas.leer())
            if int(datos["cupos"]) + ocupados > Materia.CUPOS_MAXIMOS:
                return False, "Cupos libres + matrículas exceden el máximo de 30"
        for campo, valor in datos.items():
            if campo in ("creditos", "cupos"):
                valor = int(valor)
            elif campo == "codigo":
                valor = str(valor).strip().upper()
            else:
                valor = str(valor).strip().title()
            setattr(materia, campo, valor)
        self.guardar()
        return True, f"Materia {id_materia} actualizada"

    def eliminar(self, id_materia):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"
        if hasattr(self, "matriculas") and any(m.materia_id == id_materia for m in self.matriculas.leer()):
            return False, "No se puede eliminar: tiene matrículas registradas"
        self.lista.remove(materia)
        self.guardar()
        return True, f"Materia {id_materia} eliminada"

    def materias_sin_cupo(self):
        sin_cupo = []
        for materia in self.lista:
            if not materia.hay_cupo():
                sin_cupo.append(materia)
        return sin_cupo


# =====================================================================
# CONTROLADOR DE MATRÍCULAS
# =====================================================================
class MatriculaController(CrudBase):

    def __init__(self, estudiantes, materias, archivo="data/matriculas.json"):
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))
        estudiantes.matriculas = self
        materias.matriculas = self

    def guardar(self):
        datos = []
        for matricula in self.lista:
            datos.append(matricula.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos):
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
        except (TypeError, ValueError):
            return "Los id deben ser números enteros"
        periodo = str(datos.get("periodo", "")).strip()
        if not periodo:
            return "El periodo es obligatorio"
        if self.estudiantes.obtener(estudiante_id) is None:
            return f"No existe un estudiante con id {estudiante_id}"
        materia = self.materias.obtener(materia_id)
        if materia is None:
            return f"No existe una materia con id {materia_id}"
        if not materia.hay_cupo():
            return f"No hay cupos disponibles para {materia.nombre}"
        if not Materia.es_nota_valida(datos.get("nota", 0)):
            return "La nota debe estar entre 0 y 20"
        for matricula in self.lista:
            if (matricula.estudiante_id == estudiante_id and
                    matricula.materia_id == materia_id and
                    matricula.periodo == periodo):
                return "El estudiante ya está matriculado en esa materia y periodo"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_matricula):
        for matricula in self.lista:
            if matricula.id == id_matricula:
                return matricula
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontradas = []
        if texto == "":
            return encontradas
        for matricula in self.lista:
            if texto in matricula.periodo.lower() or texto in matricula.fecha:
                encontradas.append(matricula)
        return encontradas

    def siguiente(self):
        mayor = 0
        for matricula in self.lista:
            if matricula.id > mayor:
                mayor = matricula.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error
        materia = self.materias.obtener(int(datos["materia_id"]))
        matricula = Matricula(self.siguiente(), int(datos["estudiante_id"]),
                              materia.id, str(datos["periodo"]).strip(),
                              float(datos.get("nota", 0)))
        materia.ocupar_cupo()
        self.materias.guardar()
        self.lista.append(matricula)
        self.guardar()
        return True, f"Matrícula {matricula.id} registrada correctamente"

    def actualizar(self, id_matricula, datos):
        return False, "Use registrar_nota() para modificar la nota"

    def registrar_nota(self, id_matricula, nota):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"
        if not Materia.es_nota_valida(nota):
            return False, "La nota debe ser un número entre 0 y 20"
        matricula.nota = float(nota)
        self.guardar()
        return True, f"Nota registrada: {matricula.nota:g} · {matricula.estado()}"

    def eliminar(self, id_matricula):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"
        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            materia.liberar_cupo()
            self.materias.guardar()
        self.lista.remove(matricula)
        self.guardar()
        return True, f"Matrícula {id_matricula} retirada y cupo liberado"

    def retirar_matricula(self, id_matricula):
        return self.eliminar(id_matricula)

    def certificado(self, id_matricula):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return None
        # DICCIONARIO ÍNDICE: busca cada objeto por su id.
        indice_estudiantes = {e.id: e for e in self.estudiantes.leer()}
        indice_materias = {m.id: m for m in self.materias.leer()}
        estudiante = indice_estudiantes.get(matricula.estudiante_id)
        materia = indice_materias.get(matricula.materia_id)
        nombre = estudiante.nombre_completo() if estudiante else "eliminado"
        carnet = estudiante.carnet if estudiante else "-"
        materia_nombre = materia.nombre if materia else "eliminada"
        codigo = materia.codigo if materia else "-"
        creditos = materia.creditos if materia else 0
        texto = f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
        texto += f"Estudiante: {nombre}   ({carnet})\n"
        texto += f"Materia   : {materia_nombre}   ({codigo}) · {creditos} créditos\n"
        texto += "-" * 42 + "\n"
        texto += f"Nota      : {matricula.nota:g}\n"
        texto += f"Estado    : {matricula.estado()}"
        return texto

    def matriculas_por_estudiante(self):
        """DICCIONARIO de LISTAS: agrupa las matrículas por estudiante."""
        agrupadas = {}
        for matricula in self.lista:
            agrupadas.setdefault(matricula.estudiante_id, []).append(matricula)
        return agrupadas

    def promedio_de_estudiante(self, id_estudiante):
        agrupadas = self.matriculas_por_estudiante()
        matriculas = agrupadas.get(id_estudiante, [])
        if not matriculas:
            return None
        return round(sum(m.nota for m in matriculas) / len(matriculas), 2)

    def aprobadas(self):
        return sum(m.esta_aprobada() for m in self.lista)
