// ==================================================
// CONFIGURAÇÕES E INICIALIZAÇÃO
// ==================================================
const DATA_URL = "reports.json";
let reportsData = [];

document.addEventListener("DOMContentLoaded", () => {
  fetchReports();
});

// ==================================================
// COLETA DE DADOS (FETCH)
// ==================================================
async function fetchReports() {
  const historyList = document.getElementById("history-list");
  
  try {
    const response = await fetch(DATA_URL);
    if (!response.ok) {
      throw new Error(`Erro de rede: ${response.status}`);
    }
    
    reportsData = await response.json();
    
    if (!Array.isArray(reportsData) || reportsData.length === 0) {
      showErrorState("Nenhum relatório encontrado no arquivo de dados.");
      return;
    }
    
    // Carrega o relatório mais recente por padrão (primeiro item)
    loadReport(reportsData[0].date);
    
  } catch (error) {
    console.error("Erro ao carregar os relatórios:", error);
    showErrorState("Não foi possível carregar os dados. Certifique-se de que o script foi executado e gerou o arquivo de dados.");
  }
}



// ==================================================
// CARREGAMENTO E RENDERIZAÇÃO DO RELATÓRIO SELECIONADO
// ==================================================
function loadReport(date) {
  const report = reportsData.find(r => r.date === date);
  if (!report) return;
  
  // Atualiza a exibição da data no cabeçalho
  document.getElementById("report-date-display").textContent = formatFullDate(report.date);
  
  // 1. Renderiza Google Trends Brasil
  renderTrendsList("trends-br-list", report.trends_br);
  
  // 2. Renderiza Google Trends Global
  renderTrendsList("trends-global-list", report.trends_global, true);
  
  // 3. Renderiza YouTube Brasil
  renderVideoList("yt-br-list", report.yt_br);
  
  // 4. Renderiza YouTube Global
  renderVideoList("yt-global-list", report.yt_global, true);
}

// Renderiza a lista do Google Trends
function renderTrendsList(elementId, trends, isGlobal = false) {
  const listElement = document.getElementById(elementId);
  listElement.innerHTML = "";
  
  if (!trends || trends.length === 0) {
    listElement.innerHTML = `<li class="no-data">Nenhuma tendência disponível ou tudo filtrado.</li>`;
    return;
  }
  
  trends.forEach((trend, index) => {
    const li = document.createElement("li");
    li.classList.add("trend-item");
    
    let trendNameHTML = `<span class="trend-name">${trend.title}</span>`;
    
    // Se for global e tiver o termo original, exibe embaixo da tradução
    if (isGlobal && trend.original && trend.original.toLowerCase() !== trend.title.toLowerCase()) {
      trendNameHTML = `
        <span class="trend-name">
          ${trend.title}
          <span class="trend-original">Original: ${trend.original}</span>
        </span>
      `;
    }
    
    // Gera link de pesquisa no Google (usa o termo original para trends globais para garantir melhores resultados)
    const searchQuery = trend.original || trend.title;
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(searchQuery)}`;
    
    li.innerHTML = `
      <span class="trend-rank">${index + 1}</span>
      ${trendNameHTML}
      <span class="trend-traffic"><i class="fa-regular fa-newspaper"></i> ${trend.traffic}</span>
      <a href="${searchUrl}" target="_blank" class="trend-link-btn" title="Pesquisar no Google">
        <i class="fa-solid fa-arrow-up-right-from-square"></i>
      </a>
    `;
    
    listElement.appendChild(li);
  });
}

// Renderiza a lista de vídeos do YouTube
function renderVideoList(elementId, videos, isGlobal = false) {
  const listElement = document.getElementById(elementId);
  listElement.innerHTML = "";
  
  if (!videos || videos.length === 0) {
    listElement.innerHTML = `<li class="no-data">Nenhum vídeo em alta disponível ou tudo filtrado.</li>`;
    return;
  }
  
  videos.forEach((video) => {
    const li = document.createElement("li");
    li.classList.add("video-item");
    
    let titleHTML = `<span class="video-title">${video.title}</span>`;
    if (isGlobal && video.original && video.original.toLowerCase() !== video.title.toLowerCase()) {
      titleHTML = `
        <span class="video-title">
          ${video.title}
          <span class="video-original">Original: ${video.original}</span>
        </span>
      `;
    }
    
    li.innerHTML = `
      <div class="video-play-icon">
        <i class="fa-solid fa-play"></i>
      </div>
      <div class="video-info">
        ${titleHTML}
        <span class="video-channel"><i class="fa-regular fa-circle-user"></i> ${video.channel}</span>
      </div>
      <a href="${video.url}" target="_blank" class="video-link-btn" title="Assistir no YouTube">
        <i class="fa-solid fa-arrow-up-right-from-square"></i>
      </a>
    `;
    
    listElement.appendChild(li);
  });
}

// ==================================================
// ESTADO DE ERRO (FEEDBACK DO USUÁRIO)
// ==================================================
function showErrorState(message) {
  document.getElementById("report-date-display").textContent = "Erro ao carregar dados";
  
  const placeholders = ["trends-br-list", "trends-global-list", "yt-br-list", "yt-global-list"];
  placeholders.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.innerHTML = `<li class="no-data">${message}</li>`;
    }
  });
}

// ==================================================
// FUNÇÕES AUXILIARES DE FORMATAÇÃO DE DATA
// ==================================================
function formatShortDate(dateStr) {
  if (!dateStr) return "";
  const parts = dateStr.split("-");
  if (parts.length !== 3) return dateStr;
  
  // Retorna "DD/MM/AAAA"
  return `${parts[2]}/${parts[1]}/${parts[0]}`;
}

function formatFullDate(dateStr) {
  if (!dateStr) return "";
  const parts = dateStr.split("-");
  if (parts.length !== 3) return dateStr;
  
  const year = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10) - 1;
  const day = parseInt(parts[2], 10);
  
  const date = new Date(year, month, day);
  
  // Retorna "DD de Nome_do_Mês de AAAA" (ex: 29 de Maio de 2026)
  return date.toLocaleDateString("pt-BR", {
    day: "numeric",
    month: "long",
    year: "numeric"
  });
}
