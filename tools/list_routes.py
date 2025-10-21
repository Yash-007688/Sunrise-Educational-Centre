from importlib import import_module
import sys

try:
    app_mod = import_module('app')
    app = getattr(app_mod, 'app', None)
    if not app:
        print('ERROR: app object not found in app.py')
        sys.exit(1)
    rules = sorted([(r.rule, sorted(list(r.methods))) for r in app.url_map.iter_rules()], key=lambda x: x[0])
    for rule, methods in rules:
        print(rule, methods)
except Exception as e:
    print('ERROR:', e)
    sys.exit(1)
