def render_html():
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MAGI SYSTEM</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0a12;--panel:#12121e;--border:#1a3a5c;--text:#c0c8d8;--muted:#5a6a7a;
--blue:#00d4ff;--pink:#ff69b4;--gold:#ffd700;--green:#00ff88;--red:#ff4444}
@keyframes scanline{0%{top:-100%}100%{top:100%}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes fadein{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
body{background:var(--bg);color:var(--text);font-family:'Courier New',monospace;
min-height:100vh;overflow-x:hidden;position:relative}
body::after{content:'';position:fixed;top:0;left:0;right:0;bottom:0;pointer-events:none;
background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,212,255,.015) 2px,rgba(0,212,255,.015) 4px);
z-index:9999}
.scanline{position:fixed;top:-100%;left:0;right:0;height:200px;
background:linear-gradient(transparent,rgba(0,212,255,.03),transparent);
animation:scanline 8s linear infinite;pointer-events:none;z-index:9998}
.header{background:var(--panel);border-bottom:1px solid var(--border);
padding:12px 20px;display:flex;justify-content:space-between;align-items:center}
.header h1{color:var(--blue);font-size:1.2em;letter-spacing:3px;text-transform:uppercase}
.header h1 span{color:var(--red);margin:0 6px}
.user-info{font-size:.85em;color:var(--muted);display:flex;align-items:center;gap:10px}
.user-info button{background:none;border:1px solid var(--border);color:var(--muted);
padding:4px 12px;cursor:pointer;font-family:inherit;font-size:.85em}
.user-info button:hover{border-color:var(--blue);color:var(--blue)}
.mode-bar{display:flex;gap:8px;padding:12px 20px;background:var(--panel);
border-bottom:1px solid var(--border)}
.mode-btn{padding:8px 16px;background:transparent;border:1px solid var(--border);
color:var(--muted);cursor:pointer;font-family:inherit;font-size:.85em;transition:all .2s}
.mode-btn.active{border-color:var(--blue);color:var(--blue);background:rgba(0,212,255,.08)}
.mode-btn:hover{border-color:var(--blue);color:var(--blue)}
.unit-btns{display:flex;gap:6px;margin-left:auto}
.unit-btn{padding:6px 14px;border:1px solid var(--border);background:transparent;
font-family:inherit;font-size:.8em;cursor:pointer;transition:all .2s}
.unit-btn[data-u="melchior"]{color:var(--blue)}
.unit-btn[data-u="balthasar"]{color:var(--pink)}
.unit-btn[data-u="casper"]{color:var(--gold)}
.unit-btn.active{opacity:1;background:rgba(255,255,255,.06)}
.unit-btn:not(.active){opacity:.4}
.chat{flex:1;padding:20px;max-width:900px;margin:0 auto;overflow-y:auto;height:calc(100vh - 280px)}
.msg{margin:16px 0;animation:fadein .3s ease}
.msg-user{text-align:right}
.msg-user .bubble{display:inline-block;background:rgba(0,212,255,.1);border:1px solid var(--blue);
border-radius:12px 12px 2px 12px;padding:10px 16px;max-width:70%;text-align:left}
.msg-result{text-align:center;margin:20px 0}
.result-box{display:inline-block;padding:16px 28px;border-radius:8px;font-size:1.1em;font-weight:bold}
.result-approve{border:2px solid var(--green);color:var(--green);background:rgba(0,255,136,.06)}
.result-deny{border:2px solid var(--red);color:var(--red);background:rgba(255,68,68,.06)}
.result-approve .icon{animation:pulse 1.5s ease infinite}
.msg-vote{margin:12px 0;padding:10px 16px;border-left:3px solid var(--muted);
background:rgba(255,255,255,.02);border-radius:0 8px 8px 0}
.msg-vote[data-u="melchior"]{border-left-color:var(--blue)}
.msg-vote[data-u="balthasar"]{border-left-color:var(--pink)}
.msg-vote[data-u="casper"]{border-left-color:var(--gold)}
.vote-header{font-size:.85em;margin-bottom:6px;display:flex;align-items:center;gap:8px}
.vote-header .tag{padding:2px 8px;border-radius:3px;font-size:.75em;font-weight:bold}
.tag-approve{background:rgba(0,255,136,.15);color:var(--green)}
.tag-deny{background:rgba(255,68,68,.15);color:var(--red)}
.tag-abstain{background:rgba(255,215,0,.15);color:var(--gold)}
.thinking-toggle{font-size:.75em;color:var(--muted);cursor:pointer;margin-top:6px;
border:none;background:none;font-family:inherit;text-decoration:underline}
.thinking-block{display:none;margin-top:6px;padding:8px;background:rgba(0,0,0,.3);
border-radius:4px;font-size:.85em;color:var(--muted);white-space:pre-wrap}
.thinking-block.show{display:block}
.msg-consult{margin:12px 0;padding:12px 16px;border-left:3px solid;background:rgba(255,255,255,.02);
border-radius:0 8px 8px 0}
.msg-consult[data-u="melchior"]{border-left-color:var(--blue)}
.msg-consult[data-u="balthasar"]{border-left-color:var(--pink)}
.msg-consult[data-u="casper"]{border-left-color:var(--gold)}
.spinner{display:inline-block;width:16px;height:16px;border:2px solid var(--muted);
border-top-color:var(--blue);border-radius:50%;animation:spin .8s linear infinite;vertical-align:middle}
.input-area{position:fixed;bottom:0;left:0;right:0;background:var(--panel);
border-top:1px solid var(--border);padding:12px 20px}
.input-wrap{max-width:900px;margin:0 auto;display:flex;gap:10px;align-items:center}
.input-wrap textarea{flex:1;background:var(--bg);border:1px solid var(--border);color:var(--text);
padding:10px 14px;border-radius:8px;font-family:inherit;font-size:.95em;resize:none;outline:none;
min-height:44px;max-height:120px}
.input-wrap textarea:focus{border-color:var(--blue)}
.input-wrap button{background:var(--blue);color:var(--bg);border:none;padding:10px 20px;
border-radius:8px;font-family:inherit;font-weight:bold;cursor:pointer;font-size:.95em}
.input-wrap button:hover{opacity:.85}
.input-wrap button:disabled{opacity:.4;cursor:not-allowed}
.config-toggle{position:fixed;bottom:70px;right:20px;background:var(--panel);
border:1px solid var(--border);color:var(--muted);padding:6px 12px;cursor:pointer;
font-family:inherit;font-size:.8em;border-radius:4px;z-index:10}
.config-panel{display:none;position:fixed;bottom:110px;right:20px;width:360px;
background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:16px;z-index:10}
.config-panel.show{display:block}
.config-panel label{display:block;color:var(--muted);font-size:.8em;margin:8px 0 4px}
.config-panel input,.config-panel select{width:100%;background:var(--bg);border:1px solid var(--border);
color:var(--text);padding:6px 10px;border-radius:4px;font-family:inherit;font-size:.85em}
.config-panel button{margin-top:12px;background:var(--blue);color:var(--bg);border:none;
padding:6px 16px;border-radius:4px;cursor:pointer;font-family:inherit}
.settings-modal{display:none;position:fixed;top:0;left:0;right:0;bottom:0;
background:rgba(0,0,0,.7);z-index:100;justify-content:center;align-items:center}
.settings-modal.show{display:flex}
.settings-box{background:var(--panel);border:1px solid var(--border);border-radius:12px;
padding:24px;width:90%;max-width:400px}
.settings-box h2{color:var(--blue);font-size:1em;margin-bottom:16px;letter-spacing:2px}
.settings-box label{display:block;color:var(--muted);font-size:.8em;margin:10px 0 4px}
.settings-box input{width:100%;background:var(--bg);border:1px solid var(--border);color:var(--text);
padding:8px 12px;border-radius:4px;font-family:inherit;font-size:.9em}
.settings-box .btn-row{display:flex;gap:10px;margin-top:16px}
.settings-box .btn-row button{flex:1;padding:8px;border-radius:4px;font-family:inherit;cursor:pointer}
.login-page{display:flex;justify-content:center;align-items:center;min-height:100vh}
.login-box{background:var(--panel);border:1px solid var(--border);border-radius:12px;
padding:32px;width:90%;max-width:380px}
.login-box h2{color:var(--blue);text-align:center;letter-spacing:3px;margin-bottom:24px}
.login-box input{width:100%;background:var(--bg);border:1px solid var(--border);color:var(--text);
padding:10px 14px;margin-bottom:12px;border-radius:4px;font-family:inherit}
.login-box button{width:100%;background:var(--blue);color:var(--bg);border:none;
padding:10px;border-radius:4px;font-family:inherit;font-weight:bold;cursor:pointer;font-size:1em}
.login-box .toggle{color:var(--muted);font-size:.85em;text-align:center;margin-top:12px;cursor:pointer}
.login-box .toggle:hover{color:var(--blue)}
.latency{font-size:.75em;color:var(--muted);margin-top:4px}
@media(max-width:600px){.chat{height:calc(100vh - 260px);padding:12px}
.msg-user .bubble{max-width:85%}.header h1{font-size:1em}.config-panel{width:calc(100% - 40px);right:20px}}
</style>
</head>
<body>
<div class="scanline"></div>
<div id="app"></div>
<script>
const U={
  melchior:{codename:'MELCHIOR-01',role:'科学家',color:'#00d4ff'},
  balthasar:{codename:'BALTHASAR-02',role:'母亲',color:'#ff69b4'},
  casper:{codename:'CASPER-03',role:'女人',color:'#ffd700'}
};
let state={token:null,user:null,mode:'judge',unit:'melchior',msgs:[],loading:false};

