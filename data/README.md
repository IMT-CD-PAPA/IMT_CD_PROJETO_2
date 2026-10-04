# Dados

Origem: Case Western Reserve University Bearing Data Center (https://engineering.case.edu/bearingdatacenter), rolamento SKF 6205-2RS do lado do acionamento (drive end), acelerômetro DE, 48 kHz. Os arquivos .mat vêm do espelho público https://github.com/s-whynot/CWRU-dataset, que o notebook baixa sozinho em `data/raw/` com checagem de tamanho e SHA-256 (`CHECKSUMS.sha256`).

Uso: `python scripts/baixar_dados.py` (28 arquivos, 214 MB) ou `python scripts/baixar_dados.py --so-007` (12 arquivos, 89 MB, só falha de 0,007").

Classes usadas: Normal (arquivos 97 a 100), IR (falha na pista interna, 0,007", 0,014", 0,021") e OR (pista externa posição 6h, mesmas três severidades), cargas de 0 a 3 HP.

Armadilhas encontradas e tratadas: (1) o arquivo 99.mat contém a variável X098 repetida, por isso a variável é escolhida pelo prefixo do arquivo e não pela primeira chave DE_time; (2) 174_0.mat guarda X173 com 1,3 s; (3) 175_1.mat tem uma X217 extra sem RPM; (4) 217_3.mat repete X215; (5) a taxa de amostragem dos Normais é 48 kHz (confirmada pelo pico de 1x da rotação), não 12 kHz.

Pacote do Kaggle indicado pelo professor: tem 36 arquivos de falha a 12 kHz e 4 Normais a 48 kHz, Normal_2 é cópia de Normal_1 (a X099 real não está lá) e há inconsistências de carga/RPM em B007, B021, IR021 e OR0146. Auditoria reproduzível em `scripts/auditoria_kaggle.py`. Por isso o projeto usa o espelho original com verificação de hash.
