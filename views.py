from datetime import date
from pathlib import Path
from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

BASE = Path(__file__).resolve().parent / 'data'
gestor_estudiantes = GestorJSON(BASE / 'estudiantes.json')
gestor_materias = GestorJSON(BASE / 'materias.json')
gestor_matriculas = GestorJSON(BASE / 'matriculas.json')

# Funciones genéricas: sirven para cualquier modelo que herede de ModeloBase.
def leer_objetos(gestor, clase):
    return [clase.desde_diccionario(d) for d in gestor.leer()]

def obtener_por_id(gestor, clase, id_registro):
    return next((o for o in leer_objetos(gestor, clase) if o.id == int(id_registro)), None)

def buscar(gestor, clase, termino, campos):
    # TUPLA: campos fijos en los que se permite buscar.
    termino = str(termino).strip().casefold()
    return [o for o in leer_objetos(gestor, clase)
            if termino and any(termino in str(getattr(o, c)).casefold() for c in campos)]

def siguiente_id(gestor):
    return max((r['id'] for r in gestor.leer()), default=0) + 1

def guardar_nuevo(gestor, objeto):
    registros = gestor.leer()
    registros.append(objeto.a_diccionario())
    gestor.guardar(registros)

def reemplazar(gestor, objeto):
    registros = gestor.leer()
    for i, r in enumerate(registros):
        if r['id'] == objeto.id:
            registros[i] = objeto.a_diccionario()
            gestor.guardar(registros)
            return True
    return False

def eliminar(gestor, id_registro):
    registros = gestor.leer()
    nuevos = [r for r in registros if r['id'] != int(id_registro)]
    if len(nuevos) == len(registros): return False
    gestor.guardar(nuevos)
    return True

def ids_registrados(gestor):
    # CONJUNTO: comprobar existencia de IDs sin duplicados.
    return {r['id'] for r in gestor.leer()}

def indice_por_id(objetos):
    # DICCIONARIO: acceder directamente por ID sin recorrer la lista de nuevo.
    return {obj.id: obj for obj in objetos}

def carnets_registrados(excepto_id=None):
    # CONJUNTO: evita carnets duplicados de forma eficiente.
    return {r['carnet'].strip().upper() for r in gestor_estudiantes.leer() if r['id'] != excepto_id}

def validar_estudiante(datos, id_actual=None):
    if id_actual is None:
        for campo in ('nombre', 'apellido', 'email', 'carnet'):
            if not str(datos.get(campo, '')).strip(): return f'{campo} es obligatorio'
    for campo in ('nombre', 'apellido', 'email', 'carnet'):
        if campo in datos and not str(datos[campo]).strip(): return f'{campo} no puede estar vacío'
    if 'email' in datos and not es_email_valido(datos['email']): return 'Email inválido'
    if 'carnet' in datos and str(datos['carnet']).strip().upper() in carnets_registrados(id_actual):
        return 'Carnet repetido'
    if 'email' in datos:
        emails = {r['email'].lower() for r in gestor_estudiantes.leer() if r['id'] != id_actual}
        if str(datos['email']).strip().lower() in emails: return 'Email repetido'
    return None

def crear_estudiante(datos):
    error = validar_estudiante(datos)
    if error: return (False, error)  # TUPLA: éxito y mensaje juntos.
    d = {k: str(datos.get(k, '')).strip() for k in ('nombre','apellido','email','carnet','carrera')}
    d['email'] = d['email'].lower()
    d['carnet'] = d['carnet'].upper()
    guardar_nuevo(gestor_estudiantes, Estudiante(siguiente_id(gestor_estudiantes), **d))
    return (True, 'Estudiante creado')

def obtener_estudiantes(): return leer_objetos(gestor_estudiantes, Estudiante)
def obtener_estudiante(id_registro): return obtener_por_id(gestor_estudiantes, Estudiante, id_registro)
def buscar_estudiantes(termino): return buscar(gestor_estudiantes, Estudiante, termino, ('nombre','apellido','email','carnet','carrera'))

