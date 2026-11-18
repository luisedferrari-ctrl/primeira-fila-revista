# ENTRESSALA — Diretriz de fotografia para Instagram
**Versão:** 2026-11-17  
**Status:** diretriz editorial para a branch piloto; não autoriza publicação de nenhum post.

## Princípio
O Instagram da ENTRESSALA é a extensão visual de uma revista cultural, não um catálogo de pôsteres tipográficos. Fotografias autênticas e relevantes devem ser predominantes. Como padrão, **ao menos 80% dos slides de cada carrossel devem conter imagens fotográficas reais**, idealmente um registro do próprio evento, artista, obra, cena ou espaço noticiado. A fotografia deve dominar a composição; design e tipografia organizam a informação.

## Ordem de preferência das imagens
1. Fotografia específica do evento/obra/exposição/produção em pauta, licenciada ou autorizada para o uso em Instagram.
2. Fotografia oficial de divulgação, desde que seu titular tenha concedido o uso editorial nas redes sociais.
3. Retrato ou fotografia real de arquivo do artista/companhia, com indicação visível de **FOTO DE ARQUIVO** e ano/local quando conhecido.
4. Fotografia real do equipamento cultural/venue, claramente descrita como **FOTO DO LOCAL** (não como imagem da edição ou da obra).
5. Arte tipográfica original apenas como exceção justificada (sem retratar ficticiamente eventos reais).

Não produzir imagens sintéticas de artistas, apresentações, plateias ou instalações e apresentá-las como documentais. Não copiar cartazes de produtores como padrão visual. Não usar foto genérica de banco de imagens para fingir que representa um evento.

## Seleção de pautas
Relevância e verificação factual continuam prioritárias, mas a existência de boas imagens autênticas e utilizáveis é um critério editorial relevante. Priorizar eventos com imagens reais boas e direitos esclarecidos. Quando a foto ideal estiver indisponível, solicitar material/autorização ao assessor/organizador; se isso não for resolvido, considerar alternativa de pauta com mérito equivalente. Não escolher evento medíocre apenas porque tem fotos.

## Direitos e créditos
**Crédito não equivale a permissão.** A disponibilidade de uma foto em site, press release, Instagram do artista, prefeitura ou revista não implica licença de republicação. Reutilizar quando houver licença aberta aplicável (verificar CC BY/CC BY-SA e todas as condições), licença de banco ou autorização verificável do titular que cubra o formato e o canal de publicação. Em imagens de obra de arte, verificar direitos sobre a obra representada, além da fotografia. Para CC BY-SA, cumprir também as condições de compartilhamento da adaptação; não usar licenças NC/ND sem avaliação específica.

**Diretriz de linguagem aprovada em 17/11/2026:** a legenda do Instagram deve parecer uma publicação cultural de revista, NÃO uma ficha técnica ou relatório jurídico. O assunto, a informação de serviço e a voz editorial ocupam quase todo o texto. O crédito fotográfico deve ser **discreto, natural, legível e curto**, sem parágrafos explicando direitos autorais, datas e licenças slide por slide. Evitar frases repetitivas do tipo "fotografias reais de arquivo, não registros da programação" e blocos intitulados "Créditos por slide". Informar "foto de arquivo" somente onde necessário para não induzir o leitor a erro, preferencialmente no próprio slide.

**Padrão de exibição:** crédito breve na margem do próprio slide, por exemplo `Foto: Raph_PH · arquivo` ou `Foto: Edison Marcon`. Quando vários autores exigirem menção também na legenda, preferir UMA linha final do tipo `Fotos: Raph_PH, Mike Kubacheck e Fernando Eduardo.` Sem lista numerada, sem preâmbulos didáticos. Não atribuir a um artista uma fotografia do local nem confundir arquivo com a edição atual.

