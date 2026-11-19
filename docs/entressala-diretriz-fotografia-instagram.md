# ENTRESSALA — Diretriz de fotografia para Instagram
**Versão:** 2026-11-18  
**Status:** diretriz editorial aprovada para novas criações automáticas a partir de 23/11/2026; não autoriza reenviar/editar posts históricos ou dispensar verificações de direitos.

## Princípio
O Instagram da ENTRESSALA é a extensão visual de uma revista cultural, não um catálogo de pôsteres tipográficos. Fotografias autênticas e relevantes devem ser predominantes. Como padrão, **ao menos 80% dos slides de cada carrossel devem conter imagens fotográficas reais**, idealmente um registro do próprio evento, artista, obra, cena ou espaço noticiado. A fotografia deve dominar a composição; design e tipografia organizam a informação.

## Ordem de preferência das imagens (novas publicações a partir de 23/11)
1. Fotografia específica e impactante do evento/obra/espetáculo/artista, com licença ou autorização válida para Instagram.
2. Fotografia oficial de divulgação visualmente forte, desde que o titular autorize explicitamente a republicação.
3. Outra fotografia AUTÊNTICA do mesmo artista/companhia, inédita na ENTRESSALA; se de arquivo, indicar **FOTO DE ARQUIVO** e contexto correto.
4. **Cartaz oficial da atração**, somente como alternativa quando não houver foto adequada, com permissão/licença verificável para republicação no Instagram e visual de alta qualidade.
5. Fotografia de equipamento cultural apenas quando o equipamento/local for realmente a atração ou assunto do slide; nunca como substituta genérica de uma apresentação.

**Proibidas em novos posts:** fotografias ou cartazes genéricos, imagens criadas artificialmente para simular fatos, arte tipográfica de preenchimento, fotografias de evento/obra errada e qualquer ativo visual já usado em outro slide ou post. A mesma fotografia com novo corte, resolução, tratamento, título, nome de arquivo ou sobreposição continua sendo imagem REPETIDA. Cartaz oficialmente divulgado na internet não equivale a autorização de uso.

## Seleção de pautas
Relevância e verificação factual continuam prioritárias, mas a existência de boas imagens autênticas e utilizáveis é um critério editorial relevante. Priorizar eventos com imagens reais boas e direitos esclarecidos. Quando a foto ideal estiver indisponível, solicitar material/autorização ao assessor/organizador; se isso não for resolvido, considerar alternativa de pauta com mérito equivalente. Não escolher evento medíocre apenas porque tem fotos.

## Prioridade de alcance e composição do carrossel (aprovada em 18/11/2026)
O Instagram deve atrair novos seguidores e funcionar como marketing cultural premium. **Priorizar atrações de massa, grandes shows nacionais e internacionais, festivais, grandes musicais, espetáculos teatrais, grandes concertos e eventos com apelo amplo**, desde que presentes na última edição publicada da revista e confirmados em fontes oficiais. Um grande evento de São Paulo pode ter prioridade sobre evento local menor; relevância real, informação de serviço e direitos permanecem obrigatórios. A proposta editorial da revista continua independente.

**Meta de cinco posts semanais:** se não houver cinco pautas de grande alcance com imagens inéditas válidas, completar com atrações menores da mesma revista, nunca com pautas inventadas ou imagens genéricas. Em CARROSSEL MISTO, eventos de grande apelo vão na capa/início e atrações menores no final. Não preencher slides com a mesma fotografia do artista apenas para atingir quantidade. Imagens distintas do mesmo artista/produção são permitidas, mas só quando realmente diferentes e com direito de uso validado.

**Regra absoluta de unicidade:** uma imagem-fonte só pode ser usada UMA VEZ na história editorial do Instagram da ENTRESSALA. Consultar registros de posts antigos, a fila completa e `instagram/image-history.json`. Bloquear reutilização por identidade de arquivo/URL e, quando disponível, assinatura visual; não contornar renomeando ou recortando imagens. O acervo de 17–18/11 contém repetições históricas e não deve ser editado/republicado; as fontes ali utilizadas também ficam indisponíveis para novos posts.

**Data e cidade visíveis em TODOS os slides novos**, inclusive capa. Usar campos estruturados `date_label` (por exemplo, `20–22 NOV 2026`) e `city` (por exemplo, `SÃO PAULO`) para o renderizador exibir uma tarja legível, além dos campos já existentes. Usar `appeal_tier` com valores `cover`, `mass`, `secondary`; `mass` nunca vem depois de `secondary` na sequência. Quando houver datas ou cidades diversas na capa, indicar intervalo e cidades reais, sem sugerir falsamente que todos os eventos ocorrem em ambas as localidades.

