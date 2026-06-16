import traceback

p = 'chains/interviewer.py'
try:
    src = open(p, 'r', encoding='utf-8').read()
    print('source length:', len(src))
    print('preview:\n', src[:400])
    code = compile(src, p, 'exec')
    ns = {}
    exec(code, ns)
    names = sorted([k for k in ns.keys() if not k.startswith('_')])
    print('Executed, names:', names)
except Exception:
    traceback.print_exc()
