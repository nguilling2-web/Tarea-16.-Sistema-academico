# Tarea 16: Sistema académico MVC

## Requisitos
Python 3.9 o posterior. No requiere librerías externas.

## Ejecución
En la carpeta `sistema_academico`, ejecutar:

```bash
python main.py
```

## Estructura
- `models.py`: ModeloBase, Persona, Estudiante, Materia, Matricula. Herencia y polimorfismo.
- `views.py`: controlador, CRUD, reglas y consultas, sin entrada/salida por consola.
- `main.py`: vista de consola y menús.
- `shared/json_manager.py`: persistencia JSON.
- `shared/herramientas.py`: validación de email.
- `data/*.json`: registros, inicialmente vacíos.

## Flujo de prueba
1. Crear estudiante Ana Pérez, ana@u.edu, EST2026001, Software.
2. Crear materia Cálculo I, MAT101, 4 créditos, 30 cupos.
3. Matricular estudiante 1 en materia 1, periodo 2026-1.
4. Comprobar que los cupos bajaron a 29.
5. Registrar nota 16.5 en matrícula 1 y mostrar certificado.
6. Intentar matrícula duplicada: debe rechazarse.
7. Retirar matrícula: los cupos vuelven a 30.

**Nota:** Una matrícula nueva se crea con nota 0, por lo que su estado calculado aparece como Reprobado hasta que se registre una nota aprobatoria. El enunciado solo contempla Aprobado/Reprobado, no Pendiente.

## Colecciones usadas
- `set`: carnets, códigos, IDs, carreras y duplicados de matrícula.
- `dict`: índices por ID para certificados.
- `dict` de `list`: matrículas agrupadas por estudiante con `setdefault`.
- `tuple`: campos de búsqueda, claves compuestas y retornos `(éxito, mensaje)`.

No se abren archivos fuera de `shared/`.
