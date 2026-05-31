"""MAGI System Frontend — NERV Terminal UI v2.0 with Auth"""


def render_html() -> str:
    return r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MAGI SYSTEM — NERV Terminal</title>
<style>
  :root {
    --bg: #0a0a0f; --panel: #0d0d18; --border: #1a3a1a;
    --accent: #00ff41; --accent2: #ff6600; --warn: #ff3333;
    --text: #00ff41; --text-dim: #007a20; --text-bright: #66ff88;
    --melchior: #4488ff; --balthasar: #ff4488; --casper: #ffaa00;
    --card: #111122;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:var(--bg); color:var(--text); font-family:'Courier New',monospace; min-height:100vh; overflow-x:hidden; }
  body::after { content:''; position:fixed; top:0;left:0;right:0;bottom:0; background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,65,0.015) 2px,rgba(0,255,65,0.015) 4px); pointer-events:none; z-index:9999; }

  /* Login */
  #login-page { display:flex; align-items:center; justify-content:center; min-height:100vh; padding:20px; }
  .login-box { background:var(--panel); border:1px solid var(--border); padding:40px; width:100%; max-width:420px; position:relative; }
  .login-box::before { content:'MAGI AUTHENTICATION'; position:absolute; top:-12px;left:20px; background:var(--bg); padding:0 10px; font-size:12px; color:var(--accent); letter-spacing:3px; }
  .nerv-logo { text-align:center; margin-bottom:30px; font-size:28px; font-weight:bold; color:var(--accent2); letter-spacing:8px; text-shadow:0 0 20px rgba(255,102,0,0.5); }
  .nerv-logo small { display:block; font-size:11px; color:var(--text-dim); letter-spacing:2px; margin-top:4px; }
  .login-field { margin-bottom:16px; }
  .login-field label { display:block; font-size:11px; color:var(--text-dim); letter-spacing:2px; margin-bottom:4px; }
  .login-field input { width:100%; padding:10px 14px; background:var(--bg); border:1px solid var(--border); color:var(--text); font-family:'Courier New',monospace; font-size:14px; outline:none; transition:border-color .3s; }
  .login-field input:focus { border-color:var(--accent); box-shadow:0 0 8px rgba(0,255,65,0.2); }
  .login-btn { width:100%; padding:12px; background:transparent; border:1px solid var(--accent); color:var(--accent); font-family:'Courier New',monospace; font-size:14px; letter-spacing:3px; cursor:pointer; margin-top:10px; transition:all .3s; }
  .login-btn:hover { background:var(--accent); color:var(--bg); box-shadow:0 0 20px rgba(0,255,65,0.3); }
  .login-error { color:var(--warn); font-size:12px; text-align:center; margin-top:10px; min-height:18px; }

  /* App */
  #app-page { display:none; }
  .top-bar { display:flex; align-items:center; justify-content:space-between; padding:8px 20px; border-bottom:1px solid var(--border); background:var(--panel); font-size:12px; flex-wrap:wrap; gap:8px; }
  .top-bar-left { display:flex; align-items:center; gap:20px; }
  .top-bar .nerv-mark { color:var(--accent2); font-size:16px; font-weight:bold; letter-spacing:4px; }
  .top-bar .status-text { color:var(--text-dim); letter-spacing:1px; }
  .top-bar-right { display:flex; align-items:center; gap:12px; }
  .user-badge { color:var(--accent); border:1px solid var(--border); padding:3px 10px; font-size:11px; letter-spacing:1px; }
  .user-badge.admin { border-color:var(--accent2); color:var(--accent2); }
  .logout-btn { background:transparent; border:1px solid var(--warn); color:var(--warn); padding:3px 10px; font-family:'Courier New',monospace; font-size:11px; cursor:pointer; letter-spacing:1px; transition:all .2s; }
  .logout-btn:hover { background:var(--warn); color:var(--bg); }

  /* Tabs */
  .tab-bar { display:flex; border-bottom:1px solid var(--border); background:var(--panel); padding:0 16px; overflow-x:auto; }
  .tab-btn { background:transparent; border:none; border-bottom:2px solid transparent; color:var(--text-dim); font-family:'Courier New',monospace; font-size:12px; padding:10px 16px; cursor:pointer; letter-spacing:1px; white-space:nowrap; transition:all .2s; }
  .tab-btn:hover { color:var(--text); }
  .tab-btn.active { color:var(--accent); border-bottom-color:var(--accent); }
  .tab-content { display:none; }
  .tab-content.active { display:block; }

  /* Judge */
  .magi-container { max-width:900px; margin:0 auto; padding:20px; }
  .question-box textarea { width:100%; height:80px; padding:12px; background:var(--bg); border:1px solid var(--border); color:var(--text); font-family:'Courier New',monospace; font-size:14px; resize:vertical; outline:none; }
  .question-box textarea:focus { border-color:var(--accent); }
  .judge-btn { padding:10px 30px; background:transparent; border:1px solid var(--accent); color:var(--accent); font-family:'Courier New',monospace; font-size:14px; letter-spacing:2px; cursor:pointer; transition:all .3s; }
  .judge-btn:hover { background:var(--accent); color:var(--bg); box-shadow:0 0 20px rgba(0,255,65,0.3); }
  .judge-btn:disabled { opacity:.4; cursor:not-allowed; }

  /* Vote Cards */
  .votes-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; margin-top:20px; }
  .vote-card { border:1px solid var(--border); background:var(--card); padding:16px; position:relative; }
  .vote-card::before { content:''; position:absolute; top:0;left:0;width:4px;height:100%; }
  .vote-card.melchior::before { background:var(--melchior); }
  .vote-card.balthasar::before { background:var(--balthasar); }
  .vote-card.casper::before { background:var(--casper); }
  .vote-header { display:flex; justify-content:space-between; margin-bottom:8px; font-size:11px; letter-spacing:2px; }
  .vote-header .unit-name { font-weight:bold; }
  .vote-card.melchior .unit-name { color:var(--melchior); }
  .vote-card.balthasar .unit-name { color:var(--balthasar); }
  .vote-card.casper .unit-name { color:var(--casper); }
  .vote-decision { font-size:20px; font-weight:bold; margin:8px 0; }
  .vote-decision.approve { color:var(--accent); }
  .vote-decision.deny { color:var(--warn); }
  .vote-reason { font-size:12px; color:var(--text-dim); line-height:1.6; max-height:120px; overflow-y:auto; }
  .vote-meta { margin-top:8px; font-size:10px; color:var(--text-dim); display:flex; justify-content:space-between; }

  /* Result Banner */
  .result-banner { margin-top:24px; padding:16px 20px; border:1px solid; text-align:center; font-size:16px; letter-spacing:3px; animation:banner-glow 2s ease-in-out infinite alternate; }
  .result-banner.approve { border-color:var(--accent); color:var(--accent); background:rgba(0,255,65,0.05); }
  .result-banner.deny { border-color:var(--warn); color:var(--warn); background:rgba(255,51,51,0.05); }
  @keyframes banner-glow { from{box-shadow:0 0 5px rgba(0,255,65,0.1)} to{box-shadow:0 0 25px rgba(0,255,65,0.2)} }
  .result-banner small { display:block; margin-top:6px; font-size:11px; color:var(--text-dim); letter-spacing:1px; }

  /* Config */
  .config-section { max-width:700px; margin:0 auto; padding:20px; }
  .config-group { margin-bottom:20px; border:1px solid var(--border); padding:16px; background:var(--card); }
  .config-group h3 { font-size:12px; letter-spacing:2px; color:var(--accent); margin-bottom:12px; border-bottom:1px solid var(--border); padding-bottom:6px; }
  .config-row { display:flex; align-items:center; margin-bottom:10px; gap:10px; }
  .config-row label { font-size:11px; color:var(--text-dim); letter-spacing:1px; min-width:120px; }
  .config-row input,.config-row select { flex:1; padding:6px 10px; background:var(--bg); border:1px solid var(--border); color:var(--text); font-family:'Courier New',monospace; font-size:12px; outline:none; }
  .config-row input:focus,.config-row select:focus { border-color:var(--accent); }
  .save-btn { padding:8px 24px; background:transparent; border:1px solid var(--accent); color:var(--accent); font-family:'Courier New',monospace; font-size:12px; letter-spacing:2px; cursor:pointer; transition:all .2s; }
  .save-btn:hover { background:var(--accent); color:var(--bg); }

  /* Admin Table */
  .admin-section { max-width:900px; margin:0 auto; padding:20px; }
  .data-table { width:100%; border-collapse:collapse; font-size:12px; }
  .data-table th,.data-table td { border:1px solid var(--border); padding:8px 12px; text-align:left; }
  .data-table th { background:var(--panel); color:var(--accent); letter-spacing:1px; font-weight:normal; }
  .data-table td { color:var(--text-dim); }
  .data-table tr:hover td { color:var(--text); background:rgba(0,255,65,0.03); }
  .tbl-btn { padding:3px 8px; border:1px solid; background:transparent; font-family:'Courier New',monospace; font-size:10px; cursor:pointer; letter-spacing:1px; margin-right:4px; }
  .tbl-btn.edit { border-color:var(--accent); color:var(--accent); }
  .tbl-btn.edit:hover { background:var(--accent); color:var(--bg); }
  .tbl-btn.del { border-color:var(--warn); color:var(--warn); }
  .tbl-btn.del:hover { background:var(--warn); color:var(--bg); }

  /* Conversations */
  .conv-list { max-width:900px; margin:0 auto; padding:20px; }
  .conv-entry { border:1px solid var(--border); padding:14px; margin-bottom:12px; background:var(--card); cursor:pointer; transition:border-color .2s; }
  .conv-entry:hover { border-color:var(--accent); }
  .conv-q { font-size:13px; color:var(--text-bright); margin-bottom:6px; }
  .conv-result { font-size:12px; margin-bottom:4px; }
  .conv-result.approve { color:var(--accent); }
  .conv-result.deny { color:var(--warn); }
  .conv-time { font-size:10px; color:var(--text-dim); letter-spacing:1px; }
  .conv-detail { display:none; margin-top:10px; padding-top:10px; border-top:1px dashed var(--border); }
  .conv-entry.expanded .conv-detail { display:block; }
  .conv-vote-mini { font-size:11px; margin-bottom:6px; padding-left:8px; border-left:2px solid var(--border); }
  .export-btn { padding:6px 16px; background:transparent; border:1px solid var(--accent2); color:var(--accent2); font-family:'Courier New',monospace; font-size:11px; letter-spacing:1px; cursor:pointer; margin-bottom:16px; transition:all .2s; }
  .export-btn:hover { background:var(--accent2); color:var(--bg); }

  /* Modal */
  .modal-overlay { display:none; position:fixed; top:0;left:0;right:0;bottom:0; background:rgba(0,0,0,0.7); z-index:1000; align-items:center; justify-content:center; }
  .modal-overlay.show { display:flex; }
  .modal-box { background:var(--panel); border:1px solid var(--border); padding:24px; width:90%; max-width:420px; }
  .modal-box h4 { font-size:12px; color:var(--accent); letter-spacing:2px; margin-bottom:16px; }
  .modal-field { margin-bottom:12px; }
  .modal-field label { display:block; font-size:10px; color:var(--text-dim); letter-spacing:1px; margin-bottom:3px; }
  .modal-field input,.modal-field select { width:100%; padding:6px 10px; background:var(--bg); border:1px solid var(--border); color:var(--text); font-family:'Courier New',monospace; font-size:12px; outline:none; }
  .modal-actions { display:flex; gap:10px; margin-top:16px; }
  .modal-actions button { flex:1; padding:8px; background:transparent; border:1px solid var(--accent); color:var(--accent); font-family:'Courier New',monospace; font-size:12px; cursor:pointer; letter-spacing:1px; }
  .modal-actions button.cancel { border-color:var(--text-dim); color:var(--text-dim); }
  .modal-actions button:hover { background:var(--accent); color:var(--bg); }
  .modal-actions button.cancel:hover { background:var(--text-dim); }

  .loading-text { color:var(--text-dim); font-size:12px; letter-spacing:2px; text-align:center; padding:20px; }
  .empty-text { color:var(--text-dim); font-size:12px; text-align:center; padding:30px; letter-spacing:1px; }
  .toast { position:fixed; bottom:20px; right:20px; padding:10px 20px; background:var(--panel); border:1px solid var(--accent); color:var(--accent); font-family:'Courier New',monospace; font-size:12px; z-index:2000; opacity:0; transition:opacity .3s; letter-spacing:1px; }
  .toast.error { border-color:var(--warn); color:var(--warn); }
  .toast.show { opacity:1; }

  @media(max-width:600px) {
    .top-bar{padding:6px 10px} .magi-container,.config-section,.admin-section,.conv-list{padding:12px}
    .votes-grid{grid-template-columns:1fr} .data-table{font-size:10px} .data-table th,.data-table td{padding:5px 6px}
  }
