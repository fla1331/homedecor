#!/usr/bin/env python3
"""
GERADOR DE ARTIGOS - HOMEDECOR
VERSÃO SIMPLIFICADA COM MENU ORGANIZADO
"""

from dotenv import load_dotenv
import os
load_dotenv()

import csv
import re
import random
import unicodedata
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from xml.dom import minidom
import xml.etree.ElementTree as ET
import shutil
import webbrowser
import time

# ============================================================
# ===== CONFIGURAÇÕES ========================================
# ============================================================

CONFIG = {
    'nome': 'Casa & Decoração',
    'slug': 'casa',
    'icone': '🏠',
    'nome_site': 'Home Decor',
    'descricao': 'Inspirações para transformar sua casa em um lar aconchegante e estiloso.',
    'url_base': 'https://homedecor.brightnest.blog',
    'idioma': 'pt',
    'ano': datetime.now().year,
    'csv': 'artigos.csv',
    'usar_ia_imagens': True,
    'autor': 'HomeDecor Team',
    'email_contato': 'contato@homedecorcasa.netlify.app',
    'publicar_por_dia': 3,
    'redes_sociais': {},  # SEM REDES SOCIAIS
    'cores': {
        'primaria': '#c4956a',
        'secundaria': '#8b6b4d',
        'destaque': '#e8c9a0',
        'fundo': '#f5f0eb',
        'texto': '#2d1f14',
        'card': '#ffffff',
        'hover': '#b8845a',
        'whatsapp': '#25D366'
    }
}

# ============================================================
# ===== MAPA DE IDIOMAS ======================================
# ============================================================

IDIOMAS = {
    'pt': {
        'lang': 'pt', 'locale': 'pt_BR',
        'review': 'Review Completo',
        'comprar': 'Comprar Agora',
        'ver_oferta': 'Ver Oferta',
        'menu_inicio': 'Início',
        'menu_sobre': 'Sobre',
        'menu_contato': 'Contato',
        'footer': 'Todos os direitos reservados.',
        'sobre_titulo': 'Sobre Nós',
        'contato_titulo': 'Contato',
        'privacidade_titulo': 'Política de Privacidade',
        'cookies_titulo': 'Política de Cookies',
        'nao_encontrado': 'Página não encontrada',
        'voltar_inicio': 'Voltar para o início',
        'publicado': 'Publicado',
        'rascunho': 'Rascunho',
        'leia_tambem': 'Leia também',
        'compartilhar': 'Compartilhar',
        'autor': 'Por',
        'data_publicacao': 'Publicado em',
        'faq': 'Perguntas Frequentes',
        'revisar_ia': 'Revisar com IA',
        'categorias': 'Categorias'
    },
    'en': {
        'lang': 'en', 'locale': 'en_US',
        'review': 'Complete Review',
        'comprar': 'Buy Now',
        'ver_oferta': 'View Offer',
        'menu_inicio': 'Home',
        'menu_sobre': 'About',
        'menu_contato': 'Contact',
        'footer': 'All rights reserved.',
        'sobre_titulo': 'About Us',
        'contato_titulo': 'Contact',
        'privacidade_titulo': 'Privacy Policy',
        'cookies_titulo': 'Cookies Policy',
        'nao_encontrado': 'Page not found',
        'voltar_inicio': 'Back to home',
        'publicado': 'Published',
        'rascunho': 'Draft',
        'leia_tambem': 'Read also',
        'compartilhar': 'Share',
        'autor': 'By',
        'data_publicacao': 'Published on',
        'faq': 'Frequently Asked Questions',
        'revisar_ia': 'Review with AI',
        'categorias': 'Categories'
    },
    'es': {
        'lang': 'es', 'locale': 'es_ES',
        'review': 'Review Completo',
        'comprar': 'Comprar Ahora',
        'ver_oferta': 'Ver Oferta',
        'menu_inicio': 'Inicio',
        'menu_sobre': 'Sobre',
        'menu_contato': 'Contacto',
        'footer': 'Todos los derechos reservados.',
        'sobre_titulo': 'Sobre Nosotros',
        'contato_titulo': 'Contacto',
        'privacidade_titulo': 'Política de Privacidad',
        'cookies_titulo': 'Política de Cookies',
        'nao_encontrado': 'Página no encontrada',
        'voltar_inicio': 'Volver al inicio',
        'publicado': 'Publicado',
        'rascunho': 'Borrador',
        'leia_tambem': 'Lea también',
        'compartilhar': 'Compartir',
        'autor': 'Por',
        'data_publicacao': 'Publicado el',
        'faq': 'Preguntas Frecuentes',
        'revisar_ia': 'Revisar con IA',
        'categorias': 'Categorías'
    }
}

# ============================================================
# ===== MAPA DE PROMPTS POR NICHO ============================
# ============================================================

PROMPTS_NICHO = {
    'decoração': {
        'tom': 'acolhedor, inspirador e sofisticado',
        'palavras': 'aconchegante, elegante, transforme seu espaço, estilo, personalidade, design',
        'faq': [
            'Qual o material e durabilidade?',
            'Como limpar e conservar?',
            'Combina com que estilo de decoração?',
            'Qual o prazo de entrega?',
            'Tem garantia e suporte?',
            'Vale a pena o investimento?'
        ]
    },
    'games': {
        'tom': 'energético, jovem e tecnológico',
        'palavras': 'game changer, performance, imersão, gameplay, nível, competitivo',
        'faq': [
            'Qual o desempenho nos jogos?',
            'É compatível com PC/Console?',
            'Qual a duração da bateria?',
            'Tem garantia?',
            'Vale a pena o investimento?'
        ]
    },
    'geral': {
        'tom': 'informativo, útil e confiável',
        'palavras': 'qualidade, benefícios, vantagens, recomendações, confiabilidade',
        'faq': [
            'Quais os principais benefícios?',
            'Como funciona?',
            'Vale a pena?',
            'Tem garantia?',
            'Como usar corretamente?'
        ]
    }
}

# ============================================================
# ===== CLASSE GERADORA ======================================
# ============================================================

