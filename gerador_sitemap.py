import os
from datetime import datetime

# CONFIGURAÇÃO
DOMINIO = "https://unitvsite.com.br"
PASTAS_ESTATICAS = ["blog", "cinema", "baixar", "ajuda", "tutorial", "tv-box", "confiavel", "velocidade"]
ARQUIVO_SITEMAP = "sitemap.xml"

def gerar_sitemap():
    print("🗺️ Iniciando mapeamento do site...")
    links = [DOMINIO + "/"] # Link da home
    
    for pasta in PASTAS_ESTATICAS:
        # Adiciona a página principal da pasta
        if os.path.exists(pasta):
            links.append(f"{DOMINIO}/{pasta}/")
            
            # Varre subpastas (os posts e resenhas)
            subitens = os.listdir(pasta)
            for item in subitens:
                caminho_completo = os.path.join(pasta, item)
                if os.path.isdir(caminho_completo):
                    # Verifica se tem um index.html lá dentro
                    if os.path.exists(os.path.join(caminho_completo, "index.html")):
                        links.append(f"{DOMINIO}/{pasta}/{item}/")

    # MONTAGEM DO XML
    data_atual = datetime.now().strftime("%Y-%m-%d")
    xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml_footer = '</urlset>'
    
    corpo = ""
    for link in links:
        corpo += f"  <url>\n    <loc>{link}</loc>\n    <lastmod>{data_atual}</lastmod>\n    <priority>0.8</priority>\n  </url>\n"

    with open(ARQUIVO_SITEMAP, "w", encoding="utf-8") as f:
        f.write(xml_header + corpo + xml_footer)
    
    print(f"✅ Sitemap gerado com {len(links)} links!")

if __name__ == "__main__":
    gerar_sitemap()
