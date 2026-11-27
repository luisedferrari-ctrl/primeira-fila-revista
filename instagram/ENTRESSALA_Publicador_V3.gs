/**
 * ENTRESSALA — Publicador Instagram V3 (projeto separado do distribuidor de e-mail)
 * 1) Primeiro execute entressalaV3Diagnostico.
 * 2) Execute entressalaV3PublicarHoje UMA VEZ, ainda em 17/11/2026.
 * 3) Execute entressalaV3AgendarSegundo UMA VEZ (para 18/11/2026, 19h BRT).
 * 4) Execute entressalaV3InstalarRotina SEM DATA DE FIM.
 *
 * Imagens e legendas: manifesto auditável no GitHub, somente fotos reais com direitos.
 * Secret BUFFER_API_KEY deve continuar em Script Properties. Não o cole no código.
 * Nunca execute este arquivo no projeto de distribuição da revista por e-mail.
 */
const E_V3 = {
  TZ: 'America/Sao_Paulo',
  BUFFER: 'https://api.buffer.com',
  CHANNEL: '6afca93cece6dfde5ffd0832',
  FEED: 'https://raw.githubusercontent.com/luisedferrari-ctrl/primeira-fila-revista/entressala-piloto-2026-11/instagram/fila-publicavel.json',
  LAUNCH: 'ENTRESSALA-IG-20261117-LANCAMENTO',
  SECOND: 'ENTRESSALA-IG-20261118-FIMDESEMANA',
  ALERT_EMAIL: 'luisedferrari@gmail.com',
  KEY_PREFIX: 'ENTRESSALA_V3_POST_',
  ENABLED: 'ENTRESSALA_V3_ENABLED',
  HANDLER: 'entressalaV3RotinaDiaria'
};

