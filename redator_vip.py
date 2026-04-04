import google.generativeai as genai
import os
import re
import time
import subprocess
from datetime import datetime

# ==========================================
# 1. CONFIGURAÇÕES DA MÁQUINA
# ==========================================
# Sua chave de API Oficial
genai.configure(api_key="AIzaSyCmT5HHUpHsXbtN68h6bpkRIzFpjIy2RGs")
# Usando o modelo mais inteligente e rápido para textos longos
model = genai.GenerativeModel('gemini-2.5-flash')

QTD_POSTS_POR_VEZ = 3 # Quantos posts fazer cada vez que o script rodar
PASTA_BLOG = "blog"

# ==========================================
# 2. O SEU LAYOUT BLINDADO (CABEÇALHO E RODAPÉ)
# ==========================================
# Note que os caminhos (../../) já estão ajustados para páginas dentro de blog/slug/
TEMPLATE_TOPO = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{titulo} | Blog UniTV Oficial</title>
    <meta name="description" content="{meta_desc}">
    <meta name="theme-color" content="#1a0525">
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="icon" href="../../assets/img/logo-unitv.png" type="image/png">

    <style>
        /* ESTILOS BASE DO SITE IMPORTADOS AQUI */
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }}
        :root {{ --bg-body: #050505; --bg-card: #0f0f0f; --gradiente-premium: linear-gradient(135deg, #FF512F 0%, #DD2476 100%); --cor-destaque: #ff0080; --wa-header: #075e54; --wa-bg: #e5ddd5; --wa-msg-user: #dcf8c6; }}
        html, body {{ background-color: var(--bg-body); color: #f0f0f0; overflow-x: hidden; line-height: 1.6; }}
        
        header {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 5%; position: sticky; top: 0; width: 100%; background: rgba(5, 5, 5, 0.95); backdrop-filter: blur(12px); z-index: 1000; border-bottom: 1px solid rgba(255, 255, 255, 0.08); height: 70px; }}
        .logo img {{ height: 36px; }}
        nav ul {{ display: flex; list-style: none; gap: 25px; }}
        nav a {{ color: #bbb; text-decoration: none; font-size: 0.85rem; font-weight: 500; text-transform: uppercase; transition: 0.3s; }}
        nav a:hover {{ color: var(--cor-destaque); }}
        .btn-header {{ background: var(--gradiente-premium); color: white; padding: 8px 20px; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: 800; border: none; }}
        
        /* ESTILOS ESPECÍFICOS DO BLOG (LEITURA) */
        .article-container {{ max-width: 900px; margin: 50px auto 100px; padding: 0 20px; }}
        .article-header {{ text-align: center; margin-bottom: 40px; }}
        .article-header h1 {{ font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 800; line-height: 1.2; margin-bottom: 20px; background: linear-gradient(90deg, #ff8c00, #ff0080); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .article-meta {{ color: #888; font-size: 0.9rem; font-weight: 500; display: flex; justify-content: center; gap: 15px; }}
        .article-content h2 {{ color: #fff; font-size: 2rem; margin: 50px 0 20px; font-weight: 700; border-left: 5px solid var(--cor-destaque); padding-left: 15px; }}
        .article-content h3 {{ color: #ddd; font-size: 1.4rem; margin: 30px 0 15px; font-weight: 600; }}
        .article-content p {{ color: #bbb; font-size: 1.1rem; line-height: 1.8; margin-bottom: 25px; }}
        .article-content ul {{ margin: 0 0 25px 20px; color: #bbb; font-size: 1.1rem; line-height: 1.8; }}
        .article-content li {{ margin-bottom: 10px; }}
        .article-content img {{ width: 100%; border-radius: 16px; margin: 30px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
        .article-content strong {{ color: #fff; }}
        
        .cta-box {{ background: #111; border: 1px solid #333; border-left: 5px solid #00ff88; padding: 40px; border-radius: 16px; text-align: center; margin: 50px 0; }}
        .cta-box h3 {{ color: #fff; font-size: 1.8rem; margin-bottom: 15px; }}
        .cta-box p {{ color: #aaa; margin-bottom: 25px; }}
        .btn-cta-blog {{ background: #00ff88; color: #000; padding: 15px 35px; border-radius: 50px; font-weight: 800; text-decoration: none; font-size: 1.1rem; display: inline-block; transition: 0.3s; text-transform: uppercase; }}
        .btn-cta-blog:hover {{ transform: translateY(-3px); box-shadow: 0 10px 25px rgba(0, 255, 136, 0.4); }}

        /* FOOTER & CHAT OMITIDOS AQUI PARA ECONOMIZAR ESPAÇO NO CÓDIGO PYTHON (MAS ESTARÃO NO HTML FINAL) */
    </style>
</head>
<body>
    <header>
        <div class="logo"><a href="../../index.html"><img src="../../assets/img/logo-unitv.png" alt="UniTV"></a></div>
        <nav>
            <ul>
                <li><a href="../../index.html">Início</a></li>
                <li><a href="../../planos">Planos</a></li>
                <li><a href="../index.html" class="active">Blog</a></li>
            </ul>
        </nav>
        <a href="../../index.html#comprar" class="btn-header">Assinar VIP</a>
    </header>

    <main class="article-container">
        <header class="article-header">
            <h1>{titulo}</h1>
            <div class="article-meta">
                <span><i class="fa-solid fa-calendar"></i> {data_atual}</span>
                <span><i class="fa-solid fa-user-pen"></i> Redação UniTV Oficial</span>
            </div>
        </header>
        <div class="article-content">
"""

TEMPLATE_RODAPE = """
        </div>
        
        <div class="cta-box">
            <h3>Cansado de Travamentos?</h3>
            <p>Garanta hoje o plano Anual VIP da UniTV Oficial. Assista a mais de 20 mil conteúdos em 4K nativo com tecnologia P2P.</p>
            <a href="../../index.html#comprar" class="btn-cta-blog">VER PLANOS E PREÇOS</a>
        </div>
    </main>

    <footer style="background: #050505; border-top: 1px solid #1a1a1a; padding: 60px 20px; text-align: center; color: #777;">
        <img src="../../assets/img/logo-unitv.png" alt="UniTV" style="height: 35px; margin-bottom: 20px; filter: brightness(0.8);">
        <p>© 2026 UniTV Revenda Oficial. O melhor do entretenimento digital 4K.</p>
    </footer>
</body>
</html>
"""

# ==========================================
# 3. A INTELIGÊNCIA DO ROBÔ
# ==========================================
def gerar_temas():
    print("🧠 Analisando tendências do Google e streaming...")
    prompt = """
    Crie 5 títulos de artigos MUITO chamativos e persuasivos para um blog sobre TV Box, Streaming, filmes e tecnologia Android. 
    Os temas devem ser profundos, como análises, dicas de como remover travamentos de IPTV, setups para TV Box, ou curiosidades sobre filmes em 4K.
    Retorne APENAS os títulos, um por linha.
    """
    resposta = model.generate_content(prompt)
    return [t.strip() for t in resposta.text.split('\n') if t.strip()][:QTD_POSTS_POR_VEZ]

def escrever_artigo(tema):
    print(f"✍️ Escrevendo artigo colossal sobre: {tema}")
    prompt_redator = f"""
    Aja como o melhor especialista em SEO e Tecnologia do Brasil. Escreva um artigo ÉPICO, completo e gigante (mais de 1200 palavras) sobre o título: "{tema}".
    
    REGRA DE FORMATAÇÃO (RETORNE APENAS O HTML DO CORPO DO TEXTO, NÃO USE ```html):
    1. Não inclua a tag <h1> (já está no template). Comece direto com parágrafos introdutórios persuasivos.
    2. Use várias tags <h2> e <h3> para dividir os tópicos.
    3. Cite DADOS de pesquisas inventados porém realistas (ex: "Segundo especialistas em redes, 78% dos travamentos...").
    4. Adicione 2 tags de imagem do Unsplash ao longo do texto usando esta sintaxe:
       <img src="[https://source.unsplash.com/1200x600/?technology,streaming](https://source.unsplash.com/1200x600/?technology,streaming)" alt="Imagem ilustrativa">
    5. Mantenha um tom profissional, profundo, solucionador de problemas e focado em vender a ideia de que "ter um servidor Premium (UniTV) é a única solução".
    """
    
    artigo_html = model.generate_content(prompt_redator).text.replace("```html", "").replace("```", "").strip()
    
    # Gera uma meta description rápida
    prompt_meta = f"Crie uma meta description de SEO (max 150 caracteres) para um post com o título: {tema}. Retorne apenas a frase."
    meta_desc = model.generate_content(prompt_meta).text.strip()
    
    return artigo_html, meta_desc

def criar_slug(texto):
    return re.sub(r'[^a-z0-9]+', '-', texto.lower()).strip('-')

# ==========================================
# 4. INJETOR DA TELA INICIAL DO BLOG
# ==========================================
def atualizar_pagina_principal_do_blog(titulo, slug, meta_desc):
    caminho_index = os.path.join(PASTA_BLOG, "index.html")
    
    # Se o arquivo não existir, cria uma base mínima
    if not os.path.exists(caminho_index):
        with open(caminho_index, "w", encoding="utf-8") as f:
            f.write("<html><head><title>Blog</title></head><body style='background:#050505; color:white; font-family:sans-serif; padding:50px;'><div id='posts_aqui'></div></body></html>")
            
    with open(caminho_index, "r", encoding="utf-8") as f:
        html = f.read()

    # O Design do "Quadradinho" do Blog
    card_html = f"""
        <article style="background: #0f0f0f; border: 1px solid #222; border-radius: 16px; overflow: hidden; margin-bottom: 30px; display: flex; flex-direction: column;">
            <div style="padding: 30px;">
                <span style="color: #ff0080; font-size: 0.8rem; font-weight: bold; text-transform: uppercase;">Atualizado Hoje</span>
                <h2 style="font-size: 1.5rem; margin: 10px 0;"><a href="{slug}/index.html" style="color: white; text-decoration: none;">{titulo}</a></h2>
                <p style="color: #888; margin-bottom: 20px;">{meta_desc}</p>
                <a href="{slug}/index.html" style="color: #00ff88; text-decoration: none; font-weight: bold; text-transform: uppercase; font-size: 0.9rem;">Ler Artigo Completo &rarr;</a>
            </div>
        </article>
        <div id='posts_aqui'></div>
    """

    if "<div id='posts_aqui'>" in html:
        html = html.replace("<div id='posts_aqui'>", card_html)
    else:
        # Se não achar a âncora, joga no final do body
        html = html.replace("</body>", f"<div style='max-width: 800px; margin: 0 auto;'>{card_html}</div></body>")

    with open(caminho_index, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"🔗 Artigo '{titulo}' linkado na capa do blog!")

# ==========================================
# EXECUTOR
# ==========================================
print("🚀 MÁQUINA DE SEO PROGRAMÁTICO INICIADA")
temas = gerar_temas()

for tema in temas:
    slug = criar_slug(tema)
    pasta_artigo = os.path.join(PASTA_BLOG, slug)
    
    if os.path.exists(pasta_artigo):
        print(f"⏩ Pulando '{tema}', já existe.")
        continue
        
    os.makedirs(pasta_artigo, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_artigo, "index.html")
    
    # Chama a IA
    conteudo_html, meta_desc = escrever_artigo(tema)
    data_formatada = datetime.now().strftime("%d de %B de %Y")
    
    # Junta as partes
    pagina_final = TEMPLATE_TOPO.format(titulo=tema, meta_desc=meta_desc, data_atual=data_formatada)
    pagina_final += conteudo_html
    pagina_final += TEMPLATE_RODAPE
    
    # Salva o arquivo HTML
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(pagina_final)
    
    # Linka no portal
    atualizar_pagina_principal_do_blog(tema, slug, meta_desc)
    
    # Espera 5 segundos para não estourar limite da API
    time.sleep(5)

print("\n📦 Fazendo o Push para o Servidor/GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Auto-post SEO: {datetime.now().strftime('%Y-%m-%d')}"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ DEPLOY CONCLUÍDO! O site está no ar.")
except Exception as e:
    print("⚠️ Erro no Git Push. Os arquivos foram criados localmente com sucesso, mas você precisa fazer o push manual.")
