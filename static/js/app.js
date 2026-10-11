/**
 * Ollama AI Chatbot & Admin Portal
 * Modern Full-Width Canvas, Dedicated Admin Console, Pin File Upload, Dynamic Greeting
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements - Navigation & Auth
  const authModal = document.getElementById("auth-modal");
  const tabLoginBtn = document.getElementById("tab-login-btn");
  const tabRegisterBtn = document.getElementById("tab-register-btn");
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const authAlert = document.getElementById("auth-alert");

  const loginUsernameInput = document.getElementById("login-username");
  const loginPasswordInput = document.getElementById("login-password");
  const regUsernameInput = document.getElementById("reg-username");
  const regEmailInput = document.getElementById("reg-email");
  const regPasswordInput = document.getElementById("reg-password");
  const fillAdminBtn = document.getElementById("fill-admin-btn");
  const loginSubmitBtn = document.getElementById("login-submit-btn");
  const regSubmitBtn = document.getElementById("reg-submit-btn");

  const userProfileChip = document.getElementById("user-profile-chip");
  const userNameDisplay = document.getElementById("user-name-display");
  const userRoleBadge = document.getElementById("user-role-badge");
  const userAvatarLetter = document.getElementById("user-avatar-letter");
  const logoutBtn = document.getElementById("logout-btn");

  // Navigation & Status Controls
  const userNavControls = document.getElementById("user-nav-controls");
  const ollamaStatusBadge = document.getElementById("ollama-status-badge");
  const statusText = document.getElementById("status-text");
  const modelSelect = document.getElementById("model-select");
  const clearMemoryBtn = document.getElementById("clear-memory-btn");

  // Views
  const userChatView = document.getElementById("user-chat-view");
  const adminView = document.getElementById("admin-view");

  // Chat Elements
  const chatMessages = document.getElementById("chat-messages");
  const chatInput = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const pinUploadBtn = document.getElementById("pin-upload-btn");
  const pdfUploadInput = document.getElementById("pdf-upload-input");
  const pdfStatusContainer = document.getElementById("pdf-status-container");

  // Admin Elements
  const totalUsersCount = document.getElementById("total-users-count");
  const adminSearchInput = document.getElementById("admin-search-input");
  const adminUserTableBody = document.getElementById("admin-user-table-body");
  const adminRefreshBtn = document.getElementById("admin-refresh-btn");

  // App State
  let jwtToken = localStorage.getItem("jwt_token") || null;
  let currentUser = null;
  let isProcessing = false;
  let adminUsersList = [];
  let attachedPdfInfo = null;

  // Initialize Application
  initApp();

  async function initApp() {
    setupEventListeners();
    await checkAuth();
    await fetchOllamaStatus();
  }

  function setupEventListeners() {
    // Auth Tabs
    tabLoginBtn.addEventListener("click", () => switchAuthTab("login"));
    tabRegisterBtn.addEventListener("click", () => switchAuthTab("register"));

    // Quick Fill Admin Credentials
    fillAdminBtn.addEventListener("click", () => {
      loginUsernameInput.value = "admin";
      loginPasswordInput.value = "adminpassword";
      hideAuthAlert();
    });

    // Auth Forms
    loginForm.addEventListener("submit", handleLogin);
    registerForm.addEventListener("submit", handleRegister);
    logoutBtn.addEventListener("click", handleLogout);

    // Chat Actions
    sendBtn.addEventListener("click", handleSendMessage);
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    });

    // Auto-resize chat textarea
    chatInput.addEventListener("input", () => {
      chatInput.style.height = "auto";
      chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + "px";
    });

    // Pin Button (📎) File Attachment Trigger
    pinUploadBtn.addEventListener("click", () => {
      if (!jwtToken) {
        showModal(authModal);
        showAuthAlert("Please sign in first to attach documents.");
        return;
      }
      pdfUploadInput.click();
    });

    pdfUploadInput.addEventListener("change", handlePdfUpload);

    // Clear Memory
    clearMemoryBtn.addEventListener("click", handleClearMemory);

    // Admin Toolbar
    if (adminSearchInput) {
      adminSearchInput.addEventListener("input", handleAdminSearch);
    }
    if (adminRefreshBtn) {
      adminRefreshBtn.addEventListener("click", fetchAdminUsers);
    }

    // Model Change
    modelSelect.addEventListener("change", (e) => {
      console.log("Selected model changed to:", e.target.value);
    });
  }

  // ==========================================
  // AUTHENTICATION LOGIC
  // ==========================================

  async function checkAuth() {
    if (!jwtToken) {
      showModal(authModal);
      return;
    }

    try {
      const res = await fetch("/api/me", {
        headers: { Authorization: `Bearer ${jwtToken}` }
      });
      const data = await res.json();
      if (data.status === "success" && data.user) {
        currentUser = data.user;
        updateViewMode();
        closeModal(authModal);
      } else {
        handleLogout();
      }
    } catch (err) {
      console.error("Auth check failed:", err);
      handleLogout();
    }
  }

  async function handleLogin(e) {
    e.preventDefault();
    hideAuthAlert();

    const username = loginUsernameInput.value.trim();
    const password = loginPasswordInput.value.trim();

    if (!username || !password) {
      showAuthAlert("Please enter both username and password.");
      return;
    }

    // Button loading state
    loginSubmitBtn.disabled = true;
    loginSubmitBtn.innerHTML = `<span>⏳ Signing in...</span>`;

    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();

      if (res.ok && data.status === "success") {
        jwtToken = data.token;
        localStorage.setItem("jwt_token", jwtToken);
        currentUser = data.user;
        loginForm.reset();
        closeModal(authModal);
        updateViewMode();
      } else {
        // High visibility error alert when credentials don't match
        const errorMsg = data.message || "Invalid username or password. Please try again.";
        showAuthAlert(errorMsg);
      }
    } catch (err) {
      showAuthAlert("Server connection error. Please ensure the backend is running.");
    } finally {
      loginSubmitBtn.disabled = false;
      loginSubmitBtn.innerHTML = `<span>Sign In to Continue</span>`;
    }
  }

  async function handleRegister(e) {
    e.preventDefault();
    hideAuthAlert();

    const username = regUsernameInput.value.trim();
    const email = regEmailInput.value.trim();
    const password = regPasswordInput.value.trim();

    if (!username || !email || !password) {
      showAuthAlert("Please fill in all registration fields.");
      return;
    }

    regSubmitBtn.disabled = true;
    regSubmitBtn.innerHTML = `<span>⏳ Creating account...</span>`;

    try {
      const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password })
      });
      const data = await res.json();

      if (res.ok && data.status === "success") {
        jwtToken = data.token;
        localStorage.setItem("jwt_token", jwtToken);
        currentUser = data.user;
        registerForm.reset();
        closeModal(authModal);
        updateViewMode();
      } else {
        showAuthAlert(data.message || "Registration failed. Username may already exist.");
      }
    } catch (err) {
      showAuthAlert("Failed to submit registration request.");
    } finally {
      regSubmitBtn.disabled = false;
      regSubmitBtn.innerHTML = `<span>Create My Account</span>`;
    }
  }

  function handleLogout() {
    jwtToken = null;
    currentUser = null;
    localStorage.removeItem("jwt_token");

    // Clear state
    userProfileChip.style.display = "none";
    chatMessages.innerHTML = "";
    attachedPdfInfo = null;
    renderPdfAttachmentChip(null);

    // Hide both views and show login modal
    userChatView.style.display = "none";
    adminView.style.display = "none";
    hideAuthAlert();
    showModal(authModal);
  }

  function updateViewMode() {
    if (!currentUser) return;

    // Header Greeting Display: Welcome, <username>
    userNameDisplay.textContent = currentUser.username;
    userRoleBadge.textContent = currentUser.role;
    userRoleBadge.className = `role-badge ${currentUser.role}`;
    userAvatarLetter.textContent = currentUser.username.charAt(0).toUpperCase();
    userProfileChip.style.display = "flex";

    if (currentUser.role === "admin") {
      // ==========================================
      // ADMIN PORTAL MODE (Users List ONLY, No Chat)
      // ==========================================
      userChatView.style.display = "none";
      userChatView.classList.remove("active");

      adminView.style.display = "flex";
      adminView.classList.add("active");

      // Hide user chat controls in nav
      userNavControls.style.display = "none";
      clearMemoryBtn.style.display = "none";

      // Clear any chat messages from DOM
      chatMessages.innerHTML = "";

      // Load registered users immediately
      fetchAdminUsers();
    } else {
      // ==========================================
      // STANDARD USER CHAT MODE
      // ==========================================
      adminView.style.display = "none";
      adminView.classList.remove("active");

      userChatView.style.display = "flex";
      userChatView.classList.add("active");

      // Show user chat controls in nav
      userNavControls.style.display = "flex";
      clearMemoryBtn.style.display = "inline-flex";

      // Display Warm Welcome Hero Card if messages empty
      if (chatMessages.children.length === 0) {
        renderWelcomeHero(currentUser.username);
      }
    }
  }

  function renderWelcomeHero(username) {
    chatMessages.innerHTML = `
      <div class="welcome-hero-card">
        <div class="hero-icon">👋</div>
        <div>
          <h2 class="hero-title">Welcome, ${escapeHtml(username)}!</h2>
          <p class="hero-subtitle">
            I am your intelligent assistant powered by Ollama and LangChain.
            Ask questions, check attendance, or attach documents for strict RAG querying.
          </p>
          <div class="hero-tips-list">
            <div class="hero-tip-chip">📎 <strong>PDF RAG</strong>: Click the pin icon to upload documents</div>
            <div class="hero-tip-chip">📊 <strong>Attendance</strong>: "I attended 18 out of 24 classes"</div>
            <div class="hero-tip-chip">🌐 <strong>Wikipedia</strong>: "Search Wikipedia for Quantum Computing"</div>
          </div>
        </div>
      </div>
    `;
  }

  function switchAuthTab(tab) {
    hideAuthAlert();
    if (tab === "login") {
      tabLoginBtn.classList.add("active");
      tabRegisterBtn.classList.remove("active");
      loginForm.style.display = "flex";
      registerForm.style.display = "none";
    } else {
      tabRegisterBtn.classList.add("active");
      tabLoginBtn.classList.remove("active");
      registerForm.style.display = "flex";
      loginForm.style.display = "none";
    }
  }

  function showAuthAlert(msg, type = "error") {
    authAlert.innerHTML = `<span>⚠️ ${escapeHtml(msg)}</span>`;
    authAlert.className = `auth-alert ${type}`;
    authAlert.style.display = "flex";
  }

  function hideAuthAlert() {
    authAlert.style.display = "none";
    authAlert.innerHTML = "";
  }

  // ==========================================
  // DEDICATED ADMIN PORTAL LOGIC (Users List Only)
  // ==========================================

  async function fetchAdminUsers() {
    if (!currentUser || currentUser.role !== "admin") return;

    adminUserTableBody.innerHTML = `
      <tr>
        <td colspan="5" style="text-align: center; padding: 36px; color: var(--text-muted);">
          ⏳ Fetching registered users from Admin API...
        </td>
      </tr>
    `;

    try {
      const res = await fetch("/api/admin/users", {
        headers: { Authorization: `Bearer ${jwtToken}` }
      });
      const data = await res.json();

      if (res.ok && data.status === "success" && data.users) {
        adminUsersList = data.users;
        totalUsersCount.textContent = `Total Users: ${data.total_users}`;
        renderAdminUserTable(adminUsersList);
      } else {
        adminUserTableBody.innerHTML = `
          <tr>
            <td colspan="5" style="text-align: center; padding: 30px; color: var(--accent-rose);">
              ⚠️ ${data.message || "Failed to load user records."}
            </td>
          </tr>
        `;
      }
    } catch (err) {
      adminUserTableBody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align: center; padding: 30px; color: var(--accent-rose);">
            ⚠️ Network error connecting to Admin Users API.
          </td>
        </tr>
      `;
    }
  }

  function renderAdminUserTable(users) {
    if (!users || users.length === 0) {
      adminUserTableBody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align: center; padding: 40px; color: var(--text-muted);">
            No user records found.
          </td>
        </tr>
      `;
      return;
    }

    adminUserTableBody.innerHTML = users.map(u => {
      const initial = u.username ? u.username.charAt(0).toUpperCase() : "U";
      const createdDate = u.created_at ? escapeHtml(u.created_at) : "N/A";
      return `
        <tr>
          <td><span class="table-id-tag">#${u.id}</span></td>
          <td>
            <div class="table-user-cell">
              <div class="table-user-avatar">${initial}</div>
              <span class="table-username">${escapeHtml(u.username)}</span>
            </div>
          </td>
          <td style="color: var(--text-secondary);">${escapeHtml(u.email)}</td>
          <td><span class="role-badge ${u.role}">${u.role}</span></td>
          <td style="color: var(--text-muted); font-size: 0.82rem;">${createdDate}</td>
        </tr>
      `;
    }).join("");
  }

  function handleAdminSearch(e) {
    const query = e.target.value.toLowerCase().trim();
    if (!query) {
      renderAdminUserTable(adminUsersList);
      return;
    }

    const filtered = adminUsersList.filter(u => {
      const matchName = u.username && u.username.toLowerCase().includes(query);
      const matchEmail = u.email && u.email.toLowerCase().includes(query);
      const matchRole = u.role && u.role.toLowerCase().includes(query);
      const matchId = String(u.id).includes(query);
      return matchName || matchEmail || matchRole || matchId;
    });

    renderAdminUserTable(filtered);
  }

  // ==========================================
  // OLLAMA ENGINE STATUS & MODEL SELECTOR
  // ==========================================

  async function fetchOllamaStatus() {
    try {
      const res = await fetch("/api/ollama-status");
      const data = await res.json();

      if (data.is_online) {
        ollamaStatusBadge.className = "status-badge online";
        statusText.textContent = "Online";
      } else {
        ollamaStatusBadge.className = "status-badge offline";
        statusText.textContent = "Offline";
      }

      // Populate Model Dropdown
      if (data.available_models && data.available_models.length > 0) {
        modelSelect.innerHTML = data.available_models.map(m => `
          <option value="${m}" ${m === data.current_model ? "selected" : ""}>${m}</option>
        `).join("");
      }

      // Check PDF attachment status
      if (data.pdf_info) {
        attachedPdfInfo = data.pdf_info;
        renderPdfAttachmentChip(data.pdf_info);
      } else {
        attachedPdfInfo = null;
        renderPdfAttachmentChip(null);
      }
    } catch (err) {
      ollamaStatusBadge.className = "status-badge offline";
      statusText.textContent = "Error";
    }
  }

  // ==========================================
  // PIN (📎) FILE ATTACHMENT & PDF RAG LOGIC
  // ==========================================

  async function handlePdfUpload() {
    const file = pdfUploadInput.files[0];
    if (!file) return;

    if (!jwtToken) {
      showModal(authModal);
      showAuthAlert("Please log in to upload PDF documents.");
      pdfUploadInput.value = "";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    // Visual loading state on Pin Button
    pinUploadBtn.classList.add("uploading");
    pinUploadBtn.title = "Indexing PDF with FAISS...";

    pdfStatusContainer.innerHTML = `
      <div class="attachment-chip" style="opacity: 0.8;">
        <span>⏳ Uploading & Indexing <strong>${escapeHtml(file.name)}</strong>...</span>
      </div>
    `;

    try {
      const res = await fetch("/api/upload-pdf", {
        method: "POST",
        headers: { Authorization: `Bearer ${jwtToken}` },
        body: formData
      });

      if (res.status === 401) {
        handleLogout();
        showAuthAlert("Session expired. Please log in again.");
        return;
      }

      const data = await res.json();

      if (res.ok && data.status === "success") {
        attachedPdfInfo = data.pdf_info;
        renderPdfAttachmentChip(data.pdf_info);
        appendMessage(
          "assistant",
          `✅ Document Attached & Indexed: **${data.pdf_info.file_name}**\n📄 Pages: ${data.pdf_info.total_pages} | Chunks: ${data.pdf_info.total_chunks}\n🔒 **Strict PDF RAG Mode Activated**: All questions will now be answered strictly using this document!`,
          "PDF Search (RAG)"
        );
      } else {
        const errorMsg = data.message || "Failed to index PDF document.";
        renderPdfAttachmentChip(null);
        appendMessage("assistant", `⚠️ PDF Upload Error: ${errorMsg}`);
        alert(errorMsg);
      }
    } catch (err) {
      renderPdfAttachmentChip(null);
      appendMessage("assistant", "⚠️ Error uploading PDF: Network connection interrupted.");
      alert("Error uploading PDF document. Please check backend connection.");
    } finally {
      pinUploadBtn.classList.remove("uploading");
      pinUploadBtn.title = "Attach PDF Document (RAG Q&A)";
      pdfUploadInput.value = "";
    }
  }

  async function handleClearPdf() {
    try {
      const res = await fetch("/api/clear-pdf", {
        method: "POST",
        headers: { Authorization: `Bearer ${jwtToken}` }
      });
      const data = await res.json();
      if (data.status === "success") {
        attachedPdfInfo = null;
        renderPdfAttachmentChip(null);
        appendMessage("assistant", "🗑️ Document detached. Returned to general AI assistant mode.");
      }
    } catch (err) {
      console.error("Failed to detach PDF:", err);
    }
  }

  function renderPdfAttachmentChip(pdfInfo) {
    if (pdfInfo && (pdfInfo.file_name || pdfInfo.doc_name)) {
      const name = pdfInfo.file_name || pdfInfo.doc_name;
      const pages = pdfInfo.total_pages ? `(${pdfInfo.total_pages} pages)` : "";
      pdfStatusContainer.innerHTML = `
        <div class="attachment-chip">
          <span>📄</span>
          <span class="attachment-chip-name" title="${escapeHtml(name)}">${escapeHtml(name)}</span>
          <span style="font-size: 0.72rem; color: #a5b4fc;">${pages}</span>
          <button class="attachment-chip-remove" id="detach-pdf-btn" title="Remove attached document">✕</button>
        </div>
      `;
      const detachBtn = document.getElementById("detach-pdf-btn");
      if (detachBtn) {
        detachBtn.addEventListener("click", handleClearPdf);
      }
    } else {
      pdfStatusContainer.innerHTML = "";
    }
  }

  // ==========================================
  // CONVERSATION MEMORY MANAGEMENT
  // ==========================================

  async function handleClearMemory() {
    try {
      const res = await fetch("/api/clear-memory", {
        method: "POST",
        headers: { Authorization: `Bearer ${jwtToken}` }
      });
      const data = await res.json();
      if (data.status === "success") {
        chatMessages.innerHTML = "";
        renderWelcomeHero(currentUser.username);
        appendMessage("assistant", "🧹 Conversation memory cleared.");
      }
    } catch (err) {
      console.error("Failed to clear memory:", err);
    }
  }

  // ==========================================
  // CHAT INTERACTION LOGIC
  // ==========================================

  async function handleSendMessage() {
    if (isProcessing) return;
    const message = chatInput.value.trim();
    if (!message) return;

    if (!jwtToken) {
      showModal(authModal);
      return;
    }

    // Append User Message
    appendMessage("user", message);
    chatInput.value = "";
    chatInput.style.height = "auto";

    // Append Typing Indicator
    const typingId = appendTypingIndicator();
    isProcessing = true;
    sendBtn.disabled = true;

    try {
      const selectedModel = modelSelect.value;
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${jwtToken}`
        },
        body: JSON.stringify({ message: message, model: selectedModel })
      });

      if (res.status === 401) {
        removeTypingIndicator(typingId);
        handleLogout();
        showAuthAlert("Session expired. Please sign in again.");
        return;
      }

      const data = await res.json();
      removeTypingIndicator(typingId);

      if (res.ok && data.status === "success") {
        appendMessage("assistant", data.response, data.tool_used);
      } else {
        appendMessage("assistant", `⚠️ Error: ${data.message || "Failed to process request."}`);
      }
    } catch (err) {
      removeTypingIndicator(typingId);
      appendMessage("assistant", "⚠️ Error connecting to chatbot server backend.");
    } finally {
      isProcessing = false;
      sendBtn.disabled = false;
    }
  }

  function appendMessage(sender, text, toolUsed = null) {
    const row = document.createElement("div");
    row.className = `message-row ${sender}`;

    const avatarIcon = sender === "user" ? "👤" : "🤖";
    const toolMarkup = toolUsed ? `<div class="tool-tag">🛠️ ${escapeHtml(toolUsed)}</div>` : "";

    row.innerHTML = `
      <div class="avatar">${avatarIcon}</div>
      <div class="message-content-wrapper">
        ${toolMarkup}
        <div class="message-bubble">${formatMessageText(text)}</div>
      </div>
    `;

    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function appendTypingIndicator() {
    const id = "typing-" + Date.now();
    const row = document.createElement("div");
    row.className = "message-row assistant";
    row.id = id;
    row.innerHTML = `
      <div class="avatar">🤖</div>
      <div class="message-content-wrapper">
        <div class="typing-indicator">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    `;
    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
  }

  function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function formatMessageText(text) {
    if (!text) return "";
    let formatted = escapeHtml(text);
    // Bold text
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    // Inline code
    formatted = formatted.replace(/`([^`]+)`/g, "<code>$1</code>");
    return formatted;
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function showModal(modal) {
    modal.classList.add("active");
  }

  function closeModal(modal) {
    modal.classList.remove("active");
  }
});