function eV3Props_() { return PropertiesService.getScriptProperties(); }
function eV3Hoje_() { return Utilities.formatDate(new Date(), E_V3.TZ, 'yyyy-MM-dd'); }
function eV3Token_() {
  const t = eV3Props_().getProperty('BUFFER_API_KEY');
  if (!t) throw new Error('BUFFER_API_KEY não encontrado em Propriedades do Script. NUNCA envie o token pelo chat.');
  return t;
}
function eV3Feed_() {
  const url = E_V3.FEED + '?cache=' + Math.floor(Date.now() / 60000);
  const r = UrlFetchApp.fetch(url, {muteHttpExceptions:true, followRedirects:true});
  if (r.getResponseCode() !== 200) throw new Error('Manifesto não disponível (' + r.getResponseCode() + '). Execute antes o renderizador do GitHub Actions.');
  const data = JSON.parse(r.getContentText('UTF-8'));
  if (data.brand !== 'ENTRESSALA' || data.channel !== '@entressala_' || !Array.isArray(data.posts)) throw new Error('Manifesto inesperado; nenhum envio.');
  return data;
}
function eV3Encontrar_(id) {
  const p = eV3Feed_().posts.filter(x=>x.id===id)[0];
  if (!p) throw new Error('Post ausente do manifesto: ' + id);
  return p;
}
function eV3VerificarMidias_(post) {
  if (!post.approved || !post.eligibleForScheduling || post.assetsReady!==true) throw new Error('Post não autorizado ou imagens não renderizadas: ' + post.id);
  if (!post.verified_at || !post.publish_local_date || !post.valid_through_local_date || !post.factual_sources?.length) throw new Error('Sem fontes, prazo ou revisão: ' + post.id);
  if (post.publish_local_date >= '2026-11-19') {
    const edition=String(post.source_edition_id || '');
    const article=String(post.source_article_url || '');
    const prefix='https://primeira-fila-revista.pages.dev/edicoes/'+edition.slice(3)+'/materias/';
    if (!/^EC-\d{4}-\d{2}-\d{2}$/.test(edition) || !article.startsWith(prefix) || article===prefix) {
      throw new Error('Post sem vínculo verificável com a matéria da edição regular: ' + post.id);
    }
    if (post.date_city_visible !== true || post.image_uniqueness_checked !== true ||
        (post.publish_local_date >= '2026-11-23' && post.newsfirst_option_b_checked !== true)) {
      throw new Error('Gates do renderizador ausentes: ' + post.id);
    }
  }
  const nowLocal = eV3Hoje_();
  if (nowLocal > post.valid_through_local_date) throw new Error('Prazo factual vencido: ' + post.id);
  if (post.verified_at > nowLocal) throw new Error('Data de verificação futura: ' + post.id);
  // Conteúdo de eventos datados: verificar atualização recente, não publicar texto envelhecido.
  const days = Math.floor((Date.parse(nowLocal+'T12:00:00Z') - Date.parse(post.verified_at+'T12:00:00Z')) / 86400000);
  if (post.kind !== 'lancamento' && days > 2) throw new Error('Verificação dos eventos tem mais de 48 horas: ' + post.id);
  if (!Array.isArray(post.images) || post.images.length < 1 || post.images.length > 20) throw new Error('Quantidade de imagens inválida: ' + post.id);
  if (post.images.some(x=>!/^https:\/\/raw\.githubusercontent\.com\/luisedferrari-ctrl\/primeira-fila-revista\/entressala-piloto-2026-11\/instagram\/assets\//.test(x))) throw new Error('URL da imagem fora do diretório controlado.');
  if (!post.caption || post.caption.length > 2100) throw new Error('Legenda ausente ou longa demais; créditos devem constar na legenda.');
}
function eV3ConferirImagem_(url) {
  // Apps Script UrlFetchApp aceita GET, POST, PUT, PATCH e DELETE, mas NÃO HEAD.
  // Range minimiza o volume transferido quando o servidor aceita respostas parciais.
  const r = UrlFetchApp.fetch(url, {
    method: 'get',
    headers: {'Range': 'bytes=0-1023'},
    muteHttpExceptions: true,
    followRedirects: true
  });
  const status = r.getResponseCode();
  if (status !== 200 && status !== 206) {
    throw new Error('Imagem pública indisponível: HTTP ' + status + ' ' + url);
  }
  const headers = r.getHeaders();
  const contentType = String(headers['Content-Type'] || headers['content-type'] || '').toLowerCase();
  if (!contentType.startsWith('image/')) {
    throw new Error('A URL não retornou uma imagem (Content-Type: ' + contentType + '): ' + url);
  }
}
function entressalaV3Diagnostico() {
  eV3Token_();
  const data=eV3Feed_();
  const launch=data.posts.filter(p=>p.id===E_V3.LAUNCH)[0];
  if (!launch) throw new Error('O primeiro post ainda não foi renderizado.');
  eV3VerificarMidias_(launch);
  launch.images.forEach(eV3ConferirImagem_);
  Logger.log('OK: BUFFER_API_KEY presente, canal '+E_V3.CHANNEL+', '+launch.images.length+' fotos reais publicamente disponíveis. NENHUM POST PUBLICADO NESTE TESTE.');
  return {postId:launch.id, images:launch.images.length, note:'DIAGNOSTICO APENAS — não publica'};
}
function eV3Buffer_(q) {
  const resp=UrlFetchApp.fetch(E_V3.BUFFER, {
    method:'post',
    contentType:'application/json',
    payload:JSON.stringify({query:q}),
    headers:{Authorization:'Bearer '+eV3Token_()},
    muteHttpExceptions:true
  });
  const raw=resp.getContentText('UTF-8');
  if (resp.getResponseCode()!==200) throw new Error('Buffer HTTP '+resp.getResponseCode()+': '+raw.slice(0,380));
  const j=JSON.parse(raw);
  if (j.errors?.length) throw new Error('Buffer GraphQL: '+JSON.stringify(j.errors).slice(0,700));
  const action=j.data?.createPost;
  if (!action?.post?.id) throw new Error('Buffer recusou post: '+(action?.message||raw.slice(0,380)));
  return action.post;
}
function eV3LegendaComCreditos_(post) {
  let caption = String(post.caption || '');
  if (post.publish_local_date >= '2026-11-24') {
    const url = String(post.credits_document || '');
    const expected = 'https://github.com/luisedferrari-ctrl/primeira-fila-revista/blob/entressala-piloto-2026-11/instagram/assets/' + post.id + '/CREDITOS.md';
    if (url !== expected) throw new Error('Documento de créditos ausente ou fora do post.');
    if (!caption.includes(url)) caption += '\n\nCréditos e licença: ' + url;
  }
  if (!caption || caption.length > 2200) throw new Error('Legenda final excede o limite ou está vazia.');
  return caption;
}
function eV3CriarPost_(post, mode, dueAt, automaticLocalDate) {
  const caption = eV3LegendaComCreditos_(post);
  eV3VerificarMidias_(post);
  post.images.forEach(eV3ConferirImagem_);
  const lock=LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const key=E_V3.KEY_PREFIX+post.id;
    const dayKey=automaticLocalDate ? 'ENTRESSALA_V3_DIA_'+automaticLocalDate : '';
    const props=eV3Props_();
    if (dayKey && props.getProperty(dayKey)) {
      Logger.log('BLOQUEADO: a oportunidade automática desta data já foi utilizada. '+props.getProperty(dayKey));
      return {skipped:true, previous:props.getProperty(dayKey)};
    }
    if (props.getProperty(key)) {
      if (dayKey) props.setProperty(dayKey,'POST JA TENTADO '+post.id);
      Logger.log('BLOQUEADO: já houve tentativa de envio deste post, verifique Buffer. '+props.getProperty(key));
      return {skipped:true, previous:props.getProperty(key)};
    }
    // Marcar tentativas por ID e DATA ANTES da chamada: resposta incerta jamais causa envio duplicado.
    const attempt='TENTATIVA '+new Date().toISOString();
    props.setProperty(key,attempt);
    if (dayKey) props.setProperty(dayKey,attempt+' POST '+post.id);
    const assets='['+post.images.map(url=>'{ image: { url: '+JSON.stringify(url)+' } }').join(',')+']';
    const validMode=(mode==='shareNow'||mode==='customScheduled') ? mode : 'addToQueue';
    const due=dueAt ? ', dueAt: '+JSON.stringify(dueAt) : '';
    const query='mutation EntressalaCreate { createPost(input: {'+
      'text: '+JSON.stringify(caption)+','+
      'channelId: '+JSON.stringify(E_V3.CHANNEL)+','+
      'schedulingType: automatic, mode: '+validMode+due+','+
      'assets: '+assets+','+
      'metadata: { instagram: { type: post, shouldShareToFeed: true } }'+
      '}) { ... on PostActionSuccess { post { id status dueAt } } ... on MutationError { message } } }';
    const result=eV3Buffer_(query);
    eV3Props_().setProperty(key,'ID '+result.id+' STATUS '+(result.status||'indefinido')+' DUE '+(result.dueAt||'sem-horario'));
    if (result.status === 'error') throw new Error('Buffer criou o registro, mas rejeitou a publicação. ID '+result.id+'. Verificar conexão do canal e recuperar o MESMO post no Buffer; não criar duplicata.');
    Logger.log('BUFFER CONFIRMOU CRIACAO: '+JSON.stringify(result)+'; PUBLICACAO NO INSTAGRAM AINDA PRECISA SER VERIFICADA.');
    return result;
  } catch(e) {
    Logger.log('FALHA / ENVIO INDETERMINADO. NÃO REPETIR: '+e.message);
    throw e;
  } finally { lock.releaseLock(); }
}
function entressalaV3PublicarHoje() {
  if (eV3Hoje_()!=='2026-11-17') throw new Error('Este comando é exclusivo de 17/11/2026. A data mudou: não publicar edição vencida.');
  return eV3CriarPost_(eV3Encontrar_(E_V3.LAUNCH),'shareNow',null);
}
function entressalaV3AgendarSegundo() {
  const dia=eV3Hoje_();
  if (dia > '2026-11-18') throw new Error('Não agendar post sobre 20–22/11 depois da data planejada sem revalidar.');
  return eV3CriarPost_(eV3Encontrar_(E_V3.SECOND),'customScheduled','2026-11-18T22:00:00.000Z'); // 19h BRT
}
function entressalaV3RotinaDiaria() {
  if (eV3Props_().getProperty(E_V3.ENABLED)!=='true') return;
  const date=eV3Hoje_();
  const dow=new Date(date+'T12:00:00Z').getUTCDay(); // 1..5 = segunda..sexta
  if (dow===0 || dow===6) return;
  try {
    const p=eV3Feed_().posts.filter(x=>x.publish_local_date===date && x.kind!=='lancamento' && x.id!==E_V3.SECOND && x.approved && x.eligibleForScheduling);
    if (!p.length) { eV3Aviso_(date,'Sem pauta fotográfica verificada para hoje. Nenhum post inventado.'); return; }
    if (p.length > 1) { eV3Aviso_(date,'Mais de um candidato aprovado para a mesma data. Envio bloqueado.'); return; }
    eV3CriarPost_(p[0],'shareNow',null,date);
  } catch(e) { eV3Aviso_(date,e.message); throw e; }
}
function entressalaV3InstalarRotina() {
  eV3Token_(); // evita instalar sem token
  const existing=ScriptApp.getProjectTriggers().filter(x=>x.getHandlerFunction()===E_V3.HANDLER);
  existing.forEach(t=>ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger(E_V3.HANDLER).timeBased().atHour(19).nearMinute(0).everyDays(1).inTimezone(E_V3.TZ).create();
  eV3Props_().setProperty(E_V3.ENABLED,'true');
  Logger.log('Rotina instalada SEM DATA DE FIM. Executa diariamente por volta de 19h BRT, mas só publica segunda–sexta quando existe pauta aprovada. Gatilhos de outros projetos não foram alterados.');
}
function entressalaV3PausarRotina() {
  eV3Props_().setProperty(E_V3.ENABLED,'false');
  Logger.log('Rotina pausada: nenhum novo post automático.');
}
function eV3Aviso_(date,message) {
  const key='ENTRESSALA_V3_AVISO_'+date;
  if (eV3Props_().getProperty(key)) return;
  Logger.log('BLOQUEIO EDITORIAL/OPERACIONAL: '+message);
  try {
    MailApp.sendEmail(E_V3.ALERT_EMAIL,'ENTRESSALA — Instagram: intervenção necessária ('+date+')',message+'\n\nO publicador não tentou substituir um evento ou foto sem verificação.');
    eV3Props_().setProperty(key,'true');
  } catch(error) {
    Logger.log('AVISO_EMAIL_FALHOU: '+error.message+'; causa original: '+message);
    eV3Props_().setProperty('ENTRESSALA_V3_AVISO_ERRO_'+date,String(error.message).slice(0,300));
  }
}

function entressalaV3AuditoriaSomenteLeitura() {
  const props=eV3Props_(), hoje=eV3Hoje_();
  const r={versao:'3.2-2026-11-23',dataLocal:hoje,
    rotinaHabilitada:props.getProperty(E_V3.ENABLED)==='true',
    tokenBufferPresente:Boolean(props.getProperty('BUFFER_API_KEY')),
    quantidadeGatilhos:ScriptApp.getProjectTriggers().filter(t=>t.getHandlerFunction()===E_V3.HANDLER).length,
    filaAcessivel:false,candidatosHoje:[]};
  try {
    const fila=eV3Feed_(); r.filaAcessivel=true;
    r.candidatosHoje=fila.posts.filter(p=>p.publish_local_date===hoje).map(p=>({id:p.id,aprovado:p.approved===true,imagensProntas:p.assetsReady===true}));
  } catch(e) {r.erroFila=String(e.message);}
  Logger.log(JSON.stringify(r,null,2)); return r;
}