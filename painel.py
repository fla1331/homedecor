#!/usr/bin/env python3
"""
PAINEL ADMINISTRATIVO WEB - HOMEDECOR
Interface para gerenciar o site
"""

from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import json
import csv
import os
import shutil
from pathlib import Path
from datetime import datetime

# Importa o gerador
from gerador import Gerador

app = Flask(__name__)
app.secret_key = 'admin-homedecor-2025'

# ============================================================
# ===== FUNÇÕES AUXILIARES ===================================
# ============================================================

def get_gerador():
    return Gerador()

def ler_csv():
    g = get_gerador()
    return g.ler_csv()

def salvar_csv(artigos):
    g = get_gerador()
    csv_path = g.base / g.config.get('csv', 'artigos.csv')
    if not artigos:
        return
    cabecalho = list(artigos[0].keys())
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=cabecalho)
        writer.writeheader()
        writer.writerows(artigos)

def get_config():
    g = get_gerador()
    return g.config

def salvar_config(config):
    g = get_gerador()
    g.config = config
    config_path = g.base / "config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def get_stats():
    artigos = ler_csv()
    total = len(artigos)
    publicados = sum(1 for a in artigos if a.get('status') == 'publicado')
    rascunhos = total - publicados
    categorias = set()
    for a in artigos:
        cat = a.get('categoria', 'geral')
        if cat:
            categorias.add(cat)
    
    return {
        'total': total,
        'publicados': publicados,
        'rascunhos': rascunhos,
        'categorias': len(categorias)
    }

# ============================================================
# ===== ROTAS ================================================
# ============================================================

@app.route('/')
def dashboard():
    stats = get_stats()
    artigos = ler_csv()
    
    html = '''
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Admin - HomeDecor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #1a1a2e; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        header { background: white; padding: 20px 0; border-bottom: 3px solid #c4956a; margin-bottom: 30px; }
        header h1 { font-size: 1.6rem; display: flex; align-items: center; gap: 12px; }
        header .sub { color: #666; font-size: 0.9rem; font-weight: 400; }
        
        .grid-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card-stat { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .card-stat .numero { font-size: 2.2rem; font-weight: 800; color: #c4956a; }
        .card-stat .label { color: #888; font-size: 0.85rem; margin-top: 4px; }
        .card-stat.verde .numero { color: #27ae60; }
        .card-stat.amarelo .numero { color: #f39c12; }
        .card-stat.roxo .numero { color: #9b59b6; }
        
        .menu { display: flex; gap: 12px; flex-wrap: wrap; margin: 25px 0; }
        .menu a { 
            background: white; padding: 14px 28px; border-radius: 10px; 
            text-decoration: none; color: #1a1a2e; font-weight: 600; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.05); transition: 0.3s;
            display: flex; align-items: center; gap: 8px;
        }
        .menu a:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .menu a.primary { background: #c4956a; color: white; }
        .menu a.success { background: #27ae60; color: white; }
        .menu a.danger { background: #e74c3c; color: white; }
        
        .tabela { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .tabela table { width: 100%; border-collapse: collapse; }
        .tabela th { background: #f8f9fa; text-align: left; padding: 12px 20px; font-weight: 600; color: #666; }
        .tabela td { padding: 12px 20px; border-top: 1px solid #f1f2f6; }
        .badge { display: inline-block; padding: 3px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
        .badge.publicado { background: #d4edda; color: #155724; }
        .badge.rascunho { background: #fff3cd; color: #856404; }
        .btn { display: inline-block; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 0.8rem; border: none; cursor: pointer; }
        .btn-primary { background: #c4956a; color: white; }
        .btn-success { background: #27ae60; color: white; }
        .btn-danger { background: #e74c3c; color: white; }
        .acoes { display: flex; gap: 5px; flex-wrap: wrap; }
        .footer-actions { margin-top: 20px; display: flex; gap: 10px; flex-wrap: wrap; }
        
        @media (max-width: 768px) { .tabela { overflow-x: auto; } .menu a { width: 100%; justify-content: center; } }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>🏠 Painel Admin - HomeDecor</h1>
        </div>
    </header>
    
    <div class="container">
        <div class="grid-cards">
            <div class="card-stat"><div class="numero">{{ stats.total }}</div><div class="label">📝 Total de Artigos</div></div>
            <div class="card-stat verde"><div class="numero">{{ stats.publicados }}</div><div class="label">✅ Publicados</div></div>
            <div class="card-stat amarelo"><div class="numero">{{ stats.rascunhos }}</div><div class="label">⏳ Rascunhos</div></div>
            <div class="card-stat roxo"><div class="numero">{{ stats.categorias }}</div><div class="label">🏷️ Categorias</div></div>
        </div>
        
        <div class="menu">
            <a href="/artigos">📋 Gerenciar Artigos</a>
            <a href="/novo" class="success">➕ Novo Artigo</a>
            <a href="/config" class="primary">⚙️ Configurações</a>
            <a href="/gerar" class="primary">🚀 Gerar Site</a>
            <a href="/limpar" class="danger">🔄 Limpar Cache</a>
        </div>
        
        <div class="tabela">
            <table>
                <thead><tr>
                    <th>#</th><th>Artigo</th><th>Categoria</th><th>Status</th><th>Data</th><th>Ações</th>
                </tr></thead>
                <tbody>
                    {% for a in artigos[:10] %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td>{{ a.artigo }}</td>
                        <td>{{ a.categoria or 'geral' }}</td>
                        <td><span class="badge {{ a.status or 'rascunho' }}">{{ a.status or 'rascunho' }}</span></td>
                        <td>{{ a.data_publicacao or '-' }}</td>
                        <td class="acoes">
                            <a href="/editar/{{ loop.index0 }}" class="btn btn-primary">✏️</a>
                            <a href="/publicar/{{ loop.index0 }}" class="btn btn-success">✅</a>
                            <a href="/deletar/{{ loop.index0 }}" class="btn btn-danger" onclick="return confirm('Deletar?')">🗑️</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <p style="margin-top:10px;color:#888;font-size:0.9rem;">Mostrando os 10 primeiros</p>
    </div>
</body>
</html>
'''
    return render_template_string(html, stats=stats, artigos=artigos)