class Gerador:
    def __init__(self):
        self.base = Path(__file__).parent
        self.docs = self.base / "docs"
        self.templates = self.base / "templates"
        self.assets_css = self.docs / "assets" / "css"
        self.assets_js = self.docs / "assets" / "js"
        self.assets_img = self.docs / "assets" / "img"
        
        self.assets_css.mkdir(parents=True, exist_ok=True)
        self.assets_js.mkdir(parents=True, exist_ok=True)
        self.assets_img.mkdir(parents=True, exist_ok=True)
        
        self.carregar_config()
        
        self.idioma = CONFIG.get('idioma', 'pt')
        self.t = IDIOMAS.get(self.idioma, IDIOMAS['pt'])
        
        self.ia_api_key = os.getenv("OPENROUTER_API_KEY")
        
        # Cache para descrições de categorias
        self.descricoes_categorias = {}
        
        self.criar_csv()
        self.criar_css()
        self.criar_js()
        
        self.mostrar_painel()
    
    # ==================== UTILITÁRIOS ====================
    
    def formatar_titulo_categoria(self, slug):
        """Converte 'sala-de-estar' para 'Sala de Estar'"""
        palavras = slug.replace('-', ' ').split()
        palavras_formatadas = []
        for palavra in palavras:
            if palavra.lower() in ['de', 'da', 'do', 'das', 'dos', 'e']:
                palavras_formatadas.append(palavra.lower())
            else:
                palavras_formatadas.append(palavra.capitalize())
        return ' '.join(palavras_formatadas)
    
    def criar_slug(self, texto):
        texto = unicodedata.normalize('NFKD', texto)
        texto = texto.encode('ASCII', 'ignore').decode('ASCII')
        slug = texto.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s]+', '-', slug)
        slug = re.sub(r'[-]+', '-', slug)
        return slug.strip('-')[:60]
    
    def ler_numero(self, msg, minimo=1, maximo=99):
        while True:
            try:
                valor = input(msg).strip()
                if not valor:
                    return None
                num = int(valor)
                if minimo <= num <= maximo:
                    return num
                print(f"   ⚠️ Digite entre {minimo} e {maximo}")
            except ValueError:
                print("   ⚠️ Digite um número válido")
    
    def ler_sim_nao(self, msg):
        while True:
            resp = input(msg).strip().lower()
            if resp in ['s', 'sim', 'y', 'yes']:
                return True
            if resp in ['n', 'nao', 'não', 'no']:
                return False
            print("   ⚠️ Digite 's' ou 'n'")
    
    # ==================== TEMPLATES ====================
    
    def ler_template(self, nome):
        caminho = self.templates / nome
        if caminho.exists():
            with open(caminho, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def renderizar_template(self, nome, variaveis):
        template = self.ler_template(nome)
        if template is None:
            return None
        
        html = template
        for chave, valor in variaveis.items():
            html = html.replace(f'{{{{{chave}}}}}', str(valor))
        return html
    
    # ==================== CONFIG ====================
    
    def carregar_config(self):
        config_path = self.base / "config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    CONFIG.update(dados)
                print("✅ Config carregada: config.json")
            except:
                pass
    
    # ==================== SINCRONIZAR STATUS ====================
    
    def sincronizar_status(self, mostrar_confirmacao=True):
        """Verifica se os artigos publicados ainda existem na pasta docs"""
        artigos = self.ler_csv()
        alterado = False
        afetados = []
        
        for a in artigos:
            if a.get('status') == 'publicado':
                slug = self.criar_slug(a.get('artigo', ''))
                categoria = a.get('categoria', 'geral')
                if not (self.docs / categoria / slug / "index.html").exists():
                    afetados.append(a.get('artigo'))
                    a['status'] = 'rascunho'
                    alterado = True
        
        if alterado and mostrar_confirmacao:
            print(f"\n⚠️ {len(afetados)} artigos serão voltados para rascunho:")
            for nome in afetados:
                print(f"   🔄 {nome}")
            
            if not self.ler_sim_nao("\nContinuar? (s/n): "):
                return False
        
        if alterado:
            self.salvar_csv(artigos)
            print("✅ Status sincronizado!")
        
        return alterado
    
    # ==================== PAINEL ====================
    
    def mostrar_painel(self):
        self.sincronizar_status(mostrar_confirmacao=False)
        
        artigos = self.ler_csv()
        total = len(artigos)
        
        publicados = 0
        rascunhos = 0
        categorias = set()
        for a in artigos:
            status = a.get('status', 'rascunho').lower()
            if status == 'publicado':
                publicados += 1
            else:
                rascunhos += 1
            cat = a.get('categoria', 'geral')
            if cat:
                categorias.add(cat)
        
        print("\n" + "=" * 70)
        print(f"  {CONFIG['icone']} PAINEL - {CONFIG['nome']}")
        print("=" * 70)
        print(f"  📊 {total} artigos | ✅ {publicados} publicados | ⏳ {rascunhos} rascunhos")
        print(f"  🏷️  {len(categorias)} categorias: {', '.join([self.formatar_titulo_categoria(c) for c in list(categorias)[:5]])}")
        print(f"  🌐 Idioma: {self.idioma.upper()}")
        print("=" * 70)
    
    # ==================== CSV ====================
    
    def ler_csv(self):
        csv_path = self.base / CONFIG['csv']
        if not csv_path.exists():
            return []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def salvar_csv(self, artigos):
        csv_path = self.base / CONFIG['csv']
        if not artigos:
            return
        
        cabecalho = list(artigos[0].keys())
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=cabecalho)
            writer.writeheader()
            writer.writerows(artigos)
    
    def criar_csv(self):
        csv_path = self.base / CONFIG['csv']
        if csv_path.exists():
            return
        
        dados = [
            ["artigo", "links_afiliados", "status", "categoria", "palavras_chave", "descricao", "tipo", "data_publicacao", "autor"],
            ["Poltrona Conforto Ergonômica", "", "rascunho", "sala-de-estar", "poltrona conforto ergonômica", "Review completo da Poltrona Conforto", "review", "", "HomeDecor Team"],
        ]
        
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(dados)
        print(f"✅ CSV criado: {CONFIG['csv']}")

    # ==================== PÁGINA DE BUSCA ====================
    
    def criar_pagina_busca(self):
        t = self.t
        template = self.ler_template('busca.html')
        if template:
            variaveis = {
                'NOME_SITE': CONFIG['nome_site'],
                'HEADER': self.get_header('inicio'),
                'FOOTER': self.get_footer(),
                'IDIOMA': t['lang']
            }
            html = self.renderizar_template('busca.html', variaveis)
            caminho = self.docs / "busca.html"
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(html)
            return caminho
        return None
    
    # ==================== CSS ====================
    
    def criar_css(self):
        """Cria ou copia os arquivos CSS - NUNCA SOBRESCREVE"""
        css_destino = self.assets_css / "style.css"
        custom_destino = self.assets_css / "custom.css"
        
        # ===== style.css =====
        # Se já existe no destino, NÃO FAZ NADA
        if css_destino.exists():
            print("✅ style.css já existe, mantendo o original")
        else:
            # Tenta copiar da pasta assets/
            css_origem = self.base / "assets" / "css" / "style.css"
            if css_origem.exists():
                shutil.copy2(css_origem, css_destino)
                print("✅ style.css copiado do assets/")
            else:
                # Fallback: cria um CSS básico
                c = CONFIG['cores']
                css = f"""
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

:root {{
    --primaria: {c['primaria']};
    --secundaria: {c['secundaria']};
    --destaque: {c['destaque']};
    --fundo: {c['fundo']};
    --texto: {c['texto']};
    --card: {c['card']};
    --hover: {c['hover']};
    --whatsapp: {c['whatsapp']};
    --sombra: 0 4px 20px rgba(0,0,0,0.06);
    --borda: 12px;
    --transicao: 0.3s ease;
}}

body {{
    font-family: 'Nunito', sans-serif;
    background: var(--fundo);
    color: var(--texto);
    line-height: 1.7;
}}
.container {{ max-width: 1100px; margin: 0 auto; padding: 0 20px; }}
"""
                with open(css_destino, 'w', encoding='utf-8') as f:
                    f.write(css)
                print("✅ style.css criado (fallback)")
        
        # ===== custom.css =====
        if custom_destino.exists():
            print("✅ custom.css já existe, mantendo o original")
        else:
            custom_origem = self.base / "assets" / "css" / "custom.css"
            if custom_origem.exists():
                shutil.copy2(custom_origem, custom_destino)
                print("✅ custom.css copiado do assets/")
            else:
                # Cria custom.css vazio
                with open(custom_destino, 'w', encoding='utf-8') as f:
                    f.write("/* Custom styles */\n")
                print("✅ custom.css criado (vazio)")
    
    # ==================== JS ====================
    
    def criar_js(self):
        js_origem = self.base / "assets" / "js" / "script.js"
        js_destino = self.assets_js / "script.js"
        
        if js_origem.exists():
            shutil.copy2(js_origem, js_destino)
            print("✅ JS copiado do assets/")
            return
        
        js = """
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
"""
        with open(js_destino, 'w', encoding='utf-8') as f:
            f.write(js)
        print("✅ JS criado (fallback)")
    
    # ==================== IMAGEM ====================
    
    def gerar_imagem(self, artigo, categoria=""):
        if CONFIG.get('usar_ia_imagens', True):
            try:
                prompt = f"{artigo}, {categoria}, design de interiores, ambiente aconchegante, estilo clean, alta qualidade, 4k"
                return f"https://image.pollinations.ai/prompt/{prompt}?width=1200&height=630&nologo=true"
            except:
                pass
        
        imagens = [
            'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1200&h=630&fit=crop',
            'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&h=630&fit=crop',
        ]
        return random.choice(imagens)
    
    # ==================== DESCRIÇÃO CATEGORIA COM IA ====================
    
    def gerar_descricao_categoria(self, categoria):
        """Gera uma descrição dinâmica para a página da categoria usando IA"""
        
        # Verifica se já tem em cache
        if categoria in self.descricoes_categorias:
            return self.descricoes_categorias[categoria]
        
        titulo_categoria = self.formatar_titulo_categoria(categoria)
        
        # Se não tem IA, usa descrições fixas
        if not self.ia_api_key:
            descricoes_fixas = {
                'sala-de-estar': 'Inspirações e produtos para deixar sua sala de estar mais aconchegante e estilosa. Encontre móveis, decoração e dicas para transformar esse espaço.',
                'decoração': 'Tudo sobre decoração de interiores: tendências, dicas, produtos e inspirações para cada cômodo da sua casa.',
                'quarto': 'Dicas para criar um quarto confortável e cheio de personalidade. Roupas de cama, iluminação e móveis para um espaço de descanso perfeito.',
                'cozinha': 'Tudo sobre decoração, organização e funcionalidade para sua cozinha. Inspire-se com as melhores tendências.',
                'banheiro': 'Transforme seu banheiro em um spa particular com nossas dicas de decoração, revestimentos e acessórios.',
                'escritorio': 'Ambientes produtivos e inspiradores para seu home office. Organização, móveis e decoração para trabalhar com estilo.',
                'jardim': 'Crie um oásis verde em casa com ideias para jardim e área externa. Plantas, móveis e decoração para espaços ao ar livre.',
                'iluminacao': 'A iluminação certa pode transformar completamente um ambiente. Dicas e produtos para criar a atmosfera perfeita.',
                'moveis': 'Escolha móveis que combinam design, conforto e funcionalidade. Encontre inspirações para todos os cômodos.',
                'tapetes': 'Tapetes são o toque final que todo ambiente precisa. Descubra modelos, cores e texturas para cada espaço.',
                'quadros': 'Arte na parede: quadros e painéis que contam histórias e dão personalidade à decoração.',
                'espelhos': 'Espelhos estratégicos podem ampliar e iluminar espaços. Aprenda a usar esse recurso na decoração.',
                'cortinas': 'Controle a luz com estilo usando cortinas e persianas. Dicas para escolher o modelo ideal para cada ambiente.',
                'organizacao': 'Menos bagunça, mais estilo: soluções inteligentes de organização para todos os cômodos.',
                'cores': 'Paletas de cores que transformam a atmosfera da sua casa. Descubra combinações e tendências.',
                'estilos': 'Do minimalista ao boho: encontre seu estilo de decoração e saiba como aplicá-lo em cada ambiente.'
            }
            descricao = descricoes_fixas.get(categoria, f'Inspirações e dicas para decorar sua {titulo_categoria.lower()} com estilo e personalidade.')
            self.descricoes_categorias[categoria] = descricao
            return descricao
        
        # Tenta gerar com IA
        try:
            prompt = f"""
            Crie uma descrição curta e envolvente (máximo 200 caracteres) para uma página de categoria de decoração chamada "{titulo_categoria}".
            A descrição deve ser inspiradora, mostrar o que o leitor vai encontrar e ter um tom acolhedor.
            
            Exemplos:
            - Sala de Estar: "Inspirações e produtos para deixar sua sala de estar mais aconchegante e estilosa. Encontre móveis, decoração e dicas para transformar esse espaço."
            - Decoração: "Tudo sobre decoração de interiores: tendências, dicas, produtos e inspirações para cada cômodo da sua casa."
            
            Retorne APENAS a descrição, sem aspas ou formatação.
            """
            
            headers = {"Authorization": f"Bearer {self.ia_api_key}", "Content-Type": "application/json"}
            data = {
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Você é um especialista em decoração e criação de descrições envolventes."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 200,
                "temperature": 0.8
            }
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            if response.status_code == 200:
                descricao = response.json()["choices"][0]["message"]["content"].strip()
                descricao = descricao.strip('"\'')
                self.descricoes_categorias[categoria] = descricao
                return descricao
        except Exception as e:
            print(f"   ⚠️ Erro ao gerar descrição da categoria: {e}")
        
        # Fallback
        descricao = f'Inspirações e dicas para decorar sua {titulo_categoria.lower()} com estilo e personalidade.'
        self.descricoes_categorias[categoria] = descricao
        return descricao
    
    # ==================== CONTEÚDO COM IA ====================
    
    def gerar_conteudo_ia(self, artigo, link, categoria="geral", palavras_chave="", tipo="review"):
        if not self.ia_api_key:
            return self.conteudo_basico(artigo, link, tipo)
        
        prompt_nicho = PROMPTS_NICHO.get(categoria, PROMPTS_NICHO['geral'])
        
        prompt_template = self.ler_template(f'prompts/{tipo}.txt')
        
        if prompt_template:
            print(f"   🤖 Gerando conteúdo do tipo: {tipo} para: {categoria}...")
            
            prompt = prompt_template.replace('{artigo}', artigo)
            prompt = prompt.replace('{link}', link)
            prompt = prompt.replace('{categoria}', categoria)
            prompt = prompt.replace('{tom}', prompt_nicho['tom'])
            prompt = prompt.replace('{palavras_chave}', palavras_chave or prompt_nicho['palavras'])
            prompt = prompt.replace('{quantidade}', str(random.randint(8, 12)))
        else:
            print(f"   ⚠️ Template {tipo}.txt não encontrado, usando fallback...")
            prompt = self._gerar_prompt_fallback(artigo, link, categoria, palavras_chave, tipo)
        
        try:
            headers = {"Authorization": f"Bearer {self.ia_api_key}", "Content-Type": "application/json"}
            data = {
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"Você é especialista em {categoria} e criação de conteúdo do tipo {tipo}."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 6000,
                "temperature": 0.8
            }
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=120
            )
            if response.status_code == 200:
                conteudo = response.json()["choices"][0]["message"]["content"]
                conteudo = re.sub(r'```(?:html)?\s*', '', conteudo)
                conteudo = re.sub(r'\s*```', '', conteudo)
                
                if 'faq-item' not in conteudo.lower() or 'faq-question' not in conteudo.lower():
                    conteudo += self._gerar_faq_fallback(categoria)
                
                return conteudo
            else:
                print(f"   ⚠️ Erro na API: {response.status_code}")
                return self.conteudo_basico(artigo, link, tipo)
        except Exception as e:
            print(f"   ⚠️ Erro IA: {e}")
            return self.conteudo_basico(artigo, link, tipo)
    
    def _gerar_prompt_fallback(self, artigo, link, categoria, palavras_chave, tipo="review"):
        prompt_nicho = PROMPTS_NICHO.get(categoria, PROMPTS_NICHO['geral'])
        
        # Converte o slug da categoria para título bonito
        titulo_categoria = self.formatar_titulo_categoria(categoria)
        
        tipos = {
            'review': f"""
            Crie um REVIEW COMPLETO sobre {artigo} em português do Brasil.
            
            NICHO: {titulo_categoria}
            TOM: {prompt_nicho['tom']}
            PALAVRAS-CHAVE: {palavras_chave or prompt_nicho['palavras']}
            
            ESTRUTURA OBRIGATÓRIA (REVIEW) - Use IDs e classes:
            1. Título em <h1> com id="introducao"
            2. INTRODUÇÃO (4-5 parágrafos) - <h2 id="introducao">
            3. SOBRE O PRODUTO - <h2 id="sobre-o-produto">
            4. BENEFÍCIOS - <h2 id="beneficios"> com <ul>
            5. ESPECIFICAÇÕES - <table class="article-table">
            6. PRÓS E CONTRAS - <h2 id="pros-e-contras">
            7. ANÁLISE DETALHADA - <h2 id="analise-detalhada">
            8. DICAS - <h2 id="dicas">
            9. FAQ - <div class="faq"> com <div class="faq-item">
            10. CONCLUSÃO - <h2 id="conclusao">
            11. CTA - <div class="cta-box"> com link: {link}
            
            Use classes: article-table, faq, faq-item, faq-question, faq-answer, cta-box, btn-primary
            Retorne APENAS HTML válido.
            """,
            'guia': f"""
            Crie um GUIA COMPLETO sobre {artigo} em português do Brasil.
            NICHO: {titulo_categoria}
            TOM: {prompt_nicho['tom']}
            PALAVRAS-CHAVE: {palavras_chave or prompt_nicho['palavras']}
            
            ESTRUTURA: Título, Introdução, Capítulos, FAQ, Conclusão, CTA com link: {link}
            Use classes: article-table, faq, faq-item, cta-box, btn-primary
            Retorne APENAS HTML válido.
            """,
            'lista': f"""
            Crie uma LISTA com {artigo} em português do Brasil.
            NICHO: {titulo_categoria}
            TOM: {prompt_nicho['tom']}
            PALAVRAS-CHAVE: {palavras_chave or prompt_nicho['palavras']}
            
            ESTRUTURA: Título, Introdução, 8-12 itens com <h3>, FAQ, Conclusão, CTA com link: {link}
            Use classes: article-table, faq, faq-item, cta-box, btn-primary
            Retorne APENAS HTML válido.
            """,
            'tutorial': f"""
            Crie um TUTORIAL sobre {artigo} em português do Brasil.
            NICHO: {titulo_categoria}
            TOM: {prompt_nicho['tom']}
            PALAVRAS-CHAVE: {palavras_chave or prompt_nicho['palavras']}
            
            ESTRUTURA: Título, Introdução, Materiais, Passo a passo, FAQ, Conclusão, CTA com link: {link}
            Use classes: article-table, faq, faq-item, cta-box, btn-primary
            Retorne APENAS HTML válido.
            """,
            'comparativo': f"""
            Crie um COMPARATIVO sobre {artigo} em português do Brasil.
            NICHO: {titulo_categoria}
            TOM: {prompt_nicho['tom']}
            PALAVRAS-CHAVE: {palavras_chave or prompt_nicho['palavras']}
            
            ESTRUTURA: Título, Introdução, Produtos comparados, Tabela comparativa, Análise, FAQ, Conclusão, CTA com link: {link}
            Use classes: article-table, faq, faq-item, cta-box, btn-primary
            Retorne APENAS HTML válido.
            """
        }
        
        return tipos.get(tipo, tipos['review'])
    
    def _gerar_faq_fallback(self, categoria):
        prompt_nicho = PROMPTS_NICHO.get(categoria, PROMPTS_NICHO['geral'])
        faq = prompt_nicho.get('faq', PROMPTS_NICHO['geral']['faq'])
        
        faq_html = f"""
        <h2 id="faq">{self.t['faq']}</h2>
        <div class="faq">
        """
        for pergunta in faq[:6]:
            faq_html += f"""
            <div class="faq-item">
                <button class="faq-question" type="button">
                    {pergunta}
                    <span class="faq-icon">▼</span>
                </button>
                <div class="faq-answer">
                    <p>Resposta detalhada para: {pergunta}</p>
                </div>
            </div>
            """
        faq_html += "</div>"
        return faq_html
    
    # ==================== REVISÃO COM IA ====================
    
    def revisar_com_ia(self, conteudo, artigo, categoria="geral", tipo="review"):
        if not self.ia_api_key:
            return conteudo
        
        print(f"   🔍 Revisando e aprofundando conteúdo (tipo: {tipo})...")
        
        prompt_nicho = PROMPTS_NICHO.get(categoria, PROMPTS_NICHO['geral'])
        
        # Converte o slug da categoria para título bonito
        titulo_categoria = self.formatar_titulo_categoria(categoria)
        
        prompt = f"""
        Revise e MELHORE SIGNIFICATIVAMENTE este artigo sobre {artigo}.
        
        TIPO: {tipo}
        CATEGORIA: {titulo_categoria}
        TOM: {prompt_nicho['tom']}
        
        O QUE MELHORAR:
        1. Aprofunde a introdução e adicione id="introducao"
        2. Adicione mais detalhes nos benefícios com id="beneficios"
        3. Enriqueça a tabela com class="article-table"
        4. Adicione análise de mercado com id="analise-de-mercado"
        5. Melhore o FAQ com class="faq" e class="faq-item"
        6. Adicione id="conclusao" na conclusão
        
        CONTEÚDO ORIGINAL:
        {conteudo}
        
        Retorne APENAS o HTML revisado.
        """
        
        try:
            headers = {"Authorization": f"Bearer {self.ia_api_key}", "Content-Type": "application/json"}
            data = {
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"Revisor especialista em {titulo_categoria} e conteúdo do tipo {tipo}."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 6000,
                "temperature": 0.7
            }
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=120
            )
            if response.status_code == 200:
                revisado = response.json()["choices"][0]["message"]["content"]
                revisado = re.sub(r'```(?:html)?\s*', '', revisado)
                revisado = re.sub(r'\s*```', '', revisado)
                return revisado
            else:
                return conteudo
        except Exception as e:
            print(f"   ⚠️ Erro na revisão: {e}")
            return conteudo
    
    def conteudo_basico(self, artigo, link, tipo="review"):
        t = self.t
        
        titulo_map = {
            'review': f"Review Completo: {artigo}",
            'guia': f"Guia Completo: {artigo}",
            'lista': f"Lista: {artigo}",
            'tutorial': f"Tutorial: {artigo}",
            'comparativo': f"Comparativo: {artigo}"
        }
        titulo = titulo_map.get(tipo, f"Artigo: {artigo}")
        
        return f"""
<h1 id="introducao">{titulo}</h1>

<p><strong>{artigo}</strong> é a escolha perfeita para sua casa.</p>

<p>Com design sofisticado e acabamento premium, este produto vai transformar completamente seu ambiente.</p>

<h2 id="beneficios">Benefícios</h2>
<ul>
    <li><strong>Design sofisticado:</strong> Peça que eleva o estilo do ambiente</li>
    <li><strong>Versatilidade:</strong> Combina com diferentes estilos de decoração</li>
    <li><strong>Qualidade premium:</strong> Durabilidade e acabamento impecável</li>
    <li><strong>Funcionalidade:</strong> Unindo estética e utilidade</li>
</ul>

<h2 id="especificacoes">Especificações</h2>
<table class="article-table">
    <thead>
        <tr>
            <th>Característica</th>
            <th>Detalhe</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Material</td>
            <td>Premium com acabamento sofisticado</td>
        </tr>
        <tr>
            <td>Estilo</td>
            <td>Contemporâneo e atemporal</td>
        </tr>
        <tr>
            <td>Garantia</td>
            <td>12 meses</td>
        </tr>
    </tbody>
</table>

<div class="cta-box">
    <h3>{t['comprar']}</h3>
    <p>Garanta o seu {artigo} com preço especial</p>
    <a href="{link}" class="btn-primary" target="_blank" rel="nofollow sponsored">{t['ver_oferta']}</a>
</div>
"""
    
    # ==================== CATEGORIAS ====================
    
    def get_categorias(self):
        artigos = self.ler_csv()
        categorias = set()
        for a in artigos:
            if a.get('status') == 'publicado':
                cat = a.get('categoria', '').strip()
                if cat:
                    categorias.add(cat.lower())
        return sorted(list(categorias))
    
    def get_artigos_publicados(self):
        artigos = self.ler_csv()
        publicados = []
        for a in artigos:
            if a.get('status') == 'publicado':
                publicados.append({
                    'slug': self.criar_slug(a.get('artigo', '')),
                    'nome': a.get('artigo', ''),
                    'categoria': a.get('categoria', 'geral'),
                    'data_publicacao': a.get('data_publicacao', datetime.now().strftime("%Y-%m-%d"))
                })
        return publicados
    
    # ==================== HEADER ====================
    
    def get_header(self, ativo="inicio", categoria_atual=None):
        header_template = self.ler_template('header.html')
        
        if header_template:
            categorias = self.get_categorias()
            cat_links = ""
            for cat in categorias[:6]:
                ativo_cat = 'ativo' if categoria_atual == cat else ''
                titulo_cat = self.formatar_titulo_categoria(cat)
                cat_links += f'<a href="/{cat}/" class="{ativo_cat}">{titulo_cat}</a>'
            
            header_html = header_template.replace('{{CATEGORIAS_MENU}}', cat_links)
            header_html = header_html.replace('{{NOME_SITE}}', CONFIG['nome_site'])
            return header_html
        
        t = self.t
        categorias = self.get_categorias()
        cat_links = ""
        for cat in categorias[:6]:
            ativo_cat = 'ativo' if categoria_atual == cat else ''
            titulo_cat = self.formatar_titulo_categoria(cat)
            cat_links += f'<a href="/{cat}/" class="{ativo_cat}">{titulo_cat}</a>'
        
        return f"""
<header>
    <div class="container">
        <a href="/" class="logo">
            <span class="icone">{CONFIG['icone']}</span>
            <span class="nome">{CONFIG['nome_site']}</span>
        </a>
        <button class="menu-toggle" aria-label="Menu">☰</button>
        <nav>
            <a href="/" class="{'ativo' if ativo=='inicio' else ''}">{t['menu_inicio']}</a>
            {cat_links}
            <button class="theme-toggle" aria-label="Tema">🌙</button>
        </nav>
    </div>
</header>"""
    
    # ==================== HEAD ====================
    
    def get_head(self, titulo, descricao, url, imagem="", extra=""):
        """Gera o head usando template head.html"""
        head_template = self.ler_template('head.html')
        
        if not imagem:
            imagem = f"{CONFIG['url_base']}/assets/img/og-default.jpg"
        
        if head_template:
            head_html = head_template.replace('{{TITULO}}', titulo)
            head_html = head_html.replace('{{DESCRICAO}}', descricao[:160])
            head_html = head_html.replace('{{URL}}', url)
            head_html = head_html.replace('{{IMAGEM}}', imagem)
            head_html = head_html.replace('{{NOME_SITE}}', CONFIG['nome_site'])
            head_html = head_html.replace('{{EXTRA_HEAD}}', extra)
            return head_html
        
        # Fallback se não encontrar o template
        return f"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    <meta name="description" content="{descricao[:160]}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{url}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{titulo}">
    <meta property="og:description" content="{descricao[:160]}">
    <meta property="og:url" content="{url}">
    <meta property="og:image" content="{imagem}">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="pt_BR">
    <meta property="og:site_name" content="{CONFIG['nome_site']}">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{titulo}">
    <meta name="twitter:description" content="{descricao[:160]}">
    <meta name="twitter:image" content="{imagem}">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    
    <!-- CSS -->
    <link rel="stylesheet" href="/assets/css/style.css">
    <link rel="stylesheet" href="/assets/css/custom.css">
    
    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "{titulo}",
      "description": "{descricao[:160]}",
      "image": "{imagem}",
      "url": "{url}",
      "datePublished": "{datetime.now().strftime('%Y-%m-%d')}",
      "dateModified": "{datetime.now().strftime('%Y-%m-%d')}",
      "author": {{
        "@type": "Person",
        "name": "{CONFIG['autor']}"
      }},
      "publisher": {{
        "@type": "Organization",
        "name": "{CONFIG['nome_site']}"
      }}
    }}
    </script>
    
    {extra}
