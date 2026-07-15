#!/usr/bin/env python3
"""
GERADOR DE ARTIGOS - HOMEDECOR
VERSÃO COM SINCRONIZAÇÃO AUTOMÁTICA DE STATUS
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
    'nome_site': 'Top Ofertas',
    'descricao': 'Inspirações e reviews para transformar sua casa em um lar aconchegante e estiloso.',
    'url_base': 'https://homedecorcasa.netlify.app',
    'idioma': 'pt',
    'ano': datetime.now().year,
    'csv': 'artigos.csv',
    'usar_ia_imagens': True,
    'autor': 'Equipe Top Ofertas',
    'email_contato': 'contato@homedecorcasa.netlify.app',
    'publicar_por_dia': 3,
    'redes_sociais': {
        'instagram': 'https://instagram.com/topofertas',
        'facebook': 'https://facebook.com/topofertas',
        'twitter': 'https://twitter.com/topofertas'
    },
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
        self.assets_css = self.docs / "assets" / "css"
        self.assets_js = self.docs / "assets" / "js"
        self.assets_img = self.docs / "assets" / "img"
        
        # Criar pastas
        self.assets_css.mkdir(parents=True, exist_ok=True)
        self.assets_js.mkdir(parents=True, exist_ok=True)
        self.assets_img.mkdir(parents=True, exist_ok=True)
        
        # Carregar config
        self.carregar_config()
        
        # Idioma
        self.idioma = CONFIG.get('idioma', 'pt')
        self.t = IDIOMAS.get(self.idioma, IDIOMAS['pt'])
        
        # APIs
        self.ia_api_key = os.getenv("OPENROUTER_API_KEY")
        
        # Criar arquivos base
        self.criar_csv()
        self.criar_css()
        self.criar_js()
        
        self.mostrar_painel()
    
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
    
    def sincronizar_status(self):
        """Verifica se os artigos publicados ainda existem na pasta docs"""
        artigos = self.ler_csv()
        alterado = False
        
        for a in artigos:
            if a.get('status') == 'publicado':
                slug = self.criar_slug(a.get('artigo', ''))
                categoria = a.get('categoria', 'geral')
                if not (self.docs / categoria / slug / "index.html").exists():
                    a['status'] = 'rascunho'
                    alterado = True
                    print(f"   🔄 Artigo '{a.get('artigo')}' voltou para rascunho (pasta deletada)")
        
        if alterado:
            self.salvar_csv(artigos)
            print("✅ Status sincronizado!")
        
        return alterado
    
    # ==================== PAINEL ====================
    
    def mostrar_painel(self):
        self.sincronizar_status()
        
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
        print(f"  🏷️  {len(categorias)} categorias: {', '.join(list(categorias)[:5])}")
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
            ["artigo", "links_afiliados", "status", "categoria", "palavras_chave", "descricao", "idioma", "data_publicacao", "autor"],
            ["Poltrona Conforto Ergonômica", "https://afiliado.com/poltrona", "rascunho", "decoração", "poltrona conforto ergonômica", "Review completo da Poltrona Conforto", "pt", "", "Equipe Top Ofertas"],
            ["Mesa de Centro Design Moderno", "https://afiliado.com/mesa", "rascunho", "decoração", "mesa centro design moderno", "Análise detalhada da Mesa de Centro", "pt", "", "Equipe Top Ofertas"],
            ["Luminária Pendente Industrial", "https://afiliado.com/luminaria", "rascunho", "decoração", "luminária pendente industrial", "Review da Luminária Pendente", "pt", "", "Equipe Top Ofertas"],
            ["Tapete Persa Moderno", "https://afiliado.com/tapete", "rascunho", "decoração", "tapete persa moderno", "Guia do Tapete Persa", "pt", "", "Equipe Top Ofertas"],
            ["Estante Rústica 6 Prateleiras", "https://afiliado.com/estante", "rascunho", "decoração", "estante rústica 6 prateleiras", "Review da Estante Rústica", "pt", "", "Equipe Top Ofertas"],
            ["Quadro Decorativo Abstrato", "https://afiliado.com/quadro", "rascunho", "decoração", "quadro decorativo abstrato", "Review do Quadro Decorativo", "pt", "", "Equipe Top Ofertas"],
        ]
        
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(dados)
        print(f"✅ CSV criado: {CONFIG['csv']}")
    
    # ==================== CSS ====================
    
    def criar_css(self):
        css_path = self.assets_css / "style.css"
        if css_path.exists():
            return
        
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

[data-theme="dark"] {{
    --fundo: #1a1a2e;
    --texto: #e0e0e0;
    --card: #16213e;
    --sombra: 0 4px 20px rgba(0,0,0,0.3);
}}

body {{
    font-family: 'Nunito', sans-serif;
    background: var(--fundo);
    color: var(--texto);
    line-height: 1.7;
    transition: background var(--transicao), color var(--transicao);
}}

.container {{ max-width: 1100px; margin: 0 auto; padding: 0 20px; }}

/* ===== HEADER ===== */
header {{
    background: var(--card);
    padding: 15px 0;
    border-bottom: 4px solid var(--primaria);
    box-shadow: var(--sombra);
    position: sticky;
    top: 0;
    z-index: 1000;
    transition: background var(--transicao);
}}

header .container {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
}}

.logo {{
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--texto);
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
}}
.logo .icone {{ font-size: 2rem; }}
.logo .nome {{ color: var(--primaria); }}

/* ===== MENU ===== */
.menu-toggle {{
    display: none;
    background: none;
    border: none;
    font-size: 1.8rem;
    color: var(--texto);
    cursor: pointer;
    padding: 5px 10px;
}}

nav {{
    display: flex;
    gap: 5px;
    flex-wrap: wrap;
    align-items: center;
}}

nav a {{
    color: var(--texto);
    text-decoration: none;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
    transition: all var(--transicao);
    white-space: nowrap;
}}

nav a:hover, nav a.ativo {{
    background: var(--primaria);
    color: white;
}}

.theme-toggle {{
    background: none;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    color: var(--texto);
    padding: 5px 10px;
    border-radius: 50%;
    transition: background var(--transicao);
}}
.theme-toggle:hover {{ background: var(--fundo); }}

/* ===== BANNER ===== */
.banner {{
    background: linear-gradient(135deg, var(--fundo), var(--destaque));
    padding: 40px 30px;
    border-radius: var(--borda);
    margin: 20px 0 30px;
    text-align: center;
    border: 1px solid rgba(196, 149, 106, 0.15);
}}
.banner h1 {{ font-size: 2.2rem; font-weight: 800; }}
.banner p {{ font-size: 1.05rem; opacity: 0.8; margin-top: 8px; }}

/* ===== ARTIGO ===== */
.artigo {{
    background: var(--card);
    padding: 35px;
    border-radius: var(--borda);
    margin: 20px 0;
    box-shadow: var(--sombra);
    transition: background var(--transicao);
}}

.artigo .meta {{
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    color: #888;
    font-size: 0.85rem;
    margin-bottom: 18px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--fundo);
}}
.artigo .meta .categoria {{
    background: var(--primaria);
    color: white;
    padding: 2px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
}}
.artigo .imagem-destaque {{
    width: 100%;
    height: 350px;
    object-fit: cover;
    border-radius: var(--borda);
    margin: 12px 0 20px;
}}
.artigo h1 {{ font-size: 2.2rem; margin-bottom: 12px; }}
.artigo h2 {{
    color: var(--secundaria);
    margin: 30px 0 10px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--fundo);
}}
.artigo h3 {{ color: var(--secundaria); margin: 20px 0 8px; }}
.artigo p {{ margin-bottom: 14px; font-size: 1.02rem; }}
.artigo ul {{ margin: 10px 0 16px 22px; }}
.artigo li {{ margin-bottom: 5px; }}

/* ===== FAQ ===== */
.faq-item {{
    margin: 8px 0;
    padding: 12px 18px;
    background: var(--fundo);
    border-radius: var(--borda);
    cursor: pointer;
    transition: all var(--transicao);
}}
.faq-item:hover {{ background: var(--destaque); }}
.faq-item .pergunta {{
    font-weight: 700;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.faq-item .resposta {{
    display: none;
    padding-top: 8px;
    margin-top: 8px;
    border-top: 1px solid var(--primaria);
}}
.faq-item.open .resposta {{ display: block; }}

/* ===== TABELA ===== */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 18px 0;
    border-radius: var(--borda);
    overflow: hidden;
}}
table th {{
    background: var(--primaria);
    color: white;
    padding: 10px 14px;
    text-align: left;
}}
table td {{
    padding: 8px 14px;
    border-bottom: 1px solid var(--fundo);
}}
table tr:nth-child(even) {{ background: var(--fundo); }}

/* ===== CTA ===== */
.cta {{
    background: var(--fundo);
    padding: 30px;
    border-radius: var(--borda);
    margin: 25px 0;
    text-align: center;
}}

.btn {{
    display: inline-block;
    background: var(--primaria);
    color: white;
    padding: 12px 35px;
    border-radius: 50px;
    text-decoration: none;
    font-weight: 700;
    transition: all var(--transicao);
    border: none;
    cursor: pointer;
}}
.btn:hover {{
    background: var(--secundaria);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(196, 149, 106, 0.3);
}}
.btn-pequeno {{ padding: 8px 18px; font-size: 0.85rem; }}

/* ===== SIDEBAR ===== */
.sidebar {{
    display: grid;
    gap: 20px;
    margin: 20px 0;
}}

.widget {{
    background: var(--card);
    padding: 20px;
    border-radius: var(--borda);
    box-shadow: var(--sombra);
    border-left: 4px solid var(--primaria);
    transition: background var(--transicao);
}}
.widget h3 {{ color: var(--secundaria); margin-bottom: 10px; font-size: 1.05rem; }}
.widget ul {{ list-style: none; padding: 0; }}
.widget ul li {{
    padding: 6px 0;
    border-bottom: 1px solid var(--fundo);
}}
.widget ul li a {{
    color: var(--texto);
    text-decoration: none;
    transition: color var(--transicao);
}}
.widget ul li a:hover {{ color: var(--primaria); }}

/* ===== GRID ===== */
.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 25px;
    margin: 25px 0;
}}

.card {{
    background: var(--card);
    padding: 20px;
    border-radius: var(--borda);
    box-shadow: var(--sombra);
    transition: all var(--transicao);
    border-left: 4px solid var(--primaria);
}}
.card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}}
.card .card-img {{
    width: 100%;
    height: 180px;
    object-fit: cover;
    border-radius: 10px;
    margin-bottom: 10px;
}}
.card .card-meta {{
    font-size: 0.8rem;
    color: #888;
    margin-bottom: 6px;
}}
.card h3 {{ font-size: 1.05rem; margin-bottom: 6px; }}
.card h3 a {{
    color: var(--texto);
    text-decoration: none;
    transition: color var(--transicao);
}}
.card h3 a:hover {{ color: var(--primaria); }}

/* ===== FOOTER ===== */
footer {{
    background: var(--texto);
    color: white;
    padding: 35px 0;
    margin-top: 40px;
}}
footer a {{ color: var(--primaria); text-decoration: none; }}
footer .footer-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 25px;
    margin-bottom: 20px;
}}
footer .footer-grid h4 {{
    color: var(--primaria);
    margin-bottom: 8px;
    font-size: 1.05rem;
}}
footer .footer-grid ul {{ list-style: none; padding: 0; }}
footer .footer-grid ul li {{ padding: 3px 0; }}
footer .footer-grid ul li a {{
    color: rgba(255,255,255,0.7);
    font-size: 0.9rem;
    transition: color var(--transicao);
}}
footer .footer-grid ul li a:hover {{ color: var(--primaria); }}
footer .social-links {{
    display: flex;
    gap: 12px;
    justify-content: center;
    margin: 12px 0;
}}
footer .social-links a {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
    color: white;
    font-size: 1.1rem;
    transition: all var(--transicao);
    text-decoration: none;
}}
footer .social-links a:hover {{
    background: var(--primaria);
    transform: translateY(-3px);
}}
footer .copyright {{
    text-align: center;
    font-size: 0.85rem;
    opacity: 0.6;
    padding-top: 15px;
    border-top: 1px solid rgba(255,255,255,0.08);
}}

/* ===== COOKIES ===== */
.cookies-banner {{
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--card);
    padding: 15px 25px;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
    z-index: 9999;
    display: none;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    border-top: 3px solid var(--primaria);
}}
.cookies-banner p {{ margin: 0; font-size: 0.9rem; }}
.cookies-banner .btn-cookies {{
    background: var(--primaria);
    color: white;
    border: none;
    padding: 8px 25px;
    border-radius: 50px;
    font-weight: 700;
    cursor: pointer;
    transition: background var(--transicao);
}}
.cookies-banner .btn-cookies:hover {{ background: var(--secundaria); }}

/* ===== RESPONSIVO ===== */
@media (max-width: 992px) {{
    .logo {{ font-size: 1.4rem; }}
    .artigo .imagem-destaque {{ height: 280px; }}
}}

@media (max-width: 768px) {{
    .menu-toggle {{ display: block; }}
    
    nav {{
        display: none;
        width: 100%;
        flex-direction: column;
        gap: 3px;
        padding: 12px 0;
        background: var(--card);
        border-top: 2px solid var(--fundo);
        margin-top: 10px;
    }}
    nav.open {{ display: flex; }}
    nav a {{ 
        padding: 10px 20px; 
        width: 100%; 
        text-align: center;
        border-radius: 8px;
    }}
    
    .logo {{ font-size: 1.3rem; }}
    .banner {{ padding: 25px 15px; }}
    .banner h1 {{ font-size: 1.6rem; }}
    .artigo {{ padding: 18px; }}
    .artigo h1 {{ font-size: 1.5rem; }}
    .artigo .imagem-destaque {{ height: 180px; }}
    .grid {{ grid-template-columns: 1fr; }}
    .cookies-banner {{ flex-direction: column; text-align: center; padding: 12px 15px; }}
    footer .footer-grid {{ grid-template-columns: 1fr; text-align: center; }}
}}

@media (max-width: 480px) {{
    .container {{ padding: 0 12px; }}
    .banner h1 {{ font-size: 1.3rem; }}
    .artigo h1 {{ font-size: 1.2rem; }}
    .artigo {{ padding: 14px; }}
    .artigo .imagem-destaque {{ height: 150px; }}
}}
"""
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css)
        print("✅ CSS criado")
    
    # ==================== JS ====================
    
    def criar_js(self):
        js_path = self.assets_js / "script.js"
        if js_path.exists():
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
    
    console.log('✅ Site carregado!');
});
"""
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(js)
        print("✅ JS criado")
    
    # ==================== UTILITÁRIOS ====================
    
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
    
    # ==================== CONTEÚDO COM IA ====================
    
    def gerar_conteudo_ia(self, artigo, link, categoria="geral", palavras_chave=""):
        if not self.ia_api_key:
            return self.conteudo_basico(artigo, link)
        
        prompt_nicho = PROMPTS_NICHO.get(categoria, PROMPTS_NICHO['geral'])
        faq = prompt_nicho.get('faq', PROMPTS_NICHO['geral']['faq'])
        
        faq_html = ""
        for i, pergunta in enumerate(faq[:6]):
            faq_html += f"""
            <div class="faq-item">
                <div class="pergunta">
                    <span>❓ {pergunta}</span>
                    <span>▼</span>
                </div>
                <div class="resposta">
                    <p>Resposta detalhada para: {pergunta}</p>
                </div>
            </div>"""
        
        print(f"   🤖 Gerando conteúdo rico para: {categoria}...")
        
        prompt = f"""
        Crie um review COMPLETO e MUITO DETALHADO sobre {artigo} em português do Brasil.
        
        NICHO: {categoria}
        TOM: {prompt_nicho['tom']}
        PALAVRAS-CHAVE: {prompt_nicho['palavras']}
        {f'Palavras-chave específicas: {palavras_chave}' if palavras_chave else ''}
        
        ESTRUTURA OBRIGATÓRIA:
        
        1. Título em <h1> chamativo
        2. INTRODUÇÃO (4-5 parágrafos)
        3. SOBRE O PRODUTO (2-3 parágrafos)
        4. BENEFÍCIOS em <h2> com <ul> (7-8 itens)
        5. ESPECIFICAÇÕES TÉCNICAS (tabela com 6-8 linhas)
        6. PRÓS E CONTRAS (listas separadas)
        7. ANÁLISE DETALHADA (3-4 parágrafos)
        8. DICAS E RECOMENDAÇÕES
        9. FAQ com {len(faq)} perguntas e respostas
        10. CONCLUSÃO (2-3 parágrafos) com link: {link}
        
        TOM: {prompt_nicho['tom']}
        Retorne APENAS o HTML válido.
        """
        
        try:
            headers = {"Authorization": f"Bearer {self.ia_api_key}", "Content-Type": "application/json"}
            data = {
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"Você é especialista em {categoria} e criação de conteúdo."},
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
                
                if 'faq-item' not in conteudo.lower():
                    conteudo += f"""
                    <h2>{self.t['faq']}</h2>
                    {faq_html}
                    """
                
                return conteudo
            else:
                return self.conteudo_basico(artigo, link)
        except Exception as e:
            print(f"   ⚠️ Erro IA: {e}")
            return self.conteudo_basico(artigo, link)
    
    # ==================== REVISÃO COM IA ====================
    
    def revisar_com_ia(self, conteudo, artigo, categoria="geral"):
        if not self.ia_api_key:
            return conteudo
        
        print(f"   🔍 Revisando e aprofundando conteúdo...")
        
        prompt_nicho = PROMPTS_NICHO.get(categoria, PROMPTS_NICHO['geral'])
        
        prompt = f"""
        Revise e MELHORE SIGNIFICATIVAMENTE este artigo sobre {artigo}.
        
        TOM: {prompt_nicho['tom']}
        
        O QUE MELHORAR:
        1. Aprofunde a introdução
        2. Adicione mais detalhes nos benefícios
        3. Enriqueça a tabela de especificações
        4. Adicione uma seção de "Análise de Mercado"
        5. Melhore o FAQ
        6. Adicione uma conclusão forte
        
        CONTEÚDO ORIGINAL:
        {conteudo}
        
        Retorne APENAS o HTML revisado.
        """
        
        try:
            headers = {"Authorization": f"Bearer {self.ia_api_key}", "Content-Type": "application/json"}
            data = {
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"Revisor especialista em {categoria}."},
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
    
    def conteudo_basico(self, artigo, link):
        t = self.t
        return f"""