**Registro de direitos independente da legenda:** manter autor, titular, fonte original, título da obra, URL e tipo de licença, link da licença, alterações feitas e comprovação de autorização no arquivo técnico `CREDITOS.md`/manifesto de cada carrossel, acessível publicamente quando exigido. Manter a atribuição efetiva e as indicações de licença/adaptação exigidas pela licença correspondente de forma compacta e adequada ao meio; nunca remover informação juridicamente obrigatória somente por preferência estética. Verificar se o crédito do slide + remissão pública ao registro técnico satisfaz as condições da licença concreta, ou usar imagem com autorização editorial mais adequada. Crédito não equivale a permissão. Marcar o criador quando pertinente.

## Direção de arte
- Exportação 1080 × 1350 px, proporção 4:5, boas margens para os cortes do Instagram.
- Foto ocupar cerca de 70–90% da superfície; tarja de leitura apenas onde necessário.
- Marca ENTRESSALA discreta e consistente, títulos curtos, data, local e preço/ingressos quando verificados.
- Creditar no próprio slide e no registro de fonte; não ocultar o autor sob UI, crops ou legendas minúsculas.
- Não aplicar filtros que deturpem a obra ou imagem. Crop apenas quando os termos permitirem, com registro da adaptação.
- Não apresentar fotos de edição anterior como edição de 2026; escrever `Foto de arquivo: artista em [ano]`.

## Dados mínimos por ativo (na mesma fonte JSON da revista)
`source_page_url`, `photo_url`, `photographer`, `copyright_holder`, `license_or_permission`, `license_url`, `instagram_use_allowed`, `credit_line`, `depicts`, `shot_date`, `is_archival`, `modifications`, `fact_checked_at`, `rights_checked_at`, `approved`, `eligibleForScheduling`.

Por padrão `approved:false` e `eligibleForScheduling:false`. Só virar `true` após aprovação dos dois primeiros posts e verificação completa de licenças/fatos/legibilidade.

## Revisão dos dois primeiros posts
**Post 1 — Apresentação da marca, 5 slides:** todos fotografias reais de cidades, auditórios, museus e vida cultural da região. Um slide por ideia: (1) capa com foto real e ENTRESSALA; (2) Indaiatuba e Campinas; (3) música e palco; (4) exposições, teatro, cinema e outros programas; (5) proposta editorial e revista web. Não anunciar a revista como publicada antes da homologação.

**Post 2 — Seleção cultural, 6 slides:** capa fotográfica + fotografias pertinentes a cada pauta + serviço, com preferência por eventos de 20–22/11/2026. Candidatos documentados: Best of Blues and Rock (foto real de Eddie Vedder, identificada como arquivo e sob CC BY 2.0), Campinas Hip Hop Festival (foto real de Edi Rock, identificada como arquivo e sob CC BY 2.0), exposições da Pina Estação (foto do local, não da mostra), dança no Castro Mendes (foto real do local ou material autorizado da produção), resumo de serviço. Para cada candidatura revalidar datas, ingresso, direitos e adequação do ativo. Não apresentar imagens ilustrativas como registros específicos do evento.

## Operação
Não criar posts publicados, agendamentos nem alterar os registros de `approved` ou `eligibleForScheduling` por causa desta diretriz. Preservar Buffer Free, automação de 5 posts/semana e publicação somente após aprovações, fact-check e homologação de mídia.

**Fontes de referência jurídica e visual**  
Lei 9.610/1998, arts. 29 e 79: https://www2.camara.leg.br/legin/fed/lei/1998/lei-9610-19-fevereiro-1998-365399-normaatualizada-pl.html  
Manual do Senado: https://www12.senado.leg.br/manualdecomunicacao/guia-de-direitos-autorais  
Fotos CC: https://commons.wikimedia.org/wiki/File:Eddie_Vedder_2018.jpg ; https://commons.wikimedia.org/wiki/File:Racionais_MC%27s_(12197937363).jpg ; https://commons.wikimedia.org/wiki/File:Estação_Cultura_Campinas.jpg
