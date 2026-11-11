# Detecção e diagnóstico de anomalias em vibração (CWRU)

ECM514 Ciência de Dados, IMT, Desafio 2, Grupo 4. Dataset: CWRU Bearing Data Center, 3 classes (Normal, falha na pista interna IR, falha na pista externa OR).

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/IMT-CD-PAPA/IMT_CD_PROJETO_2/blob/main/notebooks/CWRU_deteccao_diagnostico.ipynb)

## Integrantes

| Nome | RA |
|------|----|
| Felipe Kenzo Ohara Sakae | 22.00815-2 |
| Guilherme Martins Souza Paula | 22.00006-2 |
| Lucas Gozze Crapino | 22.00667-2 |
| Murillo Penha Strina | 22.00730-0 |
| Pedro Campos Dec | 22.00787-3 |
| Vinicius Garcia Imendes Dechechi | 22.01568-0 |

## Sumário dos entregáveis

- Notebook executável: `notebooks/CWRU_deteccao_diagnostico.ipynb`
- Relatório técnico: `relatorio/relatorio_tecnico.md` (anexo de matrizes de confusão em `relatorio/anexo_matrizes_confusao.md`)
- Dados: `data/raw/` (28 arquivos .mat, 214 MB), origem e hashes em `data/README.md` e `data/CHECKSUMS.sha256`
- Resultados e figuras: `results/` (tabela padronizada em `results/tabela_resumo.md`)
- Vídeo da Apresentação: https://www.youtube.com/watch?v=kIdDouMf-0E
- Slides: `slides/CWRU_Grupo4_apresentacao.pptx`

## Como reproduzir

No Colab: clique no botão acima e use Executar tudo. A primeira célula clona o repositório e baixa/verifica os dados se faltarem. Tempo total: cerca de 14 minutos no Colab (medido em uma execução; em máquina local costuma ser mais rápido).

Local: `pip install -r requirements.txt`, `python scripts/baixar_dados.py`, abrir o notebook. Semente fixa (42).

## Resultado em uma frase

Os protocolos usuais (split temporal e leave-one-load-out) saturam em 100%, então não discriminam classificadores. O teste que separa os classificadores é treinar em duas severidades de falha e testar na terceira (P3): a acurácia do melhor classificador de três classes (Random Forest com tempo + envelope) cai para 62,2%, com recall de OR de só 32,4%, e a severidade 0,014" é a que falha. O melhor resultado no P3 é um pipeline em duas etapas (Isolation Forest para detectar, Random Forest só com envelope para o tipo): 0% de falso positivo, recall de IR 100% e de OR 66,2%. Detalhes e discussão crítica no relatório.

## Estrutura

notebooks/ (notebook), scripts/ (download, auditoria do pacote Kaggle, anexos, figuras do relatório), data/, results/, relatorio/, slides/ (apresentação).

## Uso de IA

Claude (Anthropic, Sonnet 5.5) foi usado para estruturar o repositório, escrever e depurar o código, rodar os experimentos e redigir a primeira versão do relatório. Declaração completa e referência da ferramenta na seção 9 de `relatorio/relatorio_tecnico.md`.