<h1>{artigo}</h1>

<p><strong>{artigo}</strong> é a escolha perfeita para sua casa.</p>

<p>Com design sofisticado e acabamento premium, este produto vai transformar completamente seu ambiente.</p>

<h2>Benefícios</h2>
<ul>
    <li><strong>Design sofisticado:</strong> Peça que eleva o estilo do ambiente</li>
    <li><strong>Versatilidade:</strong> Combina com diferentes estilos de decoração</li>
    <li><strong>Qualidade premium:</strong> Durabilidade e acabamento impecável</li>
    <li><strong>Funcionalidade:</strong> Unindo estética e utilidade</li>
</ul>

<h2>Especificações</h2>
<table>
    <tr><th>Característica</th><th>Detalhe</th></tr>
    <tr><td>Material</td><td>Premium com acabamento sofisticado</td></tr>
    <tr><td>Estilo</td><td>Contemporâneo e atemporal</td></tr>
    <tr><td>Garantia</td><td>12 meses</td></tr>
</table>

<div class="cta">
    <h3>{t['comprar']}</h3>
    <p>Garanta o seu {artigo} com preço especial</p>
    <a href="{link}" class="btn" target="_blank" rel="nofollow sponsored">{t['ver_oferta']}</a>
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
        """Retorna lista de artigos publicados com seus dados"""
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
        t = self.t
        categorias = self.get_categorias()
        
        cat_links = ""
        for cat in categorias[:6]:
            ativo_cat = 'ativo' if categoria_atual == cat else ''
            cat_links += f'<a href="/{cat}/" class="{ativo_cat}">{cat.title()}</a>'
        
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
    
    # ==================== FOOTER ====================
    
    def get_footer(self):
        t = self.t
        redes = CONFIG.get('redes_sociais', {})
        social_links = ""
        for nome, url in redes.items():
            emoji = {'instagram': '📸', 'facebook': '📘', 'twitter': '🐦', 'youtube': '▶️'}.get(nome, '🔗')
            social_links += f'<a href="{url}" target="_blank" rel="noopener">{emoji}</a>'
        
        return f"""
<footer>
    <div class="container">
        <div class="footer-grid">
            <div>
                <h4>{CONFIG['icone']} {CONFIG['nome_site']}</h4>
                <p style="opacity:0.6;font-size:0.9rem;">{CONFIG['descricao']}</p>
            </div>
            <div>
                <h4>Links</h4>
                <ul>
                    <li><a href="/">{t['menu_inicio']}</a></li>
                    <li><a href="/sobre.html">{t['menu_sobre']}</a></li>
                    <li><a href="/contato.html">{t['menu_contato']}</a></li>
                    <li><a href="/politica-privacidade.html">{t['privacidade_titulo']}</a></li>
                    <li><a href="/cookies.html">{t['cookies_titulo']}</a></li>
                </ul>
            </div>
        </div>
        <div class="social-links">{social_links}</div>
        <p class="copyright">&copy; {CONFIG['ano']} {CONFIG['nome_site']}. {t['footer']}</p>
    </div>
</footer>
<div class="cookies-banner">
    <p>🍪 Usamos cookies para melhorar sua experiência. <a href="/cookies.html" style="color:var(--primaria);">Saiba mais</a></p>
    <button class="btn-cookies">Aceitar Cookies</button>
</div>"""
    
    def get_meta_tags(self, titulo, descricao, url, imagem="", artigo_data=None):
        t = self.t
        
        if not imagem:
            imagem = f"{CONFIG['url_base']}/assets/img/og-default.jpg"
        
        json_ld = ""
        if artigo_data:
            nome = artigo_data.get('artigo', '')
            data = artigo_data.get('data_publicacao', datetime.now().strftime("%Y-%m-%d"))
            autor = artigo_data.get('autor', CONFIG['autor'])
            
            json_ld = f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{nome}",
  "description": "{descricao[:150]}",
  "image": "{imagem}",
  "datePublished": "{data}",
  "dateModified": "{data}",
  "author": {{
    "@type": "Person",
    "name": "{autor}"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "{CONFIG['nome_site']}",
    "logo": {{
      "@type": "ImageObject",
      "url": "{CONFIG['url_base']}/assets/img/logo.png"
    }}
  }}
}}
</script>"""
        
        return f"""
