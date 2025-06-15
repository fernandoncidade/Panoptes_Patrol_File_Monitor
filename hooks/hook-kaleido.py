from PyInstaller.utils.hooks import collect_all, collect_data_files

datas, binaries, hiddenimports = collect_all('kaleido')
datas = [(src, dst) for src, dst in datas if not src.endswith('.py')]

kaleido_data = collect_data_files('kaleido')
for src, dst in kaleido_data:
    if not src.endswith('.py') and (src, dst) not in datas:
        datas.append((src, dst))