**Mídias oficiais autorizadas:** fotografias oficiais próprias do artista/espetáculo também podem ser usadas em `asset_type:'authorized_photo'` quando houver permissão/licença explícita de republicação para Instagram; são preferíveis aos cartazes se visualmente fortes. Para fotos externas autorizadas usar o mesmo esquema de prova de autorização abaixo.

**Originais para cartaz autorizado:** `asset_type:'official_poster'`, `image_url` HTTPS direta do cartaz, `source_page_url` oficial, `permission_evidence_url` com comprovação legítima de licença/autorização, `instagram_use_allowed:true`, `license:'PERMISSAO EDITORIAL'` e titular identificado no campo de crédito. Para fotografias Commons manter `asset_type:'photo'`, `file` e dados CC já existentes; **cada slide novo também deve trazer** `depicts` (descrição fiel da imagem), `specific_to_subject:true` (somente quando imagem retrata o assunto) e `venue_is_subject:true` apenas quando a atração for o próprio local; não sinalizar como apto se licença, autoria, resolução ou autorização estiverem insuficientes. O renderizador deve recusar posts novos que violem as regras verificáveis.

## Direitos e créditos
**Crédito não equivale a permissão.** A disponibilidade de uma foto em site, press release, Instagram do artista, prefeitura ou revista não implica licença de republicação. Reutilizar quando houver licença aberta aplicável (verificar CC BY/CC BY-SA e todas as condições), licença de banco ou autorização verificável do titular que cubra o formato e o canal de publicação. Em imagens de obra de arte, verificar direitos sobre a obra representada, além da fotografia. Para CC BY-SA, cumprir também as condições de compartilhamento da adaptação; não usar licenças NC/ND sem avaliação específica.

**Diretriz de linguagem aprovada em 17/11/2026:** a legenda do Instagram deve parecer uma publicação cultural de revista, NÃO uma ficha técnica ou relatório jurídico. O assunto, a informação de serviço e a voz editorial ocupam quase todo o texto. O crédito fotográfico deve ser **discreto, natural, legível e curto**, sem parágrafos explicando direitos autorais, datas e licenças slide por slide. Evitar frases repetitivas do tipo "fotografias reais de arquivo, não registros da programação" e blocos intitulados "Créditos por slide". Informar "foto de arquivo" somente onde necessário para não induzir o leitor a erro, preferencialmente no próprio slide.

**Padrão de exibição:** crédito breve na margem do próprio slide, por exemplo `Foto: Raph_PH · arquivo` ou `Foto: Edison Marcon`. Quando vários autores exigirem menção também na legenda, preferir UMA linha final do tipo `Fotos: Raph_PH, Mike Kubacheck e Fernando Eduardo.` Sem lista numerada, sem preâmbulos didáticos. Não atribuir a um artista uma fotografia do local nem confundir arquivo com a edição atual.

**Registro de direitos independente da legenda:** manter autor, titular, fonte original, título da obra, URL e tipo de licença, link da licença, alterações feitas e comprovação de autorização no arquivo técnico `CREDITOS.md`/manifesto de cada carrossel, acessível publicamente quando exigido. Manter a atribuição efetiva e as indicações de licença/adaptação exigidas pela licença correspondente de forma compacta e adequada ao meio; nunca remover informação juridicamente obrigatória somente por preferência estética. Verificar se o crédito do slide + remissão pública ao registro técnico satisfaz as condições da licença concreta, ou usar imagem com autorização editorial mais adequada. Crédito não equivale a permissão. Marcar o criador quando pertinente.

## Direção de arte
- Exportação 1080 × 1350 px, proporção 4:5, boas margens para os cortes do Instagram.
- Foto ocupar cerca de 70–90% da superfície; tarja de leitura apenas onde necessário.
- Marca ENTRESSALA discreta e consistente, títulos curtos e **DATA + CIDADE sempre legíveis em cada slide novo**, inclusive capa. Local e preço/ingressos quando verificados.
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
Não criar posts retroativos, agendamentos nem alterar os registros históricos de `approved` ou `eligibleForScheduling` por causa desta diretriz. Aplicar a novas criações automáticas, que seguem verificações de direitos e fatos. Preservar Buffer Free, automação de 5 posts/semana e publicação somente após aprovações, fact-check e homologação de mídia.

**Fontes de referência jurídica e visual**  
Lei 9.610/1998, arts. 29 e 79: https://www2.camara.leg.br/legin/fed/lei/1998/lei-9610-19-fevereiro-1998-365399-normaatualizada-pl.html  
Manual do Senado: https://www12.senado.leg.br/manualdecomunicacao/guia-de-direitos-autorais  
Fotos CC: https://commons.wikimedia.org/wiki/File:Eddie_Vedder_2018.jpg ; https://commons.wikimedia.org/wiki/File:Racionais_MC%27s_(12197937363).jpg ; https://commons.wikimedia.org/wiki/File:Estação_Cultura_Campinas.jpg
