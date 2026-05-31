const CNL=String.fromCharCode(10);
function fmt(t){return t?t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').split(CNL).join('<br>'):''}
function esc(s){return s?s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').split(CNL).join(' '):''}

let state={token:null,user:null};

function showPage(id){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  let el=document.getElementById(id+'-page');
  if(el)el.classList.add('active');
  if(id==='admin')loadUsers();
  if(id==='history')loadHistory();
  if(id==='settings')loadSettings();
}

async function doLogin(){
  let u=document.getElementById('lu').value.trim(),p=document.getElementById('lp').value;
  if(!u||!p)return;
  let r=await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
  let d=await r.json();
  if(d.access_token){state.token=d.access_token;localStorage.setItem('magi_token',d.access_token);me()}
  else{document.getElementById('login-err').textContent=d.detail||'登录失败'}
}

async function doRegister(){
  let u=document.getElementById('ru').value.trim(),p=document.getElementById('rp').value;
  if(!u||p.length<6){document.getElementById('reg-err').textContent='用户名和6位以上密码';return}
  let r=await fetch('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
  let d=await r.json();
  if(d.access_token){state.token=d.access_token;localStorage.setItem('magi_token',d.access_token);me()}
  else{document.getElementById('reg-err').textContent=d.detail||'注册失败'}
}

function toggleReg(){
  document.getElementById('login-page').classList.toggle('active');
  document.getElementById('reg-page').classList.toggle('active');
}

function doLogout(){state.token=null;localStorage.removeItem('magi_token');showPage('login')}

async function me(){
  let r=await fetch('/api/auth/me',{headers:{'Authorization':'Bearer '+state.token}});
  if(!r.ok){doLogout();return}
  state.user=await r.json();
  document.getElementById('user-label').textContent=state.user.username+'('+state.user.role+')';
  document.getElementById('btn-admin').style.display=state.user.role==='admin'?'inline':'none';
  showPage('main');
}

async function submitQuestion(){
  let q=document.getElementById('question').value.trim();
  if(!q)return;
  let btn=document.getElementById('submit-btn');
  btn.disabled=true;btn.textContent='裁决中...';
  ['melchior','balthasar','casper'].forEach(u=>{
    document.getElementById('result-'+u).innerHTML='<span class="thinking">⟳ 思考中...</span>';
  });
  document.getElementById('verdict').style.display='none';
  try{
    let r=await fetch('/api/judge?question='+encodeURIComponent(q),{method:'POST',headers:{'Authorization':'Bearer '+state.token}});
    let data=await r.json();
    const emoji={approve:'✅',deny:'❌',abstain:'➖'};
    const cls={approve:'decision-approve',deny:'decision-deny',abstain:'decision-abstain'};
    data.votes.forEach(v=>{
      document.getElementById('result-'+v.unit).innerHTML=
        '<div class="'+cls[v.decision]+'">'+emoji[v.decision]+' '+v.decision.toUpperCase()+'</div>'+
        '<div style="margin-top:6px">'+fmt(v.reasoning)+'</div>'+
        '<div class="latency">⏱'+v.latency_ms+'ms</div>';
    });
    let vCls=data.final_decision==='approve'?'approve':'deny';
    let vText=data.final_decision==='approve'?'✅ 提案承认':'❌ 提案否认';
    document.getElementById('verdict-text').textContent=vText;
    document.getElementById('verdict').className='verdict-box '+vCls;
    document.getElementById('verdict').style.display='block';
  }catch(e){
    ['melchior','balthasar','casper'].forEach(u=>{
      document.getElementById('result-'+u).innerHTML='<span style="color:#ff0040">通信错误</span>';
    });
  }
  btn.disabled=false;btn.textContent='提交裁决';
  document.getElementById('question').value='';
}

async function loadUsers(){
  let r=await fetch('/api/admin/users',{headers:{'Authorization':'Bearer '+state.token}});
  let users=await r.json();
  let h='';
  users.forEach(u=>{
    h+='<div class="user-row"><span class="name">'+esc(u.username)+'</span><span class="role">'+u.role+'</span>'+
       '<span><button onclick="delUser(\''+u.id+'\')">删除</button></span></div>';
  });
  document.getElementById('user-list').innerHTML=h;
  let cr=await fetch('/api/admin/config',{headers:{'Authorization':'Bearer '+state.token}});
  let cfg=await cr.json();
  document.getElementById('global-config').innerHTML=
    '<label>API Base</label><input id="gc-base" value="'+esc(cfg.api_base||'')+'">'+
    '<label>API Key</label><input id="gc-key" type="password" value="'+esc(cfg.api_key||'')+'">'+
    '<label>Model</label><input id="gc-model" value="'+esc(cfg.model||'')+'">'+
    '<label>Reasoning Effort</label><input id="gc-effort" value="'+esc(cfg.reasoning_effort||'medium')+'">'+
    '<button onclick="saveGlobalConfig()">保存全局配置</button>';
}

async function delUser(id){
  if(!confirm('确定删除？'))return;
  await fetch('/api/admin/users/'+id,{method:'DELETE',headers:{'Authorization':'Bearer '+state.token}});
  loadUsers();
}

async function saveGlobalConfig(){
  let body={api_base:document.getElementById('gc-base').value,api_key:document.getElementById('gc-key').value,
            model:document.getElementById('gc-model').value,reasoning_effort:document.getElementById('gc-effort').value};
  await fetch('/api/admin/config',{method:'PUT',headers:{'Authorization':'Bearer '+state.token,'Content-Type':'application/json'},body:JSON.stringify(body)});
  alert('已保存');
}

async function loadHistory(){
  let r=await fetch('/api/conversations',{headers:{'Authorization':'Bearer '+state.token}});
  let list=await r.json();
  let h='';
  list.forEach(c=>{
    h+='<div class="conv-card" onclick="toggleConv(this)">'+
       '<div class="conv-q">'+esc(c.question)+'</div>'+
       '<div class="conv-a" style="display:none">'+fmt(c.consensus||'')+'</div>'+
       '<div class="conv-meta">'+(c.final_decision||'')+' · '+new Date(c.timestamp).toLocaleString()+'</div></div>';
  });
  document.getElementById('history-list').innerHTML=h||'<p class="dim">暂无历史</p>';
}

function toggleConv(el){
  let a=el.querySelector('.conv-a');
  a.style.display=a.style.display==='none'?'block':'none';
}

function exportConvs(fmt){
  let url='/api/conversations/export?format='+(fmt||'json');
  fetch(url,{headers:{'Authorization':'Bearer '+state.token}}).then(r=>r.blob()).then(b=>{
    let a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='magi_export.'+(fmt||'json');a.click()
  });
}

async function loadSettings(){
  let r=await fetch('/api/auth/me',{headers:{'Authorization':'Bearer '+state.token}});
  let u=await r.json();
  document.getElementById('s-apikey').value='';
  document.getElementById('s-apibase').value=u.api_base||'';
  document.getElementById('s-model').value=u.model||'';
}

async function saveSettings(){
  let body={api_key:document.getElementById('s-apikey').value,api_base:document.getElementById('s-apibase').value,
            model:document.getElementById('s-model').value};
  await fetch('/api/auth/settings',{method:'PUT',headers:{'Authorization':'Bearer '+state.token,'Content-Type':'application/json'},body:JSON.stringify(body)});
  document.getElementById('settings-msg').textContent='✅ 已保存';
}

document.getElementById('question').addEventListener('keydown',e=>{if(e.ctrlKey&&e.key==='Enter')submitQuestion()});

window.onload=function(){
  let t=localStorage.getItem('magi_token');
  if(t){state.token=t;me()}
  else{showPage('login')}
};