@app.route('/artigos')
def listar_artigos():
    artigos = ler_csv()
    
    html = '''
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Artigos - Painel Admin</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #1a1a2e; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { background: white; padding: 20px 0; border-bottom: 3px solid #c4956a; margin-bottom: 30px; }
        header h1 { font-size: 1.6rem; }
        .voltar { color: #c4956a; text-decoration: none; font-weight: 600; }
        .tabela { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .tabela table { width: 100%; border-collapse: collapse; }
        .tabela th { background: #f8f9fa; text-align: left; padding: 12px 20px; font-weight: 600; color: #666; }
        .tabela td { padding: 12px 20px; border-top: 1px solid #f1f2f6; }
        .badge { display: inline-block; padding: 3px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
        .badge.publicado { background: #d4edda; color: #155724; }
        .badge.rascunho { background: #fff3cd; color: #856404; }
        .btn { display: inline-block; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 0.8rem; border: none; cursor: pointer; }
        .btn-primary { background: #c4956a; color: white; }
        .btn-success { background: #27ae60; color: white; }
        .btn-danger { background: #e74c3c; color: white; }
        .acoes { display: flex; gap: 5px; flex-wrap: wrap; }
        .adicionar { background: #27ae60; color: white; padding: 10px 25px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block; margin-bottom: 20px; }
        .adicionar:hover { background: #219a52; }
        @media (max-width: 768px) { .tabela { overflow-x: auto; } }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>📋 Gerenciar Artigos</h1>
            <a href="/" class="voltar">← Voltar</a>
        </div>
    </header>
    
    <div class="container">
        <a href="/novo" class="adicionar">+ Novo Artigo</a>
        
        <div class="tabela">
            <table>
                <thead><tr>
                    <th>#</th><th>Artigo</th><th>Categoria</th><th>Status</th><th>Data</th><th>Ações</th>
                </tr></thead>
                <tbody>
                    {% for a in artigos %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td>{{ a.artigo }}</td>
                        <td>{{ a.categoria or 'geral' }}</td>
                        <td><span class="badge {{ a.status or 'rascunho' }}">{{ a.status or 'rascunho' }}</span></td>
                        <td>{{ a.data_publicacao or '-' }}</td>
                        <td class="acoes">
                            <a href="/editar/{{ loop.index0 }}" class="btn btn-primary">✏️</a>
                            <a href="/publicar/{{ loop.index0 }}" class="btn btn-success">✅</a>
                            <a href="/deletar/{{ loop.index0 }}" class="btn btn-danger" onclick="return confirm('Deletar?')">🗑️</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <p style="margin-top:10px;color:#888;font-size:0.9rem;">Total: {{ artigos|length }} artigos</p>
    </div>
</body>
</html>
'''
    return render_template_string(html, artigos=artigos)


