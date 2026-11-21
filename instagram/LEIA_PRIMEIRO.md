# ENTRESSALA — publicação de hoje e rotina sem data de fim

Este pacote usa as ferramentas já conectadas: GitHub (hospedagem das fotos editadas), Google Apps Script "ENTRESSALA - Publicador Instagram" (token BUFFER_API_KEY já salvo) e Buffer Free (@entressala_).

## O que a automação FAZ

- A rotina editorial alimenta `instagram/fila-editorial.json` com candidatos: **um por dia útil**, sempre com fontes oficiais e fotos reais cuja licença permite republicação. Não substitui notícias por outras não verificadas.
- GitHub Actions executa `instagram/render_social.py` diariamente, obtém as fotos originais de Wikimedia Commons, verifica que são imagens e transforma-as em cards 4:5 com **crédito em cada slide**. Publica os JPEGs somente na branch `entressala-piloto-2026-11`. Se a foto falhar, não gera manifesto pronto.
- O Google Apps Script lê o manifesto `instagram/fila-publicavel.json` e publica diretamente pelo Buffer apenas posts `approved=true`, `eligibleForScheduling=true`, `assetsReady=true`, com verificação recente, válida e foto alcançável. Há trava contra repetição por ID.
- A frequência pretendida é de 5 posts/semana e a programação **não tem data de término**; a execução é **condicionada** à disponibilidade de pautas com direitos e fatos checados. Não inventa matéria nem repete evento vencido para preencher 5.

## Passo a passo inicial (17/11/2026)

1. Abra **GitHub Actions** em `https://github.com/luisedferrari-ctrl/primeira-fila-revista/actions/workflows/entressala-imagens.yml`, clique **Run workflow**. O workflow deve existir em `main`; ele constrói os slides na branch editorial sem alterar a revista pública.
2. Confira se a execução ficou verde em Actions. Confira as fotos geradas e créditos em `https://github.com/luisedferrari-ctrl/primeira-fila-revista/tree/entressala-piloto-2026-11/instagram/assets/ENTRESSALA-IG-20261117-LANCAMENTO`.
3. Abra `https://script.google.com/home` -> o projeto **ENTRESSALA - Publicador Instagram**, não o projeto do distribuidor de e-mail. Crie um novo arquivo .gs e cole `ENTRESSALA_Publicador_V3.gs` da branch piloto. Não substitua o código que passou no teste antigo. O token **BUFFER_API_KEY** permanece em Script Properties (não copie/token no chat).
4. Selecione a função `entressalaV3Diagnostico` e clique **Executar**. Confira o log: `NENHUM POST PUBLICADO NESTE TESTE` e cinco imagens públicas.
5. Se ainda for **17/11/2026**, selecione `entressalaV3PublicarHoje` e clique **Executar** uma única vez. Confira o `post.id` retornado no log; veja o status em Buffer e a publicação no Instagram. Criar post no Buffer não equivale à publicação comprovada no Instagram.
6. Para o segundo post, selecione `entressalaV3AgendarSegundo`; ele agenda para **18/11/2026, 19h BRT**. Confira a fila Buffer e posteriormente a publicação.
7. Selecione `entressalaV3InstalarRotina` uma vez. Ela mantém o gatilho **todos os dias, por volta de 19h BRT, sem data fim**. O script só envia **segunda a sexta** e exige pauta válida. O gatilho não reinstala os triggers do projeto do e-mail e não toca em tarefas antigas do projeto Instagram.
8. A automação editorial recorrente no ChatGPT deve atualizar a fonte da branch a cada dia útil; a geração de imagens deve rodar antes do horário de publicação. Se nenhum candidato passar na auditoria, o script **não publica** e envia um aviso de exceção, sem preencher a fila com invenções.

## Buffer Free

O plano Free aceita **10 posts agendados por canal na fila ao mesmo tempo**, não 10 publicações totais ou mensais. Este script publica diretamente um post aprovado por dia útil e não depende de manter centenas de agendamentos. Eventualmente pode adaptar-se para antecedência de 1-2 dias caso os testes confirmem funcionamento estável. API Free dispõe de limite por período, adequado a 1 post/dia.

## Controles de segurança

- Nunca colocar `BUFFER_API_KEY` em GitHub. Sempre somente Script Properties.
- Nunca rodar `instalarUmaVez` do projeto e-mail.
- Para interromper novas publicações: executar `entressalaV3PausarRotina` no projeto Instagram.
- Se uma tentativa der erro após enviar ao Buffer, a trava por ID impede retry automático. Verifique a fila antes de qualquer intervenção manual.
- Confirmar estado de cada publicação na conta oficial `https://www.instagram.com/entressala_/`.
- Fotos sob CC BY-SA têm obrigação de manutenção de licença compatível nas derivações: cada slide e arquivo de crédito explicita autoria/licença/recorte.

## Observação sobre estado de entrega

Este pacote contém **código/manifestos**, não comprovação de execução futura. Não afirmar que a publicação ou a automação operaram até que os logs e a publicação real sejam vistos.