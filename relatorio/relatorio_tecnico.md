# Detecção e diagnóstico de anomalias em sinais de vibração: CWRU

ECM514 Ciência de Dados, IMT. Desafio 2, Grupo 4.

**Integrantes**

| Nome | RA |
|------|----|
| Felipe Kenzo Ohara Sakae | 22.00815-2 |
| Guilherme Martins Souza Paula | 22.00006-2 |
| Lucas Gozze Crapino | 22.00667-2 |
| Murillo Penha Strina | 22.00730-0 |
| Pedro Campos Dec | 22.00787-3 |
| Vinicius Garcia Imendes Dechechi | 22.01568-0 |


## 1. Descrição do dataset

Origem: Case Western Reserve University Bearing Data Center. Os 28 arquivos .mat usados foram baixados do site oficial (engineering.case.edu/sites/default/files/NUMERO.mat) em 04/10/2026 e seus SHA-256 coincidem integralmente com os dos arquivos do espelho público do CWRU (github.com/s-whynot/CWRU-dataset) que o notebook baixa e verifica automaticamente. Uma primeira tentativa de baixar o arquivo 239 veio truncada (6.020.315 de 7.826.336 bytes, com bytes iniciais idênticos); um segundo download veio completo e bateu. O pacote do Kaggle sugerido pelo professor foi auditado (`scripts/auditoria_kaggle.py`) e não foi usado como fonte: tem falhas a 12 kHz e Normais a 48 kHz misturados, Normal_2 é cópia de Normal_1 (a gravação real do arquivo 99 não está lá) e há incoerências de carga/RPM em B007, B021, IR021 e OR0146.

Montagem física: motor de 2 HP, rolamento SKF 6205-2RS no lado do acionamento (drive end) como rolamento testado, defeitos introduzidos por eletroerosão com diâmetros de 0,007", 0,014" e 0,021", cargas de 0 a 3 HP (rotação de cerca de 1797 a 1730 rpm). Aceleração medida no lado do acionamento (DE). Geometria do rolamento: 9 elementos, d = 0,3126", D = 1,537", o que dá BPFO = 3,5848 x fr e BPFI = 5,4152 x fr (fr = frequência de rotação).

Taxa de amostragem: 48 kHz para todas as classes usadas. Os Normais (97 a 100) são gravados a 48 kHz; para não depender de documentação conflitante, confirmamos empiricamente pelo pico de 1x da rotação (48 kHz encaixa, 12 kHz não). Usar 48 kHz em tudo evita que a taxa de amostragem vire um atributo que denuncia a classe.

Classes e amostras (arquivos, amostras, duração): Normal 4 arquivos, 1.698.547 amostras, 35,4 s; IR 12 arquivos (3 severidades x 4 cargas), 4.830.126 amostras, 100,6 s; OR posição 6h, 12 arquivos, 5.122.638 amostras, 106,7 s. Em janelas de 0,5 s (24.000 amostras) com 50% de sobreposição no treino, o split P1 dá 94 janelas de treino e 17 de teste por classe. Contagens por protocolo estão em `results/contagem_janelas.csv`.

Higiene dos dados: a variável de cada arquivo é escolhida pelo prefixo, porque 99.mat traz X098 duplicada, 174_0.mat traz X173 com 1,3 s, 175_1.mat tem uma X217 extra sem RPM e 217_3.mat repete a X215.

## 2. Fundamentação das técnicas

Atributos de tempo (rms, pico, fator de crista, curtose, assimetria, fatores de forma e de impulso) são o padrão para monitoramento de condição (Randall e Antoni, 2011; Neupane e Seok, 2020). Energia em bandas de frequência resume a PSD. O espectro do envelope após demodulação em banda ressonante é a técnica clássica para falhas de rolamento, porque cada impacto da pista defeituosa excita ressonâncias estruturais e a taxa de repetição aparece como BPFO/BPFI e harmônicos (Antoni, 2007, kurtograma e banda ótima; Randall e Antoni, 2011). Usamos 10 atributos de SNR de envelope em BPFO/BPFI (harmônicos 1 a 3), 1x, 2x e bandas laterais de BPFI.