<title>{titulo}</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{descricao[:160]}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descricao[:160]}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{imagem}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{t['locale']}">
<meta name="twitter:card" content="summary_large_image">
{json_ld}"""
    
    # ==================== PÁGINAS ====================
    
    def criar_pagina(self, nome, titulo, conteudo, ativo="inicio"):
        # Página como .html na raiz (não pasta)
        caminho = self.docs / f"{nome}.html"
        t = self.t
        
        html = f"""<!DOCTYPE html>
<html lang="{t['lang']}">
<head>
    {self.get_meta_tags(f"{CONFIG['nome_site']} - {titulo}", f"{titulo} - {CONFIG['nome']}", f"{CONFIG['url_base']}/{nome}.html")}
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    {self.get_header(ativo)}
    <main class="container">
        <div class="artigo">
            <h1>{titulo}</h1>
            {conteudo}
        </div>
    </main>
    {self.get_footer()}
    <script src="assets/js/script.js"></script>
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
<table>
    <tr><th>Tipo</th><th>Finalidade</th></tr>
    <tr><td>Essenciais</td><td>Necessários para o funcionamento básico do site</td></tr>
    <tr><td>Preferências</td><td>Lembram suas configurações e preferências</td></tr>
    <tr><td>Analíticos</td><td>Nos ajudam a entender como você usa o site</td></tr>
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
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{CONFIG['nome_site']} - {t['nao_encontrado']}</title>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
    <meta name="robots" content="noindex, follow">