</head>"""
    
    # ==================== FOOTER ====================
    
    def get_footer(self):
        """Gera o footer com categorias dinâmicas - SEM REDES SOCIAIS"""
        
        # Pega as categorias para o menu
        categorias = self.get_categorias()
        cat_links = ""
        for cat in categorias[:8]:  # Limita a 8 categorias
            titulo_cat = self.formatar_titulo_categoria(cat)
            cat_links += f'<a href="/{cat}/">{titulo_cat}</a>\n'
        
        # Tenta carregar o template
        footer_template = self.ler_template('footer.html')
        
        # Se não encontrar, usa o fallback
        if footer_template is None:
            print("   ⚠️ Template footer.html não encontrado, usando fallback")
            footer_template = """<!-- ===== Footer ===== -->
<footer class="site-footer">
  <div class="container footer-inner">
    <div class="footer-brand">
      <a href="/" class="logo">
        <span class="logo-icon">🏠</span>
        {{NOME_SITE}}
      </a>
      <p>{{DESCRICAO}}</p>
    </div>

    <div class="footer-col">
      <h4>Ler</h4>
      <a href="/">Início</a>
      {{CATEGORIAS_MENU}}
    </div>

    <div class="footer-col">
      <h4>Sobre</h4>
      <a href="/sobre.html">Quem somos</a>
      <a href="/contato.html">Contato</a>
      <a href="/politica-privacidade.html">Privacidade</a>
      <a href="/cookies.html">Cookies</a>
    </div>
  </div>

  <div class="container footer-base">
    <span>© {{ANO}} {{NOME_SITE}}. Feito com cuidado.</span>
  </div>