Detecção (treino só com Normal, nenhuma falha vista): Isolation Forest (Liu et al., 2008 e 2012), One-Class SVM (Schölkopf et al., 2001) e distância de Mahalanobis com covariância Ledoit-Wolf (Ledoit e Wolf, 2004). Limiar em 95% dos escores fora da amostra de treino.

Classificação: Random Forest (Breiman, 2001), SVM com kernel RBF, kNN (k = 5) e regressão logística, mais um pipeline de duas etapas (detector + classificador de tipo).

Avaliação com particionamento que respeita dependência temporal entre janelas vizinhas (Bergmeir e Benítez, 2012). Intervalos de Wilson a 95% para TPR/FPR.

## 3. Metodologia

Janelas de 0,5 s, treino com hop de 12.000 amostras, avaliação com hop de 24.000 e guarda de 12.000 amostras entre treino e teste do mesmo sinal para não vazar janelas sobrepostas. Semente 42.

Protocolos. P1: split temporal 70/30 dentro de cada sinal. P2: leave-one-load-out (treina em 3 cargas, testa na quarta; severidade 0,007"). P3: leave-one-severity-out (treina em duas severidades de falha, testa na terceira; Normal usa split temporal como em P1). Também medimos um split aleatório de janelas ("ingênuo") só para mostrar o teto.

Atributos: tempo (7), energia em 10 bandas log, envelope (10 SNRs). A banda de demodulação é escolhida varrendo candidatas de 1 a 4 kHz de largura entre 500 e 20.000 Hz, usando só janelas de falha do treino de cada fold.

Detectores treinados só com Normal. Dois limiares: "temporal" (validação cruzada em blocos, K = 5, com descarte de vizinhas) e "por carga" (leave-one-load-out dentro dos normais do treino), este segundo existe porque a carga muda a distribuição do Normal e o primeiro subestima isso.

## 4. Resultados

Tabela padronizada completa (todos os protocolos e técnicas): `results/tabela_resumo.md`. Abaixo, o recorte principal. Colunas: Dataset | Técnica | Tipo de falha identificada | TPR | FPR | Acurácia por classe.

| Dataset | Técnica | Tipo de falha identificada | TPR (IC 95%) | FPR (IC 95%) | Acurácia por classe |
|---|---|---|---|---|---|
| CWRU | P1, qualquer técnica | IR, OR | 100% [89,8; 100] | 0% [0; 18,4] | Normal 100, IR 100, OR 100 |
| CWRU | P2, Random Forest (tempo + envelope) | IR, OR | 100% [97,3; 100] | 0% [0; 5,2] | Normal 100, IR 100, OR 100 |
| CWRU | P2, Isolation Forest (limiar temporal) | não se aplica | 100% [97,3; 100] | 17,1% [10,1; 27,6] | não se aplica (AUROC 1,000) |
| CWRU | P2, Isolation Forest (limiar por carga) | não se aplica | 100% [97,3; 100] | 11,4% [5,9; 21,0] | não se aplica (AUROC 1,000) |
| CWRU | P2, One-Class SVM (temporal / por carga) | não se aplica | 100% | 77,1% / 60,0% | não se aplica |
| CWRU | P2, Mahalanobis (temporal / por carga) | não se aplica | 100% | 82,9% / 14,3% | não se aplica |
| CWRU | P3, detectores (qualquer) | não se aplica | 100% [99,1; 100] | 0% [0; 18,4] | não se aplica (AUROC 1,000) |
| CWRU | P3, Random Forest (tempo + envelope) | IR, OR | 82,3% [78,3; 85,7] | 0% [0; 7,0] | Normal 100, IR 84,3, OR 32,4 |
| CWRU | P3, SVM RBF | IR | 82,3% | 2,0% | Normal 98,0, IR 57,4, OR 0,0 |
| CWRU | P3, kNN (k = 5) | IR, OR | 82,3% | 9,8% | Normal 90,2, IR 58,4, OR 33,3 |
| CWRU | P3, Regressão logística | IR, OR | 82,3% | 3,9% | Normal 96,1, IR 71,1, OR 33,3 |
| CWRU | P3, pipeline IF + RF (tempo + envelope) | IR, OR | 100% [99,1; 100] | 0% [0; 7,0] | Normal 100, IR 88,3, OR 32,4 |
| CWRU | P3, pipeline IF + RF (tipo só por envelope) | IR, OR | 100% | 0% | Normal 100, IR 100, OR 66,2 |
| CWRU | P3, Random Forest (só envelope) | IR, OR | 75,4% [71,0; 79,4] | 23,5% [14,0; 36,8] | Normal 76,5, IR 84,8, OR 66,7 |

Matrizes de confusão completas: `anexo_matrizes_confusao.md`.

Por severidade retida em P3 (acurácia do Random Forest, tempo / espectro / envelope / tempo + envelope): 0,007": 0,554 / 0,554 / 0,968 / 0,987. 0,014": 0,146 / 0,451 / 0,306 / 0,424. 0,021": 0,121 / 0,529 / 0,955 / 0,439. Bandas de demodulação escolhidas: 1000 a 5000 Hz em P1 e todos os folds de P2; 5000 a 9000, 2500 a 4500 e 7000 a 8000 Hz nos três folds de P3.

## 5. Discussão crítica

Teto em P1 e P2. Todas as técnicas dão 100% em P1 e P2, e o split aleatório de janelas também (acurácia 1,0). Um único atributo, o RMS, já separa as classes a 100% em P2. Isso significa que esses protocolos medem pouco: com falha de 0,007" e as mesmas máquinas, a energia total da janela já entrega a classe. Reportamos os números, mas não os usamos para ranquear técnicas.

Detecção. Com treino só em Normal, todos os detectores têm AUROC 1,0 e TPR 100% nos três protocolos, mas o FPR depende da calibração do limiar. Em P2 o limiar temporal dá FPR de 17,1% (IF), 77,1% (OCSVM) e 82,9% (Mahalanobis), porque o Normal em carga nova é uma extrapolação. O limiar por carga reduz para 11,4%, 60,0% e 14,3%. O que sobra é quase todo o fold de 0 HP, onde o único arquivo Normal tem só 5 s e variância ligeiramente diferente (desvio 0,073 contra cerca de 0,065 nas outras cargas), ou seja, é extrapolação real e não erro de calibração. Em P3 não há sobra: FPR 0%, mas com apenas 17 janelas Normais o IC vai até 18,4%.

Diagnóstico entre severidades (P3) é onde o desafio está. O melhor modelo geral (RF tempo + envelope) chega a 82,3% de TPR, mas isso esconde a classe OR, com recall de 32,4%. A severidade 0,014" falha em todos os modelos. Causa medida: a SNR do envelope nas frequências BPFO/BPFI é baixa nessa severidade (IR 0,48 e OR 0,30 na banda de 1 a 5 kHz, contra 1,4 e 1,45 em 0,007"), e há um pico dominante em cerca de 4 x fr no envelope que o Normal também apresenta, então o classificador só com envelope rotula OR014 como Normal. Em nenhuma das bandas testadas o recall de OR ficou acima de 0.

