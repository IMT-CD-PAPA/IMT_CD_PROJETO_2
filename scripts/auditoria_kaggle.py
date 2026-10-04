"""Audita o pacote CWRU do Kaggle (astrollama/cwru-case-western-reserve-university-dataset).

Uso:
    python scripts/auditoria_kaggle.py caminho/para/archive.zip

O que é verificado, sem depender de nenhum outro arquivo:
  1. variáveis, número de amostras e RPM de cada .mat;
  2. taxa de amostragem de cada arquivo, estimada pelo pico de 1x (RPM/60) no espectro, testando 48 kHz e 12 kHz;
  3. sinais duplicados entre arquivos diferentes (o caso que mais engana: um "Normal" que é cópia de outro);
  4. se Normal_0, Normal_1 e Normal_3 são idênticos (SHA-256) aos arquivos originais 97, 98 e 100 do CWRU.
"""
import sys, zipfile, tempfile, hashlib, itertools, re
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from scipy.signal import welch

NOMINAL_RPM = {0: 1797, 1: 1772, 2: 1750, 3: 1730}
ORIGINAL_SHA = {'Normal_0.mat': '16bf48babcf1c7ac224bc1a81cd9eafdb27e42d5cf559761907e067e8eeadf3c',
                'Normal_1.mat': '37e6612c05e65c415dcfa2ab27a3fda648a5863160fa898b884a14743044e045',
                'Normal_3.mat': '88a5990cb541320e91505a1d72139e1993500ffe6e292a451011667f4138ca78'}

def shaft_peak(x, fs, fr):
    f, p = welch(x - x.mean(), fs=fs, nperseg=min(len(x), fs * 4))
    m = (f > fr - 8) & (f < fr + 8)
    return f[m][np.argmax(p[m])]

def main(zip_path):
    tmp = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(tmp)
    files = sorted(tmp.rglob('*.mat'), key=lambda p: p.name)
    print(f'{len(files)} arquivos .mat em {zip_path}\n')
    sig, rows = {}, []
    for p in files:
        d = loadmat(p)
        de = [k for k in d if k.endswith('DE_time')]
        rk = [k for k in d if k.endswith('RPM')]
        load = int(re.search(r'_(\d)\.mat$', p.name).group(1))
        rpm = float(np.squeeze(d[rk[0]])) if rk else float(NOMINAL_RPM[load])
        x = np.squeeze(d[de[0]]).astype(float)
        fr = rpm / 60
        e48, e12 = abs(shaft_peak(x, 48000, fr) - fr), abs(shaft_peak(x, 12000, fr) - fr)
        fs_est = 48000 if e48 < e12 else 12000
        sig[p.name] = x
        rows.append((p.name, de, len(x), rpm, 'arquivo' if rk else 'nominal', fs_est))
    print(f'{"arquivo":14s} {"variavel(is) DE":22s} {"amostras":>9s} {"rpm":>7s} {"fonte rpm":>9s} {"fs estimada":>11s}')
    for r in rows:
        print(f'{r[0]:14s} {",".join(r[1]):22s} {r[2]:9d} {r[3]:7.0f} {r[4]:>9s} {r[5]:11d}')
    by_fs = {}
    for r in rows:
        by_fs.setdefault(r[5], []).append(r[0].replace('.mat', ''))
    print('\nTaxa de amostragem estimada por grupo de arquivos:')
    for fs, names in sorted(by_fs.items()):
        print(f'  {fs} Hz: {", ".join(names)}')
    print('\nCoerência entre o número de carga no nome e o RPM (o RPM deve cair conforme a carga sobe):')
    fam = {}
    for r in rows:
        if r[4] == 'arquivo':
            fam.setdefault(re.sub(r'_\d\.mat$', '', r[0]), []).append((int(re.search(r'_(\d)\.mat$', r[0]).group(1)), r[3], r[0]))
    bad = []
    for name, lst in sorted(fam.items()):
        lst.sort()
        if any(b[1] > a[1] + 2 for a, b in zip(lst, lst[1:])):
            bad.append(f'{name}: ' + ', '.join(f'{x[2].replace(".mat", "")}={x[1]:.0f} rpm' for x in lst))
    print('  ' + ('\n  '.join(bad) if bad else 'nenhuma inconsistência'))
    print('\nSinais duplicados entre arquivos diferentes:')
    dups = [(a, b) for a, b in itertools.combinations(sig, 2) if len(sig[a]) == len(sig[b]) and np.array_equal(sig[a][:5000], sig[b][:5000])]
    print('  ' + (', '.join(f'{a} == {b}' for a, b in dups) if dups else 'nenhum'))
    print('\nIntegridade dos Normais contra os originais do CWRU (SHA-256):')
    for name, digest in ORIGINAL_SHA.items():
        f = next((q for q in files if q.name == name), None)
        got = hashlib.sha256(f.read_bytes()).hexdigest() if f else None
        print(f'  {name}: ' + ('idêntico ao original' if got == digest else ('diferente' if got else 'ausente')))
    normals = [r for r in rows if r[0].startswith('Normal')]
    if len({r[5] for r in rows}) > 1 and normals:
        print('\nATENÇÃO: o pacote mistura taxas de amostragem. Usar os arquivos como estão compara Normal e defeitos em taxas diferentes.')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
