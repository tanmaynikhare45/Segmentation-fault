    const chatbotIcon = document.getElementById("chatbot-icon");
    const chatbotWin = document.getElementById("chatbot-window");
    const closeBtn = document.getElementById("chatbot-close");

    function openChatbot() {
      chatbotWin.style.display = "flex";
      // next tick to allow CSS transition
      requestAnimationFrame(() => chatbotWin.classList.add("open"));
      // Hide the 3D model when chat opens
      if (chatbotIcon) chatbotIcon.classList.add("chat-open");
      const inputField = document.getElementById("user-input");
      if (inputField) setTimeout(() => inputField.focus(), 120);
    }

    function closeChatbot() {
      chatbotWin.classList.remove("open");
      // Show the 3D model when chat closes
      if (chatbotIcon) chatbotIcon.classList.remove("chat-open");
      // wait for transition to finish (~220ms)
      setTimeout(() => { chatbotWin.style.display = "none"; }, 220);
    }

    if (chatbotIcon) {
      chatbotIcon.onclick = function () {
        const isHidden = chatbotWin.style.display === "none" || chatbotWin.style.display === "";
        if (isHidden) openChatbot();
        // Chat only closes when clicking the close button, not the icon
      };
    }

    if (closeBtn) closeBtn.onclick = closeChatbot;

    // ESC to close
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && chatbotWin.style.display !== "none" && chatbotWin.style.display !== "") {
        closeChatbot();
      }
    });

    const messagesDiv = document.getElementById("chatbot-messages");

    function appendMessage(type, text, extraClass = "") {
    const wrapper = document.createElement("div");
    wrapper.className = `msg ${type} ${extraClass}`.trim();
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;
    wrapper.appendChild(bubble);
    messagesDiv.appendChild(wrapper);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return wrapper;
    }

    let typingEl = null;
    function showTyping() {
    typingEl = appendMessage("bot", "Typing…", "typing");
    }
    function hideTyping() {
    if (typingEl) { messagesDiv.removeChild(typingEl); typingEl = null; }
    }

    async function sendMessage() {
    const inputField = document.getElementById("user-input");
    const message = inputField.value.trim();
    if (!message) return;

    appendMessage("user", message);
    inputField.value = "";
    showTyping();

    try {
        const response = await fetch("/chatbot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
        });
        const data = await response.json();
        hideTyping();
        appendMessage("bot", data.reply || "Sorry, I couldn't process that.");
    } catch (e) {
        hideTyping();
        appendMessage("bot", "Network error. Please try again.");
    }
    }

    // Enter to send
    const input = document.getElementById("user-input");
    if (input) {
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
        }
    });
    }

    // 3D tilt effect for chatbot icon
    (function initBotTilt(){
      const botWrap = document.querySelector('#chatbot-icon .bot-3d');
      const botImg = document.querySelector('#chatbot-icon .bot-img');
      const botGlow = document.querySelector('#chatbot-icon .bot-glow');
      if (!botWrap || !botImg) return;

      let rafId = null;
      let targetRX = 0, targetRY = 0;
      let currentRX = 0, currentRY = 0;

      const clamp = (v, min, max) => Math.max(min, Math.min(max, v));

      function animate(){
        currentRX += (targetRX - currentRX) * 0.15;
        currentRY += (targetRY - currentRY) * 0.15;
        botImg.style.transform = `rotateX(${currentRX}deg) rotateY(${currentRY}deg)`;
        if (botGlow){
          const gx = (-currentRY) * 0.6; // invert so light appears opposite
          const gy = (currentRX) * 0.6;
          botGlow.style.boxShadow = `${gx}px ${gy}px 18px rgba(59,130,246,.35), ${-gx}px ${-gy}px 22px rgba(34,211,238,.25)`;
        }
        rafId = requestAnimationFrame(animate);
      }
      rafId = requestAnimationFrame(animate);

      function onMove(e){
        const rect = botWrap.getBoundingClientRect();
        const cx = rect.left + rect.width/2;
        const cy = rect.top + rect.height/2;
        const dx = e.clientX - cx;
        const dy = e.clientY - cy;
        // map to degrees (smaller factor => smaller tilt)
        targetRY = clamp(dx / 12, -15, 15); // y rotation based on x movement
        targetRX = clamp(-dy / 12, -15, 15); // x rotation based on y movement
      }
      function reset(){ targetRX = 0; targetRY = 0; }

      window.addEventListener('mousemove', onMove);
      window.addEventListener('blur', reset);
      botWrap.addEventListener('mouseleave', reset);
    })();
