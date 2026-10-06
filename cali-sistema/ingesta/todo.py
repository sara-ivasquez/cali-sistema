"""Reconstruye el lago completo con un solo comando:  python3 ingesta/todo.py"""
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SCRIPTS = [  # agreguen aquí cada script nuevo
    "pull_escucha.py",
    "pull_desempeno.py",
    "pull_poblacion.py",
    "pull_comunas.py",
]

fallos = 0
for s in SCRIPTS:
    print(f"→ {s}")
    r = subprocess.run([sys.executable, str(AQUI / s)], cwd=AQUI)
    fallos += r.returncode != 0
sys.exit(1 if fallos else 0)
