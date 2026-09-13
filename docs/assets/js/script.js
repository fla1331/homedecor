document.addEventListener('DOMContentLoaded', function() {
    // ============================================================
    // MENU MOBILE - Funciona com .nav-toggle (classe correta)
    // ============================================================
    const menuToggle = document.querySelector('.nav-toggle');
    const nav = document.querySelector('.nav');
    
    if (menuToggle && nav) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            nav.classList.toggle('is-open');
            this.classList.toggle('is-open');
            
            const isOpen = nav.classList.contains('is-open');
            this.setAttribute('aria-expanded', isOpen);
            this.setAttribute('aria-label', isOpen ? 'Fechar menu' : 'Abrir menu');
        });
        
        document.addEventListener('click', function(e) {
            if (nav.classList.contains('is-open') && 
                !nav.contains(e.target) && 
                e.target !== menuToggle) {
                nav.classList.remove('is-open');
                menuToggle.classList.remove('is-open');
                menuToggle.setAttribute('aria-expanded', 'false');
                menuToggle.setAttribute('aria-label', 'Abrir menu');
            }
        });
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && nav.classList.contains('is-open')) {
                nav.classList.remove('is-open');
                menuToggle.classList.remove('is-open');
                menuToggle.setAttribute('aria-expanded', 'false');
                menuToggle.setAttribute('aria-label', 'Abrir menu');
                menuToggle.focus();
            }
        });
    }

    // ============================================================
    // HEADER SCROLL
    // ============================================================
    const header = document.querySelector('.site-header');
    if (header) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 20) {
                header.classList.add('is-scrolled');
            } else {
                header.classList.remove('is-scrolled');
            }
        });
    }

    // ============================================================
    // TOC (Sumário)
    // ============================================================
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

    // ============================================================
    // BUSCA
    // ============================================================
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

    // ============================================================
    // REVEAL ANIMATION
    // ============================================================
    const revealElements = document.querySelectorAll('.reveal');
    
    if (revealElements.length > 0) {
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        revealElements.forEach(el => revealObserver.observe(el));
    }

    // ============================================================
    // LANGUAGE SELECTOR
    // ============================================================
    const langBtn = document.querySelector('.lang-btn');
    const langDropdown = document.querySelector('.lang-dropdown');
    if (langBtn && langDropdown) {
        langBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            langDropdown.classList.toggle('open');
            const expanded = langDropdown.classList.contains('open');
            langBtn.setAttribute('aria-expanded', expanded);
        });
        document.addEventListener('click', function () {
            langDropdown.classList.remove('open');
            langBtn.setAttribute('aria-expanded', 'false');
        });
        langDropdown.addEventListener('click', function (e) { e.stopPropagation(); });
    }

    // ============================================================
    // COOKIE BANNER
    // ============================================================
    const COOKIE_KEY = 'travel-blog-cookie-consent';
    const banner = document.querySelector('.cookie-banner');

    function getCookieConsent() {
        try { return localStorage.getItem(COOKIE_KEY); } catch (e) { return null; }
    }
    function setCookieConsent(value) {
        try { localStorage.setItem(COOKIE_KEY, value); } catch (e) {}
    }

    if (banner) {
        const consent = getCookieConsent();
        if (!consent) {
            setTimeout(function () { banner.classList.add('show'); }, 800);
        }
        const acceptBtn = banner.querySelector('.cookie-accept');
        const rejectBtn = banner.querySelector('.cookie-reject');
        const customizeBtn = banner.querySelector('.cookie-customize');

        if (acceptBtn) {
            acceptBtn.addEventListener('click', function () {
                setCookieConsent('accepted');
                banner.classList.remove('show');
            });
        }
        if (rejectBtn) {
            rejectBtn.addEventListener('click', function () {
                setCookieConsent('rejected');
                banner.classList.remove('show');
            });
        }
        if (customizeBtn) {
            customizeBtn.addEventListener('click', function () {
                window.location.href = 'cookies.html';
            });
        }
    }

    // ============================================================
    // TEMA CLARO/ESCURO
    // ============================================================
    const themeToggle = document.querySelector('.theme-toggle');
    const html = document.documentElement;
    const STORAGE_KEY = 'travel-blog-theme';
    
    if (themeToggle) {
        const savedTheme = localStorage.getItem(STORAGE_KEY);
        if (savedTheme) {
            html.setAttribute('data-theme', savedTheme);
        } else {
            html.setAttribute('data-theme', 'light');
        }
        
        themeToggle.addEventListener('click', function() {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem(STORAGE_KEY, newTheme);
            
            console.log(`🌓 Tema alterado para: ${newTheme}`);
        });
    }

    // ============================================================
    // 📤 SHARE BUTTONS
    // ============================================================
    const shareButtons = document.querySelectorAll('.share-btn');
    
    if (shareButtons.length > 0) {
        shareButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const network = this.dataset.share;
                const title = this.dataset.title || document.querySelector('.article-title')?.textContent || 'LevelUp - Games';
                const url = window.location.href;
                const text = title + ' - ' + url;
                
                const shareUrls = {
                    whatsapp: `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`,
                    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
                    twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`,
                    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
                    pinterest: `https://pinterest.com/pin/create/button/?url=${encodeURIComponent(url)}&description=${encodeURIComponent(title)}`,
                    email: `mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent('Confira este artigo: ' + url)}`
                };
                
                const shareUrl = shareUrls[network];
                if (shareUrl) {
                    if (network === 'whatsapp') {
                        window.open(shareUrl, '_blank', 'width=600,height=500');
                    } else {
                        const width = 600;
                        const height = 500;
                        const left = (window.innerWidth - width) / 2;
                        const top = (window.innerHeight - height) / 2;
                        window.open(
                            shareUrl,
                            'share',
                            `width=${width},height=${height},left=${left},top=${top},toolbar=0,menubar=0,location=0,status=0,scrollbars=1,resizable=1`
                        );
                    }
                }
            });
        });
    }

    // ============================================================
    // 📧 FORMULÁRIO DE CONTATO - Redirect (Web3Forms)
    // ============================================================
    const contactForm = document.querySelector('form[action="https://api.web3forms.com/submit"]');

    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const form = this;
            const formData = new FormData(form);
            
            fetch(form.action, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    const pathname = window.location.pathname;
                    let idioma = pathname.split('/')[1];
                    
                    if (!idioma || idioma.length === 0) {
                        idioma = 'pt';
                    }
                    
                    const paginasObrigado = {
                        'pt': 'obrigado.html',
                        'en': 'thank-you.html',
                        'es': 'gracias.html'
                    };
                    
                    const pagina = paginasObrigado[idioma] || 'obrigado.html';
                    window.location.href = '/' + idioma + '/' + pagina;
                } else {
                    alert('Erro ao enviar. Tente novamente.');
                }
            })
            .catch(error => {
                alert('Erro ao enviar. Tente novamente.');
            });
        });
    }

    // ============================================================
    // 📧 NEWSLETTER - Webhook (Listmonk) + Web3Forms (Gmail)
    // ============================================================
    const newsletterForm = document.getElementById('newsletter-form');

    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const form = this;
            const email = form.querySelector('input[name="email"]').value;
            
            // 1. Envia para o Webhook (Listmonk)
            fetch('http://localhost:5000/webhook', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: email })
            })
            .then(response => response.json())
            .then(data => {
                console.log('✅ Listmonk:', data);
            })
            .catch(error => {
                console.error('❌ Erro no Listmonk:', error);
            });
            
            // 2. Envia para o Web3Forms (Gmail)
            const formData = new FormData(form);
            fetch('https://api.web3forms.com/submit', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    const pathname = window.location.pathname;
                    let idioma = pathname.split('/')[1];
                    
                    if (!idioma || idioma.length === 0) {
                        idioma = 'pt';
                    }
                    
                    const paginasObrigado = {
                        'pt': 'obrigado.html',
                        'en': 'thank-you.html',
                        'es': 'gracias.html'
                    };
                    
                    const pagina = paginasObrigado[idioma] || 'obrigado.html';
                    window.location.href = '/' + idioma + '/' + pagina;
                } else {
                    alert('Erro ao enviar. Tente novamente.');
                }
            })
            .catch(error => {
                alert('Erro ao enviar. Tente novamente.');
            });
        });
    }

    console.log('✅ Site carregado com sucesso!');
});