import sys
from os import listdir
from json import dump
from pathlib import Path

# Permite importar o pacote `core` que está na raiz do projeto
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import pipeline

results = []
for path in ["pics/" + p for p in listdir("pics")]:
    data = pipeline.process_file(path)
    results.append({"path": path.lstrip("pics/"), "data": data})

with open("results.json", "w") as file:
    dump(results, file, indent=2)
