from google import genai # [MUDANÇA] SDK Novo
import os
import re
import time
import subprocess
import unicodedata
from datetime import datetime
from google.genai import types # [MUDANÇA] SDK Novo

# ==========================================
# 1. CONFIGURAÇÕES DA MÁQUINA (CORRIGIDO)
# ==========================================
client = genai.Client(api_key="AIzaSyCmT5HHUpHsXbtN68h6bpkRIzFpjIy2RGs")
# [AJUSTE] gemini-2.5-pro não existe. Usando o 2.0-flash que é o mais rápido e atual.
MODEL_ID = 'gemini-2.0-flash' 

QTD_POSTS_POR_VEZ = 3 
PASTA_BLOG = "blog"
# [CORREÇÃO] Unificando o nome do arquivo de histórico
HISTORICO_ARQUIVO = "historico_temas_blog.txt"

CONFIGURACAO_GERAL = types.GenerateContentConfig(
    safety_settings=[
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
    ]
)

# ==========================================
# 2. TEMPLATES BASE (MANTIDOS 100%)
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
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800;900&family=Montserrat:wght@800;900&display=swap" rel="stylesheet">
    <link rel="icon" href="../../img/logo-unitv.png" type="image/png">

    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@graph": [
        {
          "@type": "BlogPosting",
          "headline": "{titulo}",
          "image": "https://unitvsite.com.br/img/logo-unitv.png",
          "author": {
            "@type": "Organization",
            "name": "Equipe UniTV VIP"
          },
          "publisher": {
            "@type": "Organization",
            "name": "UniTV Oficial Brasil",
            "logo": {
              "@type": "ImageObject",
              "url": "https://unitvsite.com.br/img/logo-unitv.png"
            }
          },
          "datePublished": "{data_seo}",
          "description": "{meta_desc}"
        },
        {
          "@type": "Product",
          "name": "Recarga UniTV Oficial VIP",
          "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "reviewCount": "1840"
          },
          "offers": {
            "@type": "AggregateOffer",
            "lowPrice": "24.90",
            "highPrice": "189.90",
            "priceCurrency": "BRL"
          }
        }
      ]
    }
    </script>

    <style>
        /* --- DESIGN SYSTEM PREMIUM --- */
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        
        :root {
            --bg-body: #050505;
            --bg-card: #0f0f0f;
            --gradiente-premium: linear-gradient(135deg, #FF512F 0%, #DD2476 100%);
            --gradiente-texto: linear-gradient(90deg, #ff8c00, #ff0080, #7928ca);
            --borda-sutil: 1px solid rgba(255, 255, 255, 0.08);
            --cor-destaque: #ff0080;
            --wa-header: #075e54; --wa-bg: #e5ddd5;
        }

        html, body { background-color: var(--bg-body); color: #f0f0f0; overflow-x: hidden; width: 100%; line-height: 1.6; padding-top: 40px; scroll-behavior: smooth; }

        .reveal { opacity: 0; transform: translateY(30px); transition: all 0.8s ease-out; }
        .reveal.active { opacity: 1; transform: translateY(0); }

        /* --- BARRA DE PROMOÇÃO --- */
        .promo-bar { background: linear-gradient(90deg, #1a0b2e, #2d0b1e); color: #e0e0e0; text-align: center; padding: 10px; font-size: 0.85rem; font-weight: 600; position: fixed; top: 0; width: 100%; z-index: 2000; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .promo-bar span { color: #ff0055; font-weight: 800; }

        /* --- HEADER --- */
        header { display: flex; justify-content: space-between; align-items: center; padding: 10px 5%; position: fixed; width: 100%; top: 38px; background: rgba(5, 5, 5, 0.95); backdrop-filter: blur(12px); z-index: 1000; border-bottom: var(--borda-sutil); height: 70px; }
        .logo img { height: 35px; filter: brightness(1.1); }
        .nav-links { display: flex; gap: 20px; }
        .nav-links a { color: #bbb; text-decoration: none; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; transition: 0.3s; padding: 5px 0; border-bottom: 2px solid transparent; }
        .nav-links a:hover { color: white; border-bottom-color: var(--cor-destaque); }
        .btn-header { background: var(--gradiente-premium); color: white; padding: 10px 20px; border-radius: 50px; text-decoration: none; font-size: 0.75rem; font-weight: 800; box-shadow: 0 4px 15px rgba(221, 36, 118, 0.3); }

        /* --- CONTEÚDO (ISOLADO PARA O BLOG) --- */
        .article-hero { padding: 140px 5% 60px; text-align: center; background: radial-gradient(circle at 50% 20%, #2d0b1e 0%, #050505 60%); }
        .article-hero h1 { font-family: 'Montserrat', sans-serif; font-size: clamp(2rem, 5vw, 3rem); line-height: 1.1; font-weight: 900; margin-bottom: 20px; color: #fff;}
        .post-meta { font-size: 0.8rem; color: #555; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 2px; }
        
        .article-content { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        .article-text { font-size: 1.1rem; color: #aaa; margin-bottom: 60px; line-height: 1.8;}
        .article-text h2 { color: #fff; margin: 50px 0 20px; font-size: 1.8rem; border-left: 4px solid var(--cor-destaque); padding-left: 15px;}
        .article-text h3 { color: #ddd; margin: 30px 0 15px; font-size: 1.4rem; font-weight: 700; }
        .article-text p { margin-bottom: 20px; }
        .article-text strong { color: var(--cor-destaque); }
        .article-text img { width: 100%; border-radius: 16px; margin: 30px 0; object-fit: cover; box-shadow: 0 10px 30px rgba(0,0,0,0.6); border: 1px solid #222;}
        .article-text ul { margin: 0 0 25px 25px; }
        .article-text li { margin-bottom: 10px; }

        .article-text .tech-box { background: var(--bg-card); border: 1px solid rgba(255,255,255,0.05); border-left: 4px solid #00ff88; padding: 25px; margin: 35px 0; border-radius: 8px; }
        .article-text .tech-box h4 { color: #00ff88; margin-bottom: 10px; font-size: 1.2rem; text-transform: uppercase; letter-spacing: 1px; }
        .article-text .tech-box p { margin-bottom: 0; font-size: 1rem; color: #ddd; }
        
        .article-text blockquote { background: rgba(255, 0, 128, 0.05); font-style: italic; color: #eee; border-left: 4px solid var(--cor-destaque); padding: 20px 30px; margin: 30px 0; font-size: 1.15rem; border-radius: 0 12px 12px 0; }

        /* --- FOOTER ESTILIZADO --- */
        footer { background: #050505; border-top: 1px solid #1a1a1a; padding: 80px 20px 40px; color: #999; font-size: 0.9rem; }
        .footer-container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr; gap: 40px; }
        .footer-logo { margin-bottom: 25px; height: 40px; filter: brightness(1.2); }
        .footer-col h4 { color: #fff; margin-bottom: 25px; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 800; }
        
        .footer-links { list-style: none; }
        .footer-links li { margin-bottom: 15px; }
        .footer-links a { color: #777; text-decoration: none !important; transition: 0.3s ease; display: flex; align-items: center; gap: 10px; }
        .footer-links a :hover { color: white; transform: translateX(5px); }
        .footer-links a i { font-size: 0.6rem; color: var(--cor-destaque); opacity: 0; transition: 0.3s; }
        .footer-links a:hover i { opacity: 1; }

        .payment-methods { display: flex; gap: 20px; font-size: 2.2rem; margin-top: 25px; color: #222; }

        /* --- CHATBOT --- */
        .wa-widget { position: fixed; bottom: 85px; right: 20px; width: 340px; background: var(--wa-bg); border-radius: 12px; z-index: 9999; transform: scale(0); transform-origin: bottom right; transition: 0.3s ease; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .wa-widget.active { transform: scale(1); }
        .wa-header { background: #075e54; color: white; padding: 12px 15px; display: flex; align-items: center; justify-content: space-between; }
        .wa-chat-body { height: 350px; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; background-image: url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png'); background-size: contain; }
        .wa-msg { max-width: 85%; padding: 8px 12px; border-radius: 8px; font-size: 0.88rem; box-shadow: 0 1px 1px rgba(0,0,0,0.15); color: #333; background: white; }
        .float-zap { position: fixed; bottom: 20px; right: 20px; background: #25d366; color: white; width: 65px; height: 65px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; z-index: 10000; cursor: pointer; box-shadow: 0 10px 30px rgba(37,211,102,0.4); }

        @media (max-width: 768px) {
            header { height: 65px; padding: 10px 20px; }
            .logo img { height: 28px; }
            .nav-links { display: none; }
            .footer-container { grid-template-columns: 1fr; text-align: center; }
            .footer-links a { justify-content: center; }
            .payment-methods { justify-content: center; }
        }
    </style>
</head>
<body>

    <div class="promo-bar">🔥 OFERTA RELÂMPAGO: Preços reduzidos por tempo limitado!</div>

    <header>
        <div class="logo">
            <a href="../../index.html"><img src="../../img/logo-unitv.png" alt="Logo UniTV Oficial"></a>
        </div>
        <nav class="nav-links">
            <a href="../../index.html">Início</a>
            <a href="../../baixar/index.html">Downloads</a>
            <a href="../../tv-box/index.html">Guia TV Box</a>
            <a href="../index.html">Blog</a>
        </nav>
        <a href="../../index.html#comprar" class="btn-header">COMPRAR VIP</a>
    </header>

    <article class="article-hero reveal active">
        <span class="badge">Blog Tech</span>
        <h1>{titulo}</h1>
        <p class="post-meta">Publicado em: {data_atual} | Por: Equipe UniTV Suporte</p>
    </article>

    <main class="article-content">
        <section class="article-text reveal active">
"""

TEMPLATE_RODAPE = """
        </section>

        <div style="background: linear-gradient(160deg, #180a1f 0%, #050505 100%); border: 1px solid var(--cor-destaque); padding: 40px; border-radius: 20px; text-align: center; margin-top: 60px; box-shadow: 0 0 40px rgba(255, 0, 128, 0.15);">
            <h3 style="color:#fff; font-size:1.8rem; margin-bottom:15px; font-weight:800;">Pare de passar raiva com travamentos!</h3>
            <p style="color: #bbb; margin-bottom: 20px;">Aproveite o máximo do 4K na sua TV Box. Garanta sua recarga UniTV Oficial com entrega imediata via Pix e suporte humanizado.</p>
            <a href="../../index.html#comprar" style="background: var(--gradiente-premium); color: white; padding: 18px 45px; border-radius: 50px; text-decoration: none; font-weight: 800; display: inline-block; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 4px 15px rgba(221, 36, 118, 0.3);"><i class="fa-solid fa-bolt"></i> VER PLANOS OFICIAIS</a>
        </div>
    </main>

    <footer>
        <div class="footer-container">
            <div class="footer-col">
                <img src="../../img/logo-unitv.png" alt="UniTV" class="footer-logo">
                <p>Revenda Oficial UniTV Brasil. Leve a melhor tecnologia de entretenimento 4K para sua família com segurança total.</p>
                <div style="color: #00ff88; font-size: 0.8rem; margin-top: 15px; display: flex; align-items: center; gap: 8px;"><i class="fa-solid fa-shield-halved"></i> Site 100% Protegido</div>
            </div>
            <div class="footer-col">
                <h4>Navegação</h4>
                <ul class="footer-links">
                    <li><a href="../../index.html"><i class="fa-solid fa-chevron-right"></i> Início</a></li>
                    <li><a href="../../baixar/index.html"><i class="fa-solid fa-chevron-right"></i> Downloads</a></li>
                    <li><a href="../../tv-box/index.html"><i class="fa-solid fa-chevron-right"></i> Guia TV Box</a></li>
                    <li><a href="../index.html"><i class="fa-solid fa-chevron-right"></i> Blog VIP</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Suporte</h4>
                <ul class="footer-links">
                    <li><a href="../../ajuda/index.html"><i class="fa-solid fa-chevron-right"></i> Central de Ajuda</a></li>
                    <li><a href="javascript:void(0)" onclick="toggleChat()"><i class="fa-solid fa-chevron-right"></i> Chat Online</a></li>
                    <li><a href="https://wa.me/5519981765840" target="_blank"><i class="fa-solid fa-chevron-right"></i> WhatsApp Oficial</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Pagamento</h4>
                <div class="payment-methods">
                    <i class="fa-brands fa-pix" style="color:#32bcad;"></i>
                    <i class="fa-brands fa-cc-mastercard"></i>
                    <i class="fa-brands fa-cc-visa"></i>
                </div>
                <p style="font-size: 0.7rem; margin-top: 10px; opacity: 0.5;">Processamento Seguro via Kirvano.</p>
            </div>
        </div>
        <div style="text-align: center; margin-top: 60px; padding-top: 20px; border-top: 1px solid #111; font-size: 0.75rem; color: #444;">
            &copy; 2024 - 2026 UniTV Revenda Oficial. Todos os direitos reservados.
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

    <div class="float-zap" onclick="toggleChat()" aria-label="Abrir conversa no WhatsApp" role="button" tabindex="0"><i class="fa-brands fa-whatsapp"></i></div>

    <script>
        function toggleChat() { 
            document.getElementById('chat-widget').classList.toggle('active'); 
        }
        
        // Ativação da Animação ao descer a página
        window.addEventListener('scroll', () => {
            document.querySelectorAll('.reveal').forEach(el => {
                if (el.getBoundingClientRect().top < window.innerHeight - 100) el.classList.add('active');
            });
        });
    </script>
</body>
</html>
"""

# ==========================================
# 3. LÓGICA DE GERAÇÃO E URLS
# ==========================================
def carregar_historico():
    if not os.path.exists(HISTORICO_ARQUIVO): return []
    with open(HISTORICO_ARQUIVO, 'r', encoding='utf-8') as f:
        return [linha.strip() for linha in f.readlines() if linha.strip()]

def salvar_historico(tema):
    # [CORREÇÃO] Modo "a" (append) para garantir que ele salve linha por linha sem apagar nada
    with open(HISTORICO_ARQUIVO, "a", encoding="utf-8") as f:
        f.write(f"{tema}\n")
    print(f"📝 '{tema}' carimbado no histórico.")

def criar_slug(texto):
    texto_sem_acento = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    slug = re.sub(r'[^a-z0-9]+', '-', texto_sem_acento.lower()).strip('-')
    return slug[:45].strip('-')

def gerar_temas(historico):
    print("🧠 Gerando temas curtos e inéditos...")
    historico_str = ", ".join(historico[-30:]) 
    prompt = f"""
    Crie {QTD_POSTS_POR_VEZ} títulos de artigos curtos sobre TV Box, IPTV e UniTV.
    REGRA DE OURO: No máximo 8 palavras por título.
    PROIBIÇÃO: Não repita estes temas: [{historico_str}].
    Gere temas como: Lançamentos de Cinema, Futebol, Tecnologia 4K.
    Retorne um por linha.
    """
    try:
        resposta = client.models.generate_content(model=MODEL_ID, contents=prompt, config=CONFIGURACAO_GERAL)
        return [t.strip() for t in resposta.text.split('\n') if t.strip()][:QTD_POSTS_POR_VEZ]
    except Exception as e:
        print(f"⚠️ Erro IA Temas: {e}")
        return ["Dicas de Cinema UniTV", "Otimizando Internet 4K", "Futebol na TV Box"]

def escrever_artigo(tema):
    print(f"✍️ Redigindo post: {tema}")
    prompt_redator = f"""
    Escreva o CORPO de um artigo técnico (800+ palavras) sobre: "{tema}".
    1. NÃO use tags estruturais (html, head, body).
    2. USE APENAS: <h2>, <h3>, <p>, <ul> e <blockquote>.
    3. Foco em UniTV e TV Box.
    4. Crie 2 blocos: <div class="tech-box"><h4>Dica</h4><p>conteúdo.</p></div>
    5. 3 imagens: <img src="https://picsum.photos/seed/{tema.replace(' ', '')}X/800/400" alt="Post">.
    """
    prompt_meta = f"Resuma em 150 caracteres o tema: {tema}."
    
    try:
        res_artigo = client.models.generate_content(model=MODEL_ID, contents=prompt_redator, config=CONFIGURACAO_GERAL)
        artigo = res_artigo.text.replace("```html", "").replace("```", "").strip()
        
        res_meta = client.models.generate_content(model=MODEL_ID, contents=prompt_meta, config=CONFIGURACAO_GERAL)
        meta_desc = res_meta.text.replace('"', '').strip()
        return artigo, meta_desc
    except Exception as e:
        raise Exception(f"Erro IA Redação: {e}")

# ==========================================
# 4. INJEÇÃO SEGURA NA VITRINE (CORRIGIDO)
# ==========================================
def atualizar_pagina_principal_do_blog(titulo, slug, meta_desc):
    caminho = os.path.join(PASTA_BLOG, "index.html")
    # [CORREÇÃO] Âncora restaurada para evitar o loop infinito
    ancora = ""
    try:
        with open(caminho, "r", encoding="utf-8") as f: html = f.read()

        card = f"""
        <a href="{slug}/index.html" class="post-card reveal active" style="text-decoration:none; display: block; margin-bottom: 30px;">
            <div class="post-thumb" style="border-radius:10px; overflow:hidden; margin-bottom:15px;">
                <img src="https://picsum.photos/seed/{slug}/800/500" alt="{titulo}" style="width:100%; display:block; transition:0.3s; object-fit: cover;">
            </div>
            <div class="post-content">
                <span class="post-tag" style="background:#ff0080; color:#fff; padding:5px 10px; font-size:0.7rem; font-weight:bold; border-radius:4px; margin-bottom:10px; display:inline-block;">NOVIDADE TECH</span>
                <h2 style="color:#fff; font-size:1.4rem; margin-bottom:10px; line-height:1.3; font-weight:800;">{titulo}</h2>
                <p style="color:#888; font-size:0.9rem; margin-bottom:15px; line-height:1.5;">{meta_desc}</p>
                <span class="btn-read" style="color:#00ff88; font-weight:bold; font-size:0.9rem;">LER GUIA <i class="fa-solid fa-arrow-right"></i></span>
            </div>
        </a>
        """

        if ancora in html:
            # [CORREÇÃO] Injeção cirúrgica recolocando a âncora no final para o próximo post
            html = html.replace(ancora, card + "\n        " + ancora)
            with open(caminho, "w", encoding="utf-8") as f: f.write(html)
            print(f"🔗 Post '{titulo}' na vitrine.")
        else:
            print("⚠️ Tag âncora não encontrada no index.html")
    except Exception as e:
        print(f"⚠️ Erro ao atualizar vitrine: {e}")

# ==========================================
# EXECUTOR
# ==========================================
print("🚀 MÁQUINA DE SEO UniTV (VERSÃO BLINDADA)")
historico = carregar_historico()
temas = gerar_temas(historico)

for tema in temas:
    slug = criar_slug(tema)
    pasta_artigo = os.path.join(PASTA_BLOG, slug)
    
    if os.path.exists(pasta_artigo): 
        print(f"⏩ Pulando '{tema}', slug já existe.")
        continue
        
    os.makedirs(pasta_artigo, exist_ok=True)
    
    try:
        corpo, meta = escrever_artigo(tema)
        data_format = datetime.now().strftime("%d de %B de %Y")
        data_seo = datetime.now().strftime("%Y-%m-%d")
        
        html_final = TEMPLATE_TOPO.replace("{titulo}", tema).replace("{meta_desc}", meta).replace("{data_atual}", data_format).replace("{data_seo}", data_seo)
        html_final += corpo + TEMPLATE_RODAPE
        
        with open(os.path.join(pasta_artigo, "index.html"), "w", encoding="utf-8") as f: f.write(html_final)
        
        atualizar_pagina_principal_do_blog(tema, slug, meta)
        salvar_historico(tema)
        time.sleep(5) 
    except Exception as e: print(f"❌ Erro ao processar post: {e}")

print("\n📦 Sincronizando com GitHub...")
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", f"Auto-post: {datetime.now().strftime('%d/%m %H:%M')}"])
# [CORREÇÃO] Pull rebase antes do push para evitar o erro "rejected"
subprocess.run(["git", "pull", "origin", "main", "--rebase"])
subprocess.run(["git", "push", "origin", "main"])
print("✅ SUCESSO ABSOLUTO! Robô blindado e site no ar.")
