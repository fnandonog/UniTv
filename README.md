md
md
Copiar
Expandir
# 🚀 UniTV Site Oficial

Landing pages, páginas de suporte e funis de conversão do projeto **unitvsite.com.br**.

Este repositório concentra a estrutura pública do site, com foco em:

- 🎯 **captação de leads**
- 🛒 **venda de recargas mensais e anuais**
- 📚 **conteúdo para SEO**
- 🛠️ **suporte e tutoriais**
- 📈 **rastreamento para tráfego pago**
- 📱 **experiência mobile-first**

---

## 🌐 Domínio principal

**Produção:**  
`https://unitvsite.com.br`

---

## ✨ Visão geral do projeto

O site foi construído para funcionar como um ecossistema completo de aquisição, conversão e retenção de visitantes.

Ele combina:

- 🏠 **landing page principal**
- 💳 **páginas de oferta por plano**
- 📥 **página de downloads**
- 🧪 **página de teste grátis**
- ⚡ **teste de velocidade**
- 📰 **blog com artigos SEO**
- ❓ **central de ajuda**
- 📖 **tutoriais de instalação**
- ✅ **páginas de obrigado**
- 📲 **WhatsApp e chat como canais de fechamento**
- 📊 **Meta Pixel + CAPI**

---

## 🎯 Objetivo do projeto

Este projeto existe para:

- aumentar a taxa de conversão de visitantes em compradores
- reduzir abandono antes do checkout
- melhorar clareza da oferta
- aumentar confiança do usuário
- facilitar instalação do serviço
- gerar sinais de alta qualidade para o algoritmo de anúncios
- estruturar remarketing por etapa do funil
- apoiar SEO com conteúdo de apoio e blog

---

# 🧩 Estrutura do site

## Páginas principais

### 🏠 Home
Apresenta:
- proposta de valor
- prova social
- diferenciais
- catálogo visual
- FAQ
- planos
- CTA para compra e suporte

### 💳 Página de recarga mensal
Focada em:
- conversão do plano mensal
- oferta simples
- baixa barreira de entrada
- CTA de checkout
- dúvidas específicas do mensal

### 👑 Página de recarga anual
Focada em:
- economia
- valor percebido
- comparação com mensal
- incentivo de longo prazo
- CTA de checkout anual

### 📘 Tutorial
Explica:
- como instalar
- como usar Downloader
- como configurar em TV Box, Android e outros fluxos
- resolução de objeções técnicas

### ❓ Ajuda
Central de suporte com:
- erros comuns
- problemas de login
- problemas de instalação
- atalhos para suporte
- reforço de planos

### 📰 Blog
Focado em:
- SEO
- retenção
- aquecimento de tráfego frio
- conteúdo sobre IPTV, TV Box, UniTV, filmes, séries, esportes e instalação

### ⚡ Velocidade
Ferramenta para:
- diagnosticar qualidade da conexão
- qualificar usuário
- educar sobre estabilidade
- reforçar a compra do plano

### 🧪 Teste grátis
Página voltada para:
- reduzir resistência inicial
- incentivar instalação
- transformar curiosidade em uso
- preparar o lead para upgrade

### ✅ Obrigado mensal
Página pós-compra do plano mensal:
- confirma o pagamento
- faz o redirecionamento
- dispara conversão final

### ✅ Obrigado anual
Página pós-compra do plano anual:
- confirma o pagamento
- reforça valor do plano
- dispara conversão final

---

# 🗂️ Estrutura recomendada do projeto