</footer>"""
        
        # FAZ AS SUBSTITUIÇÕES
        footer_html = footer_template.replace('{{NOME_SITE}}', CONFIG['nome_site'])
        footer_html = footer_html.replace('{{DESCRICAO}}', CONFIG['descricao'])
        footer_html = footer_html.replace('{{ANO}}', str(CONFIG['ano']))
        
        # SUBSTITUI O {{CATEGORIAS_MENU}} PELOS LINKS
        footer_html = footer_html.replace('{{CATEGORIAS_MENU}}', cat_links)
        
        # Remove placeholders de redes sociais se existirem
        footer_html = footer_html.replace('{{REDES_SOCIAIS}}', '')
        footer_html = footer_html.replace('{{REDES_SOCIAIS_LINKS}}', '')
        
        return footer_html
    
    # ==================== PÁGINAS ====================
    
    def criar_pagina(self, nome, titulo, conteudo, ativo="inicio"):
        caminho = self.docs / f"{nome}.html"
        t = self.t
        
        html = f"""<!DOCTYPE html>
<html lang="{t['lang']}">
{self.get_head(
    titulo=f"{CONFIG['nome_site']} - {titulo}",
    descricao=f"{titulo} - {CONFIG['nome']}",
    url=f"{CONFIG['url_base']}/{nome}.html"
)}
<body>
    {self.get_header(ativo)}
    <main class="container">
        <div class="artigo">
            <h1>{titulo}</h1>
            {conteudo}
        </div>
    </main>
    {self.get_footer()}
    <script src="/assets/js/script.js"></script>
</body>
</html>"""
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html)
        return caminho
    
    def criar_pagina_sobre(self):
        t = self.t
        conteudo = f"""
<p>Bem-vindo ao <strong>{CONFIG['nome_site']} - {CONFIG['nome']}</strong>!</p>

<p>Somos apaixonados por transformar casas em lares aconchegantes e estilosos. 
Criamos este espaço para compartilhar reviews honestos e análises detalhadas 
dos melhores produtos de decoração e mobiliário.</p>

<h2>Nossa Missão</h2>
<p>Ajudar você a encontrar os melhores produtos para sua casa, 
com informações claras e imparciais.</p>

<h2>Nossos Valores</h2>
<ul>
    <li><strong>Honestidade:</strong> Reviews sinceros e transparentes</li>
    <li><strong>Qualidade:</strong> Só recomendamos o que realmente vale a pena</li>
    <li><strong>Confiança:</strong> Conteúdo criado para ajudar você a decidir</li>
</ul>

<p>Esperamos que você encontre aqui a inspiração que procura para sua casa!</p>
"""
        return self.criar_pagina("sobre", t['sobre_titulo'], conteudo, "sobre")
    
    def criar_pagina_contato(self):
        t = self.t
        conteudo = f"""
<p>Quer falar conosco? Adoramos ouvir sua opinião!</p>

<form action="#" method="POST" style="max-width:600px;margin:25px 0;">
    <div class="form-group">
        <label for="nome">Seu nome</label>
        <input type="text" id="nome" placeholder="Digite seu nome" required>
    </div>
    <div class="form-group">
        <label for="email">Seu e-mail</label>
        <input type="email" id="email" placeholder="Digite seu e-mail" required>
    </div>
    <div class="form-group">
        <label for="mensagem">Mensagem</label>
        <textarea id="mensagem" placeholder="Digite sua mensagem" required></textarea>
    </div>
    <button type="submit" class="btn">{t['comprar']}</button>
</form>

<p><small>⚠️ Este é um formulário de demonstração. Em breve teremos integração com e-mail.</small></p>
"""
        return self.criar_pagina("contato", t['contato_titulo'], conteudo, "contato")
    
    def criar_pagina_privacidade(self):
        t = self.t
        conteudo = f"""
<h2>Política de Privacidade</h2>

<p>Esta Política de Privacidade descreve como coletamos, usamos e protegemos 
suas informações pessoais quando você visita nosso site.</p>

<h3>1. Informações que Coletamos</h3>
<ul>
    <li><strong>Dados de navegação:</strong> Endereço IP, tipo de navegador, páginas visitadas</li>
    <li><strong>Cookies:</strong> Pequenos arquivos que melhoram sua experiência</li>
    <li><strong>Dados fornecidos:</strong> Nome, e-mail (quando você preenche formulários)</li>
</ul>

<h3>2. Como Usamos Seus Dados</h3>
<ul>
    <li>Para melhorar nosso conteúdo e experiência do usuário</li>
    <li>Para responder suas perguntas e solicitações</li>
    <li>Para enviar atualizações e novidades (com seu consentimento)</li>
</ul>

<h3>3. Compartilhamento de Dados</h3>
<p>Não vendemos ou compartilhamos seus dados com terceiros, exceto quando 
necessário para cumprir a lei ou proteger nossos direitos.</p>

<h3>4. Seus Direitos</h3>
<p>Você tem o direito de acessar, corrigir ou excluir seus dados a qualquer momento.</p>

<h3>5. Contato</h3>
<p>Para questões sobre esta política, entre em contato através da nossa <a href="/contato.html">página de contato</a>.</p>

<p><small>Última atualização: {datetime.now().strftime("%d/%m/%Y")}</small></p>
"""
        return self.criar_pagina("politica-privacidade", t['privacidade_titulo'], conteudo)
    
    def criar_pagina_cookies(self):
        t = self.t
        conteudo = f"""
<h2>Política de Cookies</h2>

<p>Esta Política de Cookies explica como usamos cookies e tecnologias semelhantes para melhorar sua experiência em nosso site.</p>

<h3>O que são Cookies?</h3>
<p>Cookies são pequenos arquivos de texto que são armazenados no seu dispositivo quando você visita um site. Eles ajudam a lembrar suas preferências e melhorar sua navegação.</p>

<h3>Cookies que Usamos</h3>
<table class="article-table">
    <thead>
        <tr><th>Tipo</th><th>Finalidade</th></tr>
    </thead>
    <tbody>
        <tr><td>Essenciais</td><td>Necessários para o funcionamento básico do site</td></tr>
        <tr><td>Preferências</td><td>Lembram suas configurações e preferências</td></tr>
        <tr><td>Analíticos</td><td>Nos ajudam a entender como você usa o site</td></tr>
    </tbody>
</table>

<h3>Gerenciamento de Cookies</h3>
<p>Você pode controlar e/ou excluir cookies a qualquer momento através das configurações do seu navegador.</p>

<h3>Contato</h3>
<p>Para mais informações, entre em contato através da nossa <a href="/contato.html">página de contato</a>.</p>

<p><small>Última atualização: {datetime.now().strftime("%d/%m/%Y")}</small></p>
"""
        return self.criar_pagina("cookies", t['cookies_titulo'], conteudo)
    
    def criar_pagina_404(self):
        caminho = self.docs / "404.html"
        t = self.t
        
        html = f"""<!DOCTYPE html>
<html lang="{t['lang']}">
{self.get_head(
    titulo=f"{CONFIG['nome_site']} - {t['nao_encontrado']}",
    descricao=f"{t['nao_encontrado']} - {CONFIG['nome']}",
    url=f"{CONFIG['url_base']}/404.html",
    extra='<meta name="robots" content="noindex, follow">'
)}
<body>
    {self.get_header()}
    <main class="container">
        <div style="text-align:center;padding:60px 0;">
            <h1 style="font-size:4rem;color:{CONFIG['cores']['primaria']};">404</h1>
            <h2>{t['nao_encontrado']}</h2>
            <p style="margin:15px 0;">O conteúdo que você procura não está mais aqui ou foi movido.</p>
            <a href="/" class="btn">{t['voltar_inicio']}</a>
        </div>
    </main>
    {self.get_footer()}
    <script src="/assets/js/script.js"></script>
