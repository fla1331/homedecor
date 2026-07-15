
document.addEventListener('DOMContentLoaded', function() {
    // ===== MENU MOBILE =====
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('nav');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            nav.classList.toggle('open');
            this.textContent = nav.classList.contains('open') ? '✕' : '☰';
        });
        
        document.addEventListener('click', function(e) {
            if (nav.classList.contains('open') && !nav.contains(e.target) && e.target !== menuToggle) {
                nav.classList.remove('open');
                menuToggle.textContent = '☰';
            }
        });
    }
    
    // ===== DARK MODE =====
    const themeToggle = document.querySelector('.theme-toggle');
    const html = document.documentElement;
    
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        html.setAttribute('data-theme', savedTheme);
    }
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const current = html.getAttribute('data-theme');
            const newTheme = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            this.textContent = newTheme === 'dark' ? '☀️' : '🌙';
        });
        
        const initial = html.getAttribute('data-theme');
        themeToggle.textContent = initial === 'dark' ? '☀️' : '🌙';
    }
    
    // ===== COOKIES =====
    const cookiesBanner = document.querySelector('.cookies-banner');
    const cookiesBtn = document.querySelector('.btn-cookies');
    
    if (cookiesBanner && cookiesBtn) {
        if (!localStorage.getItem('cookies_aceitos')) {
            cookiesBanner.style.display = 'flex';
        }
        
        cookiesBtn.addEventListener('click', function() {
            localStorage.setItem('cookies_aceitos', 'true');
            cookiesBanner.style.display = 'none';
        });
    }
    
    // ===== FAQ =====
    document.querySelectorAll('.faq-item').forEach(item => {
        item.addEventListener('click', function() {
            this.classList.toggle('open');
        });
    });
    
    // ===== ANIMAÇÃO CARDS =====
    const cards = document.querySelectorAll('.card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        card.style.transitionDelay = (index * 0.1) + 's';
        observer.observe(card);
    });
    
    // ===== TOC DINÂMICO =====
    const content = document.getElementById('article-content');
    const tocList = document.getElementById('toc-list');
    
    if (content && tocList) {
        const headings = content.querySelectorAll('h2, h3');
        let tocItems = [];
        
        headings.forEach((heading, index) => {
            if (!heading.id) {
                heading.id = 'section-' + index;
            }
            const level = heading.tagName.toLowerCase();
            const text = heading.textContent;
            const id = heading.id;
            tocItems.push({ level, text, id });
        });
        
        if (tocItems.length > 0) {
            let tocHtml = '';
            tocItems.forEach(item => {
                const indent = item.level === 'h3' ? 'style="padding-left: 16px;"' : '';
                tocHtml += `<li ${indent}><a href="#${item.id}">${item.text}</a></li>`;
            });
            tocList.innerHTML = tocHtml;
            
            tocList.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    const target = document.getElementById(targetId);
                    if (target) {
                        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        tocList.querySelectorAll('a').forEach(a => a.classList.remove('active'));
                        this.classList.add('active');
                    }
                });
            });
        }
    }
    
    // ===== NEWSLETTER =====
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('newsletter-email').value;
            if (email) {
                alert('📧 Obrigado por assinar nossa newsletter! Em breve você receberá novidades.');
                this.reset();
            }
        });
    }
    
    // ===== BUSCA =====
    const searchBtn = document.querySelector('.btn-search');
    const headerActions = document.querySelector('.header-actions');
    
    if (searchBtn && headerActions) {
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Buscar artigos...';
        searchInput.className = 'search-input';
        searchInput.style.cssText = `
            display: none;
            position: absolute;
            top: 100%;
            right: 0;
            padding: 8px 12px;
            border: 2px solid var(--primaria);
            border-radius: 8px;
            background: var(--card);
            color: var(--texto);
            min-width: 200px;
            z-index: 100;
        `;
        headerActions.style.position = 'relative';
        headerActions.appendChild(searchInput);
        
        searchBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const isVisible = searchInput.style.display === 'block';
            searchInput.style.display = isVisible ? 'none' : 'block';
            if (!isVisible) searchInput.focus();
        });
        
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                const term = this.value.trim().toLowerCase();
                if (term) {
                    const cards = document.querySelectorAll('.post-card');
                    let found = false;
                    cards.forEach(card => {
                        const title = card.querySelector('.post-card-title a');
                        if (title) {
                            const text = title.textContent.toLowerCase();
                            if (text.includes(term)) {
                                card.style.display = 'block';
                                found = true;
                            } else {
                                card.style.display = 'none';
                            }
                        }
                    });
                    if (!found) {
                        alert('Nenhum artigo encontrado para: ' + term);
                    }
                }
            }
        });
    }
    
    // ===== SCROLL SUAVE EXPLORAR TÓPICOS =====
    const exploreBtn = document.querySelector('.btn-outline');
    if (exploreBtn) {
        exploreBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector('.layout');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }
    
    console.log('✅ Site carregado!');
});