```bash
/
├── index.html
├── recarga-mensal/
│   └── index.html
├── recarga-anual/
│   └── index.html
├── tutorial/
│   └── index.html
├── ajuda/
│   └── index.html
├── blog/
│   ├── index.html
│   └── posts...
├── velocidade/
│   └── index.html
├── teste-gratis/
│   └── index.html
├── obrigado/
│   ├── mensal/
│   │   └── index.html
│   └── anual/
│       └── index.html
├── js/
│   └── meta-tracking.js
├── api/
│   └── meta-capi.php
├── img/
└── README.md

🛠️ Tecnologias utilizadas
HTML5
CSS3
JavaScript puro
Font Awesome
Google Fonts
TMDB API
WhatsApp Click-to-Chat
Meta Pixel
Meta Conversions API (CAPI)
Kirvano como checkout externo
🎨 Identidade visual

A linguagem visual do projeto prioriza:

fundo escuro
percepção premium
contraste alto
CTA muito visível
sensação de tecnologia e estabilidade
Cores-base do projeto
🔲 Fundo principal: #050505
⬛ Cards: #0f0f0f
🌈 Gradiente principal: #FF512F → #DD2476
💖 Destaque: #ff0080
✅ Verde de confiança: #25D366
⚪ Branco: #ffffff
📈 Rastreamento e analytics
Meta Pixel principal

Pixel usado no projeto:

txt
txt
Copiar
2204821377087872

Estratégia adotada

O projeto foi estruturado para usar:

Pixel no frontend
CAPI no backend
Purchase nas páginas de obrigado
tracking por etapa do funil
Eventos principais usados
PageView
ViewContent
InitiateCheckout
Contact
Lead
Purchase
CompleteRegistration
Search
ScrollDepth
LandingEngaged
FAQOpened
ArticleClick
GuideClick
SpeedTestStart
SpeedTestResult
ChatOptionSelected
📦 JS global de tracking

Arquivo principal:

bash
bash
Copiar
/js/meta-tracking.js


Esse arquivo centraliza a lógica de rastreamento para o site inteiro.

Responsabilidades do JS global
iniciar o pixel
disparar PageView
disparar ViewContent
disparar eventos personalizados
capturar _fbp e _fbc
enviar eventos para a CAPI
capturar UTM
medir engajamento
medir scroll
padronizar eventos entre páginas
🔐 Estrutura da CAPI
Arquivo público
bash
bash
Copiar
/api/meta-capi.php

Arquivo secreto
bash
bash
Copiar
meta-config.php


O arquivo secreto não deve ficar no repositório público.

📌 Checkout e conversão

O checkout acontece via Kirvano.

Estratégia de funil
o site gera interesse e intenção
o checkout é feito externamente
o usuário volta para a página de obrigado
a compra é registrada na página final
Páginas de obrigado
/obrigado/mensal/
/obrigado/anual/

Essas páginas são fundamentais para:

confirmar pagamento
redirecionar o usuário
disparar Purchase
📲 Suporte e atendimento

O projeto utiliza canais rápidos de atendimento para reduzir abandono e aumentar fechamento.

Canais usados
WhatsApp
botões contextuais
chat em páginas específicas
fluxo guiado de atendimento
📚 Blog e SEO

O blog é uma parte estratégica do projeto.

Objetivos do blog
atrair tráfego orgânico
aquecer visitantes frios
fortalecer autoridade
responder dúvidas antes da venda
gerar remarketing
apoiar conversão indireta
Conteúdos típicos
IPTV
UniTV
TV Box
streaming
4K
futebol ao vivo
instalação
compatibilidade
comparativos
lançamentos
🧪 Página de teste grátis

A página de teste grátis existe para:

diminuir a resistência de novos usuários
incentivar download e uso inicial
gerar lead qualificado
alimentar remarketing
preparar migração para mensal ou anual
⚡ Página de velocidade

A página de velocidade funciona como:

ferramenta de valor percebido
qualificação técnica do lead
suporte pré-venda
redução de objeção por travamento
reforço do discurso de estabilidade
🧭 Experiência do usuário

O projeto foi desenhado para:

parecer confiável
reduzir estranheza
explicar o próximo passo com clareza
facilitar uso no celular
gerar menos fricção entre interesse e contato
Boas práticas aplicadas
seções previsíveis
CTA visível
FAQ claro
prova social
linguagem direta
caminhos alternativos de suporte
foco no mobile
🧱 Melhorias futuras recomendadas
Alta prioridade
✅ revisar todos os eventos no Events Manager
✅ validar duplicidade zero
✅ instalar Microsoft Clarity
✅ manter política de privacidade e termos
✅ melhorar provas sociais reais
Média prioridade
separar CSS e JS em mais arquivos
modularizar componentes
guardar mais dados de atribuição
reforçar páginas de remarketing
ampliar artigos de blog
Estratégicas
testar novas copies no hero
testar novas ofertas
testar novos CTAs
criar heatmaps
criar relatórios por origem de lead
📋 Checklist antes de publicar
 Pixel disparando corretamente
 CAPI respondendo corretamente
 checkout redirecionando para obrigado
 páginas sem erro no mobile
 FAQ funcionando
 CTAs funcionando
 links de WhatsApp funcionando
 links de checkout funcionando
 banners e imagens carregando
 Search Console ativo
📋 Checklist antes de anunciar
 testar home
 testar mensal
 testar anual
 testar tutorial
 testar ajuda
 testar blog
 testar velocidade
 testar obrigado mensal
 testar obrigado anual
 confirmar que cada compra gera apenas 1 Purchase
 revisar tempo de carregamento no celular
 revisar clareza dos CTAs
✅ Regras importantes do projeto
Pode ficar público
HTML
CSS
JS frontend
assets visuais
estrutura do site
Não pode ficar público
token de acesso da Meta
segredos da CAPI
arquivos privados do servidor
credenciais administrativas
🔍 Ordem de diagnóstico quando algo parar de converter
o pixel está disparando?
a CAPI está respondendo?
o checkout ainda está funcionando?
o redirecionamento para obrigado está certo?
o WhatsApp abre?
o mobile está bom?
houve mudança no layout?
o Events Manager está mostrando compra?
houve duplicidade?
o anúncio está mandando público compatível?
💡 Filosofia do projeto

Este projeto não é apenas “um site”.

Ele é um sistema de aquisição com quatro funções:

atrair
explicar
convencer
encaminhar

Tudo isso com suporte de rastreamento e conteúdo auxiliar.

🏁 Resumo executivo

O unitvsite.com.br é um ecossistema digital completo para:

aquisição de tráfego
educação do visitante
venda de recargas
suporte ao usuário
retenção pós-clique
reforço de marca
otimização de campanhas
📞 Contato operacional
Site
txt
txt
Copiar
unitvsite.com.br

Canais principais
WhatsApp
Kirvano
páginas de suporte
blog
tutoriais
🧠 Observação final

O valor real deste projeto está na combinação de:

boas páginas
rastreamento limpo
jornada clara
suporte rápido
oferta bem posicionada

Se esses cinco pontos estiverem funcionando juntos, a tendência é o site performar melhor com o tempo.

text
texto
Copiar

