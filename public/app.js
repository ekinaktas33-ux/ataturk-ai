const messages=document.getElementById('messages');
const welcome=document.getElementById('welcome');
const input=document.getElementById('question');
const scrollBox=document.getElementById('chatScroll');
const DATA=window.ATATURK_DATASET||[];
const core=DATA.filter(item=>!item.index);
document.getElementById('recordCount').textContent=String(DATA.length);
document.getElementById('factCount').textContent=String(core.length);

const normalize=value=>String(value||'').toLocaleLowerCase('tr-TR').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/ı/g,'i').replace(/ç/g,'c').replace(/ğ/g,'g').replace(/ö/g,'o').replace(/ş/g,'s').replace(/ü/g,'u').replace(/[^a-z0-9\s]/g,' ').replace(/\s+/g,' ').trim();
const STOP=new Set('bir ve ile de da mi mu ne nasil nedir kimdir hakkinda icin bana anlat eder misin misin misiniz lutfen ataturk turk tarih bu su peki ya acaba'.split(' '));
const SYNONYMS={
 egitim:['okul','ogrenim','maarif','ogretim','mektep','universite'], okul:['egitim','ogrenim','mektep'],
 savas:['muharebe','cephe','harekat','mucadele'], mucadele:['direnis','kurtulus','savas','millî mucadele'],
 inkilap:['devrim','yenilik','reform','donusum'], devrim:['inkilap','reform','yenilik'],
 ekonomi:['iktisat','uretim','kalkinma','sanayilesme'], iktisat:['ekonomi','kalkinma','ticaret'],
 bilim:['akil','arastirma','teknoloji','bilimsel'], akil:['bilim','mantik','gercek'],
 yonetim:['devlet','siyaset','idare','cumhuriyet'], cumhuriyet:['meclis','egemenlik','halk','yönetim'],
 dis:['diplomasi','uluslararasi','dis politika'], diplomasi:['antlasma','dis politika','lozan'],
 kadin:['kadin haklari','secme','secilebilme','medeni kanun'], hak:['haklar','hukuk','adalet'],
 nutuk:['soylev','konusma','eser','hitabe'], soz:['konusma','ifade','alinti'],
 kurtulus:['bagimsizlik','milli mucadele','direnis'], baslangic:['neden','oncesi','surec'], sonuc:['etki','sonuclari','sonra'],
 selanik:['mustafa kemal','dogum','yasami'], mustafa:['ataturk','mustafa kemal'], kemal:['ataturk','mustafa kemal'],
 samsun:['bandirma','19 mayis','milli mucadele'], amasya:['genelge','milli mucadele'], erzurum:['kongre','milli mucadele'], sivas:['kongre','milli mucadele'],
 canakkale:['gelibolu','ariburnu','anafartalar','birinci dunya savasi'], anafartalar:['conkbayiri','canakkale'],
 sakarya:['bas komutan','1921 muharebesi'], dumlupinar:['buyuk taarruz','30 agustos'], izmir:['9 eylul','kurtulus'],
 lozan:['baris antlasmasi','ismet pasa','bagimsizlik'], mudanya:['ateskes','dogu trakya'], tbmm:['meclis','buyuk millet meclisi','23 nisan'], meclis:['tbmm','egemenlik'],
 harf:['alfabe','yeni turk harfleri','okuryazarlik'], medeni:['hukuk','aile','kanun'], kadinlar:['kadin haklari','secme secilme','1934'],
 osmanli:['devlet','imparatorluk','tanzimat','mesrutiyet'], selcuklu:['alp arslan','malazgirt','anadolu'], gokturk:['orhun','bilge kagan','turk adi'], uygur:['orhun','yerlesik hayat'], hun:['attilla','bozkir'],
 ittifak:['ittifak devletleri','almanya','osmanli'], itilaf:['ingiltere','fransa','rusya'], cephe:['savas','muharebe','askeri'],
 laiklik:['din devlet','hukuk','egitim'], devletcilik:['sanayi','ekonomi','kalkinma'], halkcilik:['esitlik','toplum'], milliyetcilik:['millet','bagimsizlik'],
 turkiye:['cumhuriyet','ankara','tbmm'], cumhuriyetin:['cumhuriyet','29 ekim'], inkilaplari:['reform','yenilik','kanun'], dogum:['1881','selanik','ailesi'], olum:['10 kasim','dolmabahce','1938']
};
const SUFFIXES=['leriniz','larımız','lerimiz','larının','lerinden','larından','lerindeki','larındaki','larımızda','lerimizde','sinden','sından','lardan','lerden','larında','lerinde','lerine','larına','lerdir','lardır','lerini','larını','lerin','ların','siniz','sunuz','ımız','imiz','unuz','iniz','daki','deki','taki','sini','sına','sine','dan','den','tan','ten','dır','dir','tır','tir','lar','ler','lık','lik','luk','lük','cı','ci','cu','cü','yla','yle','ında','inde','una','üne','nin','nın','nun','nün','in','ın','un','ün','ı','i','u','ü','a','e'];
function stem(token){let out=token;for(let pass=0;pass<3;pass++){const suffix=SUFFIXES.find(end=>out.length-end.length>=3&&out.endsWith(end));if(!suffix)break;out=out.slice(0,-suffix.length)}return out}
const expandTerms=terms=>{const expanded=new Set();terms.forEach(term=>{expanded.add(term);expanded.add(stem(term));(SYNONYMS[term]||SYNONYMS[stem(term)]||[]).forEach(word=>normalize(word).split(' ').forEach(w=>{expanded.add(w);expanded.add(stem(w))}))});return [...expanded].filter(Boolean)};
const state={lastRecords:[],lastQuestion:'',lastIntent:'',turns:0};

