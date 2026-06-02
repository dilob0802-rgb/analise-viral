import os
import sys
import json
import requests
import xml.etree.ElementTree as ET
import urllib.parse
from datetime import datetime
from googleapiclient.discovery import build
from deep_translator import GoogleTranslator

# Tenta importar a biblioteca do Gemini
try:
    import google.generativeai as genai
    HAS_GEMINI_LIB = True
except ImportError:
    HAS_GEMINI_LIB = False

# Lista de palavras-chave para filtrar conteúdos políticos
POLITICAL_KEYWORDS = [
    'lula', 'bolsonaro', 'política', 'politica', 'governo', 'presidente', 'senado', 
    'eleição', 'eleições', 'eleicao', 'eleicoes', 'deputado', 'stf', 'ministro', 
    'congresso', 'biden', 'trump', 'putin', 'guerra', 'partido político', 'partido politico', 
    'impeachment', 'câmara', 'camara', 'senador', 'prefeito', 'vereador', 'voto', 
    'votação', 'votacao', 'esquerda', 'direita', 'comunismo', 'capitalismo', 'militar',
    'democracia', 'ditadura', 'ministério', 'ministerio', 'corrupção', 'corrupcao'
]

def contains_politics(text):
    """Retorna True se o texto contiver palavras-chave sobre política."""
    if not text:
        return False
    text_lower = text.lower()
    for keyword in POLITICAL_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

def translate_text(text, source='auto', target='pt'):
    """Traduz textos automaticamente para o português."""
    if not text:
        return text
    try:
        return GoogleTranslator(source=source, target=target).translate(text)
    except Exception as e:
        print(f"Aviso: Não foi possível traduzir o texto '{text}': {e}", file=sys.stderr)
        return text

def get_google_trends(geo="BR", limit=5):
    """Coleta as principais notícias do Google Notícias (Google News) como tendências atuais."""
    if geo == "BR":
        url = "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419"
    else:
        url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
        
    trends = []
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        for item in root.findall('.//item'):
            title = item.find('title').text or ""
            
            # Separa o título do nome da fonte (que o Google coloca após o último hífen " - ")
            title_parts = title.rsplit(" - ", 1)
            clean_title = title_parts[0] if len(title_parts) > 1 else title
            source = title_parts[1] if len(title_parts) > 1 else "Google Notícias"
            
            # Filtro de política
            if contains_politics(clean_title):
                continue
                
            trends.append({
                'title': clean_title,
                'traffic': source  # Armazena o nome da fonte da notícia para exibição
            })
            
            if len(trends) >= limit:
                break
                
        return trends
    except Exception as e:
        print(f"Erro ao obter Google Notícias ({geo}): {e}", file=sys.stderr)
        return []

def get_youtube_trending(api_key, region_code="BR", limit=5):
    """Busca os vídeos mais populares do YouTube no momento via API oficial."""
    if not api_key:
        print(f"Chave da API do YouTube não fornecida. Pulando busca para região {region_code}.", file=sys.stderr)
        return []
        
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=region_code,
            maxResults=limit * 3  # Pede mais para garantir que teremos o suficiente após o filtro de política
        )
        response = request.execute()
        
        videos = []
        for item in response.get('items', []):
            video_id = item['id']
            title = item['snippet']['title']
            channel = item['snippet']['channelTitle']
            description = item['snippet']['description']
            
            # Filtro de política
            if contains_politics(title) or contains_politics(description) or contains_politics(channel):
                continue
                
            videos.append({
                'title': title,
                'channel': channel,
                'url': f"https://youtu.be/{video_id}"
            })
            
            if len(videos) >= limit:
                break
                
        return videos
    except Exception as e:
        print(f"Erro ao obter vídeos do YouTube ({region_code}): {e}", file=sys.stderr)
        return []