Atributos de tempo e escala. Os atributos de tempo dependem da amplitude absoluta, e a amplitude muda com a severidade (RF só com tempo: 0,146 e 0,121 de acurácia em 0,014" e 0,021"). Os de envelope generalizam melhor (0,955 em 0,021"), mas dependem da banda escolhida, e essa escolha é frágil: a sensibilidade em 0,021" varia de 0,758 a 0,994 conforme a banda (apêndice A). Bandas fixas e maximin não resolveram 0,014", e atributos invariantes de escala (apêndice B) ajudaram só em parte.

Pipeline de duas etapas. Usar o detector antes do classificador leva TPR a 100% em P3, mas em P2 herda o FPR do detector (17,1%) enquanto o RF direto tem 0%. Ou seja, o pipeline compra sensibilidade em extrapolação de severidade e paga com falsos alarmes em extrapolação de carga.

Limitações. Três classes e uma única posição de falha OR (6h). Poucas janelas Normais (17 por teste), IC largos. Um rolamento, uma bancada: nada aqui garante generalização para outras máquinas. Janelas de um mesmo arquivo são dependentes, o que o split temporal com guarda reduz mas não elimina. Normal tem 4 gravações curtas (a de 0 HP tem 5 s).

## 6. Referências

Antoni, J. (2007). Fast computation of the kurtogram for the detection of transient faults. Mechanical Systems and Signal Processing, 21(1), 108-124. (existência confirmada por busca; conferir DOI)
Neupane, D., Seok, J. (2020). Bearing fault detection and diagnosis using Case Western Reserve University dataset with deep learning approaches: a review. IEEE Access, 8. (existência confirmada por busca)
Bergmeir, C., Benítez, J. M. (2012). On the use of cross-validation for time series predictor evaluation. Information Sciences, 191, 192-213. (existência confirmada por busca)
Liu, F. T., Ting, K. M., Zhou, Z.-H. (2012). Isolation-based anomaly detection. ACM TKDD, 6(1). (existência confirmada por busca)
Liu, F. T., Ting, K. M., Zhou, Z.-H. (2008). Isolation forest. IEEE ICDM.
Schölkopf, B., Platt, J. C., Shawe-Taylor, J., Smola, A. J., Williamson, R. C. (2001). Estimating the support of a high-dimensional distribution. Neural Computation, 13(7), 1443-1471.
Ledoit, O., Wolf, M. (2004). A well-conditioned estimator for large-dimensional covariance matrices. Journal of Multivariate Analysis, 88(2), 365-411.
Breiman, L. (2001). Random forests. Machine Learning, 45(1), 5-32.
Randall, R. B., Antoni, J. (2011). Rolling element bearing diagnostics, a tutorial. Mechanical Systems and Signal Processing, 25(2), 485-520.
Smith, W. A., Randall, R. B. (2015). Rolling element bearing diagnostics using the Case Western Reserve University data: a benchmark study. MSSP, 64-65, 100-131.
Case Western Reserve University Bearing Data Center. engineering.case.edu/bearingdatacenter.

Aviso: as referências sem a marca "existência confirmada" foram escritas de memória. Conferir cada uma (autores, ano, páginas, DOI) antes de entregar.

## 7. Declaração de uso de IA

Ferramenta: Claude (Anthropic), modelo Claude Sonnet 5.5, usado via Claude Code na interface web do claude.ai, em outubro de 2026. Referência: Anthropic. Claude Sonnet 5.5 [modelo de linguagem]. https://www.anthropic.com/claude. Acesso em 04 out. 2026. Sessão: https://claude.ai/code/session_01WLWraB5DNu6Xim3Ubt45s9

Para que foi usada: (1) comparar datasets do enunciado e recomendar o CWRU; (2) montar a estrutura do repositório conforme o enunciado e a rubrica; (3) escrever e depurar o código do notebook e dos scripts (leitura dos .mat, janelamento, atributos, detectores, classificadores, protocolos P1/P2/P3, intervalos de Wilson); (4) auditar o pacote do Kaggle e encontrar as armadilhas dos dados (taxa de amostragem dos Normais, variáveis duplicadas, Normal_2 repetido); (5) rodar os experimentos e gerar tabelas e figuras; (6) redigir a primeira versão deste relatório e dos READMEs; (7) sugerir referências.

O que a IA não substitui: as decisões de escolher o CWRU e de aceitar o escopo de 3 classes foram do grupo. Os números do relatório vêm da execução do notebook (`results/`), não de texto gerado. As referências marcadas como "existência confirmada" foram checadas por busca; as demais foram sugeridas de memória pela IA e devem ser conferidas pelo grupo, que também responde pelo conteúdo final.

Validação humana: o grupo deve registrar aqui o que revisou de fato (execução do notebook no Colab, conferência das referências, leitura do relatório): ______________________.