</style>
</head>
<body>

<div id="login-page">
  <div class="login-box">
    <div class="nerv-logo">NERV<small>SECRET — AUTHORIZATION REQUIRED</small></div>
    <div class="login-field"><label>OPERATOR ID</label><input type="text" id="login-user" autocomplete="username" autofocus></div>
    <div class="login-field"><label>ACCESS CODE</label><input type="password" id="login-pass" autocomplete="current-password"></div>
    <button class="login-btn" onclick="doLogin()">AUTHENTICATE</button>
    <div class="login-error" id="login-error"></div>
  </div>
</div>

<div id="app-page">
  <div class="top-bar">
    <div class="top-bar-left"><span class="nerv-mark">NERV</span><span class="status-text" id="conn-status">● MAGI ONLINE</span></div>
    <div class="top-bar-right"><span class="user-badge" id="user-badge"></span><button class="logout-btn" onclick="doLogout()">DISCONNECT</button></div>
  </div>
  <div class="tab-bar">
    <button class="tab-btn active" data-tab="judge" onclick="switchTab('judge')">MAGI JUDGE</button>
    <button class="tab-btn" data-tab="conversations" onclick="switchTab('conversations')">RECORDS</button>
    <button class="tab-btn" data-tab="config" id="tab-config" onclick="switchTab('config')">CONFIG</button>
    <button class="tab-btn" data-tab="admin" id="tab-admin" style="display:none" onclick="switchTab('admin')">ADMIN</button>
  </div>

  <div class="tab-content active" id="tab-judge">
    <div class="magi-container">
      <div class="question-box">
        <textarea id="question-input" placeholder="> 向 MAGI 提交裁决请求..."></textarea>
        <div style="margin-top:10px;display:flex;align-items:center;gap:12px">
          <button class="judge-btn" id="judge-btn" onclick="submitJudge()">▶ EXECUTE JUDGMENT</button>
          <span id="judge-status" style="font-size:11px;color:var(--text-dim)"></span>
        </div>
      </div>
      <div id="judge-result"></div>
    </div>
  </div>

  <div class="tab-content" id="tab-conversations">
    <div class="conv-list">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
        <h3 style="font-size:12px;letter-spacing:2px;color:var(--accent)">CONVERSATION LOG</h3>
        <button class="export-btn" onclick="exportConversations()">⬇ EXPORT</button>
      </div>
      <div id="conv-container"><div class="loading-text">LOADING...</div></div>
    </div>
  </div>

  <div class="tab-content" id="tab-config">
    <div class="config-section">
      <div class="config-group"><h3>GLOBAL API CONFIGURATION</h3>
        <div class="config-row"><label>API BASE URL</label><input type="text" id="cfg-api-base" placeholder="https://api.vveai.com/v1"></div>
        <div class="config-row"><label>DEFAULT API KEY</label><input type="password" id="cfg-api-key" placeholder="sk-***"></div>
      </div>
      <div class="config-group"><h3>MAGI UNIT MODELS</h3>
        <div class="config-row"><label style="color:var(--melchior)">MELCHIOR-01</label><select id="cfg-melchior"><option value="deepseek-v4-pro">deepseek-v4-pro</option><option value="claude-sonnet-4">claude-sonnet-4</option><option value="gpt-4o">gpt-4o</option></select></div>
        <div class="config-row"><label style="color:var(--balthasar)">BALTHASAR-02</label><select id="cfg-balthasar"><option value="deepseek-v4-pro">deepseek-v4-pro</option><option value="claude-sonnet-4">claude-sonnet-4</option><option value="gpt-4o">gpt-4o</option></select></div>
        <div class="config-row"><label style="color:var(--casper)">CASPER-03</label><select id="cfg-casper"><option value="deepseek-v4-pro">deepseek-v4-pro</option><option value="claude-sonnet-4">claude-sonnet-4</option><option value="gpt-4o">gpt-4o</option></select></div>
      </div>
      <button class="save-btn" onclick="saveConfig()">SAVE CONFIGURATION</button>
    </div>
  </div>

  <div class="tab-content" id="tab-admin">
    <div class="admin-section">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
        <h3 style="font-size:12px;letter-spacing:2px;color:var(--accent)">USER MANAGEMENT</h3>
        <button class="save-btn" onclick="showUserModal()">+ NEW USER</button>
      </div>
      <table class="data-table"><thead><tr><th>ID</th><th>USERNAME</th><th>ROLE</th><th>STATUS</th><th>TPM</th><th>TPD</th><th>CREATED</th><th>ACTIONS</th></tr></thead>
      <tbody id="user-tbody"><tr><td colspan="8" class="loading-text">LOADING...</td></tr></tbody></table>
      <div style="margin-top:30px;display:flex;align-items:center;justify-content:space-between">
        <h3 style="font-size:12px;letter-spacing:2px;color:var(--accent)">ALL CONVERSATIONS</h3>
        <button class="export-btn" onclick="exportAllConversations()">⬇ EXPORT ALL</button>
      </div>
      <div id="admin-conv-container" style="margin-top:12px"><div class="loading-text">LOADING...</div></div>
    </div>
  </div>