</head>
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
    <script src="assets/js/script.js"></script>
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
        # Categoria na raiz: /categoria/
        caminho = self.docs / categoria / "index.html"
        t = self.t
        c = CONFIG
        
        artigos = self.get_artigos_publicados()
        artigos_cat = []
        for a in artigos:
            if a.get('categoria', '').lower() == categoria.lower():
                artigos_cat.append(a)
        
        if not artigos_cat:
            return None
        
        artigos_cat.sort(key=lambda x: x['data_publicacao'], reverse=True)
        
        lista = '<div class="grid">'
        for a in artigos_cat:
            img = self.gerar_imagem(a['nome'], categoria)
            data_formatada = datetime.strptime(a['data_publicacao'], "%Y-%m-%d").strftime("%d/%m/%Y") if a['data_publicacao'] else datetime.now().strftime("%d/%m/%Y")
            lista += f"""
            <div class="card">
                <img src="{img}" alt="{a['nome']}" class="card-img" loading="lazy">
                <div class="card-meta">📅 {data_formatada}</div>
                <h3><a href="/{categoria}/{a['slug']}/">{a['nome']}</a></h3>
                <a href="/{categoria}/{a['slug']}/" class="btn btn-pequeno">{t['menu_inicio']} →</a>
            </div>"""
        lista += '</div>'
        
        html = f"""<!DOCTYPE html>
<html lang="{t['lang']}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{c['nome_site']} - {categoria.title()}</title>
    <meta name="description" content="Artigos sobre {categoria}">
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../../assets/css/style.css">
</head>
<body>
    {self.get_header('categoria', categoria)}
    <main class="container">
        <div class="banner">
            <h1>{categoria.title()}</h1>
            <p>Artigos sobre {categoria}</p>
        </div>
        {lista}
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
        
        # Remove páginas de categoria antigas que não têm mais artigos
        for pasta in self.docs.iterdir():
            if pasta.is_dir() and pasta.name not in ['assets'] and (pasta / "index.html").exists():
                if pasta.name in self.get_categorias():
                    continue
                if pasta.name not in ['sobre', 'contato', 'politica-privacidade', 'cookies', '404']:
                    print(f"   🗑️ Removendo categoria antiga: {pasta.name}")
                    shutil.rmtree(pasta)
        
        for cat in self.get_categorias():
            if self.criar_pagina_categoria(cat):
                print(f"   ✅ /{cat}/")
        
        # Recria index e sitemap após atualizar categorias
        self.criar_index()
        self.criar_sitemap()
        
        print("✅ Páginas de categoria criadas!")
    
    # ==================== ARTIGOS ====================
    
    def criar_artigo(self, artigo_data, forcar=False, revisar=True):
        nome = artigo_data.get('artigo', '').strip()
        if not nome:
            return None
        
        link = artigo_data.get('links_afiliados', 'https://afiliado.com/produto')
        palavras_chave = artigo_data.get('palavras_chave', '')
        descricao = artigo_data.get('descricao', f"Review completo de {nome}")
        categoria = artigo_data.get('categoria', 'geral')
        data_publicacao = artigo_data.get('data_publicacao', datetime.now().strftime("%Y-%m-%d"))
        autor = artigo_data.get('autor', CONFIG['autor'])
        
        slug = self.criar_slug(nome)
        # ARTIGO DENTRO DA CATEGORIA
        pasta = self.docs / categoria / slug
        t = self.t
        
        if not forcar and (pasta / "index.html").exists():
            print(f"   ⏭️ Já existe: {categoria}/{slug}")
            return pasta / "index.html"
        
        print(f"   📝 Criando: {categoria}/{slug}")
        
        imagem = self.gerar_imagem(nome, categoria)
        conteudo = self.gerar_conteudo_ia(nome, link, categoria, palavras_chave)
        
        if revisar and self.ia_api_key:
            conteudo = self.revisar_com_ia(conteudo, nome, categoria)
        
        titulo = f"{nome} - {t['review']}"
        url = f"{CONFIG['url_base']}/{categoria}/{slug}/"
        
        data_formatada = datetime.strptime(data_publicacao, "%Y-%m-%d").strftime("%d/%m/%Y") if data_publicacao else datetime.now().strftime("%d/%m/%Y")
        
        artigos_relacionados = self.get_artigos_relacionados(categoria, slug)
        
        html = f"""<!DOCTYPE html>