def actualizar_estudiante(id_registro, cambios):
    obj = obtener_estudiante(id_registro)
    if obj is None: return (False, 'Estudiante no encontrado')
    error = validar_estudiante(cambios, obj.id)
    if error: return (False, error)
    permitidos = ('nombre','apellido','email','carnet','carrera')
    for k, v in cambios.items():
        if k in permitidos:
            v = str(v).strip()
            if k == 'email': v = v.lower()
            if k == 'carnet': v = v.upper()
            setattr(obj, k, v)
    reemplazar(gestor_estudiantes, obj)
    return (True, 'Estudiante actualizado')

def eliminar_estudiante(id_registro):
    if int(id_registro) in {m.estudiante_id for m in obtener_matriculas()}:
        return (False, 'No se puede eliminar: tiene matrículas')
    return (True, 'Estudiante eliminado') if eliminar(gestor_estudiantes, id_registro) else (False, 'No encontrado')

def codigos_registrados(excepto_id=None):
    # CONJUNTO: garantiza que los códigos de materia sean únicos.
    return {r['codigo'].strip().upper() for r in gestor_materias.leer() if r['id'] != excepto_id}

def validar_materia(datos, id_actual=None):
    if id_actual is None:
        for k in ('nombre','codigo','creditos','cupos'):
            if str(datos.get(k, '')).strip() == '': return f'{k} es obligatorio'
    for k in ('nombre','codigo'):
        if k in datos and not str(datos[k]).strip(): return f'{k} no puede estar vacío'
    if 'codigo' in datos and str(datos['codigo']).strip().upper() in codigos_registrados(id_actual):
        return 'Código repetido'
    for k, minimo, maximo in (('creditos',1,10),('cupos',0,Materia.CUPOS_MAXIMOS)):
        if k in datos:
            try: numero = int(str(datos[k]))
            except (ValueError, TypeError): return f'{k} debe ser entero'
            if not minimo <= numero <= maximo: return f'{k} debe estar entre {minimo} y {maximo}'
    return None

def crear_materia(datos):
    error = validar_materia(datos)
    if error: return (False, error)
    obj = Materia(siguiente_id(gestor_materias), str(datos['nombre']).strip(),
                  str(datos['codigo']).strip().upper(), int(datos['creditos']), int(datos['cupos']))
    guardar_nuevo(gestor_materias, obj)
    return (True, 'Materia creada')

def obtener_materias(): return leer_objetos(gestor_materias, Materia)
def obtener_materia(id_registro): return obtener_por_id(gestor_materias, Materia, id_registro)
def buscar_materias(termino): return buscar(gestor_materias, Materia, termino, ('nombre','codigo'))
def materias_sin_cupo(): return [m for m in obtener_materias() if not m.hay_cupo()]

def actualizar_materia(id_registro, cambios):
    obj = obtener_materia(id_registro)
    if obj is None: return (False, 'Materia no encontrada')
    error = validar_materia(cambios, obj.id)
    if error: return (False, error)
    for k,v in cambios.items():
        if k in ('nombre','codigo','creditos','cupos'):
            if k in ('creditos','cupos'): v = int(v)
            else: v = str(v).strip()
            if k == 'codigo': v = v.upper()
            setattr(obj,k,v)
    reemplazar(gestor_materias,obj)
    return (True, 'Materia actualizada')

def eliminar_materia(id_registro):
    if int(id_registro) in {m.materia_id for m in obtener_matriculas()}:
        return (False, 'No se puede eliminar: tiene matrículas')
    return (True, 'Materia eliminada') if eliminar(gestor_materias, id_registro) else (False, 'No encontrada')

def obtener_matriculas(): return leer_objetos(gestor_matriculas, Matricula)
def obtener_matricula(id_registro): return obtener_por_id(gestor_matriculas, Matricula, id_registro)

