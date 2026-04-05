import google.generativeai as genai
import os
import re
import time
import subprocess
import unicodedata
from datetime import datetime
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# ==========================================
# 1. CONFIGURAÇÕES DA MÁQUINA (GEMINI 2.5 PRO)
# ==========================================
genai.configure(api_key="AIzaSyCmT5HHUpHsXbtN68h6bpkRIzFpjIy2RGs")
model = genai.GenerativeModel('gemini-2.5-pro')

QTD_POSTS_POR_VEZ = 3 
PASTA_BLOG = "blog"
HISTORICO_ARQUIVO = "historico_temas_blog.txt"

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# ==========================================
# 2. TEMPLATES (CSS BLINDADO + SEU FOOTER E CHATBOT)
# ==========================================

TEMPLATE_TOPO = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{titulo} | Blog UniTV Oficial</title>
    <meta name="description" content="{meta_desc}">
    <meta name="theme-color" content="#1a0525">
    
    <link rel="canonical" href="https://unitvsite.com.br/" />
    <meta name="robots" content="index, follow" />
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="icon" href="../../img/logo-unitv.png" type="image/png">

    <style>
        /* --- GERAL --- */
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        :root {
            --bg-body: #050505;
            --bg-card: #0f0f0f;
            --gradiente-premium: linear-gradient(135deg, #FF512F 0%, #DD2476 100%);
            --gradiente-texto: linear-gradient(90deg, #ff8c00, #ff0080, #7928ca);
            --borda-sutil: 1px solid rgba(255, 255, 255, 0.08);
            --verde-zap: #25D366;
            --wa-header: #075e54; --wa-bg: #e5ddd5;
            --cor-destaque: #ff0080;
            --cor-secundaria: #00ff88;
        }
        html, body { background-color: var(--bg-body); color: #f0f0f0; overflow-x: hidden; width: 100%; line-height: 1.6; }

        /* --- HEADER DO SEU SITE --- */
        .promo-bar { background: linear-gradient(90deg, #1a0b2e, #2d0b1e); color: #e0e0e0; text-align: center; padding: 8px 10px; font-size: 0.85rem; font-weight: 500; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .brand-alert { background: rgba(255, 0, 128, 0.05); border-bottom: 1px solid rgba(255, 0, 128, 0.1); color: #ffb3d9; text-align: center; padding: 8px 10px; font-size: 0.75rem; font-weight: 600; display: flex; justify-content: center; gap: 10px; }
        
        header { display: flex; justify-content: space-between; align-items: center; padding: 10px 5%; position: sticky; top: 0; width: 100%; background: rgba(5, 5, 5, 0.95); backdrop-filter: blur(12px); z-index: 1000; border-bottom: var(--borda-sutil); height: 70px; }
        .logo img { height: 36px; filter: brightness(1.1); transition: 0.3s; }
        nav ul { display: flex; list-style: none; gap: 25px; }
        nav a { color: #bbb; text-decoration: none; font-size: 0.85rem; font-weight: 500; text-transform: uppercase; transition: 0.3s; }
        nav a:hover, nav a.active { color: white; color: var(--cor-destaque); }
        .btn-header { background: rgba(255, 255, 255, 0.1); color: white; padding: 8px 20px; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.1); transition: 0.3s;}
        .btn-header:hover { background: #fff; color: #000; }

        /* ======================================================= */
        /* --- ESTILOS EXCLUSIVOS E BLINDADOS DO ARTIGO --- */
        /* ======================================================= */
        .leitura-vip { max-width: 800px; margin: 40px auto 80px; padding: 0 20px; }
        
        .leitura-vip .post-header { text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .leitura-vip h1 { font-size: clamp(1.8rem, 4vw, 2.5rem); font-weight: 800; line-height: 1.2; margin-bottom: 15px; color: #fff; text-align: left; }
        .leitura-vip .meta { color: #888; font-size: 0.9rem; font-weight: 500; display: flex; gap: 15px; flex-wrap: wrap; }
        .leitura-vip .meta i { color: var(--cor-destaque); }

        .leitura-vip .conteudo { font-size: 1.1rem; color: #ccc; line-height: 1.8; }
        .leitura-vip .conteudo h2 { color: #fff; font-size: 1.8rem; margin: 50px 0 20px; font-weight: 700; border-left: 4px solid var(--cor-destaque); padding-left: 15px; line-height: 1.3;}
        .leitura-vip .conteudo h3 { color: var(--cor-secundaria); font-size: 1.4rem; margin: 40px 0 15px; font-weight: 600; }
        .leitura-vip .conteudo p { margin-bottom: 20px; }
        .leitura-vip .conteudo img { width: 100%; border-radius: 12px; margin: 30px 0; object-fit: cover; box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 1px solid #222; }
        .leitura-vip .conteudo ul { margin: 0 0 25px 25px; }
        .leitura-vip .conteudo li { margin-bottom: 10px; }
        .leitura-vip .conteudo strong { color: #fff; }
        
        .leitura-vip .tech-box { background: var(--bg-card); border: 1px solid rgba(255,255,255,0.05); border-left: 4px solid var(--cor-secundaria); padding: 25px; margin: 35px 0; border-radius: 8px; }
        .leitura-vip .tech-box h4 { color: var(--cor-secundaria); margin-bottom: 10px; font-size: 1.2rem; text-transform: uppercase; letter-spacing: 1px; }
        .leitura-vip .tech-box p { margin-bottom: 0; font-size: 1rem; color: #ddd; }
        
        .leitura-vip blockquote { background: rgba(255, 0, 128, 0.05); font-style: italic; color: #eee; border-left: 4px solid var(--cor-destaque); padding: 20px 30px; margin: 30px 0; font-size: 1.15rem; border-radius: 0 12px 12px 0; }

        .leitura-vip .cta-banner { background: linear-gradient(160deg, #180a1f 0%, #050505 100%); border: 1px solid var(--cor-destaque); padding: 40px; border-radius: 20px; text-align: center; margin-top: 60px; box-shadow: 0 0 40px rgba(255, 0, 128, 0.15); }
        .leitura-vip .cta-banner h3 { color: #fff; font-size: 1.8rem; margin-bottom: 15px; font-weight: 800; }
        .leitura-vip .btn-cta { background: var(--gradiente-premium); color: white; padding: 18px 45px; border-radius: 50px; text-decoration: none; font-weight: 800; display: inline-block; margin-top: 20px; text-transform: uppercase; letter-spacing: 1px; transition: 0.3s; }
        .leitura-vip .btn-cta:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(221, 36, 118, 0.4); }

        /* --- O SEU FOOTER OFICIAL EXATO --- */
        footer { background: #050505; border-top: 1px solid #1a1a1a; padding: 80px 20px 40px; color: #777; font-size: 0.9rem; }
        .footer-container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr; gap: 50px; }
        .footer-logo { margin-bottom: 20px; filter: brightness(1.2); height: 40px; }
        .footer-col h4 { color: #fff; margin-bottom: 25px; font-size: 0.9rem; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; }
        .footer-links { list-style: none; }
        .footer-links li { margin-bottom: 12px; }
        .footer-links a { color: #777; text-decoration: none; transition: 0.3s; display: block; }
        .footer-links a:hover { color: #fff; transform: translateX(5px); }
        .payment-methods { display: flex; gap: 15px; font-size: 2rem; margin-top: 15px; color: #444; }
        .footer-bottom { text-align: center; margin-top: 60px; padding-top: 30px; border-top: 1px solid #111; font-size: 0.8rem; display: flex; flex-direction: column; gap: 15px; align-items: center; }
        .legal-links { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }
        .legal-links a { color: #888; text-decoration: none; }
        .legal-links a:hover { color: #fff; text-decoration: underline; }

        /* --- O SEU CHATBOT OFICIAL EXATO --- */
        .wa-widget { position: fixed; bottom: 85px; right: 20px; width: 340px; background: #e5ddd5; border-radius: 12px; z-index: 9999; transform: scale(0); transform-origin: bottom right; transition: 0.3s ease; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .wa-widget.active { transform: scale(1); }
        .wa-header { background: #075e54; color: white; padding: 12px 15px; display: flex; align-items: center; justify-content: space-between; }
        .wa-chat-body { height: 350px; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; background-image: url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png'); background-size: contain; }
        .wa-msg { max-width: 85%; padding: 8px 12px; border-radius: 8px; font-size: 0.88rem; box-shadow: 0 1px 1px rgba(0,0,0,0.15); color: #333; background: white; }
        .float-zap { position: fixed; bottom: 20px; right: 20px; background: #25d366; color: white; width: 65px; height: 65px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; z-index: 10000; cursor: pointer; box-shadow: 0 10px 30px rgba(37,211,102,0.4); }

        @media (max-width: 768px) {
            header { height: 65px; padding: 10px 20px; }
            .logo img { height: 28px; }
            nav, .header-actions { display: none; }
            .leitura-vip h1 { font-size: 1.8rem; }
            .footer-container { grid-template-columns: 1fr; text-align: center; }
            .payment-methods, .footer-links a, .legal-links { justify-content: center; }
            .wa-widget { width: calc(100% - 40px); left: 20px; right: 20px; bottom: 95px; }
        }
    </style>
</head>
<body>

    <div class="promo-bar">🔥 OFERTA RELÂMPAGO: Preços reduzidos por tempo limitado!</div>
    
    <div class="brand-alert">
        <i class="fa-solid fa-shield-check"></i> 
        <span>Atenção: Somos a <strong>Revenda UniTV Oficial</strong>. Garanta a sua segurança original.</span>
    </div>

    <header>
        <div class="logo">
            <a href="../../index.html"><img src="../../img/logo-unitv.png" alt="Logo UniTV Oficial"></a>
        </div>
        <nav>
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

    <main class="leitura-vip">
        <div class="post-header">
            <h1>{titulo}</h1>
            <div class="meta">
                <span><i class="fa-solid fa-calendar"></i> {data_atual}</span>
                <span><i class="fa-solid fa-microchip"></i> Redação Tech UniTV</span>
            </div>
        </div>
        
        <div class="conteudo">
"""

TEMPLATE_RODAPE = """
        </div>
        
        <div class="cta-banner">
            <h3>Pare de passar raiva com travamentos!</h3>
            <p style="color: #bbb; margin-bottom: 20px;">Aproveite o máximo do 4K na sua TV Box. Garanta sua recarga UniTV Oficial com entrega imediata via Pix e suporte humanizado.</p>
            <a href="../../index.html#comprar" class="btn-cta"><i class="fa-solid fa-bolt"></i> VER PLANOS OFICIAIS</a>
        </div>
    </main>

    <footer>
        <div class="footer-container">
            <div class="footer-col">
                <img src="../../img/logo-unitv.png" alt="Logo UniTV Revenda Autorizada" class="footer-logo" loading="lazy">
                <p>Somos revendedores autorizados da plataforma UniTV. Levamos entretenimento premium com qualidade 4K diretamente para a sua casa com suporte de excelência.</p>
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
                    <li><a href="javascript:void(0)" onclick="toggleChat()">Atendimento WhatsApp</a></li>
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
        <div class="footer-bottom">
            <div class="legal-links">
                <a href="#">Política de Privacidade</a>
                <a href="#">Termos de Uso</a>
                <a href="#">Política de Reembolso</a>
            </div>
            <div style="margin-top:10px;">&copy; 2024 - 2026 UniTV Revenda Oficial Autorizada. Todos os direitos reservados.</div>
            <div style="color:#444;">Acesso Digital e Serviços Tecnológicos de Streaming</div>
        </div>
    </footer>

    <div id="chat-widget" class="wa-widget">
        <div class="wa-header">
            <span style="font-weight: 800;">Suporte Blog VIP</span>
            <button onclick="toggleChat()" style="background:none; border:none; color:white; font-size:1.5rem; cursor:pointer;">×</button>
        </div>
        <div class="wa-chat-body" id="chat-content">
            <div class="wa-msg" style="align-self: flex-start; border-top-left-radius: 0;">Olá! 👋 Vi que você está lendo nossos guias de otimização. Quer saber como liberar o sistema VIP completo sem travas na sua Box?</div>
        </div>
        <div style="padding: 10px; background: #f0f0f0;">
            <button onclick="window.open('https://wa.me/5519981765840?text=Vi o post no blog e quero testar o VIP 4K', '_blank')" style="width: 100%; background: #25d366; color: white; border: none; padding: 12px; border-radius: 12px; font-weight: 800; cursor: pointer;">FALAR COM ESPECIALISTA</button>
        </div>
    </div>

    <div class="float-zap" onclick="toggleChat()"><i class="fa-brands fa-whatsapp"></i></div>

    <script>
        function toggleChat() { 
            document.getElementById('chat-widget').classList.toggle('active'); 
        }
    </script>
</body>
</html>
"""

# ==========================================
# 3. LÓGICA E GERAÇÃO DE TEXTO
# ==========================================
def carregar_historico():
    if not os.path.exists(HISTORICO_ARQUIVO): return []
    with open(HISTORICO_ARQUIVO, 'r', encoding='utf-8') as f:
        return [linha.strip() for linha in f.readlines()]

def salvar_historico(tema):
    with open(HISTORICO_ARQUIVO, 'a', encoding='utf-8') as f:
        f.write(f"{tema}\n")

def criar_slug(texto):
    texto_sem_acento = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    slug = re.sub(r'[^a-z0-9]+', '-', texto_sem_acento.lower()).strip('-')
    return slug[:45].strip('-') # Corta a URL para não dar erro 404 de tamanho

def gerar_temas(historico):
    print("🧠 Gerando temas impactantes e CURTOS (Max 8 palavras)...")
    prompt = f"""
    Crie {QTD_POSTS_POR_VEZ} títulos de artigos persuasivos sobre TV Box, IPTV e otimização.
    MUITO IMPORTANTE: Os títulos devem ser BEM CURTOS (máximo de 8 palavras).
    Exemplo: "Otimizar TV Box Android Para Rodar Liso".
    NÃO repita estes temas: {', '.join(historico[-30:])}
    Retorne APENAS os títulos, um por linha.
    """
    try:
        resposta = model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)
        return [t.strip() for t in resposta.text.split('\n') if t.strip()][:QTD_POSTS_POR_VEZ]
    except Exception:
        return ["Guia Definitivo TV Box 4K", "Otimizando a Internet Para Streaming", "Adeus Lag Na Sua TV Box"]

def escrever_artigo(tema):
    print(f"✍️ Escrevendo conteúdo: {tema}")
    prompt_redator = f"""
    Escreva um artigo técnico (800+ palavras) sobre: "{tema}".
    
    REGRA DE FORMATAÇÃO OBRIGATÓRIA:
    1. NÃO coloque tag <h1>.
    2. Use <h2> para subtítulos e <p> para o texto.
    3. Crie 2 blocos de destaque copiando exatamente este HTML:
       <div class="tech-box"><h4>Dica de Ouro</h4><p>escreva a dica aqui.</p></div>
    4. Adicione imagens dinâmicas usando: 
       <img src="https://picsum.photos/seed/{tema.replace(' ', '')}X/800/400" alt="Ilustração"> (mude X para 1, 2 e 3).
    5. Traga dicas de DNS e otimização de rede.
    6. Termine sugerindo assinar a Recarga UniTV.
    """
    try:
        resposta = model.generate_content(prompt_redator, safety_settings=SAFETY_SETTINGS)
        if not resposta.parts:
            prompt_seguro = f"Escreva um texto educativo sobre redes de internet com o tema {tema}. Retorne em HTML."
            resposta = model.generate_content(prompt_seguro, safety_settings=SAFETY_SETTINGS)
        artigo = resposta.text.replace("```html", "").replace("```", "").strip()
        desc = model.generate_content(f"Meta description SEO (150 carac): {tema}", safety_settings=SAFETY_SETTINGS).text.strip()
        return artigo, desc
    except Exception as e:
        raise Exception(f"Erro na IA: {e}")

# ==========================================
# 4. INJETOR NA VITRINE DO BLOG
# ==========================================
def atualizar_pagina_principal_do_blog(titulo, slug, meta_desc):
    caminho = os.path.join(PASTA_BLOG, "index.html")
    try:
        with open(caminho, "r", encoding="utf-8") as f: html = f.read()

        card = f"""
        <a href="{slug}/index.html" class="post-card reveal active" style="text-decoration:none;">
            <div class="post-thumb" style="border-radius:10px; overflow:hidden; margin-bottom:15px;">
                <img src="https://picsum.photos/seed/{slug}/800/600" alt="{titulo}" style="width:100%; display:block; transition:0.3s;">
            </div>
            <div class="post-content">
                <span class="post-tag" style="background:#ff0080; color:#fff; padding:5px 10px; font-size:0.7rem; font-weight:bold; border-radius:4px; margin-bottom:10px; display:inline-block;">NOVIDADE TECH</span>
                <h2 style="color:#fff; font-size:1.3rem; margin-bottom:10px; line-height:1.3;">{titulo}</h2>
                <p style="color:#888; font-size:0.9rem; margin-bottom:15px; line-height:1.5;">{meta_desc}</p>
                <span class="btn-read" style="color:#00ff88; font-weight:bold; font-size:0.9rem;">LER AGORA <i class="fa-solid fa-arrow-right"></i></span>
            </div>
        </a>
        """

        if "" in html:
            html = html.replace("", card)
            with open(caminho, "w", encoding="utf-8") as f: f.write(html)
            print(f"🔗 Injetado com sucesso na vitrine!")
        else: print("⚠️ ERRO: A tag não foi encontrada na capa do blog.")
    except FileNotFoundError: print(f"⚠️ Capa do blog não encontrada.")

# ==========================================
# EXECUTOR FINAL
# ==========================================
print("🚀 MÁQUINA DE SEO CYBERPUNK (VERSÃO MASTER)")
historico = carregar_historico()
temas = gerar_temas(historico)

for tema in temas:
    slug = criar_slug(tema)
    pasta_artigo = os.path.join(PASTA_BLOG, slug)
    
    if os.path.exists(pasta_artigo): continue
    os.makedirs(pasta_artigo, exist_ok=True)
    
    try:
        corpo, meta = escrever_artigo(tema)
        html_final = TEMPLATE_TOPO.replace("{titulo}", tema).replace("{meta_desc}", meta).replace("{data_atual}", datetime.now().strftime("%d/%m/%Y"))
        html_final += corpo + TEMPLATE_RODAPE
        
        with open(os.path.join(pasta_artigo, "index.html"), "w", encoding="utf-8") as f: f.write(html_final)
        atualizar_pagina_principal_do_blog(tema, slug, meta)
        salvar_historico(tema)
        time.sleep(8) 
    except Exception as e: print(f"❌ Erro: {e}")

print("\n📦 Fazendo o Push...")
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", f"Auto-post V-Master: {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
subprocess.run(["git", "push"])
print("✅ DEPLOY CONCLUÍDO! Layout blindado.")