def format_report_fallback(trends_br, trends_global, yt_br, yt_global):
    """Formata o relatório padrão em português com tradução automática dos itens globais."""
    lines = []
    lines.append("🤖 *RELATÓRIO DIÁRIO DE TENDÊNCIAS* 🤖\n")
    
    # 1. Google Notícias Brasil
    lines.append("🇧🇷 *Google Notícias - Brasil*")
    if trends_br:
        for idx, trend in enumerate(trends_br, 1):
            lines.append(f"{idx}. {trend['title']} (Fonte: {trend['traffic']})")
    else:
        lines.append("Sem notícias disponíveis ou todas filtradas.")
    lines.append("")
    
    # 2. Google Notícias Global (EUA) - Traduzido
    lines.append("🌎 *Google Notícias - Global (Traduzido)*")
    if trends_global:
        for idx, trend in enumerate(trends_global, 1):
            # Traduz o título da notícia para o português
            translated = translate_text(trend['title'], source='en', target='pt')
            # Traduz o nome da fonte da notícia para o português
            translated_source = translate_text(trend['traffic'], source='en', target='pt')
            if translated.lower() != trend['title'].lower():
                lines.append(f"{idx}. {translated} _({trend['title']})_ - Fonte: {translated_source}")
            else:
                lines.append(f"{idx}. {trend['title']} (Fonte: {translated_source})")
    else:
        lines.append("Sem notícias disponíveis ou todas filtradas.")
    lines.append("")
    
    # 3. YouTube Brasil
    lines.append("🎥 *Vídeos em Alta - YouTube Brasil*")
    if yt_br:
        for idx, video in enumerate(yt_br, 1):
            lines.append(f"{idx}. {video['title']}\n   Canal: _{video['channel']}_\n   🔗 {video['url']}")
    else:
        lines.append("Sem vídeos disponíveis ou todos filtrados.")
    lines.append("")
    
    # 4. YouTube Global (EUA) - Traduzido
    lines.append("🌐 *Vídeos em Alta - YouTube Global (Traduzido)*")
    if yt_global:
        for idx, video in enumerate(yt_global, 1):
            translated_title = translate_text(video['title'], source='en', target='pt')
            lines.append(f"{idx}. {translated_title}\n   Canal: _{video['channel']}_\n   🔗 {video['url']}")
    else:
        lines.append("Sem vídeos disponíveis ou todos filtrados.")
        
    return "\n".join(lines)