def crear_matricula(datos):
    try:
        eid, mid = int(datos['estudiante_id']), int(datos['materia_id'])
        periodo = str(datos['periodo']).strip()
        nota = float(datos.get('nota',0))
    except (KeyError, ValueError, TypeError): return (False, 'Datos de matrícula inválidos')
    if not periodo: return (False, 'Periodo obligatorio')
    if eid not in ids_registrados(gestor_estudiantes): return (False, 'Estudiante no existe')
    if mid not in ids_registrados(gestor_materias): return (False, 'Materia no existe')
    materia = obtener_materia(mid)
    if not materia.hay_cupo(): return (False, 'Materia sin cupos')
    if not Materia.es_nota_valida(nota): return (False, 'Nota fuera de 0 a 20')
    # TUPLA: la combinación estudiante/materia/periodo identifica duplicados.
    claves = {(m.estudiante_id,m.materia_id,m.periodo) for m in obtener_matriculas()}
    if (eid,mid,periodo) in claves: return (False, 'Matrícula duplicada en ese periodo')
    obj = Matricula(siguiente_id(gestor_matriculas),eid,mid,periodo,nota,str(datos.get('fecha') or date.today().isoformat()))
    materia.ocupar_cupo()
    reemplazar(gestor_materias,materia)
    guardar_nuevo(gestor_matriculas,obj)
    return (True, f'Matrícula creada #{obj.id}')

def registrar_nota(id_registro, nota):
    obj = obtener_matricula(id_registro)
    if obj is None: return (False, 'Matrícula no encontrada')
    if not Materia.es_nota_valida(nota): return (False, 'Nota fuera de 0 a 20')
    obj.nota = float(nota)
    reemplazar(gestor_matriculas,obj)
    return (True, f'Nota registrada. Estado: {obj.estado()}')

def retirar_matricula(id_registro):
    obj = obtener_matricula(id_registro)
    if obj is None: return (False, 'Matrícula no encontrada')
    materia = obtener_materia(obj.materia_id)
    if materia and not materia.liberar_cupo(): return (False, 'No se puede liberar cupo: límite máximo')
    if materia: reemplazar(gestor_materias,materia)
    eliminar(gestor_matriculas,id_registro)
    return (True, 'Matrícula retirada y cupo liberado')

def certificado(id_registro):
    obj = obtener_matricula(id_registro)
    if obj is None: return None
    # DICCIONARIO ÍNDICE {id: objeto}: cruza las tres entidades por ID.
    estudiantes = indice_por_id(obtener_estudiantes())
    materias = indice_por_id(obtener_materias())
    e, m = estudiantes.get(obj.estudiante_id), materias.get(obj.materia_id)
    if e is None or m is None: return None
    return (f'CERTIFICADO #{obj.id}   periodo: {obj.periodo}\n'
            f'Estudiante: {e.nombre_completo()} ({e.carnet})\n'
            f'Materia   : {m.nombre} ({m.codigo}) · {m.creditos} créditos\n'
            f'------------------------------------------\n'
            f'Nota      : {obj.nota:g}\nEstado    : {obj.estado()}')

def matriculas_por_estudiante():
    # DICCIONARIO DE LISTAS: agrupa matrículas por ID de estudiante.
    grupos = {}
    for m in obtener_matriculas(): grupos.setdefault(m.estudiante_id,[]).append(m)
    return grupos

def promedio_de_estudiante(id_registro):
    lista = matriculas_por_estudiante().get(int(id_registro),[])
    return sum(m.nota for m in lista)/len(lista) if lista else None

def resumen():
    estudiantes, matriculas = obtener_estudiantes(), obtener_matriculas()
    return {'estudiantes':len(estudiantes),
            'carreras':sorted({e.carrera for e in estudiantes if e.carrera}),
            'materias_sin_cupo':materias_sin_cupo(),
            'matriculas_aprobadas':sum(m.esta_aprobada() for m in matriculas)}
