// frontend/app.js

const API_BASE_URL = window.location.origin;

// DOM Elements
const backendStatus = document.getElementById("backend-status");
const ideaForm = document.getElementById("idea-form");
const inputTopic = document.getElementById("input-topic");
const inputPlatform = document.getElementById("input-platform");
const inputAudience = document.getElementById("input-audience");
const btnStream = document.getElementById("btn-stream");
const outputBox = document.getElementById("output-box");
const streamIndicator = document.getElementById("stream-indicator");
const streamStatus = document.getElementById("stream-status");

// 1. Healthcheck Backend
async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`);
    if (res.ok) {
      const data = await res.json();
      backendStatus.innerText = `ONLINE (${data.service})`;
      backendStatus.parentElement.className = backendStatus.parentElement.className.replace('bg-arcadeOrange', 'bg-arcadeMint');
    } else {
      throw new Error();
    }
  } catch (err) {
    backendStatus.innerText = "BACKEND OFFLINE ⚠️";
    backendStatus.parentElement.className = backendStatus.parentElement.className.replace('bg-arcadeMint', 'bg-arcadeOrange');
  }
}

// 2. Tab Switcher
function switchTab(tabName) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('bg-arcadePeach');
    btn.classList.add('bg-white');
  });

  document.getElementById(`tab-${tabName}`).classList.remove('hidden');
  const activeBtn = document.getElementById(`tab-btn-${tabName}`);
  activeBtn.classList.remove('bg-white');
  activeBtn.classList.add('bg-arcadePeach');
}

// 3. Clear Console
function clearConsole() {
  outputBox.innerHTML = `<p class="text-gray-400 font-mono text-sm">Monitor dibersihkan. Menunggu instruksi berikutnya... 🏭</p>`;
  streamStatus.innerText = "IDLE";
}

// 4. ROBUST JSON-SSE STREAM CONSUMER
ideaForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const topic = encodeURIComponent(inputTopic.value.trim());
  const platform = encodeURIComponent(inputPlatform.value);
  const audience = encodeURIComponent(inputAudience.value.trim());

  if (!topic || !audience) return;

  btnStream.disabled = true;
  btnStream.classList.add("opacity-50", "cursor-not-allowed");
  streamIndicator.classList.remove("hidden");
  streamStatus.innerText = "STREAMING...";
  
  let accumulatedMarkdown = "";
  outputBox.innerHTML = "";

  const endpoint = `${API_BASE_URL}/api/v1/ideas/generate/stream?topic=${topic}&platform=${platform}&target_audience=${audience}`;

  try {
    const response = await fetch(endpoint);
    if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let sseBuffer = "";

    // Smooth render via RAF (60 FPS)
    let renderPending = false;
    const scheduleRender = () => {
      if (!renderPending) {
        renderPending = true;
        requestAnimationFrame(() => {
          outputBox.innerHTML = marked.parse(accumulatedMarkdown);
          outputBox.scrollTop = outputBox.scrollHeight;
          renderPending = false;
        });
      }
    };

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      sseBuffer += decoder.decode(value, { stream: true });
      const lines = sseBuffer.split("\n");
      sseBuffer = lines.pop(); // Pertahankan chunk parsial

      for (const line of lines) {
        const cleanLine = line.trim();
        if (cleanLine.startsWith("data: ")) {
          const rawData = cleanLine.slice(6);
          try {
            // Parse JSON payload yang dikirim Backend
            const parsed = JSON.parse(rawData);
            if (parsed.text) {
              accumulatedMarkdown += parsed.text;
              scheduleRender();
            }
          } catch {
            // Fallback jika berupa text biasa
            accumulatedMarkdown += rawData;
            scheduleRender();
          }
        }
      }
    }

    // Render Final Markdown
    outputBox.innerHTML = marked.parse(accumulatedMarkdown);
    outputBox.scrollTop = outputBox.scrollHeight;
    streamStatus.innerText = "COMPLETED ✅";

  } catch (error) {
    console.error("Stream error:", error);
    outputBox.innerHTML += `<div class="bg-red-50 border-2 border-red-500 p-3 rounded-lg text-red-700 font-bold mt-4 font-mono text-sm">🚨 [ERROR]: ${error.message}</div>`;
    streamStatus.innerText = "FAILED ❌";
  } finally {
    btnStream.disabled = false;
    btnStream.classList.remove("opacity-50", "cursor-not-allowed");
    streamIndicator.classList.add("hidden");
  }
});

// Run Healthcheck
checkBackendHealth();