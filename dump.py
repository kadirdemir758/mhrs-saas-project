import sys
sys.stdout.reconfigure(encoding='utf-8')
from app.main import app

with open("routes.txt", "w", encoding="utf-8") as f:
    for r in app.routes:
        path = getattr(r, 'path', r.name)
        methods = getattr(r, 'methods', set())
        f.write(f"{path} {methods}\n")
