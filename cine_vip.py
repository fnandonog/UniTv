from google import genai
import requests
import os
import re
import time
import subprocess
import unicodedata
from datetime import datetime
from google.genai import types

# ==========================================
# 1. CONFIGURAÇÕES
# ==========================================
GEMINI_KEY = "AIzaSyCmT5HHUpHsXbtN68h6bpkRIzFpjIy2RGs"
TMDB_KEY = "9cb2f018163da4a3f89d718ee6be8677" # Coloque sua chave aqui se mudar
MODEL_ID = 'gemini-2.0-flash' 

QTD_FILMES_POR_VEZ = 3
PASTA_CINEMA = "cinema"
HISTORICO_CINE = "historico_cinema.txt"

client = genai.Client(api_key=GEMINI_KEY)
CONFIG_GERAL = types.GenerateContentConfig(
    safety_settings=[types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE)]
)

# ==========================================
# 2. TEMPLATE COM IMAGEM GERADA (ESTILO CABRA BOM DE BOLA)
# ==========================================
TEMPLATE_RESENHA = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>[TITULO] | Resenha VIP UniTV</title>
    <meta name="description" content="Análise do filme [TITULO]. Assista em 4K na UniTV.">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="icon" href="../../img/logo-unitv.png" type="image/png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        body { background: #050505; color: #f0f0f0; }
        header { display: flex; justify-content: space-between; align-items: center; padding: 15px 5%; background: rgba(5,5,5,0.9); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #111; }
        .logo img { height: 35px; }
        .movie-hero { width: 100%; height: 60vh; position: relative; overflow: hidden; }
        .hero-img { width: 100%; height: 100%; object-fit: cover; filter: brightness(0.5); }
        .hero-overlay { position: absolute; bottom: 0; left: 0; width: 100%; padding: 50px 5%; background: linear-gradient(to top, #050505, transparent); }
        .content { max-width: 1200px; margin: 40px auto; padding: 0 20px; display: grid; grid-template-columns: 1fr 300px; gap: 40px; }
        .main-text h2 { color: #ff0080; margin: 30px 0 15px; border-left: 4px solid #ff0080; padding-left: 15px; }
        .main-text p { font-size: 1.1rem; color: #bbb; line-height: 1.8; margin-bottom: 20px; }
        .sidebar { background: #0a0a0a; padding: 25px; border-radius: 15px; height: fit-content; border: 1px solid #1a1a1a; }
        .sidebar h3 { font-size: 1.2rem; margin-bottom: 15px; color: #fff; }
        .ficha-item { margin-bottom: 15px; font-size: 0.9rem; }
        .ficha-item span { color: #666; display: block; text-transform: uppercase; font-weight: 700; }
        .btn-cta { display: block; background: linear-gradient(135deg, #FF512F 0%, #DD2476 100%); color: #fff; text-align: center; padding: 15px; border-radius: 10px; text-decoration: none; font-weight: 800; margin-top: 20px; }
        footer { background: #000; padding: 60px 5%; text-align: center; border-top: 1px solid #111; color: #444; font-size: 0.8rem; }
    </style>
</head>
<body>
    <header>
        <div class="logo"><a href="../../index.html"><img src="../../img/logo-unitv.png"></a></div>
        <a href="../../index.html#comprar" style="color:#fff; text-decoration:none; font-weight:700;">ASSINAR VIP</a>
    </header>

    <div class="movie-hero">
        <img src="[URL_IA_BACKDROP]" class="hero-img">
        <div class="hero-overlay">
            <h1 style="font-size: clamp(2rem, 5vw, 4rem); font-weight: 900;">[TITULO]</h1>
            <p style="color: #00ff88; font-weight: 700;">⭐ [NOTA] | [ANO] | 4K ULTRA HD</p>
        </div>
    </div>

    <div class="content">
        <main class="main-text">
            [RESENHA_HTML]
            <img src="[URL_IA_EXTRA]" style="width:100%; border-radius:15px; margin:30px 0;">
        </main>
        <aside class="sidebar">
            <h3>Ficha Técnica</h3>
            <div class="ficha-item"><span>Direção</span><strong>[DIRETOR]</strong></div>
            <div class="ficha-item"><span>Gênero</span><strong>[GENEROS]</strong></div>
            <div class="ficha-item"><span>Duração</span><strong>[DURACAO]</strong></div>
            <a href="../../index.html#comprar" class="btn-cta">ASSISTIR NA UNITV</a>
        </aside>
    </div>

    <footer>&copy; 2026 UniTV Oficial - Revenda Autorizada</footer>
</body>
</html>"""

# ==========================================
# 3. LÓGICA DE EXECUÇÃO
# ==========================================

def criar_slug(texto):
    txt = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r'[^a-z0-9]+', '-', txt.lower()).strip('-')

def buscar_filmes():
    res = requests.get(f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_KEY}&language=pt-BR")
    return res.json().get('results', []) if res.status_code == 200 else []

def buscar_detalhes(m_id):
    res = requests.get(f"https://api.themoviedb.org/3/movie/{m_id}?api_key={TMDB_KEY}&language=pt-BR&append_to_response=credits")
    return res.json() if res.status_code == 200 else None

def gerar_resenha(dados):
    titulo = dados.get('title')
    prompt = f"Escreva uma resenha de cinema profissional e empolgante para o site UniTV sobre o filme {titulo}. Use apenas tags <p>, <h2> e <blockquote>. Fale sobre a trama e por que assistir em 4K."
    res = client.models.generate_content(model=MODEL_ID, contents=prompt, config=CONFIG_GERAL)
    return res.text.replace("```html", "").replace("```", "").strip()

def injetar_card(filme, slug, img_ia):
    caminho = os.path.join(PASTA_CINEMA, "index.html")
    alvo = '<main class="movie-catalog" id="movieCatalog">'
    card = f'''
        <a href="{slug}/index.html" class="movie-card reveal active">
            <img src="{img_ia}" alt="{filme['title']}" class="movie-poster">
            <div class="movie-rating-badge"><i class="fa-solid fa-star"></i> {round(filme['vote_average'],1)}</div>
            <div class="movie-overlay">
                <h3 class="movie-info-title">{filme['title']}</h3>
                <div class="movie-info-meta"><span>{filme['release_date'][:4]}</span></div>
                <div class="btn-read-review">LER RESENHA VIP</div>
            </div>
        </a>'''
    with open(caminho, "r", encoding="utf-8") as f: html = f.read()
    if alvo in html:
        with open(caminho, "w", encoding="utf-8") as f: f.write(html.replace(alvo, alvo + "\n" + card))

# --- EXECUÇÃO ---
filmes = buscar_filmes()
historico = open(HISTORICO_CINE, 'r').read() if os.path.exists(HISTORICO_CINE) else ""
processados = 0

for f in filmes:
    if processados >= QTD_FILMES_POR_VEZ: break
    slug = criar_slug(f['title'])
    if slug in historico: continue

    det = buscar_detalhes(f['id'])
    if not det: continue

    # URLS DE IMAGEM VIA IA (ESTILO QUE FUNCIONA)
    tema_url = f['title'].replace(" ", "%20")
    img_ia_poster = f"https://image.pollinations.ai/prompt/movie%20poster%20of%20{tema_url}%20cinematic%204k?width=500&height=750&nologo=true"
    img_ia_hero = f"https://image.pollinations.ai/prompt/cinematic%20scene%20from%20movie%20{tema_url}%20ultra%20detailed%204k?width=1280&height=720&nologo=true"

    pasta = os.path.join(PASTA_CINEMA, slug)
    os.makedirs(pasta, exist_ok=True)

    res_html = gerar_resenha(det)
    
    # Preenche o Template
    final = TEMPLATE_RESENHA.replace("[TITULO]", f['title']).replace("[NOTA]", str(round(f['vote_average'],1)))
    final = final.replace("[ANO]", f['release_date'][:4]).replace("[URL_IA_BACKDROP]", img_ia_hero)
    final = final.replace("[URL_IA_EXTRA]", img_ia_hero).replace("[RESENHA_HTML]", res_html)
    final = final.replace("[DIRETOR]", "Equipe UniTV").replace("[GENEROS]", det['genres'][0]['name'] if det['genres'] else "Cinema")
    final = final.replace("[DURACAO]", f"{det['runtime']} min")

    with open(os.path.join(pasta, "index.html"), "w", encoding="utf-8") as file: file.write(final)
    
    injetar_card(f, slug, img_ia_poster)
    with open(HISTORICO_CINE, "a") as h: h.write(slug + "\n")
    processados += 1

subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "Auto-Cine: Imagens corrigidas"])
subprocess.run(["git", "push", "origin", "main"])
