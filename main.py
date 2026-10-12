import views as c

def pedir_campos(campos, actual=None):
    datos = {}
    for campo in campos:
        anterior = getattr(actual,campo,'') if actual else ''
        valor = input(f'{campo} [{anterior}]: ' if actual else f'{campo}: ').strip()
        if valor or not actual: datos[campo] = valor
    return datos

def pedir_id():
    try: return int(input('ID: '))
    except ValueError:
        print('El ID debe ser entero')
        return None

def mostrar_lista(objetos):
    if not objetos: print('No hay registros')
    for obj in objetos: print(obj)  # POLIMORFISMO: etiqueta() de cada modelo.

def mostrar_detalle(objeto):
    print(objeto if objeto else 'Registro no encontrado')

def menu_crud(titulo, campos, crear, todos, buscar, obtener, actualizar, eliminar):
    while True:
        print(f'\n--- {titulo} ---\n1. Crear\n2. Ver todos\n3. Buscar\n4. Ver por ID\n5. Actualizar\n6. Eliminar\n0. Volver')
        op = input('Opción: ').strip()
        if op == '0': return
        if op == '1': print(*crear(pedir_campos(campos)))
        elif op == '2': mostrar_lista(todos())
        elif op == '3': mostrar_lista(buscar(input('Buscar: ')))
        elif op == '4':
            ident = pedir_id()
            if ident is not None: mostrar_detalle(obtener(ident))
        elif op == '5':
            ident = pedir_id()
            if ident is None: continue
            obj = obtener(ident)
            if obj: print(*actualizar(ident,pedir_campos(campos,obj)))
            else: print('Registro no encontrado')
        elif op == '6':
            ident = pedir_id()
            if ident is not None: print(*eliminar(ident))
        else: print('Opción inválida')

def menu_matriculas():
    while True:
        print('\n--- MATRÍCULAS ---\n1. Matricular\n2. Ver todas\n3. Registrar nota\n4. Ver certificado\n5. Retirar matrícula\n0. Volver')
        op = input('Opción: ').strip()
        if op == '0': return
        if op == '1': print(*c.crear_matricula(pedir_campos(('estudiante_id','materia_id','periodo'))))
        elif op == '2': mostrar_lista(c.obtener_matriculas())
        elif op == '3':
            ident = pedir_id()
            if ident is not None: print(*c.registrar_nota(ident,input('Nota (0 a 20): ')))
        elif op == '4':
            ident = pedir_id()
            if ident is not None: print(c.certificado(ident) or 'Certificado no disponible')
        elif op == '5':
            ident = pedir_id()
            if ident is not None: print(*c.retirar_matricula(ident))
        else: print('Opción inválida')

def mostrar_resumen():
    r = c.resumen()
    print('\n--- RESUMEN ---')
    print('Estudiantes:',r['estudiantes'])
    print('Carreras distintas:',', '.join(r['carreras']) or 'Ninguna')
    print('Materias sin cupo:')
    mostrar_lista(r['materias_sin_cupo'])
    print('Matrículas aprobadas:',r['matriculas_aprobadas'])

def main():
    while True:
        print('\n=== SISTEMA ACADÉMICO ===\n1. Estudiantes\n2. Materias\n3. Matrículas\n4. Resumen\n0. Salir')
        op = input('Opción: ').strip()
        if op == '0': break
        if op == '1':
            menu_crud('ESTUDIANTES',('nombre','apellido','email','carnet','carrera'),c.crear_estudiante,c.obtener_estudiantes,c.buscar_estudiantes,c.obtener_estudiante,c.actualizar_estudiante,c.eliminar_estudiante)
        elif op == '2':
            menu_crud('MATERIAS',('nombre','codigo','creditos','cupos'),c.crear_materia,c.obtener_materias,c.buscar_materias,c.obtener_materia,c.actualizar_materia,c.eliminar_materia)
        elif op == '3': menu_matriculas()
        elif op == '4': mostrar_resumen()
        else: print('Opción inválida')

if __name__ == '__main__': main()
