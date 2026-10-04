"""Baixa e confere os arquivos .mat do CWRU usados no projeto (48 kHz, lado do acoplamento).

Uso:
    python scripts/baixar_dados.py            # 28 arquivos (Normal + defeitos de 0,007", 0,014" e 0,021")
    python scripts/baixar_dados.py --so-007   # 12 arquivos (Normal + defeito de 0,007", sem o protocolo P3)

Os arquivos vão para data/raw/. Cada um é conferido por tamanho e SHA-256, então um download corrompido
ou um arquivo diferente do esperado interrompe a execução. O notebook faz a mesma coisa sozinho na primeira execução;
este script serve para popular a pasta antes de versionar os dados no Git.
"""
import sys, hashlib, urllib.request, urllib.parse
from pathlib import Path

MIRROR = 'https://raw.githubusercontent.com/s-whynot/CWRU-dataset/main/'
RAW = Path(__file__).resolve().parent.parent / 'data' / 'raw'

# (classe, severidade, carga): (arquivo local, caminho no espelho, bytes, SHA-256, prefixo da variável dentro do .mat)
REC_FILES = {
    ('Normal', '-', 0): ('97_Normal_0.mat', 'Normal/97_Normal_0.mat', 3903344, '16bf48babcf1c7ac224bc1a81cd9eafdb27e42d5cf559761907e067e8eeadf3c', 'X097'),
    ('Normal', '-', 1): ('98_Normal_1.mat', 'Normal/98_Normal_1.mat', 7742720, '37e6612c05e65c415dcfa2ab27a3fda648a5863160fa898b884a14743044e045', 'X098'),
    ('Normal', '-', 2): ('99_Normal_2.mat', 'Normal/99_Normal_2.mat', 15503928, '4b97e6b5361f45efb6951dc3b1aebcdb3b89cb69d0f96d6f5c297dd9f45eee75', 'X099'),
    ('Normal', '-', 3): ('100_Normal_3.mat', 'Normal/100_Normal_3.mat', 7770624, '88a5990cb541320e91505a1d72139e1993500ffe6e292a451011667f4138ca78', 'X100'),
    ('IR', '007', 0): ('109_0.mat', '48k_Drive_End_Bearing_Fault_Data/IR/007/109_0.mat', 3903344, 'daddef5f784879becdf8fefbe2453f11c3cfc8d061a2a671da2f546d1bb48460', 'X109'),
    ('IR', '007', 1): ('110_1.mat', '48k_Drive_End_Bearing_Fault_Data/IR/007/110_1.mat', 7779920, '9e2bc579af6f4e6d9d26bf63b7ed84ecba7775740d56a3737cc8f04f73c22d1a', 'X110'),
    ('IR', '007', 2): ('111_2.mat', '48k_Drive_End_Bearing_Fault_Data/IR/007/111_2.mat', 7770624, 'a2e64a397a990efb91ba55252a84796f755bda3eb097c4b47cc0730a08dab309', 'X111'),
    ('IR', '007', 3): ('112_3.mat', '48k_Drive_End_Bearing_Fault_Data/IR/007/112_3.mat', 7770624, '1775db11999f268c6ccf04b3ee19857f90a3636f4a582f1abd9a627f991e72d4', 'X112'),
    ('OR', '007', 0): ('135_0.mat', '48k_Drive_End_Bearing_Fault_Data/OR/007/@6/135_0.mat', 3896944, '5a1c3ceec1f2b58af9e01051e425aa9d31dd018f58a8d31cda25bbdb1ac6dca9', 'X135'),
    ('OR', '007', 1): ('136_1.mat', '48k_Drive_End_Bearing_Fault_Data/OR/007/@6/136_1.mat', 7789200, '37f259eebbc92afa8bd1b445d02af14e83608a48cd7a3cf5c323515ddc2d0f24', 'X136'),
    ('OR', '007', 2): ('137_2.mat', '48k_Drive_End_Bearing_Fault_Data/OR/007/@6/137_2.mat', 7789200, 'a81b621153e426aa32848be8157c42bcd81065a28ac7655a9a6597f3889fa3ef', 'X137'),
    ('OR', '007', 3): ('138_3.mat', '48k_Drive_End_Bearing_Fault_Data/OR/007/@6/138_3.mat', 7807760, 'b43eeb67badeb129047ddd3658bf673815dc4bd445facb4217eb04653bb2e11d', 'X138'),
    ('IR', '014', 0): ('174_0.mat', '48k_Drive_End_Bearing_Fault_Data/IR/014/174_0.mat', 1020944, 'ca7113a900d9217aa5632e0dad4f8791caed4d314321daa011719e1bc99f3026', 'X173'),
    ('IR', '014', 1): ('175_1.mat', '48k_Drive_End_Bearing_Fault_Data/IR/014/175_1.mat', 17849704, '18302e96425ad163db699da3a2ca63d8f6ef4dfc99172e97ab21a8a77a83ac17', 'X175'),
    ('IR', '014', 2): ('176_2.mat', '48k_Drive_End_Bearing_Fault_Data/IR/014/176_2.mat', 7807760, '569c7b292018e7e88cf4b375b091433c7566b9503545188979e93f6428427247', 'X176'),
    ('IR', '014', 3): ('177_3.mat', '48k_Drive_End_Bearing_Fault_Data/IR/014/177_3.mat', 7761344, '5cffc5aa2b1e5cc65a97ebcfaa369b886ad8db8b8840e0e0095e97b8b9be4c16', 'X177'),
    ('IR', '021', 0): ('213_0.mat', '48k_Drive_End_Bearing_Fault_Data/IR/021/213_0.mat', 3909760, '6afb81f36a9efcdd370a52166d71c13cb42278c7de22752c81d4b2a22fa133f0', 'X213'),
    ('IR', '021', 1): ('214_1.mat', '48k_Drive_End_Bearing_Fault_Data/IR/021/214_1.mat', 7761344, 'a8fe29f358b7f9c140f38e0cd7fbafdd7441c44e30a5b704ecb9be64cbb841ed', 'X214'),
    ('IR', '021', 2): ('215_2.mat', '48k_Drive_End_Bearing_Fault_Data/IR/021/215_2.mat', 7863472, '1e3d65088782a29aa70004896db4b9836499dd12edd3c58fb496f4befca6f746', 'X215'),
    ('IR', '021', 3): ('217_3.mat', '48k_Drive_End_Bearing_Fault_Data/IR/021/217_3.mat', 15689680, 'fb5b067c04b4c8449cbdd4ac4e376d7eb0804b9203efcab513e42aaf2f6a2cf7', 'X217'),
    ('OR', '014', 0): ('201@6_0.mat', '48k_Drive_End_Bearing_Fault_Data/OR/014/201@6_0.mat', 3922576, '6c27615a61f19f05f65cf2cc2aa4bca5bda051c9d93a708d0ee8baf5138834fa', 'X201'),
    ('OR', '014', 1): ('202@6_1.mat', '48k_Drive_End_Bearing_Fault_Data/OR/014/202@6_1.mat', 7752064, '16f1a7eadbd6703a7a1ab1a32f8d7b97b6b85c1b31b1e760c123a9e175d8ae63', 'X202'),
    ('OR', '014', 2): ('203@6_2.mat', '48k_Drive_End_Bearing_Fault_Data/OR/014/203@6_2.mat', 7789200, '3cad2848f4c96cde04fc06ca0f541ad663298ecb50eb7fc74e25b72ab29e1c5a', 'X203'),
    ('OR', '014', 3): ('204@6_3.mat', '48k_Drive_End_Bearing_Fault_Data/OR/014/204@6_3.mat', 7817056, 'f3b1736698a580c2ea44cce78045833a9e76476d9153da8af5275c2e30e38a10', 'X204'),
    ('OR', '021', 0): ('238_0.mat', '48k_Drive_End_Bearing_Fault_Data/OR/021/@6/238_0.mat', 3941808, '63209a4057f199beb42beedf5b4481987fdb3ac746c46777dd385d689bc481df', 'X238'),
    ('OR', '021', 1): ('239_1.mat', '48k_Drive_End_Bearing_Fault_Data/OR/021/@6/239_1.mat', 7826336, '4ba7dc55258359577a68f6de5c0ff6675776d2b2c30d691dd4d71640e34834af', 'X239'),
    ('OR', '021', 2): ('240_2.mat', '48k_Drive_End_Bearing_Fault_Data/OR/021/@6/240_2.mat', 7807760, 'c5d8b4db09880b660da88865fff0e81afef0f5ad68bdf0ad7b75c722ae3e7e1c', 'X240'),
    ('OR', '021', 3): ('241_3.mat', '48k_Drive_End_Bearing_Fault_Data/OR/021/@6/241_3.mat', 7826336, 'cb64eed96d401837c25df63598b7d1a00868368e1ed503a8dcef1e5226ec9caa', 'X241'),
}

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    so_007 = '--so-007' in sys.argv
    RAW.mkdir(parents=True, exist_ok=True)
    files = {k: v for k, v in REC_FILES.items() if not so_007 or k[1] in ('-', '007')}
    for key, (name, rel, size, digest, var) in files.items():
        p = RAW / name
        if not (p.exists() and p.stat().st_size == size):
            print('baixando', name)
            urllib.request.urlretrieve(MIRROR + urllib.parse.quote(rel), p)
        assert p.stat().st_size == size, f'{name}: tamanho inesperado'
        assert sha256(p) == digest, f'{name}: SHA-256 diferente do esperado'
    print(f'ok: {len(files)} arquivos verificados em {RAW}')

if __name__ == '__main__':
    main()