def generate_insights_with_gemini(api_key, trends_br, trends_global, yt_br, yt_global):
    """Utiliza a inteligência do Gemini para criar ideias e análises para o TikTok/Instagram."""
    if not HAS_GEMINI_LIB or not api_key:
        return None
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Constrói o contexto em texto das tendências coletadas
        context = "NOTÍCIAS EM DESTAQUE GOOGLE NOTÍCIAS BRASIL:\n"
        for t in trends_br:
            context += f"- {t['title']} (Fonte: {t['traffic']})\n"
            
        context += "\nNOTÍCIAS EM DESTAQUE GOOGLE NOTÍCIAS GLOBAL (EUA):\n"
        for t in trends_global:
            context += f"- {t['title']} (Fonte: {t['traffic']})\n"
            
        if yt_br:
            context += "\nVÍDEOS POPULARES YOUTUBE BRASIL:\n"
            for v in yt_br:
                context += f"- {v['title']} (Canal: {v['channel']}, Link: {v['url']})\n"
                
        if yt_global:
            context += "\nVÍDEOS POPULARES YOUTUBE GLOBAL (EUA):\n"
            for v in yt_global:
                context += f"- {v['title']} (Canal: {v['channel']}, Link: {v['url']})\n"
        
        prompt = f"""
Você é um estrategista de conteúdo digital de alta performance, especialista em tendências para TikTok, Instagram Reels e YouTube Shorts.

Sua tarefa é analisar a lista de tendências coletadas hoje e gerar um relatório diário focado em ideias de conteúdo.
O relatório deve ser enviado no WhatsApp, portanto use uma formatação limpa e envolvendo: utilize tópicos curtos, negritos (*) e emoticons amigáveis.

REGRAS CRÍTICAS:
1. Responda inteiramente em Português do Brasil (PT-BR). Traduza conceitos globais para facilitar o entendimento.
2. EXCLUA COMPLETAMENTE qualquer menção ou termo sobre política (governantes, deputados, eleições, presidentes, escândalos políticos, etc.). Foco 100% em entretenimento, curiosidades, negócios, tecnologia, memes, esportes e cultura geral.
3. Para as tendências mais fortes, crie ideias de ganchos rápidos de vídeo para o usuário postar no TikTok/Instagram (ex: sugestão de áudio, legenda ou formato de vídeo).

Aqui estão as tendências de hoje:
{context}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Erro ao gerar análise com o Gemini: {e}", file=sys.stderr)
        return None

def save_to_json_file(trends_br, trends_global, yt_br, yt_global, output_dir="web", max_history=30):
    """Salva os dados coletados e traduzidos num histórico JSON para o Dashboard Web."""
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(f"Erro ao criar diretório '{output_dir}': {e}", file=sys.stderr)
            return
            
    filepath = os.path.join(output_dir, "reports.json")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Processa as tendências globais com tradução para salvar já traduzido no JSON
    processed_global = []
    for t in trends_global:
        translated = translate_text(t['title'], source='en', target='pt')
        translated_source = translate_text(t['traffic'], source='en', target='pt')
        processed_global.append({
            'title': translated,
            'original': t['title'],
            'traffic': translated_source
        })
        
    processed_yt_global = []
    for v in yt_global:
        translated = translate_text(v['title'], source='en', target='pt')
        processed_yt_global.append({
            'title': translated,
            'original': v['title'],
            'channel': v['channel'],
            'url': v['url']
        })
        
    # Estrutura do relatório diário
    new_report = {
        "date": today_str,
        "trends_br": trends_br,
        "trends_global": processed_global,
        "yt_br": yt_br,
        "yt_global": processed_yt_global
    }
    
    history = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                history = json.load(f)
                if not isinstance(history, list):
                    history = []
        except Exception as e:
            print(f"Aviso: Erro ao ler histórico JSON anterior: {e}", file=sys.stderr)
            history = []
            
    # Remove duplicados do mesmo dia
    history = [item for item in history if item.get("date") != today_str]
    
    # Insere o mais recente no início do histórico
    history.insert(0, new_report)
    
    # Limita o histórico ao tamanho máximo configurado
    history = history[:max_history]
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"Histórico do site atualizado com sucesso em '{filepath}'!")
    except Exception as e:
        print(f"Erro ao salvar arquivo de histórico JSON: {e}", file=sys.stderr)

def send_whatsapp(phone, apikey, message):
    """Envia a mensagem de WhatsApp usando o serviço gratuito do CallMeBot."""
    if not phone or not apikey:
        print("Erro: WHATSAPP_PHONE ou WHATSAPP_API_KEY não configurados. Não é possível enviar.", file=sys.stderr)
        return False
        
    encoded_message = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_message}&apikey={apikey}"
    
    try:
        response = requests.get(url, timeout=25)
        if response.status_code == 200:
            print("Mensagem enviada com sucesso para o WhatsApp!")
            return True
        else:
            print(f"Erro do CallMeBot (Status {response.status_code}): {response.text}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Erro de conexão com o CallMeBot: {e}", file=sys.stderr)
        return False

def load_env_file():
    """Tenta carregar variáveis de um arquivo .env se ele existir localmente."""
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def main():
    # Ajusta codificação de saída no Windows para evitar UnicodeEncodeError com emojis
    if sys.platform.startswith('win'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    # Carrega variáveis locais se existirem (.env)
    load_env_file()
    
    youtube_api_key = os.environ.get('YOUTUBE_API_KEY')
    whatsapp_phone = os.environ.get('WHATSAPP_PHONE')
    whatsapp_api_key = os.environ.get('WHATSAPP_API_KEY')
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    
    # Coleta de dados
    print("Coletando notícias em alta do Google Notícias (Brasil)...")
    trends_br = get_google_trends(geo="BR", limit=5)
    
    print("Coletando notícias em alta do Google Notícias (Global)...")
    trends_global = get_google_trends(geo="US", limit=5)
    
    print("Coletando vídeos populares do YouTube (Brasil)...")
    yt_br = get_youtube_trending(youtube_api_key, region_code="BR", limit=5)
    
    print("Coletando vídeos populares do YouTube (Global)...")
    yt_global = get_youtube_trending(youtube_api_key, region_code="US", limit=5)
    
    # Salva o histórico de relatórios em JSON para o Dashboard
    save_to_json_file(trends_br, trends_global, yt_br, yt_global)
    
    # Decisão de Relatório (Gemini Inteligente ou Fallback Traduzido)
    report = None
    if gemini_api_key:
        print("Gerando relatório analítico inteligente com IA (Gemini)...")
        report = generate_insights_with_gemini(gemini_api_key, trends_br, trends_global, yt_br, yt_global)
        
    if not report:
        print("Formatando relatório clássico com tradução automática...")
        report = format_report_fallback(trends_br, trends_global, yt_br, yt_global)
    
    # Se o argumento '--dry-run' for passado ou se não houver chaves de WhatsApp, apenas exibe no console
    if '--dry-run' in sys.argv or not whatsapp_phone or not whatsapp_api_key:
        print("\n=== MODO DE TESTE (DRY-RUN) ===")
        print(report)
        print("===============================\n")
        if not whatsapp_phone or not whatsapp_api_key:
            print("Para enviar ao WhatsApp, configure as variáveis WHATSAPP_PHONE e WHATSAPP_API_KEY.")
    else:
        print("Enviando relatório diário para o WhatsApp...")
        send_whatsapp(whatsapp_phone, whatsapp_api_key, report)

if __name__ == "__main__":
    main()
