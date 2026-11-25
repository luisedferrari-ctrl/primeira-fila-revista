# Incidente de preflight — ENTRESSALA-EXTRA-20261125-CLIFF-BOOTH
Data: 25/11/2026, 16h16 BRT.
Política: entressala-metricool-extra-2026-11-25-v1.
Estado: BLOCKED. Não enviado ao Metricool, sem agendamento, sem publicação.

## Pauta
As Novas Desventuras de Cliff Booth: estreia IMAX em 25/11/2026; Campinas e Curitiba no circuito brasileiro restrito, conforme assessoria do IMAX Brasil citada pelo Omelete. Streaming em 23/12. Fontes: https://www.netflix.com/tudum/articles/david-fincher-new-film-release-date e https://www.omelete.com.br/filmes/cliff-booth-quais-salas-passarao-no-brasil.

## Evidência dos impedimentos
1. Download local do original indisponível (falha DNS). Execução isolada GitHub Actions 45683468759, job 139449769741, falhou em 19:16:05 UTC: requests.exceptions.HTTPError: 429 Client Error: Too Many Requests para https://upload.wikimedia.org/wikipedia/commons/4/4c/Brad_Pitt_2019_by_Glenn_Francis.jpg.
2. Gate local, código blob 982de1e0d1c24cf72232df1d2d5786922e86b2bc, executado em 2026-11-25T16:16:37.615820-03:00, saída 2, 7 ocorrências, approval_digest null, manifesto SHA-256 60f720fed95a896b02fc712535dd17a134cf00e5ff9ebc89914743f77827f18d. Códigos: MEDIA_SOURCE_MISSING, MEDIA_URL_MISSING, MEDIA_UNAVAILABLE, VISUAL_TEXT_MISSING, CTA_MISSING, REVIEW_MISSING, REVIEW_STALE.
3. Marca 8230360 e Instagram entressala_ conectados; nenhum post Cliff Booth encontrado no intervalo 18/11 a 02/12. Histórico conhecido não inclui a foto-fonte, mas revisão de duplicatas completa permanece pendente.
4. Foto escolhida: Glenn Francis / PacificProDigital.com, 22/07/2019, pré-estreia do filme anterior, CC BY-SA 4.0: https://commons.wikimedia.org/wiki/File:Brad_Pitt_2019_by_Glenn_Francis.jpg. Não há bytes do arquivo disponíveis para o preflight; não se alegou hash ou aprovação.

## Correção obrigatória
Obter original autorizado após liberação do fornecedor ou por upload do arquivo original, renderizar JPEG 1080x1350, inspecionar arte final e documentar atribuição e ShareAlike; realizar revisão humana independente com evidência; repetir verificações remotas, preflight e hashes antes de qualquer agendamento. Não contornar o bloqueio nem usar foto sintética. Não editar revista, fila, regular, Buffer ou posts históricos.

Execução: https://github.com/luisedferrari-ctrl/primeira-fila-revista/actions/runs/45683468759
