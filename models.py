class ModeloBase:
    def __init__(self, id_registro): self.id = int(id_registro)
    @classmethod
    def desde_diccionario(cls, datos):
        datos = dict(datos)
        return cls(datos.pop('id'), **datos)
    def a_diccionario(self): return {'id': self.id}
    def etiqueta(self): return f'registro {self.id}'
    def __str__(self): return f'[{self.id}] {self.etiqueta()}'

class Persona(ModeloBase):
    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)
        self.nombre, self.apellido, self.email = nombre, apellido, email
    def nombre_completo(self): return f'{self.nombre} {self.apellido}'
    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update(nombre=self.nombre, apellido=self.apellido, email=self.email)
        return datos
    def etiqueta(self): return self.nombre_completo()

class Estudiante(Persona):
    def __init__(self, id_registro, nombre, apellido, email, carnet='', carrera=''):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet, self.carrera = carnet, carrera
    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update(carnet=self.carnet, carrera=self.carrera)
        return datos
    def etiqueta(self): return f'{super().etiqueta()} · {self.carnet} · {self.carrera}'

class Materia(ModeloBase):
    CUPOS_MAXIMOS = 30
    NOTA_APROBACION = 14
    def __init__(self, id_registro, nombre, codigo, creditos=0, cupos=0):
        super().__init__(id_registro)
        self.nombre, self.codigo = nombre, codigo
        self.creditos, self.cupos = int(creditos), int(cupos)
    @staticmethod
    def es_nota_valida(valor):
        try:
            n = float(valor)
            return 0 <= n <= 20
        except (ValueError, TypeError, OverflowError): return False
    def hay_cupo(self): return self.cupos > 0
    def ocupar_cupo(self):
        if not self.hay_cupo(): return False
        self.cupos -= 1
        return True
    def liberar_cupo(self):
        if self.cupos >= Materia.CUPOS_MAXIMOS: return False
        self.cupos += 1
        return True
    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update(nombre=self.nombre, codigo=self.codigo, creditos=self.creditos, cupos=self.cupos)
        return datos
    def etiqueta(self): return f'{self.nombre} · {self.codigo} · {self.creditos} créditos · {self.cupos} cupos'

class Matricula(ModeloBase):
    def __init__(self, id_registro, estudiante_id, materia_id, periodo, nota=0, fecha=''):
        super().__init__(id_registro)
        self.estudiante_id, self.materia_id = int(estudiante_id), int(materia_id)
        self.periodo, self.nota, self.fecha = periodo, float(nota), fecha
    def esta_aprobada(self): return self.nota >= Materia.NOTA_APROBACION
    def estado(self): return 'Aprobado' if self.esta_aprobada() else 'Reprobado'
    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update(estudiante_id=self.estudiante_id, materia_id=self.materia_id,
                     periodo=self.periodo, nota=self.nota, fecha=self.fecha)
        return datos
    def etiqueta(self): return f'Estudiante #{self.estudiante_id} · Materia #{self.materia_id} · {self.periodo} · Nota {self.nota:g} · {self.estado()}'