function similarity(a,b){if(a===b)return 1;if(a.length<4||b.length<4)return 0;if(a.startsWith(b)||b.startsWith(a))return .7;const grams=s=>{const out=new Set();for(let i=0;i<s.length-2;i++)out.add(s.slice(i,i+3));return out};const aa=grams(a),bb=grams(b);let overlap=0;aa.forEach(x=>{if(bb.has(x))overlap++});return overlap/(aa.size+bb.size-overlap||1)}
function scoreRecord(query,record){
 const terms=expandTerms(normalize(query).split(' ').filter(t=>t.length>2&&!STOP.has(t)));
 const title=normalize(record.title),topic=normalize(record.topic),body=normalize(`${record.title} ${record.topic} ${record.text}`);
 let score=0;
 for(const token of terms){if(title.includes(token))score+=token.length>5?7:4;else if(topic.includes(token))score+=3;else if(body.includes(token))score+=1.25;else if(token.length>4){const fuzzy=title.split(' ').reduce((best,w)=>Math.max(best,similarity(token,w)),0);if(fuzzy>.57)score+=2.2*fuzzy}}
 if(state.lastRecords.some(item=>item.title===record.title)&&/devam|ac|detay|biraz daha|peki|neden|sonra|bunun/.test(normalize(query)))score+=2;
 return score;
}
function intentFor(q){const s=normalize(q);if(/^(merhaba|selam|slm|gunaydin|iyi aksamlar|iyi gunler|hey|hello)\b/.test(s))return'greeting';if(/tesekkur|sag ol|cok iyi|harika sagol|yardimin icin/.test(s))return'thanks';if(/nasilsin|ne haber|naber/.test(s))return'how';if(/sen kimsin|kimsin|ne ise yariyorsun|amac/.test(s))return'identity';if(/hoscakal|gorusuruz|bay bay/.test(s))return'bye';if(/hava nasil|saat kac|bugun tarih|guncel haber|son dakika/.test(s))return'live';if(/^(evet|hayir|tamam|olur|anladim|hmm|aynen)\b/.test(s))return'followup';if(/espri|fikra|saka yap|guldur/.test(s))return'joke';if(/esin harik|cok iyisin|seni sev|cok zekisin/.test(s))return'compliment';return'question'}
const SMALLTALK={
 greeting:['Merhaba! Atatürk’ün hayatı, Millî Mücadele ve Türk tarihi hakkında birlikte konuşabiliriz. Aklındaki konu ne?','Selam! İstersen bir olayın arka planını, nedenlerini ve sonuçlarını adım adım inceleyelim.'],
 thanks:['Rica ederim. İstersen bu konunun öncesini, sonuçlarını ya da farklı tarihçilerin yorumlarını da konuşabiliriz.','Ne demek! Merak ettiğin başka bir tarih konusu varsa sorabilirsin.'],
 how:['İyiyim, teşekkürler! Buradayım; tarih sorularını kaynaklara dayalı biçimde birlikte inceleyebiliriz. Sen nasılsın?','Gayet iyiyim, teşekkür ederim. Bugün hangi konuyu merak ediyorsun?'],
 identity:['Ben Atatürk AI adlı tarih sohbeti simülasyonuyum. Atatürk ve Türk tarihiyle ilgili kaynak özetleri sunarım; gerçek Atatürk’ün sesi, bilinci ya da birebir görüşü değilim.','Tarihî kayıtları bulup anlaşılır biçimde özetleyen bir sohbet asistanıyım. Sorularımın yanıtlarını kaynaklarla ilişkilendiririm ve kesin olmayan noktalarda bunu belirtirim.'],
 bye:['Görüşmek üzere. Dilediğin zaman yeni bir tarih sorusuyla devam edebiliriz.','Hoşça kal! Tarih merakıyla yeniden beklerim.'],
 live:['Canlı internet veya güncel haber akışına bağlı değilim; bu yüzden anlık hava, saat ve son dakika bilgisi veremem. Tarihî konularda ise elimdeki kaynak özetleriyle yardımcı olabilirim.'],
 followup:['Anladım. İstersen önceki konuyu biraz daha açayım; hangi kısmı merak ediyorsun?','Peki, buradayım. Biraz daha ayrıntı mı istersin, yoksa başka bir başlığa mı geçelim?'],
 joke:['Küçük bir tarih esprisi: Tarihçi neden takvimle tartışmaz? Çünkü günleri sayılıdır! İstersen şimdi ciddi bir tarih konusuna da geçebiliriz.'],
 compliment:['Teşekkür ederim, çok naziksin! Sana anlaşılır ve işe yarar yanıtlar vermeye çalışıyorum.']
};
const choose=list=>list[Math.floor(Math.random()*list.length)];
function findMatches(q){
 const normalized=normalize(q);
 if(/ataturk|mustafa kemal/.test(normalized)&&/kimdir|kim/.test(normalized))return ['Doğumu ve ailesi','Atatürk\'ün cumhurbaşkanlığı','Atatürk\'ün ölümü'].map(title=>core.find(item=>item.title===title)).filter(Boolean);
 if(state.lastRecords.length&&normalized.split(' ').length<7&&/^(peki|neden|sonra|bunun|bu|onu|daha|devam|hangi|ne zaman|acikla|anlat)/.test(normalized))return state.lastRecords;
 return core.map(record=>({record,score:scoreRecord(q,record)})).filter(item=>item.score>1.25).sort((a,b)=>b.score-a.score).slice(0,5).map(item=>item.record)
}
function answerQuestion(q){
 const intent=intentFor(q);
 if(intent!=='question')return {text:choose(SMALLTALK[intent]),records:[],kind:intent};
 let matches=findMatches(q);
 if(!matches.length&&state.lastRecords.length&&/^(peki|neden|sonra|bunun|bu|onu|daha|devam|acikla|anlat)/.test(normalize(q)))matches=state.lastRecords;
 if(!matches.length)return {text:'Bu soruyla doğrudan eşleşen bir kaynak özeti bulamadım. Biraz daha belirgin bir isim, tarih veya konu ekleyerek yeniden sorabilir misin? Örneğin “Sakarya Savaşı’nın sonucu ne oldu?” ya da “Atatürk’ün eğitim reformları” diye sorabilirsin.',records:[],kind:'notfound'};
 const chosen=matches.slice(0,3);
 const compact=/kisa|ozet|bir cumle|kisaca/.test(normalize(q));
 let intro='';
 if(/kimdir|hayati|yasami/.test(normalize(q)))intro='Mustafa Kemal Atatürk (1881–1938), asker ve devlet insanı; Millî Mücadele’nin önderi, Türkiye Cumhuriyeti’nin kurucusu ve ilk Cumhurbaşkanıdır. ';
 else if(/neden|niye/.test(normalize(q)))intro='Nedenini anlayabilmek için dönemin koşullarını ve önceki gelişmeleri birlikte düşünmek gerekir. ';
 else if(/fikir|dusunce|bilim|akil/.test(normalize(q)))intro='Kaynaklarda öne çıkan düşünce ve yaklaşımı şöyle özetlenebilir: ';
 else if(/ne oldu|sonuc|etki/.test(normalize(q)))intro='Başlıca sonuç ve etkiler şunlardır: ';
 else intro='Tabii, şöyle anlatayım: ';
 const paragraphs=chosen.map(record=>{
 const date=record.year&&record.year!=='—'&&record.year!=='Bugün'?`${record.year} · ${record.title}. `:`${record.title}. `;
  return `${date}${record.text}`;
 });
 let text=intro+paragraphs.join('\n\n');
 if(/bugun|gunumuz|simdi|yapay zeka|guncel|devlet danisman/.test(normalize(q)))text+='\n\nBuradaki güncel bağlantı, tarihî kaynaklardan hareketle yapılan bir değerlendirmedir; Atatürk’ün bugün için doğrudan görüşü veya hazır politika önerisi değildir.';
 if(compact)text=paragraphs[0];
 return {text,records:chosen,kind:'answer'};
}
function addMessage(text,who,meta={}){
 const row=document.createElement('div');row.className=`message ${who}`;
 if(who==='assistant'){const avatar=document.createElement('div');avatar.className='mini-avatar';avatar.textContent='A';row.append(avatar)}
 const bubble=document.createElement('div');bubble.className='bubble';bubble.textContent=text;row.append(bubble);messages.append(row);
 if(who==='assistant'&&'speechSynthesis'in window){const speaker=document.createElement('button');speaker.type='button';speaker.className='speak-btn';speaker.textContent='▶ Sesli oku';speaker.setAttribute('aria-label','Yanıtı sesli oku');speaker.addEventListener('click',()=>{window.speechSynthesis.cancel();const utterance=new SpeechSynthesisUtterance(text);utterance.lang='tr-TR';utterance.rate=.96;window.speechSynthesis.speak(utterance)});messages.append(speaker)}
 if(who==='assistant'&&meta.records?.length){
  const refs=[...new Map(meta.records.map(item=>[item.url,item])).values()];
  const refsNode=document.createElement('div');refsNode.className='answer-source';refsNode.append(document.createTextNode('Kaynaklar: '));
  refs.forEach((item,index)=>{if(index)refsNode.append(document.createTextNode(' · '));const link=document.createElement('a');link.href=item.url;link.target='_blank';link.rel='noreferrer';link.textContent=item.source;refsNode.append(link)});
  messages.append(refsNode);
 }
 scrollBox.scrollTop=scrollBox.scrollHeight;return row;
}
function send(text){const q=(text??input.value).trim();if(!q)return;welcome.classList.add('hidden');addMessage(q,'user');input.value='';input.style.height='auto';
 const thinking=addMessage('Bir düşüneyim…','assistant');
 window.setTimeout(()=>{thinking.remove();const response=answerQuestion(q);addMessage(response.text,'assistant',{records:response.records});state.turns++;state.lastQuestion=q;state.lastIntent=response.kind;if(response.records.length)state.lastRecords=response.records;},220+Math.random()*260);
}
document.getElementById('sendBtn').addEventListener('click',()=>send());
input.addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}});
input.addEventListener('input',()=>{input.style.height='auto';input.style.height=Math.min(input.scrollHeight,120)+'px'});
document.querySelectorAll('[data-prompt]').forEach(button=>button.addEventListener('click',()=>send(button.dataset.prompt)));
document.getElementById('newChat').addEventListener('click',()=>{messages.replaceChildren();state.lastRecords=[];state.lastQuestion='';state.turns=0;welcome.classList.remove('hidden');input.focus()});
const panel=document.getElementById('sourcePanel'),shell=document.querySelector('.app-shell');
function setPanel(open){if(innerWidth<=1040)panel.classList.toggle('open',open);else{panel.classList.toggle('closed',!open);shell.classList.toggle('panel-closed',!open)}}
document.getElementById('sourcesToggle').addEventListener('click',()=>setPanel(!panel.classList.contains('closed')&&!panel.classList.contains('open')));
document.getElementById('closeSources').addEventListener('click',()=>setPanel(false));
document.getElementById('shareBtn').addEventListener('click',async()=>{
 const isLocal=location.protocol==='file:'||location.hostname==='localhost'||location.hostname==='127.0.0.1';
 if(isLocal){composerHint.textContent='Bu yerel adres başkalarında açılmaz; yayınlanmış bağlantı gerekir.';return}
 try{if(navigator.share)await navigator.share({title:'Atatürk AI · Tarihî Sohbet',text:'Atatürk ve Türk tarihi üzerine kaynaklı sohbet',url:location.href});else{await navigator.clipboard.writeText(location.href);composerHint.textContent='Bağlantı kopyalandı; şimdi istediğin kişiye gönderebilirsin.';window.setTimeout(()=>composerHint.textContent='↵ Göndermek için Enter’a bas',3500)}}catch(error){if(error.name!=='AbortError')composerHint.textContent='Paylaşım açılamadı; sayfa bağlantısını adres çubuğundan kopyalayabilirsin.'}
});
const micButton=document.getElementById('micBtn'),composerHint=document.getElementById('composerHint');
const Recognition=window.SpeechRecognition||window.webkitSpeechRecognition;
if(Recognition){
 const recognition=new Recognition();recognition.lang='tr-TR';recognition.interimResults=true;recognition.continuous=false;
 recognition.onstart=()=>{micButton.classList.add('listening');composerHint.textContent='Dinliyorum… konuşmanı bitirince gönder';};
 recognition.onresult=event=>{let transcript='';for(let i=0;i<event.results.length;i++)transcript+=event.results[i][0].transcript;input.value=transcript;input.dispatchEvent(new Event('input'));};
 recognition.onerror=event=>{composerHint.textContent=event.error==='not-allowed'?'Mikrofon izni verilmedi':'Ses tanınamadı; yeniden deneyebilir veya yazabilirsin';};
 recognition.onend=()=>{micButton.classList.remove('listening');if(input.value.trim())composerHint.textContent='Soru hazır · göndermek için Enter’a bas';else composerHint.textContent='↵ Göndermek için Enter’a bas';};
 micButton.addEventListener('click',()=>{if(micButton.classList.contains('listening'))recognition.stop();else{try{recognition.start()}catch{composerHint.textContent='Mikrofon şu anda kullanılamıyor'}}});
}else{micButton.disabled=true;micButton.title='Bu tarayıcıda sesle yazma desteklenmiyor';micButton.setAttribute('aria-label','Sesle yazma bu tarayıcıda desteklenmiyor')}
