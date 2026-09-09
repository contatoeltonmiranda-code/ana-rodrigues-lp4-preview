---
name: feedback-verificar-compara-por-item
description: Elton reprova rodadas onde o agente deixa ~50% dos itens sem executar; Sofia deve auditar COMPARA item a item contra as refs antes de reportar
metadata:
  type: feedback
---

Rodo (design) reprovado com ~50% dos itens nao aplicados = falha de VERIFICACAO da Sofia, nao so do executor.

**Why:** Elton reprovou a rodada 3 da LP4 Ana ("percebi que varias coisas que pedi vc ignorou... isso nao pode acontecer de forma alguma"). O agente reportou itens como feitos mas deixou pedidos literais de lado (icone do titulo, 2 colunas, paleta de 2 cores).

**How to apply:** Ao receber rodada de ajustes: (1) salvar refs e briefing na pasta da rodada; (2) exigir do agente COMPARA (antes/depois) para CADA item; (3) Sofia abre e compara cada COMPARA com a ref antes de reportar; (4) transcrições automáticas de imagem trocam seções — mapear por crop/pixel, nunca pela transcrição. Relacionado: [[feedback-relatorio-cliente-pdf-annotado]].
