import re

def es_email_valido(email):
    return bool(re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', str(email)))
