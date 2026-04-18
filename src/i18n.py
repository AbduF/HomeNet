import json
import os

LANG_DIR = os.path.join(os.path.dirname(__file__), "..", "locales")

def load_locale(lang="en"):
    path = os.path.join(LANG_DIR, f"{lang}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

I18N = {}
def init(lang="en"):
    global I18N
    I18N = load_locale(lang)