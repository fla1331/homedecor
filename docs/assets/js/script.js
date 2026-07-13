
// ============================================================
// SCRIPT COMPLETO - MENU, DARK MODE, COOKIES, ANIMAÇÕES
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== MENU MOBILE =====
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('nav');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            nav.classList.toggle('open');
            this.textContent = nav.classList.contains('open') ? '✕' : '☰';
        });
    }
    
    // ===== DARK MODE =====
    const themeToggle = document.querySelector('.theme-toggle');
    const html = document.documentElement;
    
    // Verifica preferência salva
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
        
        // Atualiza ícone inicial
        const initial = html.getAttribute('data-theme');
        themeToggle.textContent = initial === 'dark' ? '☀️' : '🌙';
    }
    
    // ===== COOKIES BANNER =====
    const cookiesBanner = document.querySelector('.cookies-banner');
    const cookiesBtn = document.querySelector('.btn-cookies');
    
    if (cookiesBanner && cookiesBtn) {
        // Verifica se já aceitou
        if (!localStorage.getItem('cookies_aceitos')) {
            cookiesBanner.style.display = 'flex';
        } else {
            cookiesBanner.style.display = 'none';
        }
        
        cookiesBtn.addEventListener('click', function() {
            localStorage.setItem('cookies_aceitos', 'true');
            cookiesBanner.style.display = 'none';
        });
    }
    
    // ===== ANIMAÇÃO DE ENTRADA =====
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
    
    // ===== SCROLL SUAVE =====
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    console.log('✅ Site carregado com sucesso!');
});