@app.route('/novo', methods=['GET', 'POST'])
def novo_artigo():
    if request.method == 'POST':
        artigo = {
            'artigo': request.form.get('artigo'),
            'links_afiliados': request.form.get('links_afiliados'),
            'status': 'rascunho',
            'categoria': request.form.get('categoria', 'geral'),
            'palavras_chave': request.form.get('palavras_chave', ''),
            'descricao': request.form.get('descricao', ''),
            'data_publicacao': '',
            'autor': request.form.get('autor', 'Equipe')
        }
        
        artigos = ler_csv()
        artigos.append(artigo)
        salvar_csv(artigos)
        return redirect('/artigos')
    
    html = '''
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Novo Artigo - Painel Admin</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #1a1a2e; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        header { background: white; padding: 20px 0; border-bottom: 3px solid #c4956a; margin-bottom: 30px; }
        header h1 { font-size: 1.6rem; }
        .voltar { color: #c4956a; text-decoration: none; font-weight: 600; }
        .form { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .form label { display: block; font-weight: 600; margin-top: 15px; margin-bottom: 5px; }
        .form input, .form select, .form textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 1rem; }
        .form textarea { height: 80px; }
        .botoes { display: flex; gap: 10px; margin-top: 25px; }
        .btn { padding: 12px 30px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 1rem; }
        .btn-primary { background: #c4956a; color: white; }
        .btn-secondary { background: #b2bec3; color: white; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>✏️ Novo Artigo</h1>
            <a href="/artigos" class="voltar">← Voltar</a>
        </div>
    </header>
    
    <div class="container">
        <div class="form">
            <form method="POST">
                <label>Nome do Artigo *</label>
                <input type="text" name="artigo" required placeholder="Ex: Produto Exemplo">
                
                <label>Link Afiliado *</label>
                <input type="url" name="links_afiliados" required placeholder="https://afiliado.com/produto">
                
                <label>Categoria</label>
                <input type="text" name="categoria" placeholder="Ex: decoração">
                
                <label>Autor</label>
                <input type="text" name="autor" placeholder="Equipe Top Ofertas">
                
                <label>Palavras-chave</label>
                <input type="text" name="palavras_chave" placeholder="produto, review, qualidade">
                
                <label>Descrição (SEO)</label>
                <textarea name="descricao" placeholder="Breve descrição do artigo"></textarea>
                
                <div class="botoes">
                    <button type="submit" class="btn btn-primary">Salvar como Rascunho</button>
                    <a href="/artigos" class="btn btn-secondary">Cancelar</a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
'''
    return render_template_string(html)


@app.route('/editar/<int:idx>', methods=['GET', 'POST'])
def editar_artigo(idx):
    artigos = ler_csv()
    if idx >= len(artigos):
        return redirect('/artigos')
    
    artigo = artigos[idx]
    
    if request.method == 'POST':
        artigo['artigo'] = request.form.get('artigo')
        artigo['links_afiliados'] = request.form.get('links_afiliados')
        artigo['categoria'] = request.form.get('categoria', 'geral')
        artigo['palavras_chave'] = request.form.get('palavras_chave', '')
        artigo['descricao'] = request.form.get('descricao', '')
        artigo['autor'] = request.form.get('autor', 'Equipe')
        salvar_csv(artigos)
        return redirect('/artigos')
    
    html = '''
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editar Artigo - Painel Admin</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #1a1a2e; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        header { background: white; padding: 20px 0; border-bottom: 3px solid #c4956a; margin-bottom: 30px; }
        header h1 { font-size: 1.6rem; }
        .voltar { color: #c4956a; text-decoration: none; font-weight: 600; }
        .form { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .form label { display: block; font-weight: 600; margin-top: 15px; margin-bottom: 5px; }
        .form input, .form textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 1rem; }
        .form textarea { height: 80px; }
        .botoes { display: flex; gap: 10px; margin-top: 25px; }
        .btn { padding: 12px 30px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 1rem; }
        .btn-primary { background: #c4956a; color: white; }
        .btn-secondary { background: #b2bec3; color: white; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>✏️ Editar Artigo</h1>
            <a href="/artigos" class="voltar">← Voltar</a>
        </div>
    </header>
    
    <div class="container">
        <div class="form">
            <form method="POST">
                <label>Nome do Artigo</label>
                <input type="text" name="artigo" value="{{ artigo.artigo }}" required>
                
                <label>Link Afiliado</label>
                <input type="url" name="links_afiliados" value="{{ artigo.links_afiliados }}" required>
                
                <label>Categoria</label>
                <input type="text" name="categoria" value="{{ artigo.categoria or '' }}">
                
                <label>Autor</label>
                <input type="text" name="autor" value="{{ artigo.autor or 'Equipe' }}">
                
                <label>Palavras-chave</label>
                <input type="text" name="palavras_chave" value="{{ artigo.palavras_chave or '' }}">
                
                <label>Descrição (SEO)</label>
                <textarea name="descricao">{{ artigo.descricao or '' }}</textarea>
                
                <div class="botoes">
                    <button type="submit" class="btn btn-primary">Salvar</button>
                    <a href="/artigos" class="btn btn-secondary">Cancelar</a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
'''
    return render_template_string(html, artigo=artigo)


