"""Gera o anexo de matrizes de confusao (markdown) a partir de results/metricas.json."""
import json, pathlib
R = pathlib.Path(__file__).resolve().parents[1]
m = json.load(open(R/'results/metricas.json'))['matrizes_confusao']
lab = ['Normal', 'IR', 'OR']
out = []
for k, M in m.items():
    out.append(f"**{k}** (linhas = classe real, colunas = predita)\n")
    out.append("| real \\ pred | " + " | ".join(lab) + " |\n|---|---|---|---|")
    for l, row in zip(lab, M):
        out.append(f"| {l} | " + " | ".join(str(int(v)) for v in row) + " |")
    out.append("")
(R/'relatorio/anexo_matrizes_confusao.md').write_text("\n".join(out), encoding='utf-8')
print(len(m), 'matrizes')
