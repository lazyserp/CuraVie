// DHRMS Healthcare Design System - Enhanced with Mobile Navigation & Language Support
(function(){
  function $(sel,root=document){return root.querySelector(sel)}
  function $all(sel,root=document){return Array.from(root.querySelectorAll(sel))}

  // Mobile Navigation Toggle
  function initMobileNavigation() {
    const mobileToggle = $('#mobile-menu-toggle');
    const mobileNav = $('#mobile-nav');
    
    if (mobileToggle && mobileNav) {
      mobileToggle.addEventListener('click', function() {
        mobileNav.classList.toggle('active');
        // Update toggle icon
        mobileToggle.textContent = mobileNav.classList.contains('active') ? '✕' : '☰';
      });

      // Close mobile nav when clicking outside
      document.addEventListener('click', function(e) {
        if (!mobileToggle.contains(e.target) && !mobileNav.contains(e.target)) {
          mobileNav.classList.remove('active');
          mobileToggle.textContent = '☰';
        }
      });

      // Close mobile nav when clicking on a link
      $all('.mobile-nav .nav-link').forEach(link => {
        link.addEventListener('click', function() {
          mobileNav.classList.remove('active');
          mobileToggle.textContent = '☰';
        });
      });
    }
  }

  // Language Switcher
  function initLanguageSwitcher() {
    const languageSelect = $('#language-select');
    
    if (languageSelect) {
      // Load saved language preference
      const savedLang = localStorage.getItem('dhrms_language') || 'en';
      languageSelect.value = savedLang;
      
      languageSelect.addEventListener('change', function() {
        const selectedLang = this.value;
        localStorage.setItem('dhrms_language', selectedLang);
        
        // Simple language switching (you can expand this with actual translations)
        toast(`Language switched to ${this.options[this.selectedIndex].text}`);
        
        // You can add actual translation logic here
        updateLanguageContent(selectedLang);
      });
    }
  }

  // Simple language content updates (expand as needed)
  function updateLanguageContent(lang) {
    const translations = {
      'en': {
        'hero-title': 'AI-powered Digital Health Record Platform for Migrant Workers in Kerala',
        'hero-subtitle': 'Ensure secure and accessible health records for migrant workers'
      },
      'hi': {
        'hero-title': 'केरल में प्रवासी श्रमिकों के लिए AI-संचालित डिजिटल स्वास्थ्य रिकॉर्ड प्लेटफॉर्म',
        'hero-subtitle': 'प्रवासी श्रमिकों के लिए सुरक्षित और सुलभ स्वास्थ्य रिकॉर्ड सुनिश्चित करें'
      },
      'ml': {
        'hero-title': 'കേരളത്തിലെ കുടിയേറ്റ തൊഴിലാളികൾക്കായി AI-പവർഡ് ഡിജിറ്റൽ ഹെൽത്ത് റെക്കോർഡ് പ്ലാറ്റ്ഫോം',
        'hero-subtitle': 'കുടിയേറ്റ തൊഴിലാളികൾക്ക് സുരക്ഷിതവും ആക്സസ് ചെയ്യാവുന്നതുമായ ആരോഗ്യ രേഖകൾ ഉറപ്പാക്കുക'
      },
      'ta': {
        'hero-title': 'கேரளாவில் புலம்பெயர்ந்த தொழிலாளர்களுக்கான AI-இயங்கும் டிஜிட்டல் சுகாதார பதிவு தளம்',
        'hero-subtitle': 'புலம்பெயர்ந்த தொழிலாளர்களுக்கு பாதுகாப்பான மற்றும் அணுகக்கூடிய சுகாதார பதிவுகளை உறுதி செய்யுங்கள்'
      }
    };

    // Update content based on selected language
    const heroTitle = $('.hero-title');
    const heroSubtitle = $('.hero-subtitle');
    
    if (heroTitle && translations[lang] && translations[lang]['hero-title']) {
      heroTitle.textContent = translations[lang]['hero-title'];
    }
    
    if (heroSubtitle && translations[lang] && translations[lang]['hero-subtitle']) {
      heroSubtitle.textContent = translations[lang]['hero-subtitle'];
    }
  }

  // Smooth scroll animations for feature cards
  function initScrollAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }
      });
    }, observerOptions);

    // Observe feature cards
    $all('.feature-card').forEach(card => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(30px)';
      card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      observer.observe(card);
    });
  }

  // Enhanced form validation with healthcare-specific checks
  function enhancedValidate(form) {
    let isValid = true;
    const inputs = $all('input[required], select[required]', form);
    
    inputs.forEach(input => {
      const value = (input.value || '').trim();
      let fieldValid = true;
      
      // Basic required field check
      if (!value) {
        fieldValid = false;
      }
      
      // Healthcare-specific validations
      if (input.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
          fieldValid = false;
        }
      }
      
      if (input.type === 'tel' && value) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        if (!phoneRegex.test(value.replace(/\s/g, ''))) {
          fieldValid = false;
        }
      }
      
      // Visual feedback
      if (fieldValid) {
        input.style.borderColor = 'var(--secondary-color)';
        input.style.boxShadow = '0 0 0 3px rgba(76, 175, 80, 0.1)';
      } else {
        input.style.borderColor = 'var(--accent-color)';
        input.style.boxShadow = '0 0 0 3px rgba(255, 112, 67, 0.2)';
        isValid = false;
      }
    });
    
    return isValid;
  }

  // localStorage helpers for demo auth
  const KEY_USERS = 'dhrms_users';
  const KEY_CURRENT = 'dhrms_current_user';
  const KEY_ADMIN = 'dhrms_admin';
  
  // Admin credentials (in a real app, this would be server-side)
  const ADMIN_CREDENTIALS = {
    username: 'admin',
    password: 'admin123',
    email: 'admin@dhrms.com',
    fullName: 'System Administrator',
    role: 'admin'
  };
  
  function getUsers(){
    try{ return JSON.parse(localStorage.getItem(KEY_USERS)||'[]') }catch(e){ return [] }
  }
  function saveUsers(list){ localStorage.setItem(KEY_USERS, JSON.stringify(list)) }
  function setCurrent(user){ localStorage.setItem(KEY_CURRENT, JSON.stringify(user)) }
  function getCurrentUser(){
    try{ return JSON.parse(localStorage.getItem(KEY_CURRENT)||'null') }catch(e){ return null }
  }
  function clearCurrentUser(){ localStorage.removeItem(KEY_CURRENT) }
  function isAdmin(user){
    return user && (user.role === 'admin' || user.username === 'admin');
  }
  function handleLogout(){
    clearCurrentUser();
    toast('Logged out successfully');
    setTimeout(()=>{ window.location.href='index.html'; }, 800);
  }
  
  function toggleUserProfile(){
    const dropdown = document.getElementById('userProfileDropdown');
    if(dropdown){
      const isVisible = dropdown.style.display === 'block';
      dropdown.style.display = isVisible ? 'none' : 'block';
      
      // Close dropdown when clicking outside
      if(!isVisible){
        setTimeout(() => {
          document.addEventListener('click', closeUserProfile);
        }, 100);
      }
    }
  }
  
  function closeUserProfile(){
    const dropdown = document.getElementById('userProfileDropdown');
    if(dropdown){
      dropdown.style.display = 'none';
    }
    document.removeEventListener('click', closeUserProfile);
  }
  
  function toggleMobileUserProfile(){
    const mobileProfile = document.getElementById('mobileUserProfile');
    if(mobileProfile){
      const isVisible = mobileProfile.style.display === 'block';
      mobileProfile.style.display = isVisible ? 'none' : 'block';
    }
  }
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
    
    const currentUser = getCurrentUser();
    const isLoggedIn = !!currentUser;
    
    // Different links based on login status and admin role
    let links;
    if(isLoggedIn){
      links = [
        {href:'workers.html', label:'Workers'},
        {href:'health_records.html', label:'Health Records'},
        {href:'vaccinations.html', label:'Vaccinations'},
        {href:'medical.html', label:'Medical Visits'},
        {href:'facilities.html', label:'Facilities'}
      ];
      // Only show dashboard for admin users
      if(isAdmin(currentUser)){
        links.push({href:'dashboard.html', label:'Dashboard'});
      }
    } else {
      links = [
        {href:'index.html', label:'Home'},
        {href:'signin.html', label:'Sign In'},
        {href:'signup.html', label:'Sign Up'}
      ];
    }
    
    const left = document.createElement('div');
    left.style.display='flex'; left.style.gap='12px'; left.style.flexWrap='wrap'; left.style.flex='1';
    
    links.forEach(l=>{
      const a = document.createElement('a');
      a.href=l.href; a.textContent=l.label; a.className='link';
      if(currentFile===l.href.toLowerCase()){
        a.classList.add('active');
        a.setAttribute('aria-current','page');
      }
      left.appendChild(a);
    });
    
    // Add user info and logout button if logged in
    if(isLoggedIn){
      const right = document.createElement('div');
      right.style.display='flex'; right.style.alignItems='center'; right.style.gap='12px';
      
      // User profile dropdown
      const userProfileContainer = document.createElement('div');
      userProfileContainer.style.position = 'relative';
      userProfileContainer.style.display = 'inline-block';
      
      const userInfo = document.createElement('button');
      userInfo.textContent = `👤 ${currentUser.fullName || currentUser.username || 'User'}`;
      userInfo.style.fontSize='14px';
      userInfo.style.color='var(--text)';
      userInfo.style.fontWeight='500';
      userInfo.style.background='transparent';
      userInfo.style.border='none';
      userInfo.style.cursor='pointer';
      userInfo.style.padding='8px 12px';
      userInfo.style.borderRadius='8px';
      userInfo.style.transition='all 0.2s ease';
      userInfo.addEventListener('mouseenter', () => {
        userInfo.style.background='var(--soft)';
      });
      userInfo.addEventListener('mouseleave', () => {
        userInfo.style.background='transparent';
      });
      userInfo.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleUserProfile();
      });
      
      // User profile dropdown
      const userProfileDropdown = document.createElement('div');
      userProfileDropdown.id = 'userProfileDropdown';
      userProfileDropdown.style.position = 'absolute';
      userProfileDropdown.style.top = '100%';
      userProfileDropdown.style.right = '0';
      userProfileDropdown.style.background = 'var(--card)';
      userProfileDropdown.style.border = '1px solid var(--soft)';
      userProfileDropdown.style.borderRadius = '12px';
      userProfileDropdown.style.boxShadow = '0 8px 32px rgba(0,0,0,0.1)';
      userProfileDropdown.style.padding = '1rem';
      userProfileDropdown.style.minWidth = '280px';
      userProfileDropdown.style.zIndex = '1000';
      userProfileDropdown.style.display = 'none';
      userProfileDropdown.style.backdropFilter = 'blur(10px)';
      
      // Populate user profile info
      const isAdminUser = isAdmin(currentUser);
      userProfileDropdown.innerHTML = `
        <div style="text-align: center; margin-bottom: 1rem;">
          <div style="width: 60px; height: 60px; background: linear-gradient(135deg, ${isAdminUser ? 'var(--danger), var(--accent)' : 'var(--brand), var(--brand2)'}); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.5rem; font-size: 24px;">
            ${isAdminUser ? '🔐' : '👤'}
          </div>
          <h3 style="margin: 0; color: var(--text); font-size: 1.1rem;">${currentUser.fullName || 'User'}</h3>
          <p style="margin: 0.25rem 0 0 0; color: var(--muted); font-size: 0.9rem;">@${currentUser.username}</p>
          ${isAdminUser ? '<div style="background: var(--danger); color: white; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.75rem; margin-top: 0.5rem; display: inline-block;">ADMIN</div>' : ''}
        </div>
        <div style="border-top: 1px solid var(--soft); padding-top: 0.75rem;">
          <div style="display: grid; gap: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: var(--muted); font-size: 0.85rem;">📧 Email:</span>
              <span style="color: var(--text); font-size: 0.85rem;">${currentUser.email}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: var(--muted); font-size: 0.85rem;">📱 Phone:</span>
              <span style="color: var(--text); font-size: 0.85rem;">${currentUser.phone || 'Not provided'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: var(--muted); font-size: 0.85rem;">🆔 User ID:</span>
              <span style="color: var(--text); font-size: 0.85rem;">${currentUser.id}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: var(--muted); font-size: 0.85rem;">⚧ Gender:</span>
              <span style="color: var(--text); font-size: 0.85rem;">${currentUser.gender ? currentUser.gender.charAt(0).toUpperCase() + currentUser.gender.slice(1) : 'Not provided'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: var(--muted); font-size: 0.85rem;">🎂 Date of Birth:</span>
              <span style="color: var(--text); font-size: 0.85rem;">${currentUser.dob || 'Not provided'}</span>
            </div>
          </div>
        </div>
      `;
      
      userProfileContainer.appendChild(userInfo);
      userProfileContainer.appendChild(userProfileDropdown);
      
      const logoutBtn = document.createElement('button');
      logoutBtn.textContent = '🚪 Logout';
      logoutBtn.className = 'btn btn-secondary';
      logoutBtn.style.padding = '6px 12px';
      logoutBtn.style.fontSize = '14px';
      logoutBtn.addEventListener('click', handleLogout);
      
      right.appendChild(userProfileContainer);
      right.appendChild(logoutBtn);
      nav.appendChild(right);
    }
    
    nav.appendChild(left);
    document.body.prepend(nav);
  }

  // Apply light theme by default
  (function applyDefaultTheme(){
    document.body.classList.add('theme-light');
  })();

  // Update header based on login status
  function updateHeaderForLoginStatus(){
    const currentUser = getCurrentUser();
    const headerActions = document.querySelector('.header-actions');
    const mobileNav = document.querySelector('.mobile-nav .nav');
    
    if(currentUser && headerActions){
      // Update desktop header
      const loginBtn = headerActions.querySelector('a[href="signin.html"]');
      if(loginBtn){
        loginBtn.textContent = `👤 ${currentUser.fullName || currentUser.username || 'User'}`;
        loginBtn.href = 'dashboard.html';
        loginBtn.className = 'btn btn-secondary';
        
        // Add logout button
        const logoutBtn = document.createElement('button');
        logoutBtn.textContent = '🚪 Logout';
        logoutBtn.className = 'btn btn-primary';
        logoutBtn.style.marginLeft = '8px';
        logoutBtn.addEventListener('click', handleLogout);
        headerActions.insertBefore(logoutBtn, loginBtn);
      }
    }
    
    if(currentUser && mobileNav){
      // Update mobile nav
      const loginLink = mobileNav.querySelector('a[href="signin.html"]');
      if(loginLink){
        loginLink.textContent = `👤 ${currentUser.fullName || currentUser.username || 'User'}`;
        loginLink.href = '#';
        loginLink.addEventListener('click', (e) => {
          e.preventDefault();
          toggleMobileUserProfile();
        });
        
        // Add user profile info to mobile nav
        const userProfileInfo = document.createElement('div');
        userProfileInfo.id = 'mobileUserProfile';
        userProfileInfo.style.display = 'none';
        userProfileInfo.style.padding = '1rem';
        userProfileInfo.style.background = 'var(--soft)';
        userProfileInfo.style.borderRadius = '8px';
        userProfileInfo.style.margin = '0.5rem 0';
        const isAdminUser = isAdmin(currentUser);
        userProfileInfo.innerHTML = `
          <div style="text-align: center; margin-bottom: 1rem;">
            <div style="width: 50px; height: 50px; background: linear-gradient(135deg, ${isAdminUser ? 'var(--danger), var(--accent)' : 'var(--brand), var(--brand2)'}); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.5rem; font-size: 20px;">
              ${isAdminUser ? '🔐' : '👤'}
            </div>
            <h4 style="margin: 0; color: var(--text); font-size: 1rem;">${currentUser.fullName || 'User'}</h4>
            <p style="margin: 0.25rem 0 0 0; color: var(--muted); font-size: 0.85rem;">@${currentUser.username}</p>
            ${isAdminUser ? '<div style="background: var(--danger); color: white; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.75rem; margin-top: 0.5rem; display: inline-block;">ADMIN</div>' : ''}
          </div>
          <div style="display: grid; gap: 0.5rem; font-size: 0.85rem;">
            <div><strong>📧 Email:</strong> ${currentUser.email}</div>
            <div><strong>📱 Phone:</strong> ${currentUser.phone || 'Not provided'}</div>
            <div><strong>🆔 User ID:</strong> ${currentUser.id}</div>
            <div><strong>⚧ Gender:</strong> ${currentUser.gender ? currentUser.gender.charAt(0).toUpperCase() + currentUser.gender.slice(1) : 'Not provided'}</div>
            <div><strong>🎂 Date of Birth:</strong> ${currentUser.dob || 'Not provided'}</div>
          </div>
        `;
        
        // Add logout button to mobile nav
        const logoutLink = document.createElement('a');
        logoutLink.textContent = '🚪 Logout';
        logoutLink.className = 'nav-link';
        logoutLink.href = '#';
        logoutLink.addEventListener('click', (e) => {
          e.preventDefault();
          handleLogout();
        });
        
        mobileNav.appendChild(userProfileInfo);
        mobileNav.appendChild(logoutLink);
      }
    }
  }

  // Prevent access to auth pages when logged in
  function preventAuthPageAccess(){
    const currentUser = getCurrentUser();
    const currentFile = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
    
    // Pages that should be blocked when logged in
    const authPages = ['index.html', 'signin.html', 'signup.html'];
    
    if(currentUser && authPages.includes(currentFile)){
      // Show visual message on home page
      if(currentFile === 'index.html'){
        const loggedInMessage = document.getElementById('logged-in-message');
        const heroButtons = document.querySelector('.hero-buttons');
        if(loggedInMessage && heroButtons){
          heroButtons.style.display = 'none';
          loggedInMessage.style.display = 'block';
        }
      }
      
      toast('You are already logged in. Please logout to access this page.');
      setTimeout(() => {
        window.location.href = 'workers.html';
      }, 1500);
    }
  }

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
      const gender = form.querySelector('select[name="gender"]').value;
      const dob = form.querySelector('input[name="dob"]').value;
      const password = form.querySelector('input[name="password"]').value;
      const confirmPassword = form.querySelector('input[name="confirm_password"]').value;

      // Check password confirmation
      if(password !== confirmPassword){
        alert('Passwords do not match. Please try again.');
        return;
      }

      // Check terms agreement
      const terms = form.querySelector('input[name="terms"]');
      if(!terms.checked){
        alert('Please agree to the Terms of Service and Privacy Policy.');
        return;
      }

      const users = getUsers();
      const exists = users.some(u => u.id===id || u.username===username || u.email===email || u.phone===phone);
      if(exists){
        alert('User with same ID/Username/Email/Phone already exists.');
        return;
      }
      users.push({ id, fullName, username, email, phone, gender, dob, password });
      saveUsers(users);
      setCurrent({ id, fullName, username, email, phone, gender, dob });
      toast('Registration successful');
      setTimeout(()=>{ window.location.href='workers.html'; }, 800);
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

  // Signin page
  if(page==='signin'){
    const form=$('#signinForm');
    form?.addEventListener('submit',e=>{
      e.preventDefault();
      if(!validate(form)) return;
      
      const email = form.querySelector('input[name="email"]').value.trim();
      const password = form.querySelector('input[name="password"]').value;

      // Check for admin login first
      if(email === ADMIN_CREDENTIALS.username && password === ADMIN_CREDENTIALS.password){
        setCurrent(ADMIN_CREDENTIALS);
        toast('Admin login successful');
        setTimeout(()=>{ window.location.href='dashboard.html'; }, 800);
        return;
      }
      
      const users = getUsers();
      console.log('Users in storage:', users);
      console.log('Looking for email:', email);
      console.log('Looking for password:', password);
      
      // Try to match by email first, then by phone if email doesn't work
      let match = users.find(u => u.email===email && u.password===password);
      
      // If no match by email, try by phone (in case user entered phone in email field)
      if(!match){
        match = users.find(u => u.phone===email && u.password===password);
      }

      console.log('Match found:', match);

      if(!match){
        alert('Invalid credentials. Please check your email/phone and password.');
        return;
      }
      setCurrent({ id: match.id, username: match.username, email: match.email, fullName: match.fullName, phone: match.phone, gender: match.gender, dob: match.dob });
      toast('Sign in successful');
      setTimeout(()=>{ window.location.href='workers.html'; }, 800);
    });
  }

  // Forms: save data to localStorage and navigate to next
  if(page==='form'){
    const form=$('#recordForm');
    const popup=$('#popup');
    const closeBtn=$('#closePopup');
    // Require login to access forms
    try{ if(!getCurrentUser()) { window.location.href='index.html'; } }catch(e){}
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
    // must be logged in and must be admin
    const currentUser = getCurrentUser();
    if(!currentUser) { 
      window.location.href='index.html'; 
      return; 
    }
    if(!isAdmin(currentUser)){
      toast('Access denied. Admin privileges required.');
      setTimeout(() => {
        window.location.href='workers.html';
      }, 1500);
      return;
    }
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
    const users = getUsers();
    const files=['workers.html','health_records.html','vaccinations.html','medical.html','facilities.html'];
    
    // Admin info header
    const adminHeader = document.createElement('div');
    adminHeader.className = 'card';
    adminHeader.innerHTML = `
      <div class="card-inner">
        <h2 style="margin-top: 0; color: var(--brand); display: flex; align-items: center; gap: 8px;">
          🔐 Admin Dashboard
        </h2>
        <p style="color: var(--muted); margin: 0.5rem 0;">Welcome, ${currentUser.fullName || currentUser.username}. You have administrative access to all system data.</p>
      </div>
    `;
    content.appendChild(adminHeader);
    
    // System statistics
    const stats = document.createElement('div');
    stats.className = 'card';
    stats.innerHTML = `
      <div class="card-inner">
        <h3 style="margin-top: 0;">📊 System Statistics</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem;">
          <div style="text-align: center; padding: 1rem; background: var(--soft); border-radius: 8px;">
            <div style="font-size: 2rem; font-weight: bold; color: var(--brand);">${users.length}</div>
            <div style="color: var(--muted); font-size: 0.9rem;">Total Users</div>
          </div>
          <div style="text-align: center; padding: 1rem; background: var(--soft); border-radius: 8px;">
            <div style="font-size: 2rem; font-weight: bold; color: var(--ok);">${files.filter(f => localStorage.getItem('dhrms_form_'+f)).length}</div>
            <div style="color: var(--muted); font-size: 0.9rem;">Forms Submitted</div>
          </div>
          <div style="text-align: center; padding: 1rem; background: var(--soft); border-radius: 8px;">
            <div style="font-size: 2rem; font-weight: bold; color: var(--accent);">${new Date().toLocaleDateString()}</div>
            <div style="color: var(--muted); font-size: 0.9rem;">Last Updated</div>
          </div>
        </div>
      </div>
    `;
    content.appendChild(stats);
    
    content.appendChild(block('Current Admin User', currentUser||{}));
    content.appendChild(block('All Registered Users', users));
    files.forEach(f=>{
      const data = JSON.parse(localStorage.getItem('dhrms_form_'+f)||'null');
      content.appendChild(block('Form Data: '+f, data||{}));
    });
    const logoutBtn = document.getElementById('logoutBtn');
    const clearBtn = document.getElementById('clearDataBtn');
    logoutBtn?.addEventListener('click', handleLogout);
    clearBtn?.addEventListener('click',()=>{ localStorage.clear(); toast('All local data cleared'); setTimeout(()=>location.reload(),400) });
  }
  // Mobile menu functionality
  function initMobileMenu() {
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const mobileNav = document.getElementById('mobile-nav');
    
    if (mobileToggle && mobileNav) {
      mobileToggle.addEventListener('click', () => {
        mobileNav.classList.toggle('show');
      });
      
      // Close mobile menu when clicking outside
      document.addEventListener('click', (e) => {
        if (!mobileNav.contains(e.target) && !mobileToggle.contains(e.target)) {
          mobileNav.classList.remove('show');
        }
      });
    }
  }

  // Global init
  injectNavbar();
  enablePageTransitions();
  initMobileMenu();
  updateHeaderForLoginStatus();
  preventAuthPageAccess();
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