@app.route('/publicar/<int:idx>')
def publicar_artigo(idx):
    artigos = ler_csv()
    if idx < len(artigos):
        artigos[idx]['status'] = 'publicado'
        if not artigos[idx].get('data_publicacao'):
            artigos[idx]['data_publicacao'] = datetime.now().strftime("%Y-%m-%d")
        salvar_csv(artigos)
        
        g = Gerador()
        g.criar_artigo(artigos[idx])
        g.criar_index()
        g.criar_sitemap()
    
    return redirect('/artigos')


@app.route('/deletar/<int:idx>')
def deletar_artigo(idx):
    artigos = ler_csv()
    if idx < len(artigos):
        # Remove o HTML se existir
        g = Gerador()
        slug = g.criar_slug(artigos[idx].get('artigo', ''))
        pasta = g.docs / slug
        if pasta.exists():
            shutil.rmtree(pasta)
        
        del artigos[idx]
        salvar_csv(artigos)
        g.criar_index()
    
    return redirect('/artigos')


@app.route('/config', methods=['GET', 'POST'])
def config():
    config = get_config()
    
    if request.method == 'POST':
        config['nome'] = request.form.get('nome')
        config['slug'] = request.form.get('slug')
        config['icone'] = request.form.get('icone')
        config['nome_site'] = request.form.get('nome_site')
        config['descricao'] = request.form.get('descricao')
        config['url_base'] = request.form.get('url_base')
        config['autor'] = request.form.get('autor')
        config['tema'] = request.form.get('tema', 'moderno')
        config['publicar_por_dia'] = int(request.form.get('publicar_por_dia', 3))
        
        cores = {}
        for cor in ['primaria', 'secundaria', 'fundo', 'texto', 'card', 'destaque']:
            cores[cor] = request.form.get(f'cor_{cor}', '#ffffff')
        config['cores'] = cores
        
        salvar_config(config)
        
        # Recriar CSS
        g = Gerador()
        g.criar_css()
        
        return redirect('/config')
    
    html = '''
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configurações - Painel Admin</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #1a1a2e; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        header { background: white; padding: 20px 0; border-bottom: 3px solid #c4956a; margin-bottom: 30px; }
        header h1 { font-size: 1.6rem; }
        .voltar { color: #c4956a; text-decoration: none; font-weight: 600; }
        .form { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .form label { display: block; font-weight: 600; margin-top: 15px; margin-bottom: 5px; }
        .form input, .form select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 1rem; }
        .form .row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .form .color-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
        .form .color-grid input[type="color"] { width: 100%; height: 50px; padding: 0; border: 2px solid #ddd; border-radius: 8px; cursor: pointer; }
        .botoes { display: flex; gap: 10px; margin-top: 25px; }
        .btn { padding: 12px 30px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 1rem; }
        .btn-primary { background: #c4956a; color: white; }
        .btn-secondary { background: #b2bec3; color: white; }
        @media (max-width: 768px) { .form .row { grid-template-columns: 1fr; } .form .color-grid { grid-template-columns: 1fr 1fr; } }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>⚙️ Configurações</h1>
            <a href="/" class="voltar">← Voltar</a>
        </div>
    </header>
    
    <div class="container">
        <div class="form">
            <form method="POST">
                <h3>Informações do Site</h3>
                
                <label>Nome do Site</label>
                <input type="text" name="nome_site" value="{{ config.nome_site }}">
                
                <label>Slug (URL)</label>
                <input type="text" name="slug" value="{{ config.slug }}" placeholder="ex: casa">
                
                <label>Ícone (emoji)</label>
                <input type="text" name="icone" value="{{ config.icone }}" placeholder="🏠">
                
                <label>Nome do Nicho</label>
                <input type="text" name="nome" value="{{ config.nome }}">
                
                <label>Descrição</label>
                <input type="text" name="descricao" value="{{ config.descricao }}">
                
                <label>URL Base</label>
                <input type="url" name="url_base" value="{{ config.url_base }}">
                
                <label>Autor</label>
                <input type="text" name="autor" value="{{ config.autor }}">
                
                <label>Tema Visual</label>
                <select name="tema">
                    <option value="moderno" {% if config.tema == 'moderno' %}selected{% endif %}>Moderno</option>
                    <option value="classico" {% if config.tema == 'classico' %}selected{% endif %}>Clássico</option>
                    <option value="minimalista" {% if config.tema == 'minimalista' %}selected{% endif %}>Minimalista</option>
                </select>
                
                <label>Publicar por dia</label>
                <input type="number" name="publicar_por_dia" value="{{ config.publicar_por_dia or 3 }}" min="1" max="10">
                
                <h3 style="margin-top:30px;">Cores</h3>
                <div class="color-grid">
                    <div>
                        <label>Primária</label>
                        <input type="color" name="cor_primaria" value="{{ config.cores.primaria }}">
                    </div>
                    <div>
                        <label>Secundária</label>
                        <input type="color" name="cor_secundaria" value="{{ config.cores.secundaria }}">
                    </div>
                    <div>
                        <label>Fundo</label>
                        <input type="color" name="cor_fundo" value="{{ config.cores.fundo }}">
                    </div>
                    <div>
                        <label>Texto</label>
                        <input type="color" name="cor_texto" value="{{ config.cores.texto }}">
                    </div>
                    <div>
                        <label>Card</label>
                        <input type="color" name="cor_card" value="{{ config.cores.card }}">
                    </div>
                    <div>
                        <label>Destaque</label>
                        <input type="color" name="cor_destaque" value="{{ config.cores.destaque }}">
                    </div>
                </div>
                
                <div class="botoes">
                    <button type="submit" class="btn btn-primary">Salvar Configurações</button>
                    <a href="/" class="btn btn-secondary">Cancelar</a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
'''
    return render_template_string(html, config=config)


