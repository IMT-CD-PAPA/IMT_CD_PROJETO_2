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

Notebook executável: `notebooks/CWRU_deteccao_diagnostico.ipynb`
Relatório técnico: `relatorio/relatorio_tecnico.md` (anexo de matrizes de confusão em `relatorio/anexo_matrizes_confusao.md`)
Dados: `data/raw/` (28 arquivos .mat, 214 MB), origem e hashes em `data/README.md` e `data/CHECKSUMS.sha256`
Resultados e figuras: `results/` (tabela padronizada em `results/tabela_resumo.md`)
Apresentação (YouTube, até 5 min): LINK_AQUI
Slides: LINK_AQUI

## Como reproduzir

No Colab: clique no botão acima e use Executar tudo. A primeira célula clona o repositório e baixa/verifica os dados se faltarem. Tempo total em CPU: cerca de 6 a 7 minutos.

Local: `pip install -r requirements.txt`, `python scripts/baixar_dados.py`, abrir o notebook. Semente fixa (42).

## Resultado em uma frase

Os protocolos usuais (split temporal e leave-one-load-out) saturam em 100%, então não discriminam técnicas. O teste que separa as técnicas é treinar em duas severidades de falha e testar na terceira (P3): Random Forest com atributos de tempo + envelope chega a 82,3% de TPR e 0% de FPR, com recall de OR de só 32,4%, e a severidade 0,014" é a que falha. Detalhes e discussão crítica no relatório.

## Estrutura

notebooks/ (notebook), scripts/ (download, auditoria do pacote Kaggle, anexos), data/, results/, relatorio/.

## Uso de IA

Claude (Anthropic, Sonnet 5.5) foi usado para estruturar o repositório, escrever e depurar o código, rodar os experimentos e redigir a primeira versão do relatório. Declaração completa e referência da ferramenta na seção 7 de `relatorio/relatorio_tecnico.md`.