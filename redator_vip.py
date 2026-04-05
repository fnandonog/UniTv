import google.generativeai as genai
import os
import re
import time
import subprocess
from datetime import datetime

# ==========================================
# 1. CONFIGURAÇÕES DA MÁQUINA (UPGRADE PRO)
# ==========================================
genai.configure(api_key="AIzaSyCmT5HHUpHsXbtN68h6bpkRIzFpjIy2RGs")
# Usando o modelo de raciocínio profundo para estruturação impecável de HTML e Copywriting
model = genai.GenerativeModel('gemini-1.5-pro-latest')

QTD_POSTS_POR_VEZ = 3 
PASTA_BLOG = "blog"
HISTORICO_ARQUIVO = "historico_temas_blog.txt"

# ==========================================
# 2. TEMPLATES BLINDADOS (EXATAMENTE SEU SITE)
# ==========================================
# Usaremos .replace() no lugar de f-strings para proteger as chaves {} do seu CSS e JavaScript.

TEMPLATE_TOPO = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{titulo} | Blog UniTV Oficial</title>
    <meta name="description" content="{meta_desc}">
    <meta name="theme-color" content="#1a0525">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="icon" href="../../img/logo-unitv.png" type="image/png">

    <style>
        /* --- ESTILOS ORIGINAIS DO SEU SITE --- */
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        :root {
            --bg-body: #050505;
            --bg-card: #0f0f0f;
            --gradiente-premium: linear-gradient(135deg, #FF512F 0%, #DD2476 100%);
            --gradiente-texto: linear-gradient(90deg, #ff8c00, #ff0080, #7928ca);
            --borda-sutil: 1px solid rgba(255, 255, 255, 0.08);
            --verde-zap: #25D366;
            --wa-header: #075e54; --wa-bg: #e5ddd5; --wa-msg-user: #dcf8c6;
            --cor-destaque: #ff8c00;
            --cor-secundaria: #00d4ff;
        }

        html, body { background-color: var(--bg-body); color: #f0f0f0; overflow-x: hidden; width: 100%; line-height: 1.6; scroll-behavior: smooth; }

        .promo-bar { background: linear-gradient(90deg, #1a0b2e, #2d0b1e); color: #e0e0e0; text-align: center; padding: 8px 10px; font-size: 0.85rem; font-weight: 500; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .promo-bar span { color: #ff0055; font-weight: 700; margin-left: 5px; }

        header { display: flex; justify-content: space-between; align-items: center; padding: 10px 5%; position: sticky; top: 0; width: 100%; background: rgba(5, 5, 5, 0.95); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); z-index: 1000; border-bottom: var(--borda-sutil); height: 70px; }
        .logo img { height: 36px; filter: brightness(1.1); transition: 0.3s; }
        nav ul { display: flex; list-style: none; gap: 25px; }
        nav a { color: #bbb; text-decoration: none; font-size: 0.85rem; font-weight: 500; text-transform: uppercase; transition: 0.3s; }
        nav a:hover, nav a.active { color: var(--cor-destaque); }
        .header-actions { display: flex; align-items: center; gap: 15px; }
        .btn-header { background: rgba(255, 255, 255, 0.1); color: white; padding: 8px 20px; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.1); transition: 0.3s;}
        .btn-header:hover { background: #fff; color: #000; }

        /* --- ESTILOS EXCLUSIVOS PARA LEITURA DO BLOG (CYBERPUNK CLEAN) --- */
        .article-container { max-width: 850px; margin: 60px auto 100px; padding: 0 20px; }
        
        .article-header { text-align: center; margin-bottom: 50px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 30px; }
        .article-header h1 { font-size: clamp(2rem, 4vw, 3.2rem); font-weight: 800; line-height: 1.2; margin-bottom: 20px; background: var(--gradiente-texto); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .article-meta { display: flex; justify-content: center; gap: 20px; color: #888; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
        .article-meta i { color: var(--cor-secundaria); }

        .article-content { font-size: 1.15rem; color: #ccc; line-height: 1.8; }
        .article-content h2 { color: #fff; font-size: 2rem; margin: 60px 0 25px; font-weight: 700; border-left: 5px solid var(--cor-secundaria); padding-left: 15px; letter-spacing: -0.5px; }
        .article-content h3 { color: var(--cor-destaque); font-size: 1.4rem; margin: 40px 0 15px; font-weight: 600; }
        .article-content p { margin-bottom: 25px; }
        .article-content img { width: 100%; border-radius: 16px; margin: 35px 0; border: 1px solid rgba(0, 212, 255, 0.15); box-shadow: 0 15px 40px rgba(0,0,0,0.5); object-fit: cover; }
        .article-content ul, .article-content ol { margin: 0 0 30px 30px; }
        .article-content li { margin-bottom: 12px; }
        .article-content strong { color: #fff; font-weight: 700; }
        
        /* Caixas de Destaque para prender a atenção */
        .article-content blockquote { background: rgba(0, 212, 255, 0.05); border-left: 4px solid var(--cor-secundaria); padding: 25px 30px; margin: 40px 0; font-style: italic; color: #eee; border-radius: 0 12px 12px 0; font-size: 1.2rem; }
        .article-content .tech-box { background: #111; border: 1px solid #222; border-radius: 12px; padding: 25px; margin: 35px 0; border-top: 3px solid var(--cor-destaque); }
        
        .cta-banner-blog { background: linear-gradient(160deg, #180a1f 0%, #050505 100%); border: 1px solid var(--cor-destaque); padding: 40px; border-radius: 20px; text-align: center; margin-top: 60px; box-shadow: 0 0 40px rgba(255, 0, 128, 0.15); }
        .cta-banner-blog h3 { color: #fff; font-size: 1.8rem; margin-bottom: 15px; font-weight: 800; }
        .btn-cta-blog { background: var(--gradiente-premium); color: white; padding: 15px 35px; border-radius: 50px; text-decoration: none; font-weight: 800; display: inline-block; margin-top: 20px; text-transform: uppercase; letter-spacing: 1px; transition: 0.3s; }
        .btn-cta-blog:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(221, 36, 118, 0.4); }

        /* --- RODAPÉ E CHATBOT ORIGINAIS OMITIDOS AQUI NO CSS, MAS PRESENTES NO HTML --- */
        footer { background: #050505; border-top: 1px solid #1a1a1a; padding: 80px 20px 40px; color: #777; font-size: 0.9rem; }
        .footer-container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr; gap: 50px; }
        .footer-logo { margin-bottom: 20px; filter: brightness(1.2); height: 40px; }
        .footer-col h4 { color: #fff; margin-bottom: 25px; font-size: 0.9rem; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; }
        .footer-links { list-style: none; }
        .footer-links li { margin-bottom: 12px; }
        .footer-links a { color: #777; text-decoration: none; transition: 0.3s; display: block; }
        .footer-links a:hover { color: #fff; transform: translateX(5px); }
        .payment-methods { display: flex; gap: 15px; font-size: 2rem; margin-top: 15px; color: #444; }
        
        .wa-widget { position: fixed; bottom: 90px; right: 25px; width: 350px; background: var(--wa-bg); border-radius: 16px; z-index: 9999; box-shadow: 0 15px 35px rgba(0,0,0,0.4); display: flex; flex-direction: column; overflow: hidden; transform: scale(0); transform-origin: bottom right; transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
        .wa-widget.active { transform: scale(1); }
        .wa-header { background: var(--wa-header); color: white; padding: 15px 20px; display: flex; align-items: center; justify-content: space-between; }
        .wa-profile { display: flex; align-items: center; gap: 12px; }
        .wa-profile img { width: 42px; height: 42px; border-radius: 50%; background: #fff; padding: 2px; }
        .wa-info { display: flex; flex-direction: column; }
        .wa-name { font-weight: 600; font-size: 1rem; }
        .wa-status { font-size: 0.75rem; color: #cfd8dc; display: flex; align-items: center; gap: 5px;}
        .wa-status::before { content:''; display:inline-block; width:8px; height:8px; background:#00ff88; border-radius:50%; }
        .wa-close { background: none; border: none; color: white; font-size: 1.8rem; cursor: pointer; transition: 0.3s; outline: none; }
        .wa-close:hover { color: #ffcccc; transform: rotate(90deg); }
        .wa-chat-body { height: 380px; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; background-image: url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png'); background-size: contain; }
        .wa-msg { max-width: 85%; padding: 10px 15px; border-radius: 12px; font-size: 0.9rem; position: relative; box-shadow: 0 2px 5px rgba(0,0,0,0.1); line-height: 1.4; color: #333; }
        .wa-msg-bot { background: white; align-self: flex-start; border-top-left-radius: 0; }
        .wa-msg-user { background: var(--wa-msg-user); align-self: flex-end; border-top-right-radius: 0; }
        .wa-options { padding: 15px; background: #f0f0f0; border-top: 1px solid #ddd; display: flex; flex-direction: column; gap: 10px; }
        .wa-options button { background: white; border: 1px solid #ccc; padding: 12px; border-radius: 25px; font-size: 0.9rem; color: #075e54; font-weight: 600; cursor: pointer; text-align: center; width: 100%; transition: 0.3s; }
        .wa-input-fake { background: #f0f0f0; padding: 12px 20px; display: flex; align-items: center; gap: 15px; border-top: 1px solid #ddd; }
        .wa-input-box { background: white; flex: 1; padding: 10px 20px; border-radius: 25px; color: #999; font-size: 0.9rem; border: 1px solid #ccc; }
        .float-zap { position: fixed; bottom: 25px; right: 25px; background: #25d366; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; z-index: 10000; box-shadow: 0 5px 20px rgba(37, 211, 102, 0.4); cursor: pointer; transition: 0.3s; }
        
        @media (max-width: 768px) {
            header { height: 65px; padding: 10px 20px; }
            .logo img { height: 28px; }
            nav, .header-actions { display: none; }
            .article-header h1 { font-size: 2.2rem; }
            .footer-container { grid-template-columns: 1fr; text-align: center; }
            .payment-methods, .footer-links a { justify-content: center; }
        }
    </style>
</head>
<body>

    <div class="promo-bar">
        🔥 OFERTA RELÂMPAGO: Preços reduzidos por tempo limitado!
    </div>

    <header>
        <div class="logo">
            <a href="../../index.html"><img src="../../img/logo-unitv.png" alt="Logo UniTV Oficial Revenda Autorizada"></a>
        </div>
        <nav id="nav-menu">
            <ul>
                <li><a href="../../index.html">Início</a></li>
                <li><a href="../../index.html#comprar">Planos</a></li>
                <li><a href="../../tutorial/index.html">Instalação</a></li>
                <li><a href="../index.html" class="active">Blog</a></li>
            </ul>
        </nav>
        <div class="header-actions">
            <a href="../../index.html#comprar" class="btn-header">Assinar Agora</a>
        </div>
    </header>

    <main class="article-container">
        <header class="article-header">
            <h1>{titulo}</h1>
            <div class="article-meta">
                <span><i class="fa-solid fa-calendar"></i> {data_atual}</span>
                <span><i class="fa-solid fa-microchip"></i> Redação Tech UniTV</span>
            </div>
        </header>
        
        <article class="article-content">
"""

TEMPLATE_RODAPE = """
        </article>
        
        <div class="cta-banner-blog">
            <h3>Pare de passar raiva com travamentos!</h3>
            <p style="color: #bbb; margin-bottom: 20px;">Aproveite o máximo do 4K na sua TV Box. Garanta sua recarga UniTV Oficial com entrega imediata via Pix e suporte humanizado.</p>
            <a href="../../index.html#comprar" class="btn-cta-blog"><i class="fa-solid fa-bolt"></i> VER PLANOS OFICIAIS</a>
        </div>
    </main>

    <footer>
        <div class="footer-container">
            <div class="footer-col">
                <img src="../../img/logo-unitv.png" alt="Logo UniTV Revenda Autorizada" class="footer-logo" loading="lazy">
                <p class="footer-desc">Somos revendedores autorizados da plataforma UniTV. Levamos entretenimento premium com qualidade 4K diretamente para a sua casa com suporte de excelência.</p>
                <div style="display: flex; align-items: center; gap: 10px; color: #fff; font-weight: bold; margin-top: 15px;">
                    <i class="fa-solid fa-shield-halved" style="color:#00ff88"></i> Conexão 100% Segura
                </div>
            </div>
            <div class="footer-col">
                <h4>Acesso Rápido</h4>
                <ul class="footer-links">
                    <li><a href="../../index.html#comprar">Planos e Recargas</a></li>
                    <li><a href="../../tutorial/index.html">Guia de Instalação</a></li>
                    <li><a href="../index.html">Blog de Tecnologia</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Suporte Dedicado</h4>
                <ul class="footer-links">
                    <li><a href="#" onclick="toggleChat()">Atendimento WhatsApp</a></li>
                    <li><span style="color:#666; font-size:0.8rem; margin-top:5px; display:block;">Horário: Seg a Sex, das 08h às 22h</span></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Transação Segura</h4>
                <p style="margin-bottom: 15px; color: #777;">Aprovação imediata via Pix e Cartão de Crédito.</p>
                <div class="payment-methods">
                    <i class="fa-brands fa-pix" style="color:#32bcad;"></i>
                    <i class="fa-brands fa-cc-mastercard"></i>
                    <i class="fa-brands fa-cc-visa"></i>
                </div>
            </div>
        </div>
        <div style="text-align: center; margin-top: 60px; padding-top: 30px; border-top: 1px solid #111; font-size: 0.8rem; color:#888;">
            &copy; 2024 - 2026 UniTV Revenda Oficial Autorizada. Todos os direitos reservados.
        </div>
    </footer>

    <div id="chat-widget" class="wa-widget">
        <div class="wa-header">
            <div class="wa-profile">
                <img src="../../img/logo-unitv.png" alt="Atendente Virtual UniTV" loading="lazy">
                <div class="wa-info">
                    <span class="wa-name">Atendimento VIP</span>
                    <span id="wa-status" class="wa-status">Online</span>
                </div>
            </div>
            <button onclick="toggleChat()" class="wa-close" aria-label="Fechar janela de chat"><i class="fa-solid fa-times"></i></button>
        </div>
        <div id="chat-content" class="wa-chat-body">
            <div class="wa-msg wa-msg-bot">Olá! 👋 Bem-vindo ao suporte oficial UniTV. Como posso te ajudar hoje?</div>
        </div>
        <div id="wa-options" class="wa-options">
            <button onclick="window.open('../../index.html#comprar', '_self')">Ver planos disponíveis</button>
            <button onclick="window.open('https://wa.me/5519981765840', '_blank')">Falar com Suporte Humano</button>
        </div>
        <div class="wa-input-fake">
            <div class="wa-input-box">Selecione uma opção...</div>
            <i class="fa-solid fa-paper-plane" style="color: #075e54; font-size: 1.2rem;"></i>
        </div>
    </div>

    <div class="float-zap" onclick="toggleChat()"><i class="fa-brands fa-whatsapp"></i></div>

    <script>
        function toggleChat() { document.getElementById('chat-widget').classList.toggle('active'); }
    </script>
</body>
</html>
"""

# ==========================================
# 3. A INTELIGÊNCIA DA IA (COPYWRITING AVANÇADO)
# ==========================================
def carregar_historico():
    if not os.path.exists(HISTORICO_ARQUIVO):
        return []
    with open(HISTORICO_ARQUIVO, 'r', encoding='utf-8') as f:
        return [linha.strip() for linha in f.readlines()]

def salvar_historico(tema):
    with open(HISTORICO_ARQUIVO, 'a', encoding='utf-8') as f:
        f.write(f"{tema}\n")

def gerar_temas(historico):
    print("🧠 Procurando temas que engajam e vendem...")
    prompt = f"""
    Crie {QTD_POSTS_POR_VEZ} títulos de artigos altamente persuasivos e técnicos para um blog focado em TV Box, IPTV e tecnologia.
    Os títulos devem despertar curiosidade e focar na solução de problemas (ex: travamentos, configurações 4K, listas de filmes).
    NÃO repita estes temas: {', '.join(historico[-30:])}
    Retorne APENAS os títulos, um por linha.
    """
    resposta = model.generate_content(prompt)
    return [t.strip() for t in resposta.text.split('\n') if t.strip()][:QTD_POSTS_POR_VEZ]

def escrever_artigo(tema):
    print(f"✍️ Estruturando conteúdo visual rico para: {tema}")
    prompt_redator = f"""
    Escreva um artigo colossal (1200+ palavras) de altíssima conversão sobre: "{tema}".
    
    REGRA DE FORMATAÇÃO HTML OBRIGATÓRIA (RETORNE APENAS O HTML):
    1. NÃO use a tag <h1>.
    2. Use <h2> para os tópicos principais e <h3> para sub-tópicos.
    3. Para quebrar paredes de texto, envolva dicas cruciais ou dados importantes na div de destaque: <div class="tech-box">Seu texto aqui</div>
    4. Adicione exatamente 3 imagens ao longo do texto usando: <img src="https://picsum.photos/seed/{tema.replace(' ', '')}1/800/400" alt="Ilustração"> (Mude o número da seed 1, 2, 3 para não repetir a foto).
    5. Use blocos <blockquote> para citações de especialistas em tecnologia.
    6. Traga dados fictícios plausíveis (ex: "Testes mostram que 80% das TV Box...").
    7. Termine conectando o problema com a solução definitiva: Assinar a Recarga UniTV Oficial.
    """
    
    artigo_html = model.generate_content(prompt_redator).text.replace("```html", "").replace("```", "").strip()
    
    prompt_meta = f"Crie uma meta description para SEO (max 150 caracteres) focada na palavra-chave de: {tema}. Retorne apenas a frase."
    meta_desc = model.generate_content(prompt_meta).text.strip()
    
    return artigo_html, meta_desc

def criar_slug(texto):
    return re.sub(r'[^a-z0-9]+', '-', texto.lower()).strip('-')

# ==========================================
# 4. INJETOR NA TELA INICIAL DO BLOG
# ==========================================
def atualizar_pagina_principal_do_blog(titulo, slug, meta_desc):
    caminho_index = os.path.join(PASTA_BLOG, "index.html")
    
    try:
        with open(caminho_index, "r", encoding="utf-8") as f:
            html = f.read()

        # O Design EXATO do card do seu Grid
        novo_card = f"""
        <a href="{slug}/index.html" class="post-card reveal active">
            <div class="post-thumb">
                <img src="https://picsum.photos/seed/{slug}/800/600" alt="{titulo}">
            </div>
            <div class="post-content">
                <span class="post-tag">NOVIDADE TECH</span>
                <h2>{titulo}</h2>
                <p>{meta_desc}</p>
                <span class="btn-read">LER AGORA <i class="fa-solid fa-arrow-right"></i></span>
            </div>
        </a>
        """

        if "" in html:
            html = html.replace("", novo_card)
        else:
            print("⚠️ ERRO: A tag não foi encontrada no arquivo blog/index.html")

        with open(caminho_index, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"🔗 Artigo '{titulo}' linkado na vitrine do blog!")
    except FileNotFoundError:
        print(f"⚠️ O arquivo {caminho_index} não existe ainda.")

# ==========================================
# EXECUTOR
# ==========================================
print("🚀 MÁQUINA DE SEO CYBERPUNK INICIADA COM GEMINI PRO")
historico = carregar_historico()
temas = gerar_temas(historico)

for tema in temas:
    slug = criar_slug(tema)
    pasta_artigo = os.path.join(PASTA_BLOG, slug)
    
    if os.path.exists(pasta_artigo):
        print(f"⏩ Pulando '{tema}', já existe.")
        continue
        
    os.makedirs(pasta_artigo, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_artigo, "index.html")
    
    try:
        conteudo_html, meta_desc = escrever_artigo(tema)
        data_formatada = datetime.now().strftime("%d de %B de %Y")
        
        # Substituição limpa sem quebrar chaves de CSS/JS
        pagina_final = TEMPLATE_TOPO.replace("{titulo}", tema).replace("{meta_desc}", meta_desc).replace("{data_atual}", data_formatada)
        pagina_final += conteudo_html
        pagina_final += TEMPLATE_RODAPE
        
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(pagina_final)
        
        atualizar_pagina_principal_do_blog(tema, slug, meta_desc)
        salvar_historico(tema)
        time.sleep(10) # Pausa maior devido ao modelo PRO
    except Exception as e:
        print(f"❌ Erro ao gerar {tema}: {e}")

print("\n📦 Fazendo o Push Automático para o GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Auto-post Pro: {datetime.now().strftime('%Y-%m-%d %H:%M')}"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ DEPLOY CONCLUÍDO! O site está no ar e com visual premium.")
except Exception as e:
    print("⚠️ Erro no Git Push. Verifique credenciais.")