</div>

<div class="modal-overlay" id="user-modal"><div class="modal-box">
  <h4 id="modal-title">CREATE USER</h4>
  <div class="modal-field"><label>USERNAME</label><input type="text" id="modal-username"></div>
  <div class="modal-field"><label>PASSWORD</label><input type="password" id="modal-password"></div>
  <div class="modal-field"><label>ROLE</label><select id="modal-role"><option value="user">user</option><option value="admin">admin</option></select></div>
  <div class="modal-field"><label>TPM (0=unlimited)</label><input type="number" id="modal-tpm" value="0" min="0"></div>
  <div class="modal-field"><label>TPD (0=unlimited)</label><input type="number" id="modal-tpd" value="0" min="0"></div>
  <input type="hidden" id="modal-edit-id">
  <div class="modal-actions"><button class="cancel" onclick="closeUserModal()">CANCEL</button><button onclick="saveUserModal()">SAVE</button></div>
</div></div>

<div class="toast" id="toast"></div>

<script>
let authToken=localStorage.getItem('magi_token')||'',currentUser=null,allUsers=[];

async function api(p,o={}){const h={'Content-Type':'application/json'};if(authToken)h['Authorization']='Bearer '+authToken;const r=await fetch(p,{...o,headers:{...h,...o.headers}});if(r.status===401){doLogout();throw new Error('Unauthorized')}if(!r.ok){const e=await r.json().catch(()=>({detail:r.statusText}));throw new Error(e.detail||'Request failed')}return r.json()}

