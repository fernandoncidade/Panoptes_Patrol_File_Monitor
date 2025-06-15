from PyInstaller.utils.hooks import collect_all, collect_submodules

datas, binaries, hiddenimports = collect_all('plotly')
datas = [(src, dst) for src, dst in datas if not src.endswith('.py')]

additional_imports = [
    'plotly.graph_objects',
    'plotly.io',
    'plotly.io.to_image',
]

for module in additional_imports:
    hiddenimports.extend(collect_submodules(module))