@app.route('/gerar')
def gerar_site():
    g = Gerador()
    g.gerar_tudo()
    
    html = '''
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Site Gerado - HomeDecor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; text-align: center; padding: 60px 20px; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        h1 { font-size: 2.5rem; margin-bottom: 20px; color: #c4956a; }
        .btn { display: inline-block; padding: 12px 30px; background: #c4956a; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; margin-top: 20px; }
        .btn:hover { background: #b8845a; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Site Gerado!</h1>
        <p>Todos os arquivos foram gerados com sucesso na pasta <strong>docs/</strong></p>
        <a href="/" class="btn">Voltar ao Painel</a>
    </div>
</body>
</html>
'''
    return render_template_string(html)


@app.route('/limpar')
def limpar_cache():
    g = Gerador()
    # Limpa docs
    docs_path = g.docs
    if docs_path.exists():
        for item in docs_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    
    g.gerar_tudo()
    
    html = '''
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cache Limpo - HomeDecor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; text-align: center; padding: 60px 20px; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        h1 { font-size: 2.5rem; margin-bottom: 20px; color: #27ae60; }
        .btn { display: inline-block; padding: 12px 30px; background: #c4956a; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 Cache Limpo!</h1>
        <p>Todos os arquivos foram regenerados com sucesso.</p>
        <a href="/" class="btn">Voltar ao Painel</a>
    </div>
</body>
</html>
'''
    return render_template_string(html)


# ============================================================
# ===== INICIAR ==============================================
# ============================================================

if __name__ == '__main__':
    print("\n🏠 PAINEL ADMIN - HomeDecor")
    print("=" * 40)
    print("📍 http://localhost:5000")
    print("=" * 40)
    app.run(debug=True, host='0.0.0.0', port=5000)