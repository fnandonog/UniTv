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

# Filtros desativados para não barrar palavras do nicho de TV Box
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# ==========================================
# 2. TEMPLATES BLINDADOS (EXATAMENTE SEU SITE)
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
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
    <meta property="og:locale" content="pt_BR" />
    <meta property="og:type" content="article" />
    <meta property="og:title" content="{titulo}" />
    <meta property="og:description" content="{meta_desc}" />
    <meta property="og:site_name" content="UniTV Oficial Revenda" />
    
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
            --cor-destaque: #ff0080;
        }

        html, body { 
            background-color: var(--bg-body); 
            color: #f0f0f0; 
            overflow-x: hidden; 
            width: 100%;
            max-width: 100vw;
            line-height: 1.6;
            scroll-behavior: smooth;
        }

        /* --- BARRAS DE TOPO --- */
        .promo-bar { background: linear-gradient(90deg, #1a0b2e, #2d0b1e); color: #e0e0e0; text-align: center; padding: 8px 10px; font-size: 0.85rem; font-weight: 500; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .brand-alert { background: rgba(255, 0, 128, 0.05); border-bottom: 1px solid rgba(255, 0, 128, 0.1); color: #ffb3d9; text-align: center; padding: 8px 10px; font-size: 0.75rem; font-weight: 600; letter-spacing: 1px; display: flex; justify-content: center; align-items: center; gap: 10px; }
        .brand-alert strong { color: #fff; text-decoration: underline; }

        /* --- HEADER --- */
        header { display: flex; justify-content: space-between; align-items: center; padding: 10px 5%; position: sticky; top: 0; width: 100%; background: rgba(5, 5, 5, 0.95); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); z-index: 1000; border-bottom: var(--borda-sutil); height: 70px; }
        .logo img { height: 36px; filter: brightness(1.1); transition: 0.3s; }
        .logo img:hover { transform: scale(1.05); }
        nav ul { display: flex; list-style: none; gap: 25px; }
        nav a { color: #bbb; text-decoration: none; font-size: 0.85rem; font-weight: 500; text-transform: uppercase; transition: 0.3s; }
        nav a:hover, nav a.active { color: white; color: var(--cor-destaque); }
        .header-actions { display: flex; align-items: center; gap: 15px; }
        .btn-header { background: rgba(255, 255, 255, 0.1); color: white; padding: 8px 20px; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.1); transition: 0.3s;}
        .btn-header:hover { background: #fff; color: #000; }
        .menu-toggle { display: none; color: white; font-size: 1.6rem; cursor: pointer; outline: none; }

        /* ======================================================== */
        /* --- ESTILOS ISOLADOS PARA O ARTIGO (MUITO IMPORTANTE) ---*/
        /* ======================================================== */
        .post-container { max-width: 800px; margin: 40px auto 80px; padding: 0 20px; }
        
        .post-header { margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .post-title { font-size: clamp(1.8rem, 5vw, 2.5rem) !important; font-weight: 800 !important; line-height: 1.3 !important; margin-bottom: 15px !important; color: #fff !important; text-align: left !important; }
        .text-gradient { background: var(--gradiente-texto); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        
        .post-meta { color: #888; font-size: 0.9rem; font-weight: 500; display: flex; align-items: center; gap: 15px; flex-wrap: wrap; }
        .post-meta i { color: var(--cor-destaque); }

        .post-content { font-size: 1.1rem; color: #ccc; line-height: 1.8; }
        .post-content h2 { color: #fff; font-size: 1.8rem; margin: 50px 0 20px; font-weight: 700; border-left: 4px solid var(--cor-destaque); padding-left: 15px; line-height: 1.3;}
        .post-content h3 { color: #fff; font-size: 1.4rem; margin: 40px 0 15px; font-weight: 600; }
        .post-content p { margin-bottom: 20px; }
        .post-content img { width: 100%; border-radius: 12px; margin: 30px 0; object-fit: cover; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .post-content ul, .post-content ol { margin: 0 0 25px 25px; }
        .post-content li { margin-bottom: 10px; }
        .post-content a { color: var(--cor-destaque); text-decoration: none; font-weight: 600; }
        .post-content a:hover { text-decoration: underline; }
        
        .post-content .tech-box { background: var(--bg-card); border: 1px solid rgba(255,255,255,0.05); border-left: 4px solid #00ff88; padding: 25px; margin: 35px 0; border-radius: 8px; }
        .post-content .tech-box h4 { color: #00ff88; margin-bottom: 10px; font-size: 1.2rem; text-transform: uppercase; letter-spacing: 1px; }
        .post-content .tech-box p { margin-bottom: 0; font-size: 1rem; color: #ddd; }
        
        .post-content blockquote { background: rgba(255, 0, 128, 0.05); font-style: italic; color: #eee; border-left: 4px solid var(--cor-destaque); padding: 20px 30px; margin: 30px 0; font-size: 1.15rem; border-radius: 0 12px 12px 0; }
        /* ======================================================== */

        /* --- FOOTER & WHATSAPP (COPIADO DA SUA HOME) --- */
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
        .wa-options button { background: white; border: 1px solid #ccc; padding: 12px; border-radius: 25px; font-size: 0.9rem; color: #075e54; font-weight: 600; cursor: pointer; text-align: center; width: 100%; transition: 0.3s; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .wa-options button:hover { background: #075e54; color: white; border-color: #075e54; }
        .wa-input-fake { background: #f0f0f0; padding: 12px 20px; display: flex; align-items: center; gap: 15px; border-top: 1px solid #ddd; }
        .wa-input-box { background: white; flex: 1; padding: 10px 20px; border-radius: 25px; color: #999; font-size: 0.9rem; border: 1px solid #ccc; }
        .typing span { height: 8px; width: 8px; background: #bbb; display: inline-block; border-radius: 50%; margin-right: 3px; animation: waTyping 1s infinite; }
        @keyframes waTyping { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
        
        .float-zap { position: fixed; bottom: 25px; right: 25px; background: #25d366; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; z-index: 10000; box-shadow: 0 5px 20px rgba(37, 211, 102, 0.4); cursor: pointer; transition: 0.3s; }
        .float-zap:hover { transform: scale(1.1); }

        @media (max-width: 768px) {
            header { height: 65px; padding: 10px 20px; }
            .logo img { height: 28px; }
            nav, .header-actions { display: none; }
            .post-title { font-size: 1.8rem !important; }
            .footer-container { grid-template-columns: 1fr; text-align: center; }
            .payment-methods, .footer-links a, .legal-links { justify-content: center; }
            .wa-widget { width: calc(100% - 40px); left: 20px; right: 20px; bottom: 95px; max-height: 75vh; }
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

    <main class="post-container">
        <header class="post-header">
            <h1 class="post-title">{titulo}</h1>
            <div class="post-meta">
                <span><i class="fa-solid fa-calendar"></i> {data_atual}</span>
                <span><i class="fa-solid fa-microchip"></i> Redação Tech UniTV</span>
            </div>
        </header>
        
        <article class="post-content">
"""

TEMPLATE_RODAPE = """
        </article>
        
        <div style="background: linear-gradient(160deg, #180a1f 0%, #050505 100%); border: 1px solid var(--cor-destaque); padding: 40px; border-radius: 20px; text-align: center; margin-top: 60px; box-shadow: 0 0 40px rgba(255, 0, 128, 0.15);">
            <h3 style="color:#fff; font-size:1.8rem; margin-bottom:15px; font-weight:800;">Pare de passar raiva com travamentos!</h3>
            <p style="color: #bbb; margin-bottom: 20px;">Aproveite o máximo do 4K na sua TV Box. Garanta sua recarga UniTV Oficial com entrega imediata via Pix e suporte humanizado.</p>
            <a href="../../index.html#comprar" style="background: var(--gradiente-premium); color: white; padding: 18px 45px; border-radius: 50px; text-decoration: none; font-weight: 800; display: inline-block; text-transform: uppercase; letter-spacing: 1px;"><i class="fa-solid fa-bolt"></i> VER PLANOS OFICIAIS</a>
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
            <div class="wa-msg wa-msg-bot">Olá! 👋 Bem-vindo ao suporte oficial UniTV. Sou o atendente virtual focado em vendas e instalação. <span class="wa-time">agora</span></div>
            <div class="wa-msg wa-msg-bot">Sobre o que deseja falar? <span class="wa-time">agora</span></div>
        </div>
        <div id="typing-indicator" class="wa-msg wa-msg-bot typing" style="display: none;"><span></span><span></span><span></span></div>
        <div id="wa-options" class="wa-options">
            <button onclick="window.open('../../index.html#comprar', '_self')">Ver planos disponíveis</button>
            <button onclick="window.open('https://wa.me/5519981765840', '_blank')">Falar com Humano</button>
        </div>
        <div class="wa-input-fake">
            <div class="wa-input-box">Selecione uma opção...</div>
            <i class="fa-solid fa-paper-plane" style="color: #075e54; font-size: 1.2rem;"></i>
        </div>
    </div>

    <div class="float-zap" onclick="toggleChat()" aria-label="Abrir conversa no WhatsApp" role="button" tabindex="0"><i class="fa-brands fa-whatsapp"></i></div>

    <script>
        function toggleChat() { 
            document.getElementById('chat-widget').classList.toggle('active'); 
        }
    </script>
</body>
</html>
"""

# ==========================================
# 3. INTELIGÊNCIA DA IA E GERADOR DE URLS CURTOS
# ==========================================
def carregar_historico():
    if not os.path.exists(HISTORICO_ARQUIVO):
        return []
    with open(HISTORICO_ARQUIVO, 'r', encoding='utf-8') as f:
        return [linha.strip() for linha in f.readlines()]

def salvar_historico(tema):
    with open(HISTORICO_ARQUIVO, 'a', encoding='utf-8') as f:
        f.write(f"{tema}\n")

# CORREÇÃO CRÍTICA DO SLUG: Nomes curtos e sem acentos
def criar_slug(texto):
    texto_sem_acento = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    slug = re.sub(r'[^a-z0-9]+', '-', texto_sem_acento.lower()).strip('-')
    # Corta em 45 caracteres para evitar bug no servidor
    return slug[:45].strip('-')

def gerar_temas(historico):
    print("🧠 Gerando temas impactantes e CURTOS...")
    prompt = f"""
    Crie {QTD_POSTS_POR_VEZ} títulos de artigos persuasivos sobre TV Box, IPTV e otimização.
    MUITO IMPORTANTE: Os títulos devem ser CURTOS (máximo de 8 palavras).
    Exemplo de estilo: "Como Acabar Com Travamentos na Sua TV Box".
    NÃO repita estes temas: {', '.join(historico[-30:])}
    Retorne APENAS os títulos, um por linha.
    """
    try:
        resposta = model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)
        return [t.strip() for t in resposta.text.split('\n') if t.strip()][:QTD_POSTS_POR_VEZ]
    except Exception as e:
        # Título de emergência caso a IA falhe
        return ["Otimizacao de Rede TV Box", "Como Melhorar o Sinal 4K", "Fim do Lag no Streaming"]

def escrever_artigo(tema):
    print(f"✍️ Escrevendo artigo formatado para: {tema}")
    prompt_redator = f"""
    Escreva um artigo de blog técnico e persuasivo (800+ palavras) sobre: "{tema}".
    
    REGRA OBRIGATÓRIA DE HTML (NÃO QUEBRE O LAYOUT):
    1. NÃO coloque a tag <h1>.
    2. Use <h2> para subtítulos principais.
    3. Crie 2 blocos de destaque copiando exatamente este HTML:
       <div class="tech-box"><h4>Dica de Ouro</h4><p>escreva uma dica forte aqui.</p></div>
    4. Adicione imagens dinâmicas usando: 
       <img src="https://picsum.photos/seed/{tema.replace(' ', '')}X/800/400" alt="Tecnologia"> (mude o X para 1, 2 e 3).
    5. Use blocos <blockquote> para citações importantes.
    6. Traga dados de performance. Fale sobre DNS e otimização de rede.
    7. Termine oferecendo a Recarga UniTV Oficial como solução premium.
    """
    
    try:
        resposta_artigo = model.generate_content(prompt_redator, safety_settings=SAFETY_SETTINGS)
        if not resposta_artigo.parts:
            print("⚠️ Aviso: Filtro bloqueou o texto principal. Tentando versão segura...")
            prompt_seguro = f"Escreva um guia educativo sobre redes de internet focado em {tema}. Retorne em HTML simples."
            resposta_artigo = model.generate_content(prompt_seguro, safety_settings=SAFETY_SETTINGS)
            
        artigo_html = resposta_artigo.text.replace("```html", "").replace("```", "").strip()
    except Exception as e:
        raise Exception(f"Erro na IA ao gerar artigo: {e}")
    
    prompt_meta = f"Crie uma meta description (max 150 caracteres) para: {tema}."
    meta_desc = model.generate_content(prompt_meta, safety_settings=SAFETY_SETTINGS).text.strip()
    
    return artigo_html, meta_desc

# ==========================================
# 4. INJETOR CORRIGIDO (SEM SUBSTITUIR VAZIO)
# ==========================================
def atualizar_pagina_principal_do_blog(titulo, slug, meta_desc):
    caminho_index = os.path.join(PASTA_BLOG, "index.html")
    
    try:
        with open(caminho_index, "r", encoding="utf-8") as f:
            html = f.read()

        novo_card = f"""
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

        # Agora a substituição é super segura!
        if "" in html:
            html = html.replace("", novo_card)
            with open(caminho_index, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"🔗 Artigo '{titulo}' linkado com sucesso na vitrine!")
        else:
            print("⚠️ ERRO: A tag sumiu do blog/index.html")

    except FileNotFoundError:
        print(f"⚠️ O arquivo {caminho_index} não existe ainda.")

# ==========================================
# EXECUTOR
# ==========================================
print("🚀 MÁQUINA DE SEO CYBERPUNK INICIADA (V-MASTER)")
historico = carregar_historico()
temas = gerar_temas(historico)

for tema in temas:
    slug = criar_slug(tema)
    pasta_artigo = os.path.join(PASTA_BLOG, slug)
    
    if os.path.exists(pasta_artigo):
        print(f"⏩ Pulando '{tema}', a pasta já existe.")
        continue
        
    os.makedirs(pasta_artigo, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_artigo, "index.html")
    
    try:
        conteudo_html, meta_desc = escrever_artigo(tema)
        data_formatada = datetime.now().strftime("%d de %B de %Y")
        
        # Monta a página inteira blindada
        pagina_final = TEMPLATE_TOPO.replace("{titulo}", tema).replace("{meta_desc}", meta_desc).replace("{data_atual}", data_formatada)
        pagina_final += conteudo_html
        pagina_final += TEMPLATE_RODAPE
        
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(pagina_final)
        
        atualizar_pagina_principal_do_blog(tema, slug, meta_desc)
        salvar_historico(tema)
        
        print("⏳ Aguardando a IA respirar para evitar bloqueios...")
        time.sleep(8) 
    except Exception as e:
        print(f"❌ Erro grave ao gerar {tema}: {e}")

print("\n📦 Fazendo o Push Automático para o GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Auto-post V-Master: {datetime.now().strftime('%Y-%m-%d %H:%M')}"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ DEPLOY CONCLUÍDO! O site está no ar e com visual premium.")
except Exception as e:
    print("⚠️ Erro no Git Push. Faça o 'git pull' antes de tentar rodar novamente se o GitHub recusar o envio.")