function toast(m,e=false){const el=document.getElementById('toast');el.textContent=m;el.className='toast'+(e?' error':'')+' show';setTimeout(()=>el.className='toast',2500)}

async function doLogin(){const u=document.getElementById('login-user').value.trim(),p=document.getElementById('login-pass').value,er=document.getElementById('login-error');er.textContent='';if(!u||!p)return er.textContent='ALL FIELDS REQUIRED';try{const d=await api('/api/auth/login',{method:'POST',body:JSON.stringify({username:u,password:p})});authToken=d.access_token;localStorage.setItem('magi_token',authToken);currentUser=await api('/api/auth/me');showApp()}catch(e){er.textContent=e.message||'AUTH FAILED'}}
document.getElementById('login-pass').addEventListener('keydown',e=>{if(e.key==='Enter')doLogin()});

function doLogout(){authToken='';localStorage.removeItem('magi_token');currentUser=null;document.getElementById('login-page').style.display='flex';document.getElementById('app-page').style.display='none';document.getElementById('login-pass').value=''}

async function showApp(){document.getElementById('login-page').style.display='none';document.getElementById('app-page').style.display='block';const b=document.getElementById('user-badge');b.textContent=currentUser.username+' ['+currentUser.role+']';b.className='user-badge'+(currentUser.role==='admin'?' admin':'');document.getElementById('tab-config').style.display=currentUser.role==='admin'?'':'none';document.getElementById('tab-admin').style.display=currentUser.role==='admin'?'':'none';if(currentUser.role==='admin'){loadConfig();loadUsers();loadAdminConversations()}loadConversations()}