</body>
</html>"""
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html)
        return caminho
    
    def criar_todas_paginas(self):
        print("\n📄 CRIANDO PÁGINAS")
        print("-" * 40)
        self.criar_pagina_sobre()
        self.criar_pagina_contato()
        self.criar_pagina_privacidade()
        self.criar_pagina_cookies()
        self.criar_pagina_404()
        print("✅ Páginas criadas!")
    
    # ==================== PÁGINAS DE CATEGORIA ====================
    
    def criar_pagina_categoria(self, categoria):
        caminho = self.docs / categoria / "index.html"
        t = self.t
        c = CONFIG
        
        # Converte slug para título bonito
        titulo_categoria = self.formatar_titulo_categoria(categoria)
        
        # Gera descrição dinâmica (com IA se disponível)
        descricao = self.gerar_descricao_categoria(categoria)
        
        # Títulos dinâmicos para cada categoria
        titulos_dinamicos = {
            'sala-de-estar': 'Sala de Estar: Conforto e Estilo para sua Casa',
            'decoração': 'Decoração de Interiores: Inspire-se com as Melhores Tendências',
            'quarto': 'Quarto dos Sonhos: Dicas para um Espaço Aconchegante',
            'cozinha': 'Cozinha Funcional e Charmosa: Inspire-se',
            'banheiro': 'Banheiro de Luxo: Ideias para Renovar seu Espaço',
            'escritorio': 'Home Office Produtivo: Decoração e Organização',
            'jardim': 'Jardim e Área Externa: Natureza em Casa',
            'iluminacao': 'Iluminação que Transforma: Dicas e Tendências',
            'moveis': 'Móveis que Contam Histórias: Escolhas Perfeitas',
            'tapetes': 'Tapetes que Aconchegam: O Toque Final na Decoração',
            'quadros': 'Quadros e Arte: Personalidade nas Paredes',
            'espelhos': 'Espelhos que Ampliam: Elegância e Funcionalidade',
            'cortinas': 'Cortinas e Persianas: Controle de Luz com Estilo',
            'organizacao': 'Organização Inteligente: Menos Bagunça, Mais Estilo',
            'cores': 'Cores que Inspiram: Paletas para Cada Ambiente',
            'estilos': 'Estilos de Decoração: Do Clássico ao Contemporâneo'
        }
        
        titulo_pagina = titulos_dinamicos.get(categoria, f'Decoração {titulo_categoria}')
        
        artigos = self.get_artigos_publicados()
        artigos_cat = []
        for a in artigos:
            if a.get('categoria', '').lower() == categoria.lower():
                artigos_cat.append(a)
        
        if not artigos_cat:
            return None
        
        artigos_cat.sort(key=lambda x: x['data_publicacao'], reverse=True)
        
        # Gera os cards manualmente para evitar placeholders
        lista_cards = ""
        for a in artigos_cat:
            img = self.gerar_imagem(a['nome'], categoria)
            data_formatada = datetime.strptime(a['data_publicacao'], "%Y-%m-%d").strftime("%d/%m/%Y") if a['data_publicacao'] else datetime.now().strftime("%d/%m/%Y")
            tempo_leitura = random.randint(4, 8)
            
            card = f'''<article class="post-card">
  <a href="/{categoria}/{a['slug']}/" class="post-card-img">
    <img src="{img}" alt="{a['nome']}">
  </a>
  <div class="post-card-body">
    <a href="/{categoria}/" class="tag">{titulo_categoria}</a>
    <h3 class="post-card-title"><a href="/{categoria}/{a['slug']}/">{a['nome']}</a></h3>
    <div class="post-card-meta">
      <span>{data_formatada}</span>
      <span class="meta-dot">·</span>
      <span>{tempo_leitura} min de leitura</span>
    </div>
    <p class="post-card-excerpt">{a['nome'][:120]}...</p>
    <a href="/{categoria}/{a['slug']}/" class="read-more">Ler mais →</a>
  </div>
</article>'''
            lista_cards += card
        
        template = self.ler_template('categoria.html')
        
        if template:
            variaveis = {
                'CATEGORIA': titulo_categoria,
                'TITULO_PAGINA': titulo_pagina,
                'DESCRICAO_CATEGORIA': descricao,
                'ARTIGOS_CATEGORIA': lista_cards,
                'HEADER': self.get_header('categoria', categoria),
                'FOOTER': self.get_footer(),
                'IDIOMA': t['lang']
            }
            html = self.renderizar_template('categoria.html', variaveis)
            
        else:
            html = f"""<!DOCTYPE html>
<html lang="{t['lang']}">
{self.get_head(
    titulo=f"{c['nome_site']} - {titulo_categoria}",
    descricao=descricao,
    url=f"{c['url_base']}/{categoria}/"
)}
<body>
    {self.get_header('categoria', categoria)}
    <main class="container">
        <div class="banner">
            <h1>{titulo_pagina}</h1>
            <p>{descricao}</p>
        </div>
        <div class="post-grid">
            {lista_cards}
        </div>
    </main>
    {self.get_footer()}
    <script src="/assets/js/script.js"></script>
