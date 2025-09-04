// DHRMS Simple behaviors: signup/login alerts, routing, validation, popup
(function(){
  function $(sel,root=document){return root.querySelector(sel)}
  function $all(sel,root=document){return Array.from(root.querySelectorAll(sel))}

  // localStorage helpers for demo auth
  const KEY_USERS = 'dhrms_users';
  const KEY_CURRENT = 'dhrms_current_user';
  function getUsers(){
    try{ return JSON.parse(localStorage.getItem(KEY_USERS)||'[]') }catch(e){ return [] }
  }
  function saveUsers(list){ localStorage.setItem(KEY_USERS, JSON.stringify(list)) }
  function setCurrent(user){ localStorage.setItem(KEY_CURRENT, JSON.stringify(user)) }
  function toast(message){
    const el = document.createElement('div');
    el.textContent = message;
    el.style.position='fixed';
    el.style.left='50%';
    el.style.bottom='24px';
    el.style.transform='translateX(-50%)';
    el.style.padding='10px 14px';
    el.style.borderRadius='12px';
    el.style.background='rgba(0,0,0,.6)';
    el.style.color='#fff';
    el.style.zIndex='9999';
    el.style.backdropFilter='blur(6px)';
    document.body.appendChild(el);
    setTimeout(()=>{ el.style.transition='opacity .3s'; el.style.opacity='0'; setTimeout(()=>el.remove(),300); }, 1200);
  }

  // Utility: basic required validation
  function validate(form){
    let ok=true;
    $all('input[required], select[required]', form).forEach(el=>{
      const v=(el.value||'').trim();
      if(!v){
        el.style.boxShadow='0 0 0 3px rgba(239,68,68,.35)';
        ok=false;
      } else {
        el.style.boxShadow='none';
      }
    });
    return ok;
  }

  const page = document.body.getAttribute('data-page');
  const currentFile = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  // Corrected flow order across forms (includes medical.html)
  const sequence = ['workers.html','health_records.html','vaccinations.html','medical.html','facilities.html'];
  function nextInSequence(file){
    const i = sequence.indexOf(file);
    if(i === -1) return null;
    return sequence[i+1] || null;
  }

  // Inject shared navbar with links and theme toggle
  function injectNavbar(){
    if($('#site-nav')) return;
    const nav = document.createElement('nav');
    nav.id='site-nav';
    nav.style.position='sticky';
    nav.style.top='0';
    nav.style.zIndex='10';
    nav.style.padding='12px 16px';
    nav.style.margin='0 auto 12px';
    nav.style.maxWidth='1000px';
    nav.style.display='flex';
    nav.style.alignItems='center';
    nav.style.gap='14px';
    nav.style.backdropFilter='blur(10px)';
    nav.style.background='var(--card)';
    nav.style.border='1px solid var(--soft)';
    nav.style.borderRadius='14px';
    const links = [
      {href:'dashboard.html', label:'Dashboard'},
      {href:'index.html', label:'Login'},
      {href:'signup.html', label:'Sign Up'},
      {href:'workers.html', label:'Workers'},
      {href:'health_records.html', label:'Health Records'},
      {href:'vaccinations.html', label:'Vaccinations'},
      {href:'medical.html', label:'Medical Visits'},
      {href:'facilities.html', label:'Facilities'}
    ];
    const left = document.createElement('div');
    left.style.display='flex'; left.style.gap='12px'; left.style.flexWrap='wrap';
    links.forEach(l=>{
      const a = document.createElement('a');
      a.href=l.href; a.textContent=l.label; a.className='link';
      if(currentFile===l.href.toLowerCase()) a.style.color='var(--text)';
      left.appendChild(a);
    });
    const right = document.createElement('div');
    right.style.marginLeft='auto';
    const toggle=document.createElement('button');
    toggle.className='btn btn-ghost';
    toggle.textContent='Toggle Theme';
    toggle.addEventListener('click',()=>{
      const isLight = document.body.classList.toggle('theme-light');
      if(isLight){ document.body.classList.remove('theme-dark') } else { document.body.classList.add('theme-dark') }
      localStorage.setItem('dhrms_theme', document.body.classList.contains('theme-light') ? 'light' : 'dark');
    });
    right.appendChild(toggle);
    nav.appendChild(left); nav.appendChild(right);
    document.body.prepend(nav);
  }

  // Apply saved theme on load
  (function applySavedTheme(){
    const saved = localStorage.getItem('dhrms_theme');
    if(saved==='light'){ document.body.classList.add('theme-light') }
    else { document.body.classList.add('theme-dark') }
  })();

  // Page load/leave transitions
  function enablePageTransitions(){
    document.body.classList.add('page-enter');
    $all('a[href]')
      .filter(a=>!a.target && a.getAttribute('href') && !a.getAttribute('href').startsWith('#'))
      .forEach(a=>{
        a.addEventListener('click', (e)=>{
          const url = a.getAttribute('href');
          if(!url) return;
          e.preventDefault();
          document.body.classList.add('page-leave');
          setTimeout(()=>{ window.location.href = url; }, 220);
        });
      });
  }

  // Signup page
  if(page==='signup'){
    const form=$('#signupForm');
    form?.addEventListener('submit',e=>{
      e.preventDefault();
      if(!validate(form)) return;
      const id = form.querySelector('input[name="id"]').value.trim();
      const fullName = form.querySelector('input[name="full_name"]').value.trim();
      const username = form.querySelector('input[name="username"]').value.trim();
      const email = form.querySelector('input[name="email"]').value.trim();
      const phone = form.querySelector('input[name="phone"]').value.trim();
      const password = form.querySelector('input[name="password"]').value;

      const users = getUsers();
      const exists = users.some(u => u.id===id || u.username===username || u.email===email || u.phone===phone);
      if(exists){
        alert('User with same ID/Username/Email/Phone already exists.');
        return;
      }
      users.push({ id, fullName, username, email, phone, password });
      saveUsers(users);
      toast('Registration successful');
      setTimeout(()=>{ window.location.href='index.html'; }, 800);
    });
  }

  // Login page
  if(page==='login'){
    const form=$('#loginForm');
    form?.addEventListener('submit',e=>{
      e.preventDefault();
      // only password is strictly required; at least one identifier must be provided
      const id = form.querySelector('input[name="id"]').value.trim();
      const username = form.querySelector('input[name="username"]').value.trim();
      const email = form.querySelector('input[name="email"]').value.trim();
      const phone = form.querySelector('input[name="phone"]').value.trim();
      const password = form.querySelector('input[name="password"]').value;

      if(!password){
        alert('Please enter your password.');
        return;
      }
      if(!(id||username||email||phone)){
        alert('Enter at least one of ID / Username / Email / Phone.');
        return;
      }
      const users = getUsers();
      const match = users.find(u => (u.id===id || u.username===username || u.email===email || u.phone===phone) && u.password===password);
      if(!match){
        alert('Invalid credentials. Please check and try again.');
        return;
      }
      setCurrent({ id: match.id, username: match.username, email: match.email });
      toast('Login successful');
      window.location.href='workers.html';
    });
  }

  // Forms: save data to localStorage and navigate to next
  if(page==='form'){
    const form=$('#recordForm');
    const popup=$('#popup');
    const closeBtn=$('#closePopup');
    // Require login to access forms
    try{ if(!JSON.parse(localStorage.getItem(KEY_CURRENT)||'null')) { window.location.href='index.html'; } }catch(e){}
    form?.addEventListener('submit',e=>{
      e.preventDefault();
      if(!validate(form)) return;
      // Save form values
      const data = {};
      $all('input,select', form).forEach(el=>{
        const key = el.name || (el.previousElementSibling && el.previousElementSibling.textContent ? el.previousElementSibling.textContent.toLowerCase().replace(/\s+/g,'_') : 'field');
        data[key] = el.value;
      });
      const file = (location.pathname.split('/').pop()||'').toLowerCase();
      localStorage.setItem('dhrms_form_'+file, JSON.stringify(data));
      popup.classList.add('show');
    });
    closeBtn?.addEventListener('click',()=>{
      popup.classList.remove('show');
      form.reset();
      const next = nextInSequence(currentFile);
      if(next){ window.location.href = next; }
    });
    popup?.addEventListener('click',(e)=>{
      if(e.target===popup){ popup.classList.remove('show'); }
    })
  }
  // Dashboard page
  if(page==='dashboard'){
    // must be logged in
    try{ if(!JSON.parse(localStorage.getItem(KEY_CURRENT)||'null')) { window.location.href='index.html'; return; } }catch(e){}
    const content = document.getElementById('dashboardContent');
    function block(title, obj){
      const wrap = document.createElement('div');
      wrap.className='card';
      const inner = document.createElement('div');
      inner.className='card-inner';
      const h = document.createElement('h3'); h.textContent = title; h.style.marginTop='0';
      inner.appendChild(h);
      const pre = document.createElement('pre'); pre.style.whiteSpace='pre-wrap'; pre.style.margin='0'; pre.textContent = JSON.stringify(obj, null, 2);
      inner.appendChild(pre);
      wrap.appendChild(inner);
      return wrap;
    }
    const current = JSON.parse(localStorage.getItem(KEY_CURRENT)||'null');
    const users = JSON.parse(localStorage.getItem(KEY_USERS)||'[]');
    const files=['workers.html','health_records.html','vaccinations.html','medical.html','facilities.html'];
    content.appendChild(block('Current User', current||{}));
    content.appendChild(block('Registered Users', users));
    files.forEach(f=>{
      const data = JSON.parse(localStorage.getItem('dhrms_form_'+f)||'null');
      content.appendChild(block('Form: '+f, data||{}));
    });
    const logoutBtn = document.getElementById('logoutBtn');
    const clearBtn = document.getElementById('clearDataBtn');
    logoutBtn?.addEventListener('click',()=>{ localStorage.removeItem(KEY_CURRENT); toast('Logged out'); setTimeout(()=>location.href='index.html',400) });
    clearBtn?.addEventListener('click',()=>{ localStorage.clear(); toast('All local data cleared'); setTimeout(()=>location.reload(),400) });
  }
  // Global init
  injectNavbar();
  enablePageTransitions();
})();

// Button ripple enhancement
document.addEventListener('click', function(e){
  const target = e.target.closest('.btn');
  if(!target) return;
  const rect = target.getBoundingClientRect();
  const span = document.createElement('span');
  span.className='ripple';
  span.style.left = (e.clientX - rect.left) + 'px';
  span.style.top = (e.clientY - rect.top) + 'px';
  target.appendChild(span);
  setTimeout(()=>span.remove(), 600);
});


