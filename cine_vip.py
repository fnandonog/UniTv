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
# 1. CONFIGURAÇÕES (CHAVES INJETADAS)
# ==========================================
GEMINI_KEY = "AIzaSyCmT5HHUpHsXbtN68h6bpkRIzFpjIy2RGs"
TMDB_KEY = "9cb2f018163da4a3f89d718ee6be8677"
MODEL_ID = 'gemini-2.0-flash' 

QTD_FILMES_POR_VEZ = 2
PASTA_CINEMA = "cinema"
HISTORICO_CINE = "historico_cinema.txt"

client = genai.Client(api_key=GEMINI_KEY)
CONFIG_GERAL = types.GenerateContentConfig(
    safety_settings=[
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
    ]
)

# ==========================================
# 2. TEMPLATE DA PÁGINA DE RESENHA DO FILME
# ==========================================
TEMPLATE_RESENHA = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo} | Resenha Cinema VIP UniTV</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800;900&display=swap" rel="stylesheet">
    <link rel="icon" href="../../img/logo-unitv.png" type="image/png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }}
        body {{ background-color: #050505; color: #fff; overflow-x: hidden; }}
        
        .hero-backdrop {{ width: 100%; height: 65vh; background: url('{backdrop_url}') center top / cover no-repeat; position: relative; border-bottom: 1px solid rgba(255,115,0,0.2); }}
        .hero-overlay {{ position: absolute; bottom: 0; width: 100%; height: 100%; background: linear-gradient(to top, #050505 5%, rgba(5,5,5,0.8) 40%, transparent 100%); }}
        
        .nav-voltar {{ position: absolute; top: 30px; left: 5%; z-index: 20; }}
        .nav-voltar a {{ color: #fff; text-decoration: none; font-weight: 800; background: rgba(0,0,0,0.5); padding: 10px 20px; border-radius: 50px; backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.1); transition: 0.3s; }}
        .nav-voltar a:hover {{ background: #ff7300; border-color: #ff7300; }}

        .content {{ max-width: 900px; margin: -150px auto 50px; position: relative; z-index: 10; padding: 0 20px; }}
        h1 {{ font-size: clamp(2.5rem, 5vw, 4rem); font-weight: 900; line-height: 1.1; margin-bottom: 15px; text-transform: uppercase; text-shadow: 2px 2px 20px rgba(0,0,0,0.8); }}
        
        .meta-tags {{ display: flex; gap: 15px; align-items: center; margin-bottom: 40px; flex-wrap: wrap; }}
        .meta-tags span {{ background: rgba(255,255,255,0.1); padding: 5px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: 700; border: 1px solid rgba(255,255,255,0.05); backdrop-filter: blur(5px); }}
        .meta-tags .nota {{ color: #ffcc00; border-color: rgba(255,204,0,0.3); }}
        .meta-tags .qualidade {{ background: linear-gradient(135deg, #ff7300, #dd2476); color: white; border: none; }}

        .resenha-body {{ font-size: 1.15rem; line-height: 1.8; color: #ccc; background: #0a0a0a; padding: 40px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 20px 40px rgba(0,0,0,0.5); }}
        .resenha-body h2 {{ color: #00f3ff; margin: 40px 0 20px; font-size: 1.8rem; font-weight: 800; border-bottom: 1px solid rgba(0, 243, 255, 0.2); padding-bottom: 10px; }}
        .resenha-body p {{ margin-bottom: 25px; }}
        .resenha-body blockquote {{ border-left: 4px solid #ff7300; background: rgba(255, 115, 0, 0.05); padding: 20px; margin: 30px 0; font-style: italic; color: #fff; font-weight: 600; border-radius: 0 10px 10px 0; }}

        .cta-box {{ text-align: center; margin-top: 60px; padding: 40px; border-radius: 20px; background: radial-gradient(circle at center, #2d0b1e 0%, #050505 100%); border: 1px solid #dd2476; }}
        .cta-box h3 {{ font-size: 1.8rem; margin-bottom: 15px; color: #fff; }}
        .btn-assinar {{ display: inline-block; background: linear-gradient(135deg, #ff7300, #dd2476); color: white; padding: 15px 40px; border-radius: 50px; font-weight: 800; text-decoration: none; text-transform: uppercase; margin-top: 20px; transition: 0.3s; }}
        .btn-assinar:hover {{ transform: scale(1.05); box-shadow: 0 10px 20px rgba(221, 36, 118, 0.4); }}
    </style>
</head>
<body>

    <div class="hero-backdrop"><div class="hero-overlay"></div></div>
    
    <div class="nav-voltar">
        <a href="../index.html"><i class="fa-solid fa-arrow-left"></i> Catálogo</a>
    </div>

    <div class="content">
        <h1>{titulo}</h1>
        <div class="meta-tags">
            <span class="nota"><i class="fa-solid fa-star"></i> {nota}</span>
            <span>{ano}</span>
            <span class="qualidade">4K HDR</span>
            <span>Resenha VIP</span>
        </div>
        
        <div class="resenha-body">
            {corpo_resenha}
        </div>

        <div class="cta-box">
            <h3>Disponível agora no app UniTV</h3>
            <p style="color:#aaa;">Assista a este e milhares de outros filmes em 4K real, sem travamentos.</p>
            <a href="../../index.html#comprar" class="btn-assinar">LIBERAR ACESSO VIP</a>
        </div>
    </div>

</body>
</html>"""

# ==========================================
# 3. FUNÇÕES BASE
# ==========================================
def carregar_historico():
    if not os.path.exists(HISTORICO_CINE): return []
    with open(HISTORICO_CINE, 'r', encoding='utf-8') as f:
        return [l.strip() for l in f.readlines() if l.strip()]

def criar_slug(texto):
    txt = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r'[^a-z0-9]+', '-', txt.lower()).strip('-')

# ==========================================
# 4. BUSCA NA API TMDB E GERAÇÃO
# ==========================================
def buscar_filmes_em_alta():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_KEY}&language=pt-BR"
    print("🎬 Buscando lançamentos no TMDB...")
    res = requests.get(url)
    if res.status_code == 200:
        return res.json().get('results', [])
    return []

def escrever_resenha_gemini(filme):
    titulo = filme['title']
    sinopse = filme['overview']
    
    prompt = f"""
    Escreva uma resenha imersiva para o blog de cinema VIP (aprox. 500 palavras) sobre o filme: "{titulo}".
    Sinopse base: {sinopse}.
    
    REGRAS HTML (Use APENAS tags permitidas: <h2>, <p>, <blockquote>):
    1. Crie um <h2> chamado "Nos Bastidores" e conte 2 curiosidades reais sobre as gravações ou o elenco deste filme.
    2. Crie um <h2> chamado "Por que assistir na UniTV?" e explique como a fotografia/efeitos desse filme foram feitos para serem vistos em 4K sem travamentos.
    3. Use um <blockquote> para destacar a melhor característica do filme.
    Não use tags <html>, <head>, ou <body>.
    """
    
    try:
        print(f"✍️ Gemini redigindo resenha de: {titulo}...")
        res = client.models.generate_content(model=MODEL_ID, contents=prompt, config=CONFIG_GERAL)
        return res.text.replace("```html", "").replace("```", "").strip()
    except Exception as e:
        print(f"⚠️ Erro IA: {e}")
        return f"<p>{sinopse}</p><p>Assista agora na sua TV Box 4K.</p>"

def injetar_card_na_vitrine(filme, slug):
    caminho = os.path.join(PASTA_CINEMA, "index.html")
    ancora = ""
    
    titulo = filme['title']
    nota = round(filme['vote_average'], 1)
    ano = filme['release_date'][:4] if 'release_date' in filme else "2024"
    poster_url = f"https://image.tmdb.org/t/p/w500{filme['poster_path']}"
    
    card = f"""
        <a href="{slug}/index.html" class="movie-card reveal active">
            <img src="{poster_url}" alt="{titulo}" class="movie-poster">
            <div class="movie-rating-badge"><i class="fa-solid fa-star"></i> {nota}</div>
            <div class="movie-overlay">
                <h3 class="movie-info-title">{titulo}</h3>
                <div class="movie-info-meta">
                    <span>{ano}</span>
                    <span>Em Alta</span>
                </div>
                <div class="btn-read-review">LER RESENHA VIP</div>
            </div>
        </a>
    """
    
    with open(caminho, "r", encoding="utf-8") as f: html = f.read()
    if ancora in html:
        html = html.replace(ancora, card + "\n        " + ancora)
        with open(caminho, "w", encoding="utf-8") as f: f.write(html)
        print(f"🔗 Pôster de '{titulo}' colado na vitrine.")

# ==========================================
# EXECUTOR DO CINEMA
# ==========================================
historico = carregar_historico()
filmes = buscar_filmes_em_alta()

processados = 0
for filme in filmes:
    if processados >= QTD_FILMES_POR_VEZ: break
    
    titulo = filme['title']
    slug = criar_slug(titulo)
    
    if slug in historico or not filme.get('poster_path') or not filme.get('backdrop_path'):
        continue
        
    pasta_filme = os.path.join(PASTA_CINEMA, slug)
    os.makedirs(pasta_filme, exist_ok=True)
    
    corpo_html = escrever_resenha_gemini(filme)
    backdrop_url = f"https://image.tmdb.org/t/p/original{filme['backdrop_path']}"
    nota = round(filme['vote_average'], 1)
    ano = filme['release_date'][:4] if 'release_date' in filme else "Lançamento"
    
    html_final = TEMPLATE_RESENHA.format(
        titulo=titulo, 
        backdrop_url=backdrop_url, 
        nota=nota, 
        ano=ano, 
        corpo_resenha=corpo_html
    )
    
    with open(os.path.join(pasta_filme, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_final)
        
    injetar_card_na_vitrine(filme, slug)
    
    with open(HISTORICO_CINE, "a", encoding="utf-8") as f: f.write(f"{slug}\n")
    processados += 1
    time.sleep(3)

print("\n📦 Subindo lançamentos para o GitHub...")
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", f"Auto-Cine: Adicionado {processados} filmes em alta"])
subprocess.run(["git", "pull", "origin", "main", "--rebase"])
subprocess.run(["git", "push", "origin", "main"])
print("✅ SUCESSO! A Sessão Pipoca está no ar.")