</body>
</html>"""
        
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html)
        return caminho
    
    def criar_todas_categorias(self):
        print("\n📂 CRIANDO PÁGINAS DE CATEGORIA")
        print("-" * 40)
        
        # Remove categorias antigas que não existem mais
        for pasta in self.docs.iterdir():
            if pasta.is_dir() and pasta.name not in ['assets'] and (pasta / "index.html").exists():
                if pasta.name not in self.get_categorias():
                    if pasta.name not in ['sobre', 'contato', 'politica-privacidade', 'cookies', '404']:
                        print(f"   🗑️ Removendo categoria antiga: {pasta.name}")
                        shutil.rmtree(pasta)
        
        # Cria páginas para cada categoria
        for cat in self.get_categorias():
            if self.criar_pagina_categoria(cat):
                titulo = self.formatar_titulo_categoria(cat)
                descricao = self.descricoes_categorias.get(cat, '')
                print(f"   ✅ /{cat}/ - {titulo}")
                if descricao:
                    print(f"      📝 {descricao[:80]}...")
        
        self.criar_index()
        self.criar_sitemap()
        
        print("✅ Páginas de categoria criadas!")
    
    # ==================== INDEX (HOME) ====================
    
    def criar_index(self, pagina=1):
        t = self.t
        c = CONFIG
        
        artigos = self.get_artigos_publicados()
        artigos.sort(key=lambda x: x['data_publicacao'], reverse=True)
        
        # ===== PAGINAÇÃO =====
        artigos_por_pagina = 6
        total_artigos = len(artigos)
        total_paginas = (total_artigos + artigos_por_pagina - 1) // artigos_por_pagina if total_artigos > 0 else 1
        
        if pagina < 1:
            pagina = 1
        if pagina > total_paginas:
            pagina = total_paginas
        
        inicio = (pagina - 1) * artigos_por_pagina
        fim = inicio + artigos_por_pagina
        artigos_pagina = artigos[inicio:fim]
        
        # ===== GERA OS CARDS =====
        lista_cards = ""
        if artigos_pagina:
            for a in artigos_pagina:
                img = self.gerar_imagem(a['nome'], a['categoria'])
                data_formatada = datetime.strptime(a['data_publicacao'], "%Y-%m-%d").strftime("%d/%m/%Y") if a['data_publicacao'] else datetime.now().strftime("%d/%m/%Y")
                titulo_categoria = self.formatar_titulo_categoria(a['categoria'])
                tempo_leitura = random.randint(4, 8)
                
                card = f'''<article class="post-card">
  <a href="/{a['categoria']}/{a['slug']}/" class="post-card-img">
    <img src="{img}" alt="{a['nome']}">
  </a>
  <div class="post-card-body">
    <a href="/{a['categoria']}/" class="tag">{titulo_categoria}</a>
    <h3 class="post-card-title"><a href="/{a['categoria']}/{a['slug']}/">{a['nome']}</a></h3>
    <div class="post-card-meta">
      <span>{data_formatada}</span>
      <span class="meta-dot">·</span>
      <span>{tempo_leitura} min de leitura</span>
    </div>
    <p class="post-card-excerpt">{a['nome'][:120]}...</p>
    <a href="/{a['categoria']}/{a['slug']}/" class="read-more">Ler mais →</a>
  </div>
</article>'''
                lista_cards += card
        else:
            lista_cards = '<p style="text-align:center;padding:40px 0;">Nenhum artigo publicado ainda.</p>'
        
        # ===== SIDEBAR =====
        relacionados_sidebar = ""
        for a in artigos[:4]:
            img = self.gerar_imagem(a['nome'], a['categoria'])
            data_formatada = datetime.strptime(a['data_publicacao'], "%Y-%m-%d").strftime("%d/%m/%Y") if a['data_publicacao'] else datetime.now().strftime("%d/%m/%Y")
            titulo_categoria = self.formatar_titulo_categoria(a['categoria'])
            relacionados_sidebar += f'''
                <a href="/{a['categoria']}/{a['slug']}/" class="related-item">
                    <img src="{img}" alt="{a['nome']}">
                    <div class="related-item-body">
                        <span class="related-item-cat">{titulo_categoria}</span>
                        <span class="related-item-title">{a['nome']}</span>
                        <span class="related-item-date">{data_formatada}</span>
                    </div>
                </a>'''
        
        # ===== TAGS =====
        tags = ""
        for cat in self.get_categorias()[:7]:
            tags += f'<a href="/{cat}/">{self.formatar_titulo_categoria(cat)}</a>\n'
        
        primeiro_artigo = f"/{artigos[0]['categoria']}/{artigos[0]['slug']}/" if artigos else "#"
        
        # ===== PAGINAÇÃO =====
        navegacao = ""
        if total_paginas > 1:
            navegacao = '<div class="pagination">'
            if pagina > 1:
                navegacao += f'<a href="/index{pagina-1}.html" class="page-link">« Anterior</a>'
            else:
                navegacao += '<span class="page-link disabled">« Anterior</span>'
            
            for p in range(1, total_paginas + 1):
                if p == pagina:
                    navegacao += f'<span class="page-link active">{p}</span>'
                elif p == 1:
                    navegacao += f'<a href="/" class="page-link">{p}</a>'
                else:
                    navegacao += f'<a href="/index{p}.html" class="page-link">{p}</a>'
            
            if pagina < total_paginas:
                navegacao += f'<a href="/index{pagina+1}.html" class="page-link">Próximo »</a>'
            else:
                navegacao += '<span class="page-link disabled">Próximo »</span>'
            navegacao += '</div>'
        
        # ===== HTML CORRETO COM SECTION CLASS="HERO" =====
        html = f'''<!DOCTYPE html>
<html lang="{t['lang']}">
{self.get_head(
    titulo=f"{c['nome_site']} - {c['nome']}",
    descricao=c['descricao'],
    url=c['url_base']
)}
<body>
    {self.get_header('inicio')}
    
    <main class="container">
        <!-- ===== Hero ===== -->
        <section class="hero">
            <span class="hero-eyebrow">{c['nome']} · Est. {c['ano']}</span>
            <h1>{c['nome']}<br>Viva com <em>calor</em>.</h1>
            <p>{c['descricao']}</p>
            <div class="hero-actions">
                <a href="{primeiro_artigo}" class="btn-primary">Ler a história da semana</a>
                <a href="#artigos-section" class="btn-outline">Explorar tópicos</a>
            </div>
        </section>

        <!-- ===== Layout com grid + sidebar ===== -->
        <div class="layout" id="artigos-section">
            <div>
                <div class="section-head">
                    <h2>Histórias recentes</h2>
                    <a href="/categoria/" class="see-all">Ver tudo →</a>
                </div>

                <div class="post-grid">
                    {lista_cards}
                </div>
                {navegacao}
            </div>

            <!-- ===== Sidebar ===== -->
            <aside class="sidebar">
                <div class="sidebar-block">
                    <h3>Posts relacionados</h3>
                    {relacionados_sidebar}
                </div>

                <div class="sidebar-block sidebar-newsletter" id="newsletter">
                    <h3>A carta de sexta</h3>
                    <p>Um e-mail por semana. Uma ideia para a sua casa. Sem spam.</p>
                    <form id="newsletter-form" action="#" method="POST">
                        <input type="email" id="newsletter-email" placeholder="seu@email.com" required>
                        <button type="submit" class="btn-primary">Assinar</button>
                    </form>
                </div>

                <div class="sidebar-block">
                    <h3>Tags populares</h3>
                    <div class="sidebar-tags">
                        {tags}
                    </div>
                </div>
            </aside>
        </div>
    </main>

    {self.get_footer()}
    <script src="/assets/js/script.js"></script>
</body>
</html>'''
        
        # ===== SALVA =====
        caminho = self.docs / "index.html" if pagina == 1 else self.docs / f"index{pagina}.html"
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Index página {pagina} atualizado ({len(artigos_pagina)} artigos)")
        return caminho
    
    # ==================== ARTIGOS CORRIGIDO ====================
    
    def criar_artigo(self, artigo_data, forcar=False, revisar=True):
        nome = artigo_data.get('artigo', '').strip()
        if not nome:
            return None
        
        link = artigo_data.get('links_afiliados', '')
        palavras_chave = artigo_data.get('palavras_chave', '')
        descricao = artigo_data.get('descricao', f"Review completo de {nome}")
        categoria = artigo_data.get('categoria', 'geral')
        tipo = artigo_data.get('tipo', 'review')
        data_publicacao = artigo_data.get('data_publicacao', datetime.now().strftime("%Y-%m-%d"))
        autor = artigo_data.get('autor', CONFIG['autor'])
        
        # Converte slug da categoria para título bonito
        titulo_categoria = self.formatar_titulo_categoria(categoria)
        
        slug = self.criar_slug(nome)
        pasta = self.docs / categoria / slug
        t = self.t
        
        if not forcar and (pasta / "index.html").exists():
            print(f"   ⏭️ Já existe: {categoria}/{slug}")
            return pasta / "index.html"
        
        print(f"   📝 Criando: {categoria}/{slug} (tipo: {tipo})")
        
        imagem = self.gerar_imagem(nome, categoria)
        conteudo = self.gerar_conteudo_ia(nome, link, categoria, palavras_chave, tipo)
        
        # ===== LIMPEZA DO CONTEÚDO =====
        # Remove HTML duplicado que a IA pode ter gerado
        conteudo = re.sub(r'<!DOCTYPE html>.*?<head>.*?</head>', '', conteudo, flags=re.DOTALL | re.IGNORECASE)
        conteudo = re.sub(r'<body.*?>', '', conteudo, flags=re.IGNORECASE)
        conteudo = re.sub(r'</body>', '', conteudo, flags=re.IGNORECASE)
        conteudo = re.sub(r'<html.*?>', '', conteudo, flags=re.IGNORECASE)
        conteudo = re.sub(r'</html>', '', conteudo, flags=re.IGNORECASE)
        conteudo = re.sub(r'<style>.*?</style>', '', conteudo, flags=re.DOTALL | re.IGNORECASE)
        conteudo = re.sub(r'<script type="text/javascript">.*?</script>', '', conteudo, flags=re.DOTALL | re.IGNORECASE)
        
        # ===== REMOVE O TÍTULO "Introdução" =====
        conteudo = re.sub(r'<h2[^>]*>Introdução\s*</h2>', '', conteudo, flags=re.IGNORECASE)
        conteudo = re.sub(r'<h2[^>]*id="[^"]*introducao[^"]*"[^>]*>Introdução\s*</h2>', '', conteudo, flags=re.IGNORECASE)
        
        if revisar and self.ia_api_key:
            conteudo = self.revisar_com_ia(conteudo, nome, categoria, tipo)
            # Limpeza novamente após revisão
            conteudo = re.sub(r'<!DOCTYPE html>.*?<head>.*?</head>', '', conteudo, flags=re.DOTALL | re.IGNORECASE)
            conteudo = re.sub(r'<body.*?>', '', conteudo, flags=re.IGNORECASE)
            conteudo = re.sub(r'</body>', '', conteudo, flags=re.IGNORECASE)
            conteudo = re.sub(r'<html.*?>', '', conteudo, flags=re.IGNORECASE)
            conteudo = re.sub(r'</html>', '', conteudo, flags=re.IGNORECASE)
            conteudo = re.sub(r'<style>.*?</style>', '', conteudo, flags=re.DOTALL | re.IGNORECASE)
            conteudo = re.sub(r'<script type="text/javascript">.*?</script>', '', conteudo, flags=re.DOTALL | re.IGNORECASE)
            # ===== REMOVE O TÍTULO "Introdução" NOVAMENTE =====
            conteudo = re.sub(r'<h2[^>]*>Introdução\s*</h2>', '', conteudo, flags=re.IGNORECASE)
            conteudo = re.sub(r'<h2[^>]*id="[^"]*introducao[^"]*"[^>]*>Introdução\s*</h2>', '', conteudo, flags=re.IGNORECASE)
        
        titulo_map = {
            'review': f"{nome} - {t['review']}",
            'guia': f"Guia Completo: {nome}",
            'lista': f"Lista: {nome}",
            'tutorial': f"Tutorial: {nome}",
            'comparativo': f"Comparativo: {nome}",
            'artigo': f"{nome} - {t['review']}"
        }
        titulo = titulo_map.get(tipo, f"{nome} - {t['review']}")
        
        url = f"{CONFIG['url_base']}/{categoria}/{slug}/"
        data_formatada = datetime.strptime(data_publicacao, "%Y-%m-%d").strftime("%d/%m/%Y") if data_publicacao else datetime.now().strftime("%d/%m/%Y")
        
        template = self.ler_template('artigo.html')
        
        if template:
            relacionados_html = ""
            relacionados = self.get_artigos_publicados()
            relacionados = [a for a in relacionados if a['slug'] != slug][:4]
            for a in relacionados:
                img = self.gerar_imagem(a['nome'], a['categoria'])
                data_formatada_rel = datetime.strptime(a['data_publicacao'], "%Y-%m-%d").strftime("%d/%m/%Y") if a['data_publicacao'] else datetime.now().strftime("%d/%m/%Y")
                titulo_cat_rel = self.formatar_titulo_categoria(a['categoria'])
                tempo_leitura = random.randint(4, 8)
                
                card = f'''<article class="post-card">
  <a href="/{a['categoria']}/{a['slug']}/" class="post-card-img">
    <img src="{img}" alt="{a['nome']}">
  </a>
  <div class="post-card-body">
    <a href="/{a['categoria']}/" class="tag">{titulo_cat_rel}</a>
    <h3 class="post-card-title"><a href="/{a['categoria']}/{a['slug']}/">{a['nome']}</a></h3>
    <div class="post-card-meta">
      <span>{data_formatada_rel}</span>
      <span class="meta-dot">·</span>
      <span>{tempo_leitura} min de leitura</span>
    </div>
    <p class="post-card-excerpt">{a['nome'][:120]}...</p>
    <a href="/{a['categoria']}/{a['slug']}/" class="read-more">Ler mais →</a>
  </div>
</article>'''
                relacionados_html += card
            
            # ===== ADICIONA O HEAD =====
            head_html = self.get_head(titulo, descricao, url, imagem)
            
            variaveis = {
                'HEAD': head_html,
                'TITULO': titulo,
                'CONTEUDO': conteudo,
                'CATEGORIA': titulo_categoria,
                'DATA': data_formatada,
                'IMAGEM': imagem,
                'AUTOR': autor,
                'LINK_AFILIADO': link,
                'URL': url,
                'DESCRICAO': descricao,
                'TEMPO_LEITURA': str(random.randint(4, 8)),
                'IDIOMA': t['lang'],
                'NOME_SITE': CONFIG['nome_site'],
                'HEADER': self.get_header('inicio', categoria),
                'FOOTER': self.get_footer(),
                'RELACIONADOS': relacionados_html
            }
            html = self.renderizar_template('artigo.html', variaveis)
            
        else:
            artigos_relacionados = self.get_artigos_relacionados(categoria, slug)
            
            if link and link.strip():
                cta_html = f"""
                <div class="cta-box">
                    <h3>{t['comprar']}</h3>
                    <p>Garanta o seu {nome} com preço especial</p>
                    <a href="{link}" class="btn-primary" target="_blank" rel="nofollow sponsored">{t['ver_oferta']}</a>
                </div>
                """
            else:
                cta_html = ""
            
            html = f"""<!DOCTYPE html>
<html lang="{t['lang']}">
{self.get_head(
    titulo=titulo,
    descricao=descricao,
    url=url,
    imagem=imagem,
    extra=''
)}
<body>
    {self.get_header('inicio', categoria)}
    <main class="container">
        <div class="banner">
            <h1>{CONFIG['nome']}</h1>
            <p>{CONFIG['descricao']}</p>
        </div>
        
        <div class="artigo">
            <div class="meta">
                <span>📅 {t['data_publicacao']} {data_formatada}</span>
                <span>✍️ {t['autor']} {autor}</span>
                <span class="categoria">📂 {titulo_categoria}</span>
                <span>⏱️ {random.randint(4, 8)} min de leitura</span>
            </div>
            
            <h1 id="introducao">{titulo}</h1>
            <img src="{imagem}" alt="{nome}" class="imagem-destaque" loading="lazy">
            
            {conteudo}
            
            {cta_html}
            
            <div style="margin-top:25px;padding-top:15px;border-top:1px solid var(--fundo);">
                <p><strong>{t['compartilhar']}:</strong>
                <a href="https://wa.me/?text={titulo} - {url}" target="_blank" style="color:var(--whatsapp);font-weight:600;text-decoration:none;">WhatsApp</a> |
                <a href="https://www.facebook.com/sharer/sharer.php?u={url}" target="_blank" style="color:#1877f2;font-weight:600;text-decoration:none;">Facebook</a> |
                <a href="https://twitter.com/intent/tweet?text={titulo}&url={url}" target="_blank" style="color:#000;font-weight:600;text-decoration:none;">Twitter</a>
                </p>
            </div>
        </div>
        
        <aside class="sidebar">
            <div class="widget">
                <h3>📚 {t['leia_tambem']}</h3>
                <ul>
                    {artigos_relacionados}
                </ul>
            </div>
        </aside>
    </main>
    {self.get_footer()}
    <script src="/assets/js/script.js"></script>
