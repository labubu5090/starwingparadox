"""Analyze PE analysis results."""
import json

with open(r'C:\Users\KAHO\Pictures\Starwing\tools\ida\pe_analysis_results.json', 'r') as f:
    data = json.load(f)

# Analyze AcrGame-Win64-Shipping.exe imports
print('=== AcrGame-Win64-Shipping.exe Imports ===')
shipping = data['AcrGame-Win64-Shipping.exe']
for dll, funcs in shipping['imports'].items():
    print(f'\n{dll} ({len(funcs)} functions):')
    for func in funcs[:10]:
        name = func['name']
        print(f'  - {name}')
    if len(funcs) > 10:
        print(f'  ... and {len(funcs) - 10} more')

print('\n\n=== GALAXYIO.dll Imports ===')
galaxy = data['GALAXYIO.dll']
for dll, funcs in galaxy['imports'].items():
    print(f'\n{dll} ({len(funcs)} functions):')
    for func in funcs[:10]:
        name = func['name']
        print(f'  - {name}')
    if len(funcs) > 10:
        print(f'  ... and {len(funcs) - 10} more')

print('\n\n=== GALAXYIO.dll Exports ===')
for exp in galaxy['exports']:
    name = exp['name']
    ordinal = exp['ordinal']
    print(f'  - {name} (ordinal: {ordinal})')

print('\n\n=== AcrGame.exe Imports ===')
launcher = data['AcrGame.exe']
for dll, funcs in launcher['imports'].items():
    print(f'\n{dll} ({len(funcs)} functions):')
    for func in funcs:
        name = func['name']
        print(f'  - {name}')

print('\n\n=== Lua524.dll Exports (first 30) ===')
lua = data['Lua524.dll']
for exp in lua['exports'][:30]:
    name = exp['name']
    ordinal = exp['ordinal']
    print(f'  - {name} (ordinal: {ordinal})')

print('\n\n=== QRreader.dll Exports ===')
qr = data['QRreader.dll']
for exp in qr['exports']:
    name = exp['name']
    ordinal = exp['ordinal']
    print(f'  - {name} (ordinal: {ordinal})')
