# ENTRESSALA — Rodada 2/5: preparação, pré-condições e testes isolados
**Estado:** PREPARADA, NÃO EXECUTADA / NÃO HOMOLOGADA  
**Data:** 23/11/2026  
**Dono do estado de estabilização:** [Plano Mestre](https://chatgpt.com/space/page_2577921888a08191aa9714f18b013546)  
**Contrato anterior:** [Política v1.0.0-rc1](./entressala-politica-editorial-visual-operacional-v1.0.0-rc1.md) e [JSON Schema](../instagram/contracts/entressala-post.v1.schema.json). Este roteiro não substitui nenhum dos dois.

## 0. Pré-condição imperativa: incidente C03 de 23/11
**Falha comprovada da cadeia regular:** a automação `ENTRESSALA — manhã: alertas e Instagram` (ID `6afdcc3c8f708190bfa5e39465a71d7a`) foi agendada para 23/11 09:00:30 BRT, iniciou 09:03:20 e terminou 09:05:32 com `recorded_status=completed`, `requires_user_action=false`. **Não gerou pauta**. Seu resultado alegou que o repositório só possuía a prévia/teste de 17/11 e não havia revista semanal regular publicada.

**Contraprova objetiva:** o GitHub `main` possui `edicoes/2026-11-19/index.html`, `edicoes/2026-11-19/dados/edicao-2026-11-19.json` com `id=EC-2026-11-19`, `status=PUBLISHED`, matérias `materias/blues`, `materias/folego`, `materias/opera`, `materias/hiphop` e `materias/pina`, além de manifesto de 5 reportagens; [Actions de verificação pública run 44539852483](https://github.com/luisedferrari-ctrl/primeira-fila-revista/actions/runs/44539852483) terminou `success` para a edição. O [monitor independente às 12h05](https://chatgpt.com/space/page_2577921888a08191aa9714f18b013546) confirmou a contradição e a ausência de post de 23/11 em `fila-editorial.json` e `fila-publicavel.json`.

**Causa comprovável:** falsa conclusão de ausência de edição canônica na etapa ChatGPT 09h. **Hipótese provável, não provada:** inspeção da branch editorial `entressala-piloto-2026-11` (contém prévia 17/11) no lugar de `main`, ou falha de resolver a fonte pública. Sem transcrição completa das ações internas da tarefa, não atribuir uma operação específica como certeza.

**Correção aplicada antes da R2:** atualizado SOMENTE o prompt da automação EXISTENTE ID `6afdcc3c8f708190bfa5e39465a71d7a`, acrescentando bloco prioritário `CORREÇÃO DE ORIGEM C03 — incidente comprovado em 23/11/2026`. Nova regra: localizar sempre última edição regular publicada em `main`, inspecionar `status=PUBLISHED` e artigos; confirmar Cloudflare ou smoke Actions do commit quando a ferramenta direta falhar; só depois abrir fila Instagram na branch piloto; nunca inferir que ausência de post significa ausência de revista; procurar outro artigo não vencido da mesma edição, sem inventar ou reutilizar foto; distinguir ausência comprovada de indisponibilidade de acesso. **A atualização foi gravada e relida, com habilitação, título e horário 09h preservados. Não houve run_now, criação retroativa ou mudança na fila.**

**Limite explícito da correção:** uma alteração de prompt corrige a instrução que produziu o falso negativo, mas **não prova que a tarefa futura gerará uma pauta nem que haverá publicação no Instagram**. C03 segue EM EXECUÇÃO/NÃO HOMOLOGADA. A execução agendada de **24/11/2026 09h** é a primeira oportunidade objetiva de validar a correção; o erro de 23/11 permanece no histórico e não pode ser substituído por post manual ou extraordinário. A execução Actions ~12h27 e Apps Script ~19h não devem ser forçadas para “completar” a data de 23/11.

### Prova de correção C03 (obrigatória antes de dizer RESOLVIDO)
| Passo | O que observar em 24/11 | Aceitação | Falha |
| --- | --- | --- | --- |
| C03-01 Fonte | Execução agendada no modo Chat consulta `main` e identifica `EC-2026-11-19`, salvo edição mais nova realmente publicada | ID, caminho do manifesto e prova da publicação coerentes | Retorna “só existe 17/11” ou usa prévia como fonte |
| C03-02 Pauta | Consulta `fila-editorial.json` na branch piloto somente depois de resolver edição; seleciona notícia/evento vigente e matéria única | Novo ID de 24/11, `source_edition_id`, `source_article_url`, fontes, licenças, service_items, editorial_scope | Ausente/URL de capa/assunto vencido |
| C03-03 Preflight | Confronta `image-history.json` incluindo Primavera Sound e fotos 17–18; sem reutilização | Fotos inéditas, direitos verificáveis e QA legível | Duplicidade, falta de foto/serviço/CTA → bloqueio seguro (não publicar) |
| C03-04 Render | GitHub Actions do workflow de imagens previsto 12h27 gera saída de prova para o ID do dia | SHA/arquivos válidos, fila publicável e histórico atualizados, sem placeholder | Workflows não executados/falha/arquivo inválido |
| C03-05 Publicador | Apps Script e Buffer à noite → Instagram | Recibo externo, URL pública real, 1 tentativa; monitor detecta transição | Sem acesso a logs = não verificável; Buffer queued ≠ Instagram published |

**C03-01 exige observação da tarefa realmente agendada**; um teste isolado manual, uma chamada a `run_now`, um post Metricool ou uma edição de prompt não podem satisfazê-lo.

## 1. Objetivos e escopo estrito da Rodada 2
1. **Proteger a descoberta da última edição:** testes reprodutíveis de fonte `main` versus branch editorial, com falso negativo bloqueado/diagnosticado, utilizando fixture local de `EC-2026-11-19` e um caso sem acesso ao Cloudflare mas com smoke de Actions recente.
2. **Consolidar validador comum em modo dry-run**, compatível com EVENTO, RADAR e NOTÍCIA CULTURAL, política v1.0.0-rc1 e JSON Schema, sem aceitar autoaprovação vinda de JSON.
3. **Auditar imagens/autorizações e dedupe** dos dois canais por URL original, SHA-256 e dHash 256 bits, preservando histórico; propor reserva atômica em R3, NÃO simular transação interplataformas agora.
4. **Inspecionar visualmente três prévias com fotografia real e direito comprovado:** uma de EVENTO, uma de RADAR e uma de NOTÍCIA, sem publicação, sem criação de post ativo e sem copiar estilos específicos de terceiros.
5. **Verificar falha segura e compatibilidade legada** antes de qualquer recomendação de integração, preservando a cadeia regular e extraordinária separadas.

**Fora de escopo na R2:** mudanças em `main`, Cloudflare, Apps Script implantado, Buffer, Metricool publicador, gatilhos, tarefas agendadas, distribuição da revista, arquivos existentes `fila-editorial.json`/`fila-publicavel.json`, fotos históricas, C01/C02 ou qualquer envio/post real. Não introduzir workflows por publicação nem alterá-los silenciosamente.

## 2. Sequência executável e critérios de aceite
### R2-A — Bootstrap / prova do incidente
- Capturar refs/SHAs atuais antes de testar. Rodar verificação **somente leitura** de `main` para IDs em `edicoes/AAAA-MM-DD`. Separar diretório de `previews/` e a branch Instagram. Associar `status=PUBLISHED` ao `EC-` e provar URL pública por smoke condizente.
- Fixture negativa: `entressala-piloto-2026-11` com apenas `edicoes/2026-11-17`; algoritmo deve continuar consultando `main`, **não** devolver “nenhuma edição”.
- Fixtures: HTTP direto indisponível + smoke verde; smoke antigo que não corresponde à nova edição; estrutura de edição incompleta; `status` draft; duas edições com datas diferentes; edição 26/11 presente sem deploy (NÃO escolhê-la); item vencido isolado mas outras pautas elegíveis.
- Saída: relatório de casos pass/fail, IDs, não sobrescrita, nenhuma gravação na fila.

### R2-B — Validação canônica do contrato
- Executar verificação de JSON Schema Draft 2020-12 para fixtures positivas EVENTO, RADAR e NEWS e negativas: ausência de `source_edition_id` no regular; NEWS com bilheteria fictícia; RADAR com data inventada; período passado; URL sem HTTPS; prova de direitos incompleta; CTA ausente; `service_index` inválido; notícia sem `source_url` em `factual_sources`/legenda.
- Checar distinção `publication_channel=regular|extraordinary`, `origin_id`, `story_id`, `angle_id`, `publication_dedupe_key`, `image_source_id`, hashes e QA rastreável. Origem de extraordinário NÃO herda exigência de edição regular.
- Corrigir como parte da R2 apenas falhas verificadas de schema e validador, sem inserir objeto novo nas filas de produção.
- Limitações conhecidas do schema a testar explicitamente: URL oficial HTTPS de domínio raiz, `city` versus `scope_label` em NEWS, formas de “LOCAL A CONFIRMAR”, autorização condicionada ao objeto real, vinculação de `service_index` ao tipo concreto e formatos diferentes de mídia. Schema isolado nunca prova licença ou imagem visualmente adequada.

### R2-C — Autenticidade, direitos e repetição
- Casos de dedupe: foto original idêntica com URL query diferente; renomeada; crop; resize; arquivo da mesma fonte em Buffer e Metricool; fotos visualmente parecidas mas de cenas distintas; arquivo usado na prévia histórica; fonte usada pelo Primavera Sound Metricool 22/11.
- Requerer registro de autor, titular, URL oficial de origem e prova de licença compatível com repost e adaptação no Instagram. Para CC BY-SA registrar adaptação e respectivas condições; para obra representada, verificar direitos de obra e de fotografia. Não aceitar licença presumida por simples divulgação ou crédito.
- Testar `visual_hashes={}` atual: deve ser declarado inventário visual incompleto e nunca chamado de cobertura retroativa integral. Não inventar hashes de fontes originais não recuperadas.
- Gate de 80% fotografias reais nos slides quando aplicável; poster/obra reproduzida não inflaciona contagem.

### R2-D — Três provas visuais reais, em isolamento
- Usar três fotografias públicas legitimamente licenciadas ou material próprio/autorizado, **sem reusar** fontes listadas em `instagram/image-history.json`. Guardar prova de autoria, contexto, direitos e transformação; se fotografia adequada não existir, marcar fixture bloqueada, nunca substituir por foto genérica.
- Gerar cards `1080×1350` apenas em diretório de teste não observado pelo publicador. Inspecionar original, 360 px e 180 px em cada tema EVENTO/RADAR/NEWS. Fazer QA humano de manchete (1 s), dados úteis (3 s), legibilidade, safe area, contraste ≥4.5:1 quando pertinente, crédito, contexto “arquivo”, fontes e CTA, sem cobertura de rostos/obras.
- Documentar para cada card: source ID/URL, licença/permissão, SHA, crop, largura/altura, miniaturas verificadas, nota por critério, resultado APROVADO ou REPROVADO e motivo.
- Teste negativo visual: headline longa, endereço extenso, ingressos ainda não divulgados, fonte com domínio longo, crédito no limite inferior, foto com rosto no terço inferior, gradiente insuficiente, 2 editorias em um carrossel.

### R2-E — QA CI e regressão
- Preservar os 37 testes offline de `instagram/test_image_policy.py`, adicionando testes novos somente para erros reais. Reportar números antes/depois e execuções CI com SHA específico.
- Sem rede, sem tokens, sem chamadas ao Buffer/Metricool em testes de erro. Se usar dados da internet, somente leitura para checagem de licença e status, nunca como bypass.
- Confirmação de que zero arquivos antigos de `instagram/assets`, `image-history.json`, filas e `main` sofreram modificação por testes.
- Inspecionar diff, saída CI, URL de evidência e reversibilidade; falhas bloqueiam promoção e são registradas no Plano Mestre.

## 3. Gates de passagem e dependências temporais
| Gate | Evidência | Decisão |
| --- | --- | --- |
| G0 C03 fonte | Prompt corrigido e relido na tarefa existente, 23/11 | **CONFIGURADO**; NÃO homologado por execução |
| G1 C03 agendada | 24/11 09h prova de descoberta `main` sem falso negativo | NECESSÁRIO para declarar correção operante, mas não bloquear preparo técnico isolado |
| G2 contrato | Todos casos positivos e negativos passam na branch isolada | Exigido para R2 concluída |
| G3 imagens reais | 3 prévias reais, prova de direitos e QA visual móvel | Exigido para R2 concluída |
| G4 estabilidade | 37 testes anteriores verdes + novos, fila/histórico/main intocados | Exigido para R2 concluída |
| G5 C05 preservada | Execução de 26/11 08h permanece com gatilho/produção inalterados | Exigido sempre; não condicionar C05 a R2 |

**Permissão para começar trabalho R2 em isolamento:** G0 e existência deste roteiro. **Proibição de homologação R2:** enquanto G2–G4 faltarem. **Proibição de afirmar correção C03 validada:** até G1 (e, para publicação regular, até C03-05). R3 só pode incorporar adaptadores e dedupe após resultados documentados de R2, sem publicadores não inspecionados.

## 4. Registro do que esta preparação realmente fez
- Revisou o incidente pelo resultado de automação 09h, resultado do monitor 12h05 e fontes GitHub `main`.
- Atualizou o prompt da automação existente às 09h e releu o agendamento; não executou a tarefa fora de hora.
- Criou somente este documento de preparação na branch editorial; nenhum teste de mídia, CI, revisão jurídica completa ou publicação foi executado pela preparação.
- Riscos: instrução textual pode não ser obedecida na execução futura; acesso incompleto ao Apps Script em produção/Buffer; 23/11 sem post e sem prova ponta a ponta; cron 12h27 e publicador da noite não devem receber conteúdo fabricado.
- Reversão do ajuste da automação, se necessário: restaurar apenas o texto anterior retirando exatamente o bloco inicial `CORREÇÃO DE ORIGEM C03 ... FIM DA CORREÇÃO C03.`, mantendo todo o prompt original, ID e agenda. Reverter este arquivo por commit pontual, sem resetar a branch ou alterar C01/C02.
- Plano Mestre: registrar só o incidente, evidência `main`, prompt corrigido, status não homologado, documento criado/commit e gate de 24/11.

**Próxima ação real sem intervenção manual:** observar a tarefa das 9h de 24/11, conferir dados na branch editorial e resultado do renderizador/publicador em seus próprios horários; nunca apresentar o resultado de hoje ou documentação como prova substituta.