</body>
</html>"""
        
        pasta.mkdir(parents=True, exist_ok=True)
        caminho = pasta / "index.html"
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html)
        
        artigo_data['status'] = 'publicado'
        if not artigo_data.get('data_publicacao'):
            artigo_data['data_publicacao'] = datetime.now().strftime("%Y-%m-%d")
        if not artigo_data.get('autor'):
            artigo_data['autor'] = CONFIG['autor']
            
        artigos = self.ler_csv()
        for a in artigos:
            if a.get('artigo') == nome:
                a['status'] = 'publicado'
                if not a.get('data_publicacao'):
                    a['data_publicacao'] = datetime.now().strftime("%Y-%m-%d")
                if not a.get('autor'):
                    a['autor'] = CONFIG['autor']
                break
        self.salvar_csv(artigos)
        
        self.criar_pagina_categoria(categoria)
        
        print(f"   ✅ Salvo: docs/{categoria}/{slug}/index.html")
        return caminho
    
    def get_artigos_relacionados(self, categoria_atual, slug_atual):
        artigos = self.get_artigos_publicados()
        relacionados = []
        for a in artigos:
            if a['slug'] != slug_atual:
                relacionados.append(a)
        
        if not relacionados:
            return '<li>Nenhum artigo relacionado</li>'
        
        relacionados = relacionados[:4]
        html = ""
        for a in relacionados:
            html += f'<li><a href="/{a["categoria"]}/{a["slug"]}/">{a["nome"]}</a></li>\n'
        
        return html
    
    # ==================== SITEMAP ====================
    
    def criar_sitemap(self):
        print("\n🗺️ GERANDO SITEMAP")
        print("-" * 40)
        
        sitemap_path = self.docs / "sitemap.xml"
        urlset = ET.Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        
        c = CONFIG
        
        paginas = [
            ('', 1.0),
            ('sobre.html', 0.5),
            ('contato.html', 0.5),
            ('politica-privacidade.html', 0.3),
            ('cookies.html', 0.3),
        ]
        
        for pagina, prioridade in paginas:
            url_elem = ET.SubElement(urlset, 'url')
            loc = ET.SubElement(url_elem, 'loc')
            loc.text = f"{c['url_base']}/{pagina}"
            lastmod = ET.SubElement(url_elem, 'lastmod')
            lastmod.text = datetime.now().strftime('%Y-%m-%d')
            changefreq = ET.SubElement(url_elem, 'changefreq')
            changefreq.text = 'monthly'
            priority = ET.SubElement(url_elem, 'priority')
            priority.text = str(prioridade)
        
        for cat in self.get_categorias():
            url_elem = ET.SubElement(urlset, 'url')
            loc = ET.SubElement(url_elem, 'loc')
            loc.text = f"{c['url_base']}/{cat}/"
            lastmod = ET.SubElement(url_elem, 'lastmod')
            lastmod.text = datetime.now().strftime('%Y-%m-%d')
            changefreq = ET.SubElement(url_elem, 'changefreq')
            changefreq.text = 'weekly'
            priority = ET.SubElement(url_elem, 'priority')
            priority.text = '0.6'
        
        for a in self.get_artigos_publicados():
            url_elem = ET.SubElement(urlset, 'url')
            loc = ET.SubElement(url_elem, 'loc')
            loc.text = f"{c['url_base']}/{a['categoria']}/{a['slug']}/"
            lastmod = ET.SubElement(url_elem, 'lastmod')
            lastmod.text = datetime.now().strftime('%Y-%m-%d')
            changefreq = ET.SubElement(url_elem, 'changefreq')
            changefreq.text = 'weekly'
            priority = ET.SubElement(url_elem, 'priority')
            priority.text = '0.7'
        
        xml_str = ET.tostring(urlset, encoding='unicode')
        xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")
        
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(xml_pretty)
        print("✅ Sitemap.xml criado")
        
        robots_path = self.docs / "robots.txt"
        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write(f"""User-agent: *
Allow: /
Disallow: /assets/
Disallow: /404.html