async function init(){if(!authToken)return;try{currentUser=await api('/api/auth/me');showApp()}catch{doLogout()}}
init();

function switchTab(n){document.querySelectorAll('.tab-btn').forEach(b=>b.classList.toggle('active',b.dataset.tab===n));document.querySelectorAll('.tab-content').forEach(c=>c.classList.toggle('active',c.id==='tab-'+n));if(n==='conversations')loadConversations();if(n==='admin'&&currentUser?.role==='admin'){loadUsers();loadAdminConversations()}}

async function submitJudge(){const t=document.getElementById('question-input').value.trim();if(!t)return toast('QUESTION REQUIRED',true);const b=document.getElementById('judge-btn'),s=document.getElementById('judge-status');b.disabled=true;s.textContent='■ MAGI PROCESSING...';try{const d=await api('/api/judge',{method:'POST',body:JSON.stringify({text:t})});renderJudgment(d);s.textContent=''}catch(e){toast(e.message,true);s.textContent=''}b.disabled=false}
document.getElementById('question-input').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey))submitJudge()});

function renderJudgment(d){const el=document.getElementById('judge-result');const uc={melchior:'melchior',balthasar:'balthasar',casper:'casper'};const decs=d.votes.map(v=>v.decision);const ac=decs.filter(x=>x==='approve').length;const fc=ac>=2?'approve':'deny';el.innerHTML=`<div class="votes-grid">${d.votes.map(v=>`<div class="vote-card ${uc[v.unit]||''}"><div class="vote-header"><span class="unit-name">${v.codename}</span><span>${v.role}</span></div><div class="vote-decision ${v.decision}">${v.decision==='approve'?'✓ APPROVE':'✗ DENY'}</div><div class="vote-reason">${esc(v.reasoning)}</div><div class="vote-meta"><span>confidence: ${(v.confidence*100).toFixed(1)}%</span><span>${v.latency_ms}ms</span></div></div>`).join('')}</div><div class="result-banner ${fc}">${fc==='approve'?'✓ RESOLUTION APPROVED':'✗ RESOLUTION DENIED'}<small>CONSENSUS: ${d.consensus} | ${ac}/3 APPROVE | LATENCY: ${d.total_latency_ms}ms</small></div>`}