<html lang="{t['lang']}">
<head>
    {self.get_meta_tags(titulo, descricao, url, imagem, {'artigo': nome, 'data_publicacao': data_publicacao, 'autor': autor})}
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../../assets/css/style.css">
</head>
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
                <span class="categoria">📂 {categoria.title()}</span>
                <span>⏱️ {random.randint(4, 8)} min de leitura</span>
            </div>
            
            <h1>{titulo}</h1>
            <img src="{imagem}" alt="{nome}" class="imagem-destaque" loading="lazy">
            
            {conteudo}
            
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
                <h3>🎯 {t['ver_oferta']}</h3>
                <p><strong>{nome}</strong></p>
                <a href="{link}" class="btn btn-pequeno" target="_blank" rel="nofollow sponsored">{t['ver_oferta']}</a>
            </div>
            
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
        
        # Recria a página da categoria
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
    
    # ==================== INDEX ====================
    
    def criar_index(self):
        index_path = self.docs / "index.html"
        t = self.t
        c = CONFIG
        
        artigos = self.get_artigos_publicados()
        artigos.sort(key=lambda x: x['data_publicacao'], reverse=True)
        
        if artigos:
            lista = '<div class="grid">'
            for a in artigos[:12]:
                img = self.gerar_imagem(a['nome'], a['categoria'])
                data_formatada = datetime.strptime(a['data_publicacao'], "%Y-%m-%d").strftime("%d/%m/%Y") if a['data_publicacao'] else datetime.now().strftime("%d/%m/%Y")
                lista += f"""
                <div class="card">
                    <img src="{img}" alt="{a['nome']}" class="card-img" loading="lazy">
                    <div class="card-meta">📅 {data_formatada}</div>
                    <h3><a href="/{a['categoria']}/{a['slug']}/">{a['nome']}</a></h3>
                    <a href="/{a['categoria']}/{a['slug']}/" class="btn btn-pequeno">{t['menu_inicio']} →</a>
                </div>"""
            lista += '</div>'
        else:
            lista = '<p style="text-align:center;padding:40px 0;">Nenhum artigo publicado ainda.</p>'
        
        html = f"""<!DOCTYPE html>
<html lang="{t['lang']}">
<head>
    {self.get_meta_tags(f"{c['nome_site']} - {c['nome']}", c['descricao'], f"{c['url_base']}/")}
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    {self.get_header('inicio')}
    <main class="container">
        <div class="banner">
            <h1>{c['nome']}</h1>
            <p>{c['descricao']}</p>
        </div>
        {lista}
    </main>
    {self.get_footer()}
    <script src="assets/js/script.js"></script>
</body>
</html>"""
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print("✅ Index atualizado")
    
    # ==================== PUBLICAR EM LOTES ====================
    
    def publicar_lotes(self):
        """Publica artigos em lotes controlados"""
        print("\n📦 PUBLICAR EM LOTES")
        print("=" * 50)
        
        artigos = self.ler_csv()
        pendentes = [a for a in artigos if a.get('status', 'rascunho').lower() != 'publicado']
        
        if not pendentes:
            print("✅ Nenhum artigo pendente para publicar")
            input("\nPressione Enter...")
            return
        
        print(f"📊 {len(pendentes)} artigos disponíveis para publicar")
        
        print("\n📝 PREVIEW DOS ARTIGOS:")
        for i, a in enumerate(pendentes, 1):
            print(f"   {i}. {a.get('artigo', 'Sem nome')} ({a.get('categoria', 'geral')})")
        
        print("\n🎯 Quantos artigos você quer publicar neste lote?")
        print("   (Digite um número ou 't' para todos)")
        
        opcao = input("\n➡️  ").strip().lower()
        
        if opcao == 't':
            quantidade = len(pendentes)
        else:
            try:
                quantidade = int(opcao)
                if quantidade <= 0:
                    print("❌ Número inválido")
                    input("\nPressione Enter...")
                    return
            except ValueError:
                print("❌ Opção inválida")
                input("\nPressione Enter...")
                return
        
        if quantidade > len(pendentes):
            print(f"⚠️ Você tem apenas {len(pendentes)} artigos disponíveis")
            if not self.ler_sim_nao(f"Publicar todos os {len(pendentes)}? (s/n): "):
                return
            quantidade = len(pendentes)
        
        publicar_agora = pendentes[:quantidade]
        
        print(f"\n📦 Publicando {len(publicar_agora)} artigos...")
        print("-" * 40)
        
        for i, a in enumerate(publicar_agora, 1):
            print(f"\n[{i}/{len(publicar_agora)}] Publicando: {a.get('artigo')}")
            
            data_pub = (datetime.now() + timedelta(days=i-1)).strftime("%Y-%m-%d")
            a['data_publicacao'] = data_pub
            
            self.criar_artigo(a, revisar=True)
            
            if i < len(publicar_agora):
                espera = random.randint(3, 8)
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
                espera = random.randint(5, 15)
                print(f"   ⏳ Aguardando {espera}s...")
                time.sleep(espera)
        
        self.criar_index()
        self.criar_todas_categorias()
        self.criar_sitemap()
        
        print("\n✅ Publicação natural concluída!")
        input("\nPressione Enter...")
    
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
        """Recria tudo do zero: index, páginas, categorias, sitemap"""
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
        """Sincroniza status e recria tudo"""
        print("\n🔄 SINCRONIZANDO AGORA")
        print("=" * 40)
        self.sincronizar_status()
        self.criar_index()
        self.criar_todas_categorias()
        self.criar_sitemap()
        print("✅ Sincronização concluída!")
        input("\nPressione Enter...")
    
    # ==================== MENU PRINCIPAL ====================
    
    def menu(self):
        while True:
            self.mostrar_painel()
            
            print("\n  📝 ARTIGOS")
            print("  [1] Ver todos os artigos")
            print("  [2] Publicar TODOS (com revisão IA)")
            print("  [3] Publicar UM (com preview e revisão)")
            print("  [4] Publicar NATURAL (espaçado)")
            print("  [5] 📦 Publicar em LOTES (escolher quantidade)")
            print("  [6] Revisar/Regenerar um artigo")
            print("  [7] Despublicar (voltar para rascunho)")
            print("  [8] Deletar artigo")
            
            print("\n  📄 PÁGINAS")
            print("  [9] Ver páginas e categorias")
            print("  [10] Recriar páginas e categorias")
            
            print("\n  ⚙️ CONFIG")
            print("  [11] Alterar idioma")
            print("  [12] Alterar cores")
            
            print("\n  🛠️ FERRAMENTAS")
            print("  [13] Gerar Sitemap/Robots")
            print("  [14] Limpar cache (regenerar tudo)")
            print("  [15] 🔄 Recriar TUDO (index + páginas + categorias + sitemap)")
            print("  [16] 🔄 Sincronizar status agora")
            
            print("\n  [0] Sair")
            print("=" * 70)
            
            opcao = input("\n🎯 Escolha: ").strip()
            
            if opcao == "1":
                self.ver_artigos()
            elif opcao == "2":
                self.publicar_todos()
            elif opcao == "3":
                self.publicar_um()
            elif opcao == "4":
                self.publicar_natural()
            elif opcao == "5":
                self.publicar_lotes()
            elif opcao == "6":
                self.revisar_artigo()
            elif opcao == "7":
                self.despublicar_artigo()
            elif opcao == "8":
                self.deletar_artigo()
            elif opcao == "9":
                self.ver_paginas()
            elif opcao == "10":
                self.recriar_paginas()
            elif opcao == "11":
                self.alterar_idioma()
            elif opcao == "12":
                self.alterar_cores()
            elif opcao == "13":
                self.criar_sitemap()
                input("\nPressione Enter...")
            elif opcao == "14":
                self.limpar_cache()
            elif opcao == "15":
                self.recriar_tudo()
            elif opcao == "16":
                self.sincronizar_agora()
            elif opcao == "0":
                print("\n👋 Até logo!")
                break
            else:
                print("❌ Opção inválida")
                input("\nPressione Enter...")
    
    # ==================== MÉTODOS FALTANTES ====================
    
    def ver_artigos(self):
        self.sincronizar_status()
        artigos = self.ler_csv()
        if not artigos:
            print("\n❌ Nenhum artigo cadastrado")
            input("\nPressione Enter...")
            return
        
        print("\n📋 TODOS OS ARTIGOS")
        print("-" * 70)
        print(f"{'#':<4} {'Artigo':<40} {'Status':<12} {'Categoria':<12}")
        print("-" * 70)
        
        for i, a in enumerate(artigos, 1):
            nome = a.get('artigo', 'Sem nome')[:38]
            status = a.get('status', 'rascunho').lower()
            status_icon = "✅" if status == 'publicado' else "⏳"
            status_text = self.t['publicado'] if status == 'publicado' else self.t['rascunho']
            categoria = a.get('categoria', 'geral')[:10]
            print(f"{i:<4} {nome:<40} {status_icon} {status_text:<10} {categoria}")
        
        print("-" * 70)
        input("\nPressione Enter...")
    
    def publicar_todos(self):
        self.sincronizar_status()
        print("\n🚀 PUBLICAR TODOS")
        print("=" * 40)
        
        artigos = self.ler_csv()
        if not artigos:
            print("❌ Nenhum artigo")
            input("\nPressione Enter...")
            return
        
        pendentes = [a for a in artigos if a.get('status', 'rascunho').lower() != 'publicado']
        if not pendentes:
            print("✅ Todos já publicados!")
            input("\nPressione Enter...")
            return
        
        print(f"📊 {len(pendentes)} artigos para publicar")
        
        print("\n📝 PREVIEW DOS ARTIGOS:")
        for i, a in enumerate(pendentes, 1):
            print(f"   {i}. {a.get('artigo', 'Sem nome')} ({a.get('categoria', 'geral')})")
        
        if not self.ler_sim_nao("\nPublicar todos? (s/n): "):
            return
        
        for i, a in enumerate(pendentes, 1):
            print(f"\n[{i}/{len(pendentes)}]")
            self.criar_artigo(a, revisar=True)
        
        self.criar_index()
        self.criar_todas_categorias()
        self.criar_sitemap()
        print("\n✅ Todos publicados!")
        input("\nPressione Enter...")
    
    def publicar_um(self):
        self.sincronizar_status()
        artigos = self.ler_csv()
        if not artigos:
            print("\n❌ Nenhum artigo")
            input("\nPressione Enter...")
            return
        
        print("\n📋 ARTIGOS:")
        print("-" * 50)
        for i, a in enumerate(artigos, 1):
            status = "✅" if a.get('status') == 'publicado' else "⏳"
            print(f"   {i}. {status} {a.get('artigo', 'Sem nome')} ({a.get('categoria', 'geral')})")
        print("-" * 50)
        
        escolha = self.ler_numero("\nNúmero: ", 1, len(artigos))
        if escolha is None:
            return
        
        a = artigos[escolha - 1]
        
        print(f"\n📝 PREVIEW:")
        print(f"   Artigo: {a.get('artigo')}")
        print(f"   Categoria: {a.get('categoria', 'geral')}")
        print(f"   Link: {CONFIG['url_base']}/{a.get('categoria')}/{self.criar_slug(a.get('artigo'))}/")
        
        if a.get('status') == 'publicado' and not self.ler_sim_nao("\nJá publicado. Regenerar? (s/n): "):
            return
        
        if not self.ler_sim_nao("\nPublicar? (s/n): "):
            return
        
        self.criar_artigo(a, forcar=True, revisar=True)
        self.criar_index()
        self.criar_todas_categorias()
        self.criar_sitemap()
        print("✅ Publicado!")
        input("\nPressione Enter...")
    
    def despublicar_artigo(self):
        publicados = self.get_artigos_publicados()
        
        if not publicados:
            print("\n❌ Nenhum artigo publicado")
            input("\nPressione Enter...")
            return
        
        print("\n📋 PUBLICADOS:")
        for i, p in enumerate(publicados, 1):
            print(f"   {i}. {p['nome']} ({p['categoria']})")
        
        escolha = self.ler_numero("\nNúmero: ", 1, len(publicados))
        if escolha is None:
            return
        
        slug = publicados[escolha - 1]['slug']
        nome = publicados[escolha - 1]['nome']
        categoria = publicados[escolha - 1]['categoria']
        
        if not self.ler_sim_nao(f"Despublicar '{nome}'? (s/n): "):
            return
        
        pasta = self.docs / categoria / slug
        if pasta.exists():
            shutil.rmtree(pasta)
            print(f"   🗑️ HTML removido: {categoria}/{slug}")
        
        artigos = self.ler_csv()
        for a in artigos:
            if self.criar_slug(a.get('artigo', '')) == slug:
                a['status'] = 'rascunho'
                break
        self.salvar_csv(artigos)
        
        self.criar_index()
        self.criar_todas_categorias()
        self.criar_sitemap()
        
        print(f"✅ '{nome}' voltou para rascunho!")
        input("\nPressione Enter...")
    
    def revisar_artigo(self):
        publicados = self.get_artigos_publicados()
        
        if not publicados:
            print("\n❌ Nenhum artigo publicado")
            input("\nPressione Enter...")
            return
        
        print("\n📋 PUBLICADOS:")
        for i, p in enumerate(publicados, 1):
            print(f"   {i}. {p['nome']} ({p['categoria']})")
        
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
            print(f"   {i}. {p['nome']} ({p['categoria']})")
        
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
    
    def ver_paginas(self):
        print("\n📄 PÁGINAS")
        print("-" * 50)
        paginas = ['index.html', 'sobre.html', 'contato.html', 'politica-privacidade.html', 'cookies.html', '404.html', 'sitemap.xml', 'robots.txt']
        for arquivo in paginas:
            existe = "✅" if (self.docs / arquivo).exists() else "❌"
            print(f"   {existe} {arquivo}")
        
        print("\n📂 CATEGORIAS:")
        for cat in self.get_categorias():
            existe = "✅" if (self.docs / cat / "index.html").exists() else "❌"
            print(f"   {existe} /{cat}/")
        
        print("\n📰 ARTIGOS PUBLICADOS:")
        for a in self.get_artigos_publicados():
            existe = "✅" if (self.docs / a['categoria'] / a['slug'] / "index.html").exists() else "❌"
            print(f"   {existe} /{a['categoria']}/{a['slug']}/ - {a['nome']}")
        
        input("\nPressione Enter...")
    
    def recriar_paginas(self):
        print("\n🔄 RECRIANDO PÁGINAS E CATEGORIAS")
        print("=" * 40)
        self.criar_todas_paginas()
        self.criar_todas_categorias()
        print("✅ Páginas recriadas!")
        input("\nPressione Enter...")
    
    def alterar_idioma(self):
        print("\n🌐 IDIOMA")
        print(f"Atual: {self.idioma.upper()}")
        print("[1] pt | [2] en | [3] es")
        opcao = input("Escolha: ").strip()
        idiomas = {'1': 'pt', '2': 'en', '3': 'es'}
        if opcao in idiomas:
            self.idioma = idiomas[opcao]
            self.t = IDIOMAS[self.idioma]
            CONFIG['idioma'] = self.idioma
            print(f"✅ Idioma alterado para {self.idioma.upper()}")
            self.criar_index()
            self.criar_todas_paginas()
            self.criar_todas_categorias()
            self.criar_sitemap()
        input("\nPressione Enter...")
    
    def alterar_cores(self):
        print("\n🎨 CORES")
        for cor, valor in CONFIG['cores'].items():
            novo = input(f"{cor} ({valor}): ").strip()
            if novo:
                CONFIG['cores'][cor] = novo
        self.criar_css()
        print("✅ Cores atualizadas!")
        input("\nPressione Enter...")
    
    def limpar_cache(self):
        print("\n🔄 LIMPAR CACHE (REGENERAR TUDO)")
        print("=" * 40)
        print("⚠️ Isso vai apagar e recriar TODOS os artigos publicados.")
        
        if not self.ler_sim_nao("\nConfirmar? (s/n): "):
            return
        
        print("\n📁 Removendo artigos antigos...")
        
        publicados = self.get_artigos_publicados()
        
        if not publicados:
            print("⚠️ Nenhum artigo publicado para regenerar.")
            print("💡 Publique alguns artigos primeiro (opção 2 ou 3)")
            input("\nPressione Enter...")
            return
        
        print(f"📊 {len(publicados)} artigos serão regenerados")
        
        for a in publicados:
            pasta = self.docs / a['categoria'] / a['slug']
            if pasta.exists():
                shutil.rmtree(pasta)
                print(f"   🗑️ Removido: {a['categoria']}/{a['slug']}")
        
        # Remove pastas de categoria
        for cat in self.get_categorias():
            pasta = self.docs / cat
            if pasta.exists():
                shutil.rmtree(pasta)
                print(f"   🗑️ Removido categoria: {cat}")
        
        print("\n📝 Regenerando artigos...")
        
        artigos_csv = self.ler_csv()
        publicados_artigos = [a for a in artigos_csv if a.get('status') == 'publicado']
        
        for i, a in enumerate(publicados_artigos, 1):
            print(f"\n[{i}/{len(publicados_artigos)}] Regenerando: {a.get('artigo')}")
            self.criar_artigo(a, forcar=True, revisar=True)
            
            if i < len(publicados_artigos):
                time.sleep(2)
        
        print("\n📄 Recriando páginas...")
        self.criar_index()
        self.criar_todas_paginas()
        self.criar_todas_categorias()
        self.criar_sitemap()
        
        print("\n✅ Cache limpo e tudo regenerado!")
        input("\nPressione Enter...")

# ============================================================
# ===== EXECUÇÃO ==============================================
# ============================================================

if __name__ == "__main__":
    gerador = Gerador()
    gerador.menu()