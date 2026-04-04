import google.generativeai as genai
import os
import re
import time
import subprocess
from datetime import datetime

# ==========================================
# 1. CONFIGURAÇÕES DA MÁQUINA
# ==========================================
genai.configure(api_key="AIzaSyCmT5HHUpHsXbtN68h6bpkRIzFpjIy2RGs")
model = genai.GenerativeModel('gemini-2.5-flash')

QTD_POSTS_POR_VEZ = 3 
PASTA_BLOG = "blog"
HISTORICO_ARQUIVO = "historico_temas_blog.txt"

# ==========================================
# 2. TEMPLATES BLINDADOS (ESTÉTICA CYBERPUNK/TECH)
# ==========================================
TEMPLATE_TOPO = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{titulo} | Blog UniTV Oficial</title>
    <meta name="description" content="{meta_desc}">
    <meta name="theme-color" content="#1a0525">
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800;900&family=Montserrat:wght@800;900&display=swap" rel="stylesheet">
    <link rel="icon" href="../../img/logo-unitv.png" type="image/png">

    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }}
        :root {{ 
            --bg-body: #050505; 
            --bg-card: #0f0f0f; 
            --gradiente-premium: linear-gradient(135deg, #00d4ff 0%, #ff8c00 100%); 
            --gradiente-texto: linear-gradient(90deg, #ff8c00, #00d4ff); 
            --cor-destaque: #ff8c00;
            --cor-secundaria: #00d4ff;
            --borda-sutil: 1px solid rgba(255, 255, 255, 0.08);
            --wa-header: #075e54; --wa-bg: #e5ddd5;
        }}
        html, body {{ background-color: var(--bg-body); color: #f0f0f0; overflow-x: hidden; line-height: 1.6; }}
        
        header {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 5%; position: sticky; top: 0; width: 100%; background: rgba(5, 5, 5, 0.95); backdrop-filter: blur(15px); z-index: 1000; border-bottom: var(--borda-sutil); height: 75px; }}
        .logo img {{ height: 40px; filter: brightness(1.2); }}
        nav ul {{ display: flex; list-style: none; gap: 20px; }}
        nav a {{ color: #bbb; text-decoration: none; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; transition: 0.3s; padding: 5px 0; border-bottom: 2px solid transparent; }}
        nav a:hover, nav a.active {{ color: white; border-bottom-color: var(--cor-secundaria); }}
        .btn-header {{ background: var(--gradiente-premium); color: white; padding: 10px 22px; border-radius: 50px; text-decoration: none; font-size: 0.75rem; font-weight: 800; box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3); }}
        
        .article-container {{ max-width: 900px; margin: 60px auto 100px; padding: 0 20px; }}
        .article-header {{ text-align: center; margin-bottom: 50px; }}
        .article-header h1 {{ font-family: 'Montserrat', sans-serif; font-size: clamp(2.2rem, 5vw, 4rem); font-weight: 900; line-height: 1.1; margin-bottom: 20px; background: var(--gradiente-texto); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1px; }}
        .article-meta {{ color: #888; font-size: 0.9rem; font-weight: 600; display: flex; justify-content: center; gap: 20px; text-transform: uppercase; letter-spacing: 1px; }}
        .article-meta i {{ color: var(--cor-secundaria); }}
        
        .article-content h2 {{ color: #fff; font-size: 2.2rem; margin: 60px 0 25px; font-weight: 800; border-left: 5px solid var(--cor-secundaria); padding-left: 15px; letter-spacing: -0.5px; }}
        .article-content h3 {{ color: var(--cor-destaque); font-size: 1.5rem; margin: 40px 0 15px; font-weight: 700; }}
        .article-content p {{ color: #bbb; font-size: 1.15rem; line-height: 1.8; margin-bottom: 25px; }}
        .article-content ul {{ margin: 0 0 30px 20px; color: #bbb; font-size: 1.15rem; line-height: 1.8; }}
        .article-content li {{ margin-bottom: 12px; }}
        .article-content img {{ width: 100%; border-radius: 20px; margin: 40px 0; border: 1px solid rgba(0, 212, 255, 0.2); box-shadow: 0 10px 40px rgba(0,0,0,0.6); }}
        .article-content strong {{ color: #fff; font-weight: 700; }}
        .article-content blockquote {{ background: rgba(0, 212, 255, 0.05); border-left: 4px solid var(--cor-secundaria); padding: 20px 30px; margin: 30px 0; font-style: italic; color: #ddd; border-radius: 0 15px 15px 0; }}
        
        .cta-box {{ background: #0a0a0a; border: 1px solid #222; border-left: 5px solid var(--cor-destaque); padding: 50px 40px; border-radius: 20px; text-align: center; margin: 60px 0; position: relative; overflow: hidden; }}
        .cta-box::before {{ content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(circle at top right, rgba(255, 140, 0, 0.1), transparent 50%); pointer-events: none; }}
        .cta-box h3 {{ color: #fff; font-size: 2rem; margin-bottom: 15px; font-weight: 900; }}
        .cta-box p {{ color: #aaa; margin-bottom: 30px; font-size: 1.1rem; }}
        .btn-cta-blog {{ background: var(--gradiente-premium); color: #fff; padding: 18px 40px; border-radius: 50px; font-weight: 900; text-decoration: none; font-size: 1.1rem; display: inline-block; transition: 0.4s; text-transform: uppercase; box-shadow: 0 10px 30px rgba(255, 140, 0, 0.3); letter-spacing: 1px; }}
        .btn-cta-blog:hover {{ transform: translateY(-5px); box-shadow: 0 15px 40px rgba(255, 140, 0, 0.5); filter: brightness(1.1); }}

        /* FOOTER & ZAP */
        footer {{ background: #050505; border-top: 1px solid #1a1a1a; padding: 80px 20px 40px; color: #999; font-size: 0.9rem; }}
        .footer-container {{ max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr; gap: 40px; }}
        .footer-logo {{ margin-bottom: 25px; height: 45px; filter: brightness(1.2); }}
        .footer-col h4 {{ color: #fff; margin-bottom: 25px; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 800; }}
        .footer-links {{ list-style: none; }}
        .footer-links li {{ margin-bottom: 15px; }}
        .footer-links a {{ color: #666; text-decoration: none; transition: 0.3s; display: flex; align-items: center; gap: 12px; }}
        .footer-links a:hover {{ color: #fff; transform: translateX(10px); }}
        .footer-links a i {{ font-size: 0.7rem; color: var(--cor-destaque); opacity: 0.5; transition: 0.3s; }}
        .footer-links a:hover i {{ opacity: 1; transform: scale(1.2); }}
        .payment-methods {{ display: flex; gap: 20px; font-size: 2.2rem; margin-top: 25px; color: #222; }}
        .float-zap {{ position: fixed; bottom: 20px; right: 20px; background: #25d366; color: white; width: 65px; height: 65px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; z-index: 10000; cursor: pointer; box-shadow: 0 10px 30px rgba(37, 211, 102, 0.4); text-decoration: none; transition: 0.3s; }}
        .float-zap:hover {{ transform: scale(1.1); }}

        @media (max-width: 768px) {{
            .article-header h1 {{ font-size: 2.4rem; }}
            header nav {{ display: none; }}
            .footer-container {{ grid-template-columns: 1fr; text-align: center; }}
            .footer-links a {{ justify-content: center; }}
            .payment-methods {{ justify-content: center; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="logo"><a href="../../index.html"><img src="../../img/logo-unitv.png" alt="UniTV Oficial"></a></div>
        <nav>
            <ul>
                <li><a href="../../index.html">Início</a></li>
                <li><a href="../../baixar/index.html">Downloads</a></li>
                <li><a href="../../aparelhos/tv-box/index.html">Guia TV Box</a></li>
                <li><a href="../index.html" class="active">Blog</a></li>
            </ul>
        </nav>
        <a href="../../index.html#comprar" class="btn-header">ADQUIRIR VIP</a>
    </header>

    <main class="article-container">
        <header class="article-header">
            <h1>{titulo}</h1>
            <div class="article-meta">
                <span><i class="fa-solid fa-calendar"></i> {data_atual}</span>
                <span><i class="fa-solid fa-microchip"></i> Redação Tech UniTV</span>
            </div>
        </header>
        <div class="article-content">
"""

TEMPLATE_RODAPE = """
        </div>
        
        <div class="cta-box">
            <h3>A Revolução do 4K na Sua Sala</h3>
            <p>Não perca mais tempo com listas travando. Garanta hoje o plano Anual VIP da UniTV Oficial e assista a milhares de conteúdos com estabilidade absoluta.</p>
            <a href="../../index.html#comprar" class="btn-cta-blog">VER PLANOS E PREÇOS <i class="fa-solid fa-bolt"></i></a>
        </div>
    </main>

    <footer>
        <div class="footer-container">
            <div class="footer-col">
                <img src="../../img/logo-unitv.png" alt="UniTV" class="footer-logo">
                <p>Revenda Autorizada UniTV Brasil. Entretenimento de elite com segurança total para sua família.</p>
            </div>
            <div class="footer-col">
                <h4>Navegação</h4>
                <ul class="footer-links">
                    <li><a href="../../index.html"><i class="fa-solid fa-chevron-right"></i> Home Page</a></li>
                    <li><a href="../../baixar/index.html"><i class="fa-solid fa-chevron-right"></i> Downloads</a></li>
                    <li><a href="../index.html"><i class="fa-solid fa-chevron-right"></i> Blog Oficial</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Suporte</h4>
                <ul class="footer-links">
                    <li><a href="https://wa.me/5519981765840" target="_blank"><i class="fa-solid fa-chevron-right"></i> Falar no WhatsApp</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Pagamento Seguro</h4>
                <div class="payment-methods">
                    <i class="fa-brands fa-pix" style="color:#32bcad;"></i>
                    <i class="fa-brands fa-cc-mastercard"></i>
                    <i class="fa-brands fa-cc-visa"></i>
                </div>
            </div>
        </div>
        <div style="text-align: center; margin-top: 60px; padding-top: 20px; border-top: 1px solid #111; font-size: 0.75rem; color: #444;">
            &copy; 2026 UniTV Revenda Oficial. O melhor do entretenimento digital 4K.
        </div>
    </footer>
    <a href="https://wa.me/5519981765840" target="_blank" class="float-zap"><i class="fa-brands fa-whatsapp"></i></a>
</body>
</html>
"""

# ==========================================
# 3. A INTELIGÊNCIA DA IA
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
    print("🧠 Analisando tendências do Google e streaming...")
    prompt = f"""
    Crie {QTD_POSTS_POR_VEZ} títulos de artigos MUITO chamativos e persuasivos para um blog sobre TV Box, IPTV, filmes e tecnologia Android. 
    Eles devem atrair quem busca soluções para travamentos, setups e filmes 4K.
    REGRA DE OURO: NÃO repita nenhum destes temas: {', '.join(historico[-30:])}
    Retorne APENAS os títulos, um por linha.
    """
    resposta = model.generate_content(prompt)
    return [t.strip() for t in resposta.text.split('\n') if t.strip()][:QTD_POSTS_POR_VEZ]

def escrever_artigo(tema):
    print(f"✍️ Escrevendo artigo ÉPICO sobre: {tema}")
    prompt_redator = f"""
    Aja como o melhor especialista em SEO e Tecnologia. Escreva um artigo completo e gigante (1200+ palavras) sobre: "{tema}".
    
    REGRA DE FORMATAÇÃO (RETORNE APENAS O HTML DO CORPO DO TEXTO):
    1. Sem tag <h1> (já está no template).
    2. Use <h2> e <h3>.
    3. Cite DADOS de pesquisas (pode ser estimativas plausíveis).
    4. Adicione 2 imagens dinâmicas usando: <img src="https://picsum.photos/seed/{tema.replace(' ', '')}/800/400" alt="Tecnologia">
    5. Crie listas ordenadas e blocos <blockquote>.
    6. Mantenha tom profundo e mostre como o servidor Premium (UniTV) é a solução.
    """
    
    artigo_html = model.generate_content(prompt_redator).text.replace("```html", "").replace("```", "").strip()
    
    prompt_meta = f"Crie uma meta description de SEO (max 150 caracteres) para: {tema}. Retorne apenas a frase."
    meta_desc = model.generate_content(prompt_meta).text.strip()
    
    return artigo_html, meta_desc

def criar_slug(texto):
    return re.sub(r'[^a-z0-9]+', '-', texto.lower()).strip('-')

# ==========================================
# 4. INJETOR NA TELA INICIAL DO BLOG
# ==========================================
def atualizar_pagina_principal_do_blog(titulo, slug, meta_desc):
    caminho_index = os.path.join(PASTA_BLOG, "index.html")
    
    with open(caminho_index, "r", encoding="utf-8") as f:
        html = f.read()

    # O Design EXATO do card do seu Grid
    novo_card = f"""
        <a href="{slug}/index.html" class="post-card reveal active">
            <div class="post-thumb">
                <img src="https://picsum.photos/seed/{slug}/800/600" alt="{titulo}">
            </div>
            <div class="post-content">
                <span class="post-tag">NOVIDADE</span>
                <h2>{titulo}</h2>
                <p>{meta_desc}</p>
                <span class="btn-read">LER AGORA <i class="fa-solid fa-arrow-right"></i></span>
            </div>
        </a>
    """

    if "" in html:
        html = html.replace("", novo_card)

    with open(caminho_index, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"🔗 Artigo '{titulo}' linkado na capa com seu design original!")

# ==========================================
# EXECUTOR
# ==========================================
print("🚀 MÁQUINA DE SEO CYBERPUNK INICIADA")
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
        
        pagina_final = TEMPLATE_TOPO.format(titulo=tema, meta_desc=meta_desc, data_atual=data_formatada)
        pagina_final += conteudo_html
        pagina_final += TEMPLATE_RODAPE
        
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(pagina_final)
        
        atualizar_pagina_principal_do_blog(tema, slug, meta_desc)
        salvar_historico(tema)
        time.sleep(5)
    except Exception as e:
        print(f"❌ Erro ao gerar {tema}: {e}")

print("\n📦 Fazendo o Push Automático para o GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Auto-post Cyberpunk: {datetime.now().strftime('%Y-%m-%d %H:%M')}"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ DEPLOY CONCLUÍDO! O site está no ar e lindo.")
except Exception as e:
    print("⚠️ Erro no Git Push. Verifique credenciais.")
