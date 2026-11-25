# ENTRESSALA — Bloqueio editorial dos extraordinários Metricool

**Versão do controle:** `entressala-metricool-extra-2026-11-25-v2`  
**Data:** 25/11/2026  
**Escopo:** somente novos posts extraordinários da marca Metricool `8230360`.  
**Referência:** `instagram/metricool-extraordinarios.md` e política editorial unificada v1.0.0-rc1.  
**Estado:** preflight offline implementado/testado; o conector de publicação Metricool ainda **não tem imposição técnica desse preflight**.

## Por que este bloqueio é necessário

As regras anteriores sobre imagem autêntica, direitos e priorização cultural existiam, mas uma publicação do Quebra-Nozes foi criada com ilustração de IA e o Campinas Matsuri usou imagem genérica do espaço. A falha estrutural é que a API do Metricool aceita agendamentos diretos, sem exigir um recibo de QA da ENTRESSALA. **Documentação por si só não barra o envio.**

## Fluxo seguro para cada novo extraordinário

1. **Pauta e evidências.** Registrar data, assunto, novidade, notoriedade/reconhecimento, incentivo a compartilhar, classe event/radar/news, fonte primária e situação de serviço. Priorizar pessoa/obra/atração reconhecível. Não escolher pauta nichada apenas para preencher agenda.
2. **Imagem e direitos.** Separar arquivos finais 1080 x 1350, fonte original e SHA-256 da foto-fonte, licença e URL que COMPROVE permissão de reutilização no Instagram, titular e crédito. O recibo deve apontar para uma inspeção editorial concreta. Fotografia real, específica do artista/obra/evento, na capa; ao menos 80% dos slides com fotos reais, salvo obra autêntica que seja ela mesma a matéria com exceção fundamentada. Não aceitar ilustração sintética para simular acontecimento ou foto genérica do espaço.
3. **Segunda passagem de revisão editorial pelo ChatGPT.** Após concluir a produção, conferir a imagem em tamanho de celular, título factual, serviço na imagem, data e local, legenda, CTA para seguir a ENTRESSALA e fonte. Registrar o ChatGPT como responsável, decisão final, observações e evidências revisáveis vinculadas à arte e legenda exatas — um `true` escrito sem conferência não é prova. Não solicitar aprovação humana de rotina nem fingir independência humana. Revisar também duplicatas no histórico da revista, Instagram regular e Metricool.
4. **Preflight local antes da API.** Executar `metricool_gate.py` usando manifesto real e arquivos finais. O script gera `report.json`, com `BLOCKED` ou `APPROVED_FOR_METRICOOL_SUBMISSION`. Arquivo ausente, dados inconsistentes, falta de direitos e quaisquer dúvidas geram `BLOCKED`. Se bloqueado, **NÃO chamar `createScheduledPost` nem `updateScheduledPost`**.
5. **Hash do pacote aprovado.** Conservar `manifest_sha256`, `approval_digest`, hashes de imagens finais e versão da política. Antes de montar a chamada do Metricool, revalidar que o JSON e os JPEGs permanecem idênticos. Qualquer modificação obriga novo QA.
6. **Conferência remota.** Na janela anterior ao envio, consultar conectividade da marca correta, verificar duplicata em Metricool e confirmar ausência de colisão com publicação regular. A evidência deve ser real, registrada no manifesto, com hora. O script não acessa APIs remotas e depende dessa prova externa.
7. **Publicação e recibo.** Só chamar Metricool após `APPROVED`; salvar ID, UUID e URL do planner. `PENDING` **não equivale** a `PUBLISHED`. Depois, consultar status até `PUBLISHED` e URL pública ou registrar `ERROR`. Não repetir envio remotamente incerto sem reconciliação por UUID.
8. **Conformidade posterior.** Revisar post publicado contra manifesto e arte efetiva. Ausência de aprovação, divergência de imagens, alterações de legenda ou erro remoto são **incidentes reportáveis**, com tipo de desvio, evidência, impacto, ação corretiva, responsável e estado. Jamais apagar ou republicar silenciosamente um post histórico.

## Execução (exemplo de comando)

```bash
python instagram/metricool_gate.py \
  --manifest /caminho/para/o-candidato.json \
  --assets-root /caminho/para/as-imagens \
  --history instagram/image-history.json \
  --report /caminho/para/relatorio-qa.json
```

O comando **não publica**. Status de saída `0` significa que as verificações locais e as provas declaradas passaram; saída `2` indica bloqueio. Todos os itens do relatório incluem `code`, `field`, `finding` e `resolution` para explicar por que foram bloqueados e o que corrigir.

**Exemplo de ocorrência** (sintética, não um post real):

```json
{
  "post_id": "ENTRESSALA-EXTRA-20261125-DEMO",
  "verdict": "BLOCKED",
  "issue_count": 2,
  "issues": [
    {"code": "COVER_NOT_AUTHENTIC", "field": "slides[0].media_kind", "finding": "Capa sem fotografia real pertinente.", "resolution": "Usar fotografia autentica do artista/obra/evento, licenciada."},
    {"code": "PHOTO_RATIO", "field": "slides", "finding": "Proporcao fotografica de 0%, abaixo de 80%.", "resolution": "Usar fotografias reais em pelo menos 80% das laminas."}
  ]
}
```

## Tipos de bloqueio e tratamento

| Tipo | Bloqueio imediato | Como recuperar |
| --- | --- | --- |
| Fato sem fonte ou sem data recente | Sim | Verificar fonte primária e atualizar hora de conferência |
| Evento com imagem de IA genérica | Sim | Obter fotografia autêntica e autorizada; caso impossível, mudar pauta |
| Foto do edifício quando ele não é a notícia | Sim | Substituir por registro da atração/artista; não criar substituto sintético |
| Fotografia sem licença/reutilização comprovada | Sim | Obter titular/licença válida ou desistir de usá-la |
| Origem da imagem já publicada | Sim | Escolher imagem-fonte diferente e revalidar |
| Falta de serviço/CTA ou arte ilegível | Sim | Revisar legenda/arte e repetir QA visual |
| Marca desconectada, duplicata encontrada | Sim | Reconectar/conciliar ID antes do envio |
| Resultado remoto `ERROR`/status desconhecido | Não declarar sucesso | Documentar, consultar ID/UUID, corrigir a causa, então reenviar apenas se seguro |

## Limites e garantia real

- O código verifica estrutura, arquivos, dimensões, SHA-256, janela de atualização, campos, registros de direitos e flags de revisão. **Não consegue provar por si só que a pessoa retratada é o artista certo, que a notícia é verdadeira nem que uma licença web é válida.** O ChatGPT, como revisor responsável, precisa observar as evidências na segunda passagem, não preencher campos fictícios. O gate não comprova que a revisão ocorreu apenas por encontrar uma declaração.
- Este script não intercepta chamadas diretas pelo conector do Metricool. Portanto **não existe, neste momento, garantia técnica de que 100% de posts criados por qualquer usuário ou agente passe pelo bloqueio**. Isso exige um gateway único que seja o ÚNICO publicador autorizado, com credenciais de publicação restritas, conferência do hash e rejeição de pacotes não aprovados. Não instalar esse gateway sem teste e plano de rollback.
- Esta implementação fica na branch editorial `entressala-piloto-2026-11`. **Não modifica** o publicador regular, GitHub `main`, Apps Script, Buffer, Cloudflare ou as automações da revista.

## Meta de conformidade e informação ao usuário

**Meta operacional:** 100% das publicações extraordinárias enviadas por este fluxo devem ter relatório `APPROVED`, hashes consistentes e recibo Metricool; 100% das reprovações devem emitir `BLOCKED` com causa e correção. Isso é uma meta verificável por auditoria, não uma promessa de ausência de erro editorial ou técnico.

Sempre que houver impedimento: comunicar `BLOQUEADO`, evidência, causa, solução e se houve envio ao Metricool. Em caso de erro detectado **após** a publicação: comunicar `INCIDENTE DE CONFORMIDADE`, link público, regra violada, risco, ação proposta e preservação do histórico. Sem reparação silenciosa.

## Regra de continuidade: duas tentativas por pauta e substituição obrigatória (25/11/2026)

Aplicar o procedimento de seleção e recuperação descrito em [metricool-extraordinarios.md](./metricool-extraordinarios.md). Cada candidata admite uma primeira tentativa de preparação e, se houver falha recuperável específica da pauta, uma segunda tentativa documentada. Se a segunda falhar, descartar a candidata no ciclo e selecionar outra, mantendo os critérios de notoriedade, fotografia autêntica pertinente e direitos. Reexecutar o gate integralmente para cada novo pacote, sem reaproveitar aprovação nem hashes de outra candidata. Continuar até encontrar pacote integralmente aprovado dentro da execução disponível. Não trocar indefinidamente de assunto se a causa for sistêmica (conexão, permissões ou impossibilidade de concluir a segunda passagem editorial com evidências); registrar impedimento e solução. Não confundir tentativas de preparação com reenvios ao Metricool: qualquer estado remoto incerto exige reconciliação, não uma segunda criação. O validador permanece fail-closed e não há exceção para aprovações fictícias. Registrar tentativas e resultado final.

## Aprovação final autônoma — contrato v2

A aprovação editorial final dos novos extraordinários é delegada pelo usuário ao ChatGPT, sem aprovação humana individual. A segunda passagem de revisão é separada da produção, mas não constitui revisão independente por outra pessoa. O gate mantém o veto determinístico e a auditoria posterior permanece somente leitura. O campo obrigatório é `editorial_review` (não `human_review`):

- `reviewer_type`: `assistant`; `reviewer`: identificação explícita do ChatGPT; `decision`: `APPROVED`; `checked_at`: ISO com fuso; `evidence_url`: URL HTTPS para registro concreto.
- Flags obrigatórias verdadeiras somente após verificação efetiva: `facts_checked`, `rights_evidence_checked`, `subject_match_checked`, `visual_mobile_checked`, `caption_checked`, `dedupe_checked`, `editorial_appeal_checked`, `authenticity_checked`.
- `findings`: objeto com observação específica para cada flag, remetendo às evidências reais; afirmações vagas não constituem prova editorial. `reviewed_media_sha256`: lista ordenada dos SHA-256 de todas as lâminas finais; `reviewed_caption_sha256`: SHA-256 do texto UTF-8 exato de `caption`.
- Ausência de revisão/observação, decisão negativa, revisão vencida ou alteração da arte/legenda implica bloqueio; não declarar uma aprovação humana que não ocorreu. Aprovação anterior ao conteúdo final não é suficiente.

A v1 fica preservada para registros históricos, inclusive BABYMETAL. Para novas submissões, usar exclusivamente a v2 e revalidar o pacote. O nome deste documento e a rotina CI existentes são mantidos para compatibilidade de links; a versão declarada é que determina a política. Nenhuma alteração nas rotinas regulares.
