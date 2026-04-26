const API_URL = "https://sesiescolafacilita.onrender.com/api/chat";

const fileBox = document.getElementById("fileBox");
const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");
const uploadForm = document.getElementById("uploadForm");
const submissionsList = document.getElementById("submissionsList");

const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");

let submissions = [];

fileBox.addEventListener("click", () => {
  fileInput.click();
});

fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    fileName.textContent = fileInput.files[0].name;
  } else {
    fileName.textContent = "Nenhum arquivo selecionado";
  }
});

uploadForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const name = document.getElementById("studentName").value.trim();
  const turma = document.getElementById("studentClass").value.trim();
  const teacher = document.getElementById("teacherName").value.trim();
  const subject = document.getElementById("subject").value.trim();
  const title = document.getElementById("activityTitle").value.trim();
  const description = document.getElementById("description").value.trim();
  const file = fileInput.files[0];

  if (!file) {
    alert("Selecione um arquivo antes de registrar o envio.");
    return;
  }

  const submission = {
    name,
    turma,
    teacher,
    subject,
    title,
    description,
    fileName: file.name,
    date: new Date().toLocaleString("pt-BR")
  };

  submissions.unshift(submission);
  renderSubmissions();

  uploadForm.reset();
  fileName.textContent = "Nenhum arquivo selecionado";

  alert("Envio registrado no site. Para salvar de verdade no servidor, é necessário criar uma rota de upload no Flask.");
});

function renderSubmissions() {
  submissionsList.innerHTML = "";

  if (submissions.length === 0) {
    submissionsList.innerHTML = `<p class="empty">Nenhum envio registrado ainda.</p>`;
    return;
  }

  submissions.forEach((item) => {
    const div = document.createElement("div");
    div.className = "submission-item";

    div.innerHTML = `
      <strong>${escapeHTML(item.title)}</strong>
      <span>${escapeHTML(item.name)} • ${escapeHTML(item.turma)}</span><br>
      <span>${escapeHTML(item.subject)} • ${escapeHTML(item.teacher)}</span><br>
      <span>Arquivo: ${escapeHTML(item.fileName)}</span><br>
      <span>${item.date}</span>
    `;

    submissionsList.appendChild(div);
  });
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = chatInput.value.trim();

  if (!question) return;

  addMessage(question, "user");
  chatInput.value = "";

  const loadingMessage = addMessage("Allen está pensando...", "bot loading");

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        question: question
      })
    });

    if (!response.ok) {
      throw new Error("Erro na resposta do servidor.");
    }

    const data = await response.json();

    loadingMessage.remove();

    if (data.status === "success") {
      addMessage(data.message, "bot");
    } else {
      addMessage("Não consegui responder agora. Tente novamente.", "bot");
    }

  } catch (error) {
    loadingMessage.remove();

    addMessage(
      "Não consegui conectar ao servidor do Allen. Verifique se o servidor está online no Render.",
      "bot"
    );

    console.error(error);
  }
});

function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = `message ${type}`;
  div.textContent = text;

  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  return div;
}

function escapeHTML(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