async function loadConfig(){try{const c=await api('/api/admin/config');document.getElementById('cfg-api-base').value=c.api_base||'';document.getElementById('cfg-api-key').value='';document.getElementById('cfg-api-key').placeholder=c.api_key_masked||'sk-***';for(const u of['melchior','balthasar','casper']){const s=document.getElementById('cfg-'+u);if(s&&c.units&&c.units[u])s.value=c.units[u].model||'deepseek-v4-pro'}}catch{}}

async function saveConfig(){const u={};for(const i of['melchior','balthasar','casper'])u[i]={model:document.getElementById('cfg-'+i).value};const b={api_base:document.getElementById('cfg-api-base').value||undefined,api_key:document.getElementById('cfg-api-key').value||undefined,units:u};try{await api('/api/admin/config',{method:'PUT',body:JSON.stringify(b)});toast('CONFIGURATION SAVED');loadConfig()}catch(e){toast(e.message,true)}}

async function loadUsers(){try{allUsers=await api('/api/admin/users');document.getElementById('user-tbody').innerHTML=allUsers.map(u=>`<tr><td>${u.id.slice(0,8)}…</td><td>${u.username}</td><td>${u.role}</td><td style="color:${u.is_active!==false?'var(--accent)':'var(--warn)'}">${u.is_active!==false?'ACTIVE':'DISABLED'}</td><td>${u.tpm_limit||'∞'}</td><td>${u.tpd_limit||'∞'}</td><td>${u.created_at?new Date(u.created_at).toLocaleDateString():'-'}</td><td><button class="tbl-btn edit" onclick="editUser('${u.id}')">EDIT</button><button class="tbl-btn del" onclick="deleteUser('${u.id}','${u.username}')">DEL</button></td></tr>`).join('')}catch{}}

function showUserModal(id){document.getElementById('user-modal').classList.add('show');document.getElementById('modal-title').textContent=id?'EDIT USER':'CREATE USER';document.getElementById('modal-edit-id').value=id||'';if(!id){document.getElementById('modal-username').value='';document.getElementById('modal-password').value='';document.getElementById('modal-role').value='user';document.getElementById('modal-tpm').value='0';document.getElementById('modal-tpd').value='0'}}
function closeUserModal(){document.getElementById('user-modal').classList.remove('show')}
function editUser(id){const u=allUsers.find(x=>x.id===id);if(!u)return;showUserModal(id);document.getElementById('modal-username').value=u.username;document.getElementById('modal-password').value='';document.getElementById('modal-role').value=u.role;document.getElementById('modal-tpm').value=u.tpm_limit||0;document.getElementById('modal-tpd').value=u.tpd_limit||0}

async function saveUserModal(){const eid=document.getElementById('modal-edit-id').value;const b={username:document.getElementById('modal-username').value.trim(),role:document.getElementById('modal-role').value,tpm_limit:parseInt(document.getElementById('modal-tpm').value)||0,tpd_limit:parseInt(document.getElementById('modal-tpd').value)||0};const pw=document.getElementById('modal-password').value;if(pw)b.password=pw;try{if(eid){await api('/api/admin/users/'+eid,{method:'PUT',body:JSON.stringify(b)});toast('USER UPDATED')}else{if(!pw)return toast('PASSWORD REQUIRED',true);await api('/api/admin/users',{method:'POST',body:JSON.stringify(b)});toast('USER CREATED')}closeUserModal();loadUsers()}catch(e){toast(e.message,true)}}

async function deleteUser(id,un){if(un==='admin')return toast('CANNOT DELETE ADMIN',true);if(!confirm('DELETE USER: '+un+'?'))return;try{await api('/api/admin/users/'+id,{method:'DELETE'});toast('USER DELETED');loadUsers()}catch(e){toast(e.message,true)}}

async function loadConversations(){const c=document.getElementById('conv-container');c.innerHTML='<div class="loading-text">LOADING...</div>';try{const d=await api('/api/conversations');if(!d.length){c.innerHTML='<div class="empty-text">NO CONVERSATION RECORDS</div>';return}c.innerHTML=d.map(x=>renderConv(x)).join('')}catch{c.innerHTML='<div class="empty-text">FAILED TO LOAD</div>'}}

async function loadAdminConversations(){const c=document.getElementById('admin-conv-container');c.innerHTML='<div class="loading-text">LOADING...</div>';try{const d=await api('/api/admin/conversations');if(!d.length){c.innerHTML='<div class="empty-text">NO CONVERSATION RECORDS</div>';return}c.innerHTML=d.map(x=>renderConv(x,true)).join('')}catch{c.innerHTML='<div class="empty-text">FAILED TO LOAD</div>'}}

function renderConv(c,su=false){const ac=c.votes?c.votes.filter(v=>v.decision==='approve').length:0;const fc=ac>=2?'approve':'deny';const ts=c.timestamp?new Date(c.timestamp).toLocaleString():'-';return`<div class="conv-entry" onclick="this.classList.toggle('expanded')"><div class="conv-q">${su?'<span style=color:var(--accent2)>['+(c.username||c.user_id?.slice(0,8))+']</span> ':''}${esc(c.question||'')}</div><div class="conv-result ${fc}">${fc==='approve'?'✓ APPROVED':'✗ DENIED'} (${ac}/3)</div><div class="conv-time">${ts} | ${c.total_latency_ms||'?'}ms</div><div class="conv-detail">${(c.votes||[]).map(v=>`<div class="conv-vote-mini"><strong>${v.codename||v.unit}</strong>: ${v.decision==='approve'?'✓':'✗'} ${(v.confidence*100).toFixed(0)}% — ${esc(v.reasoning||'').slice(0,200)}</div>`).join('')}</div></div>`}

function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML}

async function exportConversations(){try{const d=await api('/api/conversations/export');downloadJSON(d,'magi-my-conversations.json');toast('EXPORT COMPLETE')}catch(e){toast(e.message,true)}}

async function exportAllConversations(){try{const d=await api('/api/admin/conversations/export');downloadJSON(d,'magi-all-conversations.json');toast('EXPORT COMPLETE')}catch(e){toast(e.message,true)}}

function downloadJSON(d,f){const b=new Blob([JSON.stringify(d,null,2)],{type:'application/json'}),u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download=f;a.click();URL.revokeObjectURL(u)}
</script>
</body>
</html>'''
