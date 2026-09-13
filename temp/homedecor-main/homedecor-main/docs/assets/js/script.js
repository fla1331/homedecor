
document.addEventListener('DOMContentLoaded', function() {
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
    
    console.log('✅ Site carregado!');
});
