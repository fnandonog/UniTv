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
# 1. CONFIGURAÇÕES DA MÁQUINA
# ==========================================
GEMINI_KEY = "AIzaSyCmT5HHUpHsXbtN68h6bpkRIzFpjIy2RGs"
TMDB_KEY = "9cb2f018163da4a3f89d718ee6be8677"
MODEL_ID = 'gemini-2.0-flash' 

QTD_FILMES_POR_VEZ = 3
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
# 2. TEMPLATE GIGANTE DA RESENHA VIP
# ==========================================
TEMPLATE_RESENHA = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>[TITULO] | Resenha Completa e Onde Assistir | UniTV Oficial</title>
    <meta name="description" content="Descubra os bastidores, elenco e análise do filme [TITULO]. Assista agora mesmo em 4K nativo na sua TV Box com a UniTV.">
    <meta name="theme-color" content="#050505">
    
    <meta name="referrer" content="no-referrer">
    
    <link rel="canonical" href="https://unitvsite.com.br/cinema/" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&family=Montserrat:wght@800;900&display=swap" rel="stylesheet">
    <link rel="icon" href="../../img/logo-unitv.png" type="image/png">

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        :root { --bg-body: #050505; --bg-card: #0a0a0a; --neon-azul: #00f3ff; --neon-laranja: #ff7300; --gradiente-premium: linear-gradient(135deg, #FF512F 0%, #DD2476 100%); --borda-sutil: 1px solid rgba(255, 255, 255, 0.08); --wa-header: #075e54; --wa-bg: #e5ddd5; --wa-msg-user: #dcf8c6; }
        html, body { background-color: var(--bg-body); color: #f0f0f0; overflow-x: hidden; scroll-behavior: smooth; }
        ::-webkit-scrollbar { width: 10px; } ::-webkit-scrollbar-track { background: var(--bg-body); } ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; } ::-webkit-scrollbar-thumb:hover { background: var(--neon-laranja); }
        
        .promo-bar { background: linear-gradient(90deg, #1a0b2e, #2d0b1e); color: #e0e0e0; text-align: center; padding: 10px; font-size: 0.85rem; font-weight: 600; position: fixed; top: 0; width: 100%; z-index: 2000; border-bottom: 1px solid rgba(255,255,255,0.05); } .promo-bar span { color: #ff0055; font-weight: 800; }
        header { display: flex; justify-content: space-between; align-items: center; padding: 10px 5%; position: fixed; width: 100%; top: 38px; background: rgba(5, 5, 5, 0.85); backdrop-filter: blur(15px); z-index: 1000; border-bottom: var(--borda-sutil); height: 75px; transition: 0.4s; }
        .logo img { height: 40px; filter: brightness(1.2); }
        .nav-links { display: flex; gap: 25px; list-style: none; } .nav-links a { color: #bbb; text-decoration: none; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; transition: 0.3s; } .nav-links a:hover { color: #fff; } 
        .btn-header { background: var(--gradiente-premium); color: white; padding: 10px 25px; border-radius: 50px; text-decoration: none; font-size: 0.75rem; font-weight: 800; box-shadow: 0 4px 15px rgba(221, 36, 118, 0.3); transition: 0.3s; }

        .movie-hero { height: 75vh; width: 100%; position: relative; margin-top: 38px; }
        .hero-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, var(--bg-body) 0%, rgba(5,5,5,0.8) 50%, rgba(5,5,5,0.3) 100%); display: flex; align-items: flex-end; padding: 0 5% 50px; }
        .btn-voltar { position: absolute; top: 30px; left: 5%; background: rgba(0,0,0,0.5); color: #fff; padding: 10px 20px; border-radius: 50px; text-decoration: none; font-weight: 700; font-size: 0.9rem; border: 1px solid rgba(255,255,255,0.2); backdrop-filter: blur(5px); z-index: 10; transition: 0.3s; } .btn-voltar:hover { background: var(--neon-laranja); border-color: var(--neon-laranja); }
        
        .hero-info { max-width: 1000px; display: flex; gap: 40px; align-items: flex-end; }
        .hero-poster { width: 220px; border-radius: 12px; box-shadow: 0 20px 50px rgba(0,0,0,0.8); border: 1px solid rgba(255,255,255,0.1); }
        .hero-text h1 { font-family: 'Montserrat', sans-serif; font-size: clamp(2.5rem, 5vw, 4.5rem); line-height: 1; color: #fff; text-transform: uppercase; font-weight: 900; margin-bottom: 15px; text-shadow: 2px 2px 20px rgba(0,0,0,0.8); }
        .hero-tags { display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 20px; }
        .hero-tags span { background: rgba(255,255,255,0.1); padding: 5px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: 700; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(5px); }
        .hero-tags .nota { color: #ffcc00; border-color: rgba(255,204,0,0.4); background: rgba(0,0,0,0.6); }
        .hero-tags .quatrok { background: var(--gradiente-premium); color: #fff; border: none; }

        .content-wrapper { max-width: 1400px; margin: 50px auto; padding: 0 5%; display: grid; grid-template-columns: 1fr 350px; gap: 60px; align-items: start; }
        .main-article { font-size: 1.15rem; line-height: 1.8; color: #ccc; }
        .main-article h2 { color: #fff; margin: 40px 0 20px; font-size: 2rem; font-weight: 800; border-bottom: 2px solid rgba(255, 115, 0, 0.3); padding-bottom: 10px; display: inline-block; }
        .main-article p { margin-bottom: 25px; }
        .main-article blockquote { background: rgba(255, 115, 0, 0.05); border-left: 4px solid var(--neon-laranja); padding: 25px; margin: 30px 0; font-size: 1.2rem; font-style: italic; border-radius: 0 12px 12px 0; color: #eee; }
        .mid-backdrop { width: 100%; border-radius: 16px; margin: 30px 0; border: 1px solid #222; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }

        .sidebar { background: #0a0a0a; border: 1px solid #1a1a1a; padding: 30px; border-radius: 16px; position: sticky; top: 130px; }
        .sidebar h3 { color: #fff; font-size: 1.3rem; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #222; }
        .ficha-item { margin-bottom: 20px; }
        .ficha-item span { display: block; font-size: 0.8rem; color: #777; text-transform: uppercase; font-weight: 700; margin-bottom: 5px; }
        .ficha-item strong { display: block; color: #ddd; font-size: 1rem; }
        .ficha-item .elenco-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 5px; }
        .ficha-item .elenco-tags div { background: #151515; padding: 5px 10px; border-radius: 4px; font-size: 0.85rem; border: 1px solid #222; color: #bbb; }

        .about-unitv { padding: 100px 5%; background: radial-gradient(circle at right bottom, #1a0525 0%, #050505 60%); border-top: 1px solid #111; margin-top: 50px; }
        .about-grid { display: grid; grid-template-columns: 1fr 1fr; align-items: center; gap: 60px; max-width: 1300px; margin: 0 auto; }
        .about-text h2 { font-size: 2.8rem; font-weight: 900; line-height: 1.1; margin-bottom: 20px; color: #fff; } .about-text h2 span { background: var(--gradiente-premium); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .about-text p { color: #aaa; font-size: 1.1rem; line-height: 1.7; margin-bottom: 30px; }
        .about-features { list-style: none; margin-bottom: 40px; } .about-features li { display: flex; align-items: center; gap: 15px; color: #ddd; font-size: 1.05rem; font-weight: 600; margin-bottom: 15px; } .about-features i { color: #00ff88; font-size: 1.3rem; }
        .btn-cta-about { background: var(--gradiente-premium); color: white; padding: 18px 45px; border-radius: 50px; font-size: 1.1rem; font-weight: 800; text-decoration: none; display: inline-flex; align-items: center; gap: 12px; transition: 0.4s; box-shadow: 0 10px 30px -5px rgba(221, 36, 118, 0.4); text-transform: uppercase; letter-spacing: 1px; } .btn-cta-about:hover { transform: translateY(-5px); box-shadow: 0 15px 35px -5px rgba(221, 36, 118, 0.6); }
        .about-img img { width: 100%; filter: drop-shadow(0 20px 40px rgba(0,0,0,0.8)); transform: perspective(1000px) rotateY(-15deg); transition: 0.5s; } .about-grid:hover .about-img img { transform: perspective(1000px) rotateY(0deg); }

        footer { background: #050505; border-top: 1px solid #1a1a1a; padding: 80px 20px 40px; color: #777; font-size: 0.9rem; }
        .footer-container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr; gap: 50px; }
        .footer-logo { margin-bottom: 20px; filter: brightness(1.2); height: 40px; }
        .footer-col h4 { color: #fff; margin-bottom: 25px; font-size: 0.9rem; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; }
        .footer-links { list-style: none; } .footer-links li { margin-bottom: 12px; }
        .footer-links a { color: #777; text-decoration: none; transition: 0.3s; display: flex; align-items: center; gap: 8px; } .footer-links a:hover { color: #fff; transform: translateX(5px); }
        .payment-methods { display: flex; gap: 15px; font-size: 2rem; margin-top: 15px; color: #444; }
        .footer-bottom { text-align: center; margin-top: 60px; padding-top: 30px; border-top: 1px solid #111; font-size: 0.8rem; display: flex; flex-direction: column; gap: 15px; align-items: center; }
        .legal-links { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; } .legal-links a { color: #888; text-decoration: none; } .legal-links a:hover { color: #fff; text-decoration: underline; }

        .wa-widget { position: fixed; bottom: 90px; right: 25px; width: 350px; background: var(--wa-bg); border-radius: 16px; z-index: 9999; box-shadow: 0 15px 35px rgba(0,0,0,0.4); display: flex; flex-direction: column; overflow: hidden; transform: scale(0); transform-origin: bottom right; transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
        .wa-widget.active { transform: scale(1); }
        .wa-header { background: var(--wa-header); color: white; padding: 15px 20px; display: flex; align-items: center; justify-content: space-between; }
        .wa-profile { display: flex; align-items: center; gap: 12px; } .wa-profile img { width: 42px; height: 42px; border-radius: 50%; background: #fff; padding: 2px; }
        .wa-info { display: flex; flex-direction: column; } .wa-name { font-weight: 600; font-size: 1rem; } .wa-status { font-size: 0.75rem; color: #cfd8dc; display: flex; align-items: center; gap: 5px;} .wa-status::before { content:''; display:inline-block; width:8px; height:8px; background:#00ff88; border-radius:50%; }
        .wa-close { background: none; border: none; color: white; font-size: 1.8rem; cursor: pointer; transition: 0.3s; outline: none; } .wa-close:hover { color: #ffcccc; transform: rotate(90deg); }
        .wa-chat-body { height: 380px; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; background-image: url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png'); background-size: contain; }
        .wa-msg { max-width: 85%; padding: 10px 15px; border-radius: 12px; font-size: 0.9rem; position: relative; box-shadow: 0 2px 5px rgba(0,0,0,0.1); line-height: 1.4; color: #333; }
        .wa-msg-bot { background: white; align-self: flex-start; border-top-left-radius: 0; } .wa-msg-user { background: var(--wa-msg-user); align-self: flex-end; border-top-right-radius: 0; }
        .wa-time { font-size: 0.65rem; color: #999; display: block; text-align: right; margin-top: 5px; }
        .wa-options { padding: 15px; background: #f0f0f0; border-top: 1px solid #ddd; display: flex; flex-direction: column; gap: 10px; }
        .wa-options button { background: white; border: 1px solid #ccc; padding: 12px; border-radius: 25px; font-size: 0.9rem; color: #075e54; font-weight: 600; cursor: pointer; text-align: center; width: 100%; transition: 0.3s; box-shadow: 0 2px 5px rgba(0,0,0,0.05); } .wa-options button:hover { background: #075e54; color: white; border-color: #075e54; }
        .wa-input-fake { background: #f0f0f0; padding: 12px 20px; display: flex; align-items: center; gap: 15px; border-top: 1px solid #ddd; } .wa-input-box { background: white; flex: 1; padding: 10px 20px; border-radius: 25px; color: #999; font-size: 0.9rem; border: 1px solid #ccc; }
        .typing span { height: 8px; width: 8px; background: #bbb; display: inline-block; border-radius: 50%; margin-right: 3px; animation: waTyping 1s infinite; } @keyframes waTyping { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
        .float-zap { position: fixed; bottom: 25px; right: 25px; background: #25d366; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; z-index: 10000; box-shadow: 0 5px 20px rgba(37, 211, 102, 0.4); cursor: pointer; transition: 0.3s; } .float-zap:hover { transform: scale(1.1); }

        @media (max-width: 992px) { .content-wrapper { grid-template-columns: 1fr; } .hero-info { flex-direction: column; align-items: center; text-align: center; } .hero-tags { justify-content: center; } .about-grid { grid-template-columns: 1fr; text-align: center; } .about-features li { justify-content: center; } }
        @media (max-width: 768px) { header { padding: 10px 20px; } .nav-links { display: none; } .hero-text h1 { font-size: 2.2rem; } .footer-container { grid-template-columns: 1fr; text-align: center; } .footer-links a { justify-content: center; } .payment-methods { justify-content: center; } .wa-widget { width: calc(100% - 40px); left: 20px; right: 20px; bottom: 95px; max-height: 75vh; } }
    </style>
</head>
<body>

    <div class="promo-bar">⚡ SINAL LIBERADO: Assista a todos os lançamentos do cinema em 4K. <span>Aproveite o VIP!</span></div>

    <header id="main-header">
        <div class="logo"><a href="../../index.html"><img src="../../img/logo-unitv.png" alt="UniTV Oficial"></a></div>
        <nav class="nav-links">
            <a href="../../index.html">Início</a>
            <a href="../../baixar/index.html">Downloads</a>
            <a href="../../blog/index.html">Blog Tech</a>
            <a href="../index.html">Catálogo VIP</a>
        </nav>
        <a href="../../index.html#comprar" class="btn-header"><i class="fa-solid fa-crown"></i> ASSINAR VIP</a>
    </header>

    <div class="movie-hero" style="background: url('[BACKDROP_PRINCIPAL]') center top / cover no-repeat;">
        <div class="hero-overlay">
            <a href="../index.html" class="btn-voltar"><i class="fa-solid fa-arrow-left"></i> Voltar ao Catálogo</a>
            <div class="hero-info">
                <img src="[POSTER_URL]" alt="[TITULO]" class="hero-poster">
                <div class="hero-text">
                    <h1>[TITULO]</h1>
                    <div class="hero-tags">
                        <span class="nota"><i class="fa-solid fa-star"></i> [NOTA]</span>
                        <span>[ANO]</span>
                        <span>[DURACAO]</span>
                        <span class="quatrok">4K UHD</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="content-wrapper">
        <main class="main-article">
            [RESENHA_HTML]
            <img src="[BACKDROP_SECUNDARIO]" alt="Cena do Filme" class="mid-backdrop" onerror="this.style.display='none'">
        </main>
        
        <aside class="sidebar">
            <h3>Ficha Técnica Oficial</h3>
            <div class="ficha-item">
                <span>Gêneros</span>
                <strong>[GENEROS]</strong>
            </div>
            <div class="ficha-item">
                <span>Direção</span>
                <strong>[DIRETOR]</strong>
            </div>
            <div class="ficha-item">
                <span>Elenco Principal</span>
                <div class="elenco-tags">
                    [ELENCO_HTML]
                </div>
            </div>
            <div class="ficha-item" style="margin-top: 30px;">
                <a href="../../index.html#comprar" style="display: block; text-align: center; background: var(--gradiente-premium); color: #fff; text-decoration: none; padding: 15px; border-radius: 8px; font-weight: 800; font-size: 1rem;"><i class="fa-solid fa-play"></i> LIBERAR ACESSO</a>
            </div>
        </aside>
    </div>

    <section class="about-unitv">
        <div class="about-grid">
            <div class="about-text">
                <h2>Muito mais que apenas <span>Cinema</span></h2>
                <p>A <strong>UniTV Oficial</strong> é a sua central de entretenimento definitiva. Além de um catálogo VOD colossal atualizado diariamente com os maiores sucessos do cinema, você transforma a sua TV Box ou Smartphone numa verdadeira máquina de diversão.</p>
                <ul class="about-features">
                    <li><i class="fa-solid fa-check"></i> <strong>Canais de TV ao Vivo:</strong> Esportes, Notícias e Variedades.</li>
                    <li><i class="fa-solid fa-check"></i> <strong>Sem Travamentos:</strong> Servidores P2P de altíssima velocidade.</li>
                    <li><i class="fa-solid fa-check"></i> <strong>Sistema Multi-Telas:</strong> Assista na TV e no Celular simultaneamente.</li>
                </ul>
                <a href="../../index.html#comprar" class="btn-cta-about"><i class="fa-solid fa-rocket"></i> Conheça os Planos e Assine Agora</a>
            </div>
            <div class="about-img">
                <img src="../../img/hero-tv.png" alt="Interface da UniTV Oficial">
            </div>
        </div>
    </section>

    <footer>
        <div class="footer-container">
            <div class="footer-col">
                <img src="../../img/logo-unitv.png" alt="Logo UniTV Revenda Autorizada" class="footer-logo" loading="lazy">
                <p class="footer-desc">Somos revendedores autorizados da plataforma UniTV. Levamos entretenimento premium com qualidade 4K diretamente para a sua casa com suporte de excelência.</p>
                <div style="display: flex; align-items: center; gap: 10px; color: #fff; font-weight: bold; margin-top: 15px;"><i class="fa-solid fa-shield-halved" style="color:#00ff88"></i> Conexão 100% Segura</div>
            </div>
            <div class="footer-col">
                <h4>Acesso Rápido</h4>
                <ul class="footer-links">
                    <li><a href="../../index.html#comprar"><i class="fa-solid fa-angle-right"></i> Planos e Recargas</a></li>
                    <li><a href="../../tutorial/index.html"><i class="fa-solid fa-angle-right"></i> Guia de Instalação</a></li>
                    <li><a href="../../blog/index.html"><i class="fa-solid fa-angle-right"></i> Blog de Tecnologia</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Suporte Dedicado</h4>
                <ul class="footer-links">
                    <li><a href="../../ajuda/index.html"><i class="fa-solid fa-angle-right"></i> Central de Ajuda (FAQ)</a></li>
                    <li><a href="javascript:void(0)" onclick="toggleChat()"><i class="fa-solid fa-angle-right"></i> Atendimento WhatsApp</a></li>
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
            <div class="legal-links"><a href="#">Política de Privacidade</a><a href="#">Termos de Uso</a><a href="#">Política de Reembolso</a></div>
            <div>&copy; 2026 UniTV Revenda Oficial Autorizada. Todos os direitos reservados.</div>
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
            <button onclick="userAction('Quero assinar / ver planos', 'preco')">Ver planos disponíveis</button>
            <button onclick="userAction('Funciona na minha Smart TV?', 'smart_tv_select')">Minha TV é Samsung/LG</button>
            <button onclick="userAction('Como instalar o app?', 'pre_download')">Dúvidas sobre Instalação</button>
            <button onclick="userAction('Comprei e não chegou', 'atraso_codigo')">Comprei e o código não chegou</button>
        </div>
        <div class="wa-input-fake">
            <div class="wa-input-box">Selecione uma opção...</div>
            <i class="fa-solid fa-paper-plane" style="color: #075e54; font-size: 1.2rem;"></i>
        </div>
    </div>

    <div class="float-zap" onclick="toggleChat()" aria-label="Abrir conversa no WhatsApp" role="button" tabindex="0"><i class="fa-brands fa-whatsapp"></i></div>

    <script>
        window.addEventListener('scroll', () => {
            const header = document.getElementById('main-header');
            if (window.scrollY > 50) { header.classList.add('scrolled'); } else { header.classList.remove('scrolled'); }
        });

        function toggleChat() { document.getElementById('chat-widget').classList.toggle('active'); }
        function showTyping(callback) {
            const status = document.getElementById('wa-status'), typing = document.getElementById('typing-indicator'), content = document.getElementById('chat-content');
            status.innerText = "Digitando..."; typing.style.display = "block"; content.appendChild(typing); content.scrollTop = content.scrollHeight;
            setTimeout(() => { typing.style.display = "none"; status.innerText = "Online"; callback(); }, 1200);
        }
        function addMessage(text, side) {
            const content = document.getElementById('chat-content'), now = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}), checks = side === 'user' ? ' <i class="fa-solid fa-check-double" style="color:#34b7f1; font-size: 0.7rem"></i>' : '';
            content.innerHTML += `<div class="wa-msg wa-msg-${side}">${text}<span class="wa-time">${now}${checks}</span></div>`;
            content.scrollTop = content.scrollHeight;
        }
        function setOptions(options) {
            const container = document.getElementById('wa-options'); container.innerHTML = "";
            options.forEach(opt => { const btn = document.createElement('button'); btn.innerText = opt.label; btn.onclick = () => userAction(opt.label, opt.type); container.appendChild(btn); });
        }
        
        function userAction(text, type) {
            addMessage(text, 'user'); setOptions([]);
            showTyping(() => {
                if(type === 'preco') {
                    addMessage("<strong>Planos Oficiais Sem Mensalidade:</strong><br><br>💳 <a href='https://pay.kirvano.com/07f96a4e-ecdf-4538-83ca-01e5c35f1425' target='_blank' rel='noopener noreferrer'><strong>PLANO 30 DIAS (R$ 24,90)</strong></a><br>🚀 <a href='https://pay.kirvano.com/0aadf253-f4b6-47dd-8d0a-f5f16714ce98' target='_blank' rel='noopener noreferrer'><strong>ANUAL VIP (R$ 189,90)</strong></a>", 'bot');
                    setOptions([{label: 'Já fiz o pagamento', type: 'pix_feito'}, {label: 'Quero testar antes', type: 'suporte_humano'}]);
                } else if(type === 'pix_feito') {
                    addMessage("Perfeito! Se você pagou via Pix, o código é enviado automaticamente em menos de 1 minuto para o seu WhatsApp e E-mail. Olhe a caixa de SPAM.", 'bot'); 
                    setOptions([{label: 'Não recebi ainda', type: 'atraso_codigo'}, {label: 'Voltar ao início', type: 'reset'}]);
                } else if(type === 'atraso_codigo') {
                    addMessage("Vou te transferir para um especialista da equipe. Tenha o comprovante em mãos.", 'bot');
                    const btn = document.createElement('button'); btn.innerText = "Falar com Humano"; btn.style.background = "#25d366"; btn.style.color = "white"; btn.onclick = () => window.open("https://wa.me/5519981765840?text=Comprei e meu código não chegou, segue o comprovante:", '_blank', 'noopener,noreferrer'); document.getElementById('wa-options').appendChild(btn);
                } else if(type === 'smart_tv_select') {
                    addMessage("Nessas marcas (LG/Samsung) o UniTV não roda direito. Para não travar, instalamos um app parceiro chamado <strong>ULTRA PLAYER</strong>.", 'bot');
                    setTimeout(() => showTyping(() => { 
                        addMessage("Vá na loja de apps da sua TV e pesquise por 'Ultra Player'.", 'bot'); 
                        setOptions([{label: 'Baixei, e agora?', type: 'baixou_ultra'}, {label: 'Não achei', type: 'suporte_humano'}]); 
                    }), 1500);
                } else if(type === 'baixou_ultra') {
                    addMessage("Ótimo. Abra o app, tire foto do código MAC na tela e me envie no WhatsApp humano para eu liberar.", 'bot');
                    const btn = document.createElement('button'); btn.innerText = "ENVIAR FOTO DO MAC"; btn.style.background = "#25d366"; btn.style.color = "white"; btn.onclick = () => window.open("https://wa.me/5519981765840?text=Baixei o Ultra Player na Smart TV, foto do MAC:", '_blank', 'noopener,noreferrer'); document.getElementById('wa-options').appendChild(btn);
                } else if(type === 'pre_download') {
                    addMessage("A instalação é simples! Em TV Box ou Firestick, use o app Downloader e digite o código <strong>867283</strong>.", 'bot'); 
                    setTimeout(() => showTyping(() => { 
                        addMessage("Para Android de celular, use nosso link oficial: <a href='http://mkdw.qrdldunitvss.com/download' target='_blank' rel='noopener noreferrer'>Baixar APK Mobile</a>", 'bot'); 
                        setOptions([{label: 'Instalado. Quero assinar!', type: 'preco'}, {label: 'Deu erro', type: 'suporte_humano'}]); 
                    }), 1500);
                } else if(type === 'suporte_humano') {
                    addMessage("Ok, vou abrir o chat com nosso time humano de suporte técnico.", 'bot');
                    const btn = document.createElement('button'); btn.innerText = "Conversar no WhatsApp"; btn.style.background = "#25d366"; btn.style.color = "white"; btn.onclick = () => window.open("https://wa.me/5519981765840?text=Preciso de atendimento humano VIP", '_blank', 'noopener,noreferrer'); document.getElementById('wa-options').appendChild(btn);
                } else if(type === 'reset') {
                    addMessage("Como mais posso te ajudar a garantir sua diversão?", 'bot'); 
                    setOptions([{label: 'Ver Planos', type: 'preco'}, {label: 'Instalação', type: 'pre_download'}, {label: 'Atendimento Humano', type: 'suporte_humano'}]);
                }
            });
        }
    </script>
</body>
</html>"""

# ==========================================
# 3. LÓGICA TMDB E GEMINI
# ==========================================
def carregar_historico():
    if not os.path.exists(HISTORICO_CINE): return []
    with open(HISTORICO_CINE, 'r', encoding='utf-8') as f:
        return [l.strip() for l in f.readlines() if l.strip()]

def criar_slug(texto):
    txt = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r'[^a-z0-9]+', '-', txt.lower()).strip('-')

def buscar_filmes_em_alta():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_KEY}&language=pt-BR"
    print("🎬 Buscando lançamentos no TMDB...")
    res = requests.get(url)
    if res.status_code == 200:
        return res.json().get('results', [])
    return []

def buscar_detalhes_do_filme(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_KEY}&language=pt-BR&append_to_response=credits,images&include_image_language=pt,en,null"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    return None

def formatar_tempo(minutos):
    if not minutos: return "Desconhecido"
    h = minutos // 60
    m = minutos % 60
    return f"{h}h {m}m"

def escrever_resenha_gemini(dados_completos):
    titulo = dados_completos.get('title', 'Filme')
    sinopse = dados_completos.get('overview', '')
    nota = round(dados_completos.get('vote_average', 0), 1)
    
    prompt = f"""
    Aja como o crítico de cinema oficial do portal UniTV VIP. Escreva uma super resenha envolvente sobre o filme: "{titulo}".
    Sinopse oficial: {sinopse}.
    Nota atual do público: {nota}/10.
    
    Escreva a resposta APENAS em formato HTML, sem a tag ```html e sem markdown. 
    Use tags <p>, <blockquote> (para destacar a melhor coisa do filme), e obrigatoriamente crie as seguintes 4 seções usando a tag <h2>:
    <h2>A Trama</h2> (Desenvolva a história sem spoilers)
    <h2>Por Trás das Câmeras</h2> (Invente ou conte 2 curiosidades de bastidores e efeitos práticos que justifiquem a superprodução)
    <h2>Público-Alvo e Análise da Nota ({nota}/10)</h2> (Explique por que recebeu essa nota e para que tipo de fã é recomendado)
    <h2>Por que assistir em 4K na UniTV?</h2> (Venda a experiência de assistir na TV Box sem travamentos e com áudio cristalino)
    """
    
    try:
        print(f"✍️ Gemini escrevendo Super Resenha de: {titulo}...")
        res = client.models.generate_content(model=MODEL_ID, contents=prompt, config=CONFIG_GERAL)
        return res.text.replace("```html", "").replace("```", "").strip()
    except Exception as e:
        print(f"⚠️ Erro IA: {e}")
        return f"<p>{sinopse}</p><p>Assista agora na sua TV Box 4K.</p>"

def injetar_card_na_vitrine(filme, slug):
    caminho = os.path.join(PASTA_CINEMA, "index.html")
    alvo = '<main class="movie-catalog" id="movieCatalog">'
    
    titulo = filme['title']
    nota = round(filme['vote_average'], 1)
    ano = filme['release_date'][:4] if 'release_date' in filme else "2024"
    poster_url = f"[https://image.tmdb.org/t/p/w500](https://image.tmdb.org/t/p/w500){filme['poster_path']}"
    
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
        </a>"""
    
    try:
        with open(caminho, "r", encoding="utf-8") as f: html = f.read()
        if alvo in html:
            html = html.replace(alvo, alvo + "\n" + card)
            with open(caminho, "w", encoding="utf-8") as f: f.write(html)
            print(f"🔗 Vitrine atualizada com '{titulo}'.")
    except Exception as e:
        print(f"⚠️ Erro ao salvar vitrine: {e}")

# ==========================================
# EXECUTOR DO CINEMA VIP
# ==========================================
print("🚀 MOTOR DE CINEMA VIP ATIVADO")
historico = carregar_historico()
filmes = buscar_filmes_em_alta()

processados = 0
for filme in filmes:
    if processados >= QTD_FILMES_POR_VEZ: break
    
    titulo = filme['title']
    slug = criar_slug(titulo)
    
    if slug in historico or not filme.get('poster_path') or not filme.get('backdrop_path'):
        continue
        
    detalhes = buscar_detalhes_do_filme(filme['id'])
    if not detalhes: continue

    pasta_filme = os.path.join(PASTA_CINEMA, slug)
    os.makedirs(pasta_filme, exist_ok=True)
    
    nota_str = str(round(filme['vote_average'], 1))
    ano_str = filme['release_date'][:4] if 'release_date' in filme else "Lançamento"
    duracao_str = formatar_tempo(detalhes.get('runtime', 0))
    generos_str = ", ".join([g['name'] for g in detalhes.get('genres', [])][:3])
    
    diretor_str = "Desconhecido"
    elenco_html = "<div>Desconhecido</div>"
    if 'credits' in detalhes:
        crew = detalhes['credits'].get('crew', [])
        diretores = [c['name'] for c in crew if c['job'] == 'Director']
        if diretores: diretor_str = diretores[0]
        
        cast = detalhes['credits'].get('cast', [])[:3]
        if cast: elenco_html = "".join([f"<div>{ator['name']}</div>" for ator in cast])

    # Voltando para o link oficial da API do TMDB que funciona
    bg_principal = f"[https://image.tmdb.org/t/p/original](https://image.tmdb.org/t/p/original){filme['backdrop_path']}"
    bg_secundario = bg_principal
    if 'images' in detalhes and 'backdrops' in detalhes['images']:
        bgs = [b['file_path'] for b in detalhes['images']['backdrops'] if b['file_path'] != filme['backdrop_path']]
        if bgs: bg_secundario = f"[https://image.tmdb.org/t/p/w1280](https://image.tmdb.org/t/p/w1280){bgs[0]}"

    poster_principal = f"[https://image.tmdb.org/t/p/w500](https://image.tmdb.org/t/p/w500){filme['poster_path']}"
    
    corpo_resenha = escrever_resenha_gemini(detalhes)
    
    html_final = TEMPLATE_RESENHA
    html_final = html_final.replace("[TITULO]", titulo)
    html_final = html_final.replace("[BACKDROP_PRINCIPAL]", bg_principal)
    html_final = html_final.replace("[BACKDROP_SECUNDARIO]", bg_secundario)
    html_final = html_final.replace("[POSTER_URL]", poster_principal)
    html_final = html_final.replace("[NOTA]", nota_str)
    html_final = html_final.replace("[ANO]", ano_str)
    html_final = html_final.replace("[DURACAO]", duracao_str)
    html_final = html_final.replace("[GENEROS]", generos_str)
    html_final = html_final.replace("[DIRETOR]", diretor_str)
    html_final = html_final.replace("[ELENCO_HTML]", elenco_html)
    html_final = html_final.replace("[RESENHA_HTML]", corpo_resenha)
    
    with open(os.path.join(pasta_filme, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_final)
        
    injetar_card_na_vitrine(filme, slug)
    
    with open(HISTORICO_CINE, "a", encoding="utf-8") as f: f.write(f"{slug}\n")
    processados += 1
    time.sleep(3)

print("\n📦 Subindo lançamentos de cinema para o GitHub...")
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", f"Auto-Cine: {processados} resenhas completas"])
subprocess.run(["git", "pull", "origin", "main", "--rebase"])
subprocess.run(["git", "push", "origin", "main"])
print("✅ SUCESSO ABSOLUTO!")
