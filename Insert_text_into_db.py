# import_speckled_band.py

import json
from data_models import db, Text
from backend_app import app

with open("Sources/speckled_band.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with app.app_context():
    entry = Text(
        title=data["title"],
        author=data["author"],
        content=data["text"]
    )
    db.session.add(entry)
    db.session.commit()
    print(f"Imported Text ID: {entry.id}")
