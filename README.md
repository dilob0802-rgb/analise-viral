# 🤖 Agente Viral de Análise Diária

Este repositório contém o código de um agente automatizado em Python que monitora diariamente as tendências de pesquisa do Google Trends (Brasil e Global) e os vídeos em alta no YouTube, filtra qualquer assunto sobre política e envia um relatório bem formatado diretamente para o seu WhatsApp.

Toda a execução é gratuita e roda em segundo plano usando o **GitHub Actions**.

---

## 🛠️ Pré-requisitos e Configuração das APIs

Para que o agente consiga coletar os dados do YouTube e enviar as mensagens no seu WhatsApp, você precisará configurar duas chaves de acesso gratuitas.

### 1. WhatsApp (CallMeBot) - Gratuito
O CallMeBot é um serviço simples que permite enviar mensagens do Python para o seu próprio WhatsApp.
1. Adicione o número do CallMeBot aos seus contatos do celular: **+34 613 01 49 37** (ou [clique aqui para abrir a conversa](https://wa.me/34613014937)).
2. Envie a seguinte mensagem no chat do WhatsApp para eles:
   ```text
   I allow callmebot to send me messages
   ```
3. O bot responderá com uma mensagem contendo sua **ApiKey** (um número de 6 ou mais dígitos) e um link de teste. Guarde essa chave!

### 2. YouTube Data API v3 (Google Cloud) - Gratuito
Para obter a chave de acesso do YouTube:
1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Faça login com sua conta do Google e crie um novo projeto (ex: `Agente-Viral-Analise`).
3. No menu lateral esquerdo, vá em **APIs e Serviços** > **Biblioteca**.
4. Procure por **YouTube Data API v3** e clique em **Ativar**.
5. Após ativar, clique no menu lateral **APIs e Serviços** > **Credenciais**.
6. Clique no botão **+ Criar Credenciais** na parte superior e selecione **Chave de API**.
7. Copie a chave de API gerada. Guarde-a de forma segura.

---

## 🚀 Como Hospedar e Automatizar no GitHub

Depois de conseguir as chaves, siga os passos abaixo para colocar o agente para rodar na nuvem:

### Passo 1: Subir o código para o seu GitHub
1. Crie um repositório **Privado** no seu GitHub.
2. Inicialize o repositório localmente na sua máquina dentro da pasta do projeto e envie os arquivos para lá:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git
   git push -u origin main
   ```

### Passo 2: Configurar as Variáveis Secretas (Secrets)
Para não expor suas chaves publicamente, configure-as como Secrets no GitHub:
1. Vá na página do seu repositório no GitHub.
2. Clique na aba **Settings** (Configurações) no topo.
3. No menu esquerdo, vá em **Secrets and variables** > **Actions**.
4. Clique no botão verde **New repository secret** (Novo segredo do repositório) para criar cada uma destas 3 variáveis:

| Nome do Segredo | Descrição / Valor |
| :--- | :--- |
| `YOUTUBE_API_KEY` | A chave de API gerada no Google Cloud Console. |
| `WHATSAPP_PHONE` | Seu número de WhatsApp com DDI e DDD (Ex: `5511999999999` para o Brasil). |
| `WHATSAPP_API_KEY` | A chave de API enviada pelo bot do CallMeBot no WhatsApp. |

### Passo 3: Executar ou Testar Manualmente
* **Execução Automática**: O script está configurado para rodar sozinho todos os dias às **09:00 (Horário de Brasília)**.
* **Execução Manual**: Se quiser gerar um relatório na hora:
  1. Vá na aba **Actions** no topo do repositório no GitHub.
  2. No menu esquerdo, clique em **Daily Viral Trends Report**.
  3. Clique no botão **Run workflow** do lado direito e selecione a branch `main`.
  4. O script iniciará imediatamente e enviará o relatório para o seu WhatsApp em instantes!

---

## 💻 Teste Local (Dry Run)

Se você quiser rodar o agente localmente no seu computador sem enviar nada para o WhatsApp (apenas para ver o relatório no terminal):

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute o script com a flag `--dry-run`:
   ```bash
   python agent.py --dry-run
   ```

### 🖥️ Como visualizar o Dashboard Web Localmente
Como os navegadores bloqueiam a leitura de arquivos locais via JavaScript (`fetch()`) por motivos de segurança (CORS), para visualizar o site localmente você precisa de um servidor local simples.
1. Abra o terminal na pasta do projeto e digite:
   ```bash
   python -m http.server 8000
   ```
2. Abra seu navegador no endereço: [http://localhost:8000/web/](http://localhost:8000/web/)

---

## 🌐 Como configurar o Site no GitHub Pages

Para colocar o seu Dashboard no ar gratuitamente e atualizado automaticamente:
1. Na página do seu repositório no GitHub, clique na aba **Settings** (Configurações) no topo.
2. No menu esquerdo, clique em **Pages**.
3. Na seção **Build and deployment**:
   - Em **Source**, deixe como *Deploy from a branch*.
   - Em **Branch**, selecione a branch `main` e altere a pasta de `/ (root)` para **`/web`**.
   - Clique em **Save**.
4. Em alguns minutos, o GitHub disponibilizará o link público onde seu histórico de relatórios estará online!
