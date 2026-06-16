import runpy
import traceback

try:
    ns = runpy.run_path('chains/interviewer.py')
    keys = sorted([k for k in ns.keys() if not k.startswith('_')])
    print('Defined names:', keys)
except Exception:
    traceback.print_exc()