Sitemap: {c['url_base']}/sitemap.xml
""")
        print("✅ Robots.txt criado")
    
    # ==================== RECRIAR TUDO ====================
    
    def recriar_tudo(self):
        print("\n🔄 RECRIANDO TUDO DO ZERO")
        print("=" * 40)
        print("📄 Recriando páginas...")
        self.criar_todas_paginas()
        print("📂 Recriando categorias...")
        self.criar_todas_categorias()
        print("🏠 Recriando index...")
        self.criar_index()
        print("🗺️ Recriando sitemap...")
        self.criar_sitemap()
        print("\n✅ Tudo recriado com sucesso!")
        input("\nPressione Enter...")
    
    def sincronizar_agora(self):
        print("\n🔄 SINCRONIZANDO STATUS")
        print("=" * 40)
        print("Verifica se os artigos marcados como 'publicado'")
        print("ainda existem na pasta docs/.")
        print("Se um artigo foi deletado manualmente,")
        print("ele volta para 'rascunho' no CSV.\n")
        
        self.sincronizar_status(mostrar_confirmacao=True)
        self.criar_index()
        self.criar_todas_categorias()
        self.criar_sitemap()
        print("\n✅ Sincronização concluída!")
        input("\nPressione Enter...")
    
    # ==================== VER POR CATEGORIA ====================
    
    def ver_por_categoria(self):
        artigos = self.ler_csv()
        categorias = self.get_categorias()
        categorias_com_artigos = set()
        
        # Pega todas as categorias que têm artigos (publicados ou rascunhos)
        for a in artigos:
            cat = a.get('categoria', 'geral')
            if cat:
                categorias_com_artigos.add(cat)
        
        if not categorias_com_artigos:
            print("\n❌ Nenhuma categoria encontrada")
            input("\nPressione Enter...")
            return
        
        categorias_lista = sorted(list(categorias_com_artigos))
        
        print("\n📂 CATEGORIAS DISPONÍVEIS:")
        for i, cat in enumerate(categorias_lista, 1):
            titulo = self.formatar_titulo_categoria(cat)
            count = len([a for a in artigos if a.get('categoria') == cat])
            publicados = len([a for a in artigos if a.get('categoria') == cat and a.get('status') == 'publicado'])
            print(f"  {i}. {titulo} ({publicados}/{count} publicados)")
        
        escolha = self.ler_numero("\nEscolha uma categoria: ", 1, len(categorias_lista))
        if escolha is None:
            return
        
        categoria = categorias_lista[escolha - 1]
        artigos_cat = [a for a in artigos if a.get('categoria') == categoria]
        titulo_cat = self.formatar_titulo_categoria(categoria)
        
        print(f"\n📋 ARTIGOS DA CATEGORIA {titulo_cat.upper()}:")
        print("-" * 60)
        for i, a in enumerate(artigos_cat, 1):
            status = a.get('status', 'rascunho')
            status_icon = "✅" if status == 'publicado' else "⏳"
            status_text = "Publicado" if status == 'publicado' else "Rascunho"
            nome = a.get('artigo', 'Sem nome')[:40]
            print(f"  {i}. {status_icon} {nome}")
        print("-" * 60)
        input("\nPressione Enter...")
    
    # ==================== PUBLICAR UM (COM PREVIEW) ====================
    
    def publicar_um(self):
        self.sincronizar_status(mostrar_confirmacao=False)
        artigos = self.ler_csv()
        pendentes = [a for a in artigos if a.get('status', 'rascunho').lower() != 'publicado']
        
        if not pendentes:
            print("\n✅ Nenhum artigo pendente para publicar")
            input("\nPressione Enter...")
            return
        
        print("\n📋 RASCUNHOS DISPONÍVEIS:")
        print("-" * 60)
        for i, a in enumerate(pendentes, 1):
            titulo_cat = self.formatar_titulo_categoria(a.get('categoria', 'geral'))
            print(f"  {i}. {a.get('artigo', 'Sem nome')} ({titulo_cat})")
        print("-" * 60)
        
        escolha = self.ler_numero("\nEscolha o número do artigo: ", 1, len(pendentes))
        if escolha is None:
            return
        
        a = pendentes[escolha - 1]
        titulo_cat = self.formatar_titulo_categoria(a.get('categoria', 'geral'))
        
        # PREVIEW
        print("\n" + "=" * 60)
        print("📝 PREVIEW DO ARTIGO:")
        print("=" * 60)
        print(f"  Título: {a.get('artigo')}")
        print(f"  Categoria: {titulo_cat}")
        print(f"  Palavras-chave: {a.get('palavras_chave', '')}")
        print(f"  Descrição: {a.get('descricao', '')}")
        print(f"  Tipo: {a.get('tipo', 'review')}")
        print(f"  Data: {a.get('data_publicacao', 'Não definida')}")
        print("=" * 60)
        
        if not self.ler_sim_nao("\nPublicar este artigo? (s/n): "):
            return
        
        self.criar_artigo(a, forcar=True, revisar=True)
        self.criar_index()
        self.criar_todas_categorias()
        self.criar_sitemap()
        print("\n✅ Publicado!")
        input("\nPressione Enter...")
    
    # ==================== PUBLICAR EM LOTES ====================
    
    def publicar_lotes(self):
        print("\n📦 PUBLICAR EM LOTES")
        print("=" * 50)
        
        artigos = self.ler_csv()
        pendentes = [a for a in artigos if a.get('status', 'rascunho').lower() != 'publicado']
        
        if not pendentes:
            print("✅ Nenhum artigo pendente para publicar")
            input("\nPressione Enter...")
            return
        
        # Mostrar categorias com contagem
        categorias = {}
        for a in pendentes:
            cat = a.get('categoria', 'geral')
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(a)
        
        print(f"\n📊 {len(pendentes)} artigos disponíveis")
        print("\n📂 CATEGORIAS DISPONÍVEIS:")
        cats = list(categorias.keys())
        for i, cat in enumerate(cats, 1):
            titulo = self.formatar_titulo_categoria(cat)
            print(f"  {i}. {titulo} ({len(categorias[cat])} artigos)")
        
        print("\nEscolha uma opção:")
        print("  [0] Publicar de todas as categorias")
        for i, cat in enumerate(cats, 1):
            titulo = self.formatar_titulo_categoria(cat)
            print(f"  [{i}] Publicar apenas da categoria {titulo}")
        
        opcao = input("\n➡️  ").strip()
        
        if opcao == '0':
            artigos_selecionados = pendentes
        elif opcao.isdigit() and 1 <= int(opcao) <= len(cats):
            cat_selecionada = cats[int(opcao) - 1]
            artigos_selecionados = categorias[cat_selecionada]
            titulo_cat = self.formatar_titulo_categoria(cat_selecionada)
            print(f"\n📋 ARTIGOS DA CATEGORIA {titulo_cat.upper()}:")
            for i, a in enumerate(artigos_selecionados, 1):
                print(f"  {i}. {a.get('artigo', 'Sem nome')}")
        else:
            print("❌ Opção inválida")
            input("\nPressione Enter...")
            return
        
        if not artigos_selecionados:
            print("❌ Nenhum artigo selecionado")
            input("\nPressione Enter...")
            return
        
        print(f"\n🎯 Quantos artigos publicar? (máx {len(artigos_selecionados)})")
        print("   (Digite um número ou 't' para todos)")
        
        opcao_qtd = input("\n➡️  ").strip().lower()
        
        if opcao_qtd == 't':
            quantidade = len(artigos_selecionados)
        else:
            try:
                quantidade = int(opcao_qtd)
                if quantidade <= 0:
                    print("❌ Número inválido")
                    input("\nPressione Enter...")
                    return
                quantidade = min(quantidade, len(artigos_selecionados))
            except ValueError:
                print("❌ Opção inválida")
                input("\nPressione Enter...")
                return
        
        publicar_agora = artigos_selecionados[:quantidade]
        
        print(f"\n📦 Publicando {len(publicar_agora)} artigos...")
        print("-" * 40)
        
        for i, a in enumerate(publicar_agora, 1):
            print(f"\n[{i}/{len(publicar_agora)}] Publicando: {a.get('artigo')}")
            
            data_pub = (datetime.now() + timedelta(days=i-1)).strftime("%Y-%m-%d")
            a['data_publicacao'] = data_pub
            
            self.criar_artigo(a, revisar=True)
            
            if i < len(publicar_agora):
                espera = random.randint(2, 5)
                print(f"   ⏳ Aguardando {espera}s...")
                time.sleep(espera)
        
        self.criar_index()
        self.criar_todas_categorias()
        self.criar_sitemap()
        
        print("\n" + "=" * 40)
        print(f"✅ {len(publicar_agora)} artigos publicados com sucesso!")
        print(f"📊 Restam {len(pendentes) - len(publicar_agora)} artigos pendentes")
        input("\nPressione Enter...")
    
    # ==================== PUBLICAR NATURAL ====================
    
    def publicar_natural(self, quantidade=None):
        if quantidade is None:
            quantidade = CONFIG.get('publicar_por_dia', 3)
        
        print(f"\n🌱 PUBLICAR NATURAL ({quantidade} artigos por dia)")
        print("=" * 50)
        
        artigos = self.ler_csv()
        pendentes = [a for a in artigos if a.get('status', 'rascunho').lower() != 'publicado']
        
        if not pendentes:
            print("✅ Nenhum artigo pendente para publicar")
            input("\nPressione Enter...")
            return
        
        print(f"📊 {len(pendentes)} artigos disponíveis")
        print(f"⏱️  Serão publicados {min(quantidade, len(pendentes))} agora")
        
        if not self.ler_sim_nao("\nContinuar? (s/n): "):
            return
        
        publicar_agora = pendentes[:quantidade]
        
        for i, a in enumerate(publicar_agora, 1):
            print(f"\n[{i}/{len(publicar_agora)}] Publicando: {a.get('artigo')}")
            
            data_pub = (datetime.now() + timedelta(days=i-1)).strftime("%Y-%m-%d")
            a['data_publicacao'] = data_pub
            
            self.criar_artigo(a, revisar=True)
            
            if i < len(publicar_agora):
                espera = random.randint(5, 10)
                print(f"   ⏳ Aguardando {espera}s...")
                time.sleep(espera)
        
        self.criar_index()
        self.criar_todas_categorias()
        self.criar_sitemap()
        
        print("\n✅ Publicação natural concluída!")
        input("\nPressione Enter...")
    
    # ==================== MENU PRINCIPAL ====================
    
    def ver_artigos(self):
        self.sincronizar_status(mostrar_confirmacao=False)
        artigos = self.ler_csv()
        
        if not artigos:
            print("\n❌ Nenhum artigo cadastrado")
            input("\nPressione Enter...")
            return
        
        # Estatísticas
        total = len(artigos)
        publicados = [a for a in artigos if a.get('status') == 'publicado']
        rascunhos = [a for a in artigos if a.get('status') != 'publicado']
        
        # Contagem por categoria
        categorias = {}
        for a in artigos:
            cat = a.get('categoria', 'geral')
            if cat not in categorias:
                categorias[cat] = {'total': 0, 'publicados': 0}
            categorias[cat]['total'] += 1
            if a.get('status') == 'publicado':
                categorias[cat]['publicados'] += 1
        
        print("\n" + "=" * 70)
        print("📋 TODOS OS ARTIGOS")
        print("=" * 70)
        
        # Resumo
        print(f"\n📊 TOTAL: {total} artigos")
        print(f"   ✅ Publicados: {len(publicados)}")
        print(f"   ⏳ Rascunhos: {len(rascunhos)}")
        
        if categorias:
            print("\n📂 POR CATEGORIA:")
            for cat, dados in categorias.items():
                titulo = self.formatar_titulo_categoria(cat)
                barra = "█" * int((dados['publicados'] / dados['total']) * 20) if dados['total'] > 0 else ""
                print(f"   {titulo}: {dados['publicados']}/{dados['total']} publicados {barra}")
        
        # Lista de artigos
        print("\n" + "-" * 70)
        print(f"{'#':<4} {'Artigo':<45} {'Status':<12} {'Categoria':<12}")
        print("-" * 70)
        
        for i, a in enumerate(artigos, 1):
            nome = a.get('artigo', 'Sem nome')[:42]
            status = a.get('status', 'rascunho')
            status_icon = "✅" if status == 'publicado' else "⏳"
            status_text = "Publicado" if status == 'publicado' else "Rascunho"
            categoria = self.formatar_titulo_categoria(a.get('categoria', 'geral'))[:10]
            print(f"{i:<4} {nome:<45} {status_icon} {status_text:<10} {categoria}")
        
        print("-" * 70)
        
        # Artigos publicados em destaque
        if publicados:
            print("\n✅ ARTIGOS PUBLICADOS:")
            for a in publicados:
                print(f"   📄 {a.get('artigo')} → /{a['categoria']}/{self.criar_slug(a.get('artigo'))}/")
        else:
            print("\n✅ ARTIGOS PUBLICADOS: (nenhum)")
        
        input("\nPressione Enter...")
    
    def revisar_artigo(self):
        publicados = self.get_artigos_publicados()
        
        if not publicados:
            print("\n❌ Nenhum artigo publicado")
            input("\nPressione Enter...")
            return
        
        print("\n📋 PUBLICADOS:")
        for i, p in enumerate(publicados, 1):
            titulo_cat = self.formatar_titulo_categoria(p['categoria'])
            print(f"   {i}. {p['nome']} ({titulo_cat})")
        
        escolha = self.ler_numero("\nNúmero: ", 1, len(publicados))
        if escolha is None:
            return
        
        slug = publicados[escolha - 1]['slug']
        nome = publicados[escolha - 1]['nome']
        categoria = publicados[escolha - 1]['categoria']
        
        while True:
            print(f"\n📝 {nome}")
            print("1. 📖 Ver no navegador")
            print("2. 🔄 Regenerar com IA (com revisão)")
            print("3. 🗑️ Despublicar (voltar para rascunho)")
            print("4. ❌ Voltar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                caminho = self.docs / categoria / slug / "index.html"
                if caminho.exists():
                    webbrowser.open(str(caminho))
                else:
                    print("❌ Arquivo não encontrado!")
                input("Pressione Enter...")
            elif opcao == "2":
                print("\n🔄 Regenerando com revisão...")
                artigos = self.ler_csv()
                link = "https://afiliado.com/produto"
                for a in artigos:
                    if self.criar_slug(a.get('artigo', '')) == slug:
                        link = a.get('links_afiliados', 'https://afiliado.com/produto')
                        break
                self.criar_artigo({'artigo': nome, 'links_afiliados': link, 'categoria': categoria}, forcar=True, revisar=True)
                self.criar_index()
                print("✅ Regenerado com revisão!")
                input("Pressione Enter...")
            elif opcao == "3":
                if self.ler_sim_nao(f"Despublicar '{nome}'? (s/n): "):
                    pasta = self.docs / categoria / slug
                    if pasta.exists():
                        shutil.rmtree(pasta)
                    artigos = self.ler_csv()
                    for a in artigos:
                        if self.criar_slug(a.get('artigo', '')) == slug:
                            a['status'] = 'rascunho'
                            break
                    self.salvar_csv(artigos)
                    self.criar_index()
                    self.criar_todas_categorias()
                    print(f"✅ '{nome}' voltou para rascunho!")
                    input("Pressione Enter...")
                    return
            elif opcao == "4":
                return
    
    def deletar_artigo(self):
        publicados = self.get_artigos_publicados()
        
        if not publicados:
            print("\n❌ Nenhum artigo")
            input("\nPressione Enter...")
            return
        
        print("\n🗑️ DELETAR:")
        for i, p in enumerate(publicados, 1):
            titulo_cat = self.formatar_titulo_categoria(p['categoria'])
            print(f"   {i}. {p['nome']} ({titulo_cat})")
        
        escolha = self.ler_numero("\nNúmero: ", 1, len(publicados))
        if escolha is None:
            return
        
        slug = publicados[escolha - 1]['slug']
        nome = publicados[escolha - 1]['nome']
        categoria = publicados[escolha - 1]['categoria']
        
        if not self.ler_sim_nao(f"Deletar '{nome}'? (s/n): "):
            return
        
        pasta = self.docs / categoria / slug
        if pasta.exists():
            shutil.rmtree(pasta)
            print(f"   🗑️ Pasta removida: {categoria}/{slug}")
        
        artigos = self.ler_csv()
        for a in artigos:
            if self.criar_slug(a.get('artigo', '')) == slug:
                a['status'] = 'rascunho'
                break
        self.salvar_csv(artigos)
        self.criar_index()
        self.criar_todas_categorias()
        self.criar_sitemap()
        print(f"✅ {nome} deletado!")
        input("\nPressione Enter...")
    
    def menu(self):
        while True:
            self.mostrar_painel()
            
            print("\n📝 CONTEÚDO")
            print("  [1] Ver todos os artigos")
            print("  [2] Ver por categoria")
            print("  [3] Publicar UM (com preview)")
            print("  [4] Publicar em LOTES")
            print("  [5] Revisar/Regenerar artigo")
            
            print("\n🛠️ FERRAMENTAS")
            print("  [6] Recriar TUDO")
            print("  [7] Sincronizar status")
            print("  [8] Deletar artigo")
            
            print("\n  [0] Sair")
            print("=" * 70)
            
            opcao = input("\n🎯 Escolha: ").strip()
            
            if opcao == "1":
                self.ver_artigos()
            elif opcao == "2":
                self.ver_por_categoria()
            elif opcao == "3":
                self.publicar_um()
            elif opcao == "4":
                self.publicar_lotes()
            elif opcao == "5":
                self.revisar_artigo()
            elif opcao == "6":
                self.recriar_tudo()
            elif opcao == "7":
                self.sincronizar_agora()
            elif opcao == "8":
                self.deletar_artigo()
            elif opcao == "0":
                print("\n👋 Até logo!")
                break
            else:
                print("❌ Opção inválida")
                input("\nPressione Enter...")

# ============================================================
# ===== EXECUÇÃO ==============================================
# ============================================================

if __name__ == "__main__":
    gerador = Gerador()
    gerador.menu()