function html(t){const d=document.createElement('div');d.innerHTML=t;return d.firstElementChild}
function qs(s,p){return(p||document).querySelector(s)}
function qsa(s,p){return[...(p||document).querySelectorAll(s)]}

function render(){
  if(!state.token)return renderLogin();
  const app=qs('#app');
  app.innerHTML=`
  <div class="header"><h1>MAGI<span>|</span>SYSTEM</h1>
  <div class="user-info"><span>${state.user?.username||''}</span>
  <button onclick="showSettings()">⚙</button><button onclick="logout()">登出</button></div></div>
  <div class="mode-bar">
  <button class="mode-btn ${state.mode==='judge'?'active':''}" onclick="setMode('judge')">⚖ 三贤人裁决</button>
  <button class="mode-btn ${state.mode==='consult'?'active':''}" onclick="setMode('consult')">◈ 单通道咨询</button>
  ${state.mode==='consult'?`<div class="unit-btns">${Object.entries(U).map(([k,v])=>
  `<button class="unit-btn ${state.unit===k?'active':''}" data-u="${k}" onclick="setUnit('${k}')">${v.codename}</button>`
  ).join('')}</div>`:''}</div>
  <div class="chat" id="chat"></div>
  <button class="config-toggle" onclick="toggleConfig()">⚙ 配置</button>
  <div class="config-panel" id="cfgPanel"></div>
  <div class="input-area"><div class="input-wrap">
  <textarea id="q" placeholder="${state.mode==='judge'?'向 MAGI 提出提案...':'向 '+U[state.unit].codename+' 咨询...'}" rows="1"
  onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();submit()}"></textarea>
  <button onclick="submit()" ${state.loading?'disabled':''}>${state.loading?'⏳':'▶'}</button>
  </div></div>
  <div class="settings-modal" id="settModal"></div>`;
  renderChat();
  if(state.user?.role==='admin')renderConfig();
}

function renderChat(){
  const c=qs('#chat');if(!c)return;
  c.innerHTML=state.msgs.map(m=>renderMsg(m)).join('');
  c.scrollTop=c.scrollHeight;
}

function renderMsg(m){
  if(m.type==='user')return `<div class="msg msg-user"><div class="bubble">${esc(m.text)}</div></div>`;
  if(m.type==='result'){
    const ok=m.decision==='approve';
    return `<div class="msg msg-result"><div class="result-box ${ok?'result-approve':'result-deny'}">${ok?'✅ 承认':'❌ 否决'}</div></div>`;
  }
  if(m.type==='thinking')return `<div class="msg msg-vote" data-u="${m.unit}"><div class="vote-header"><span class="spinner"></span> ${U[m.unit].codename} (${U[m.unit].role}) 思考中...</div></div>`;
  if(m.type==='vote'){
    const dc=m.decision==='approve'?'tag-approve':m.decision==='deny'?'tag-deny':'tag-abstain';
    const dl=m.decision==='approve'?'承认':m.decision==='deny'?'否认':'弃权';
    let th='';
    if(m.thinking)th=`<button class="thinking-toggle" onclick="this.nextElementSibling.classList.toggle('show')">💭 展开思考</button><div class="thinking-block">${esc(m.thinking)}</div>`;
    return `<div class="msg msg-vote" data-u="${m.unit}"><div class="vote-header"><span style="color:${U[m.unit].color}">${U[m.unit].codename}</span> <span style="color:var(--muted)">(${U[m.unit].role})</span> <span class="tag ${dc}">${dl}</span></div><div>${fmt(m.reasoning)}</div>${th}<div class="latency">⏱ ${m.latency}ms | 置信度 ${(m.confidence*100).toFixed(0)}%</div></div>`;
  }
  if(m.type==='consult'){
    let th='';
    if(m.thinking)th=`<button class="thinking-toggle" onclick="this.nextElementSibling.classList.toggle('show')">💭 展开思考</button><div class="thinking-block">${esc(m.thinking)}</div>`;
    return `<div class="msg msg-consult" data-u="${m.unit}"><div class="vote-header"><span style="color:${U[m.unit].color}">${U[m.unit].codename}</span> <span style="color:var(--muted)">(${U[m.unit].role})</span></div><div>${fmt(m.response)}</div>${th}<div class="latency">⏱ ${m.latency}ms | 置信度 ${(m.confidence*100).toFixed(0)}%</div></div>`;
  }
  return '';
}

function fmt(t){return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>')}
function esc(t){return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>')}

function renderLogin(){
  const app=qs('#app');
  app.innerHTML=`<div class="login-page"><div class="login-box"><h2>MAGI SYSTEM</h2>
  <input id="lu" placeholder="用户名"><input id="lp" type="password" placeholder="密码">
  <button onclick="doLogin()">登录</button><div class="toggle" onclick="toggleReg()">没有账号？注册</div></div></div>`;
}

function toggleReg(){
  const box=qs('.login-box');
  if(qs('#lr')){qs('#lr').remove();qs('.toggle').textContent='没有账号？注册';return}
  box.innerHTML+=`<input id="lr" placeholder="确认密码" style="display:block">`;
  qs('.toggle').textContent='已有账号？登录';
}

async function doLogin(){
  const u=qs('#lu').value,p=qs('#lp').value,r=qs('#lr')?.value;
  const endpoint=r?'/api/auth/register':'/api/auth/login';
  const body=r?{username:u,password:p}:{username:u,password:p};
  try{
    const res=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const data=await res.json();
    if(!res.ok)throw new Error(data.detail||'Error');
    if(r){state.token=(await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})}).then(r=>r.json())).access_token;}
    else state.token=data.access_token;
    state.user=await fetch('/api/auth/me',{headers:{'Authorization':'Bearer '+state.token}}).then(r=>r.json());
    localStorage.setItem('magi_token',state.token);
    render();
  }catch(e){alert(e.message)}
}

function logout(){state.token=null;state.user=null;state.msgs=[];localStorage.removeItem('magi_token');render()}

function setMode(m){state.mode=m;render()}
function setUnit(u){state.unit=u;render()}

async function submit(){
  const ta=qs('#q');const text=ta.value.trim();if(!text||state.loading)return;
  state.loading=true;ta.value='';
  state.msgs.push({type:'user',text});render();

  if(state.mode==='judge'){
    Object.keys(U).forEach(u=>state.msgs.push({type:'thinking',unit:u}));
    render();
    try{
      const res=await fetch('/api/judge',{
        method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+state.token},
        body:JSON.stringify({question:text})
      });
      const data=await res.json();
      state.msgs=state.msgs.filter(m=>m.type!=='thinking');
      data.votes.forEach(v=>{
        state.msgs.push({type:'vote',unit:v.unit,decision:v.decision,reasoning:v.reasoning,thinking:v.thinking,confidence:v.confidence,latency:v.latency_ms});
      });
      state.msgs.push({type:'result',decision:data.final_decision});
    }catch(e){state.msgs=state.msgs.filter(m=>m.type!=='thinking');state.msgs.push({type:'user',text:'❌ '+e.message})}
  }else{
    try{
      const res=await fetch('/api/consult',{
        method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+state.token},
        body:JSON.stringify({text,unit:state.unit})
      });
      const data=await res.json();
      state.msgs.push({type:'consult',unit:data.unit,response:data.response,thinking:data.thinking,confidence:data.confidence,latency:data.latency_ms});
    }catch(e){state.msgs.push({type:'user',text:'❌ '+e.message})}
  }
  state.loading=false;render();
}

function renderConfig(){
  const p=qs('#cfgPanel');if(!p)return;
  fetch('/api/admin/config',{headers:{'Authorization':'Bearer '+state.token}}).then(r=>r.json()).then(cfg=>{
    p.innerHTML=`<h3 style="color:var(--blue);font-size:.9em;margin-bottom:12px">全局配置 (管理员)</h3>
    <label>API Base</label><input id="cb" value="${cfg.api_base||''}">
    <label>API Key</label><input id="ck" type="password" value="${cfg.api_key||''}" placeholder="留空不修改">
    <label>思考强度</label><select id="ce"><option value="">默认</option>
    <option value="low" ${cfg.reasoning_effort==='low'?'selected':''}>Low</option>
    <option value="medium" ${cfg.reasoning_effort==='medium'?'selected':''}>Medium</option>
    <option value="high" ${cfg.reasoning_effort==='high'?'selected':''}>High</option></select>
    <button onclick="saveConfig()">保存</button>`;
  });
}

function toggleConfig(){qs('#cfgPanel').classList.toggle('show')}

async function saveConfig(){
  const body={api_base:qs('#cb').value,reasoning_effort:qs('#ce').value||null};
  const k=qs('#ck').value;if(k)body.api_key=k;
  const units={};Object.keys(U).forEach(uid=>{units[uid]={}});
  body.units=units;
  await fetch('/api/admin/config',{method:'PUT',headers:{'Content-Type':'application/json','Authorization':'Bearer '+state.token},body:JSON.stringify(body)});
  qs('#cfgPanel').classList.remove('show');
}

function showSettings(){
  const m=qs('#settModal');
  m.className='settings-modal show';
  m.innerHTML=`<div class="settings-box"><h2>⚙ 个人设置</h2>
  <label>自定义 API Base (可选)</label><input id="sbase" value="${state.user?.api_base||''}" placeholder="https://api.vveai.com/v1">
  <label>自定义 API Key (可选)</label><input id="skey" type="password" placeholder="留空不修改">
  <div class="btn-row"><button onclick="saveSettings()" style="background:var(--blue);color:var(--bg);border:none">保存</button>
  <button onclick="qs('#settModal').className='settings-modal'" style="background:none;border:1px solid var(--border);color:var(--muted)">取消</button></div></div>`;
}

async function saveSettings(){
  const body={api_base:qs('#sbase').value||null,api_key:qs('#skey').value||null};
  await fetch('/api/auth/settings',{method:'PUT',headers:{'Content-Type':'application/json','Authorization':'Bearer '+state.token},body:JSON.stringify(body)});
  state.user=await fetch('/api/auth/me',{headers:{'Authorization':'Bearer '+state.token}}).then(r=>r.json());
  qs('#settModal').className='settings-modal';render();
}

// Auto-login
(async()=>{
  const t=localStorage.getItem('magi_token');
  if(t){try{state.token=t;state.user=await fetch('/api/auth/me',{headers:{'Authorization':'Bearer '+t}}).then(r=>r.json());if(state.user.id)render();else throw 0}catch{localStorage.removeItem('magi_token');renderLogin()}}else renderLogin()
})();
</script>
</body></html>"""
