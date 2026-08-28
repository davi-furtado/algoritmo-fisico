from pathlib import Path
import sys
from json import dumps

sys.path.append(str(Path(__file__).parent.parent))

from core import pipeline

path = input()
result = pipeline.process_file(path)
print(dumps(result, indent=2))
