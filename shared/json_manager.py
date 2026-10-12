import json
from pathlib import Path

class GestorJSON:
    """Única clase que lee y escribe archivos JSON."""
    def __init__(self, ruta):
        self.ruta = Path(ruta)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
    def leer(self):
        if not self.ruta.exists(): return []
        with self.ruta.open(encoding='utf-8') as archivo:
            datos = json.load(archivo)
        if not isinstance(datos, list): raise ValueError('El JSON debe contener una lista')
        return datos
    def guardar(self, datos):
        with self.ruta.open('w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, indent=2, ensure_ascii=False)
