const state = {
    spread: "single_card",
    mode: "auto",
    topic: "general",
    tone: "warm",
    spreads: {},
    blindDeck: [],
    selectedBlindIds: [],
    drawnCards: [],
    drawnPositions: [],
    interpretation: "",
};

const els = {
    question: document.getElementById("question"),
    questionCount: document.getElementById("question-count"),
    topic: document.getElementById("topic"),
    tone: document.getElementById("tone"),
    spreadOptions: document.getElementById("spread-options"),
    spreadDetail: document.getElementById("spread-detail"),
    modeBtns: document.querySelectorAll(".mode-btn"),
    drawBtn: document.getElementById("draw-btn"),
    resetBtn: document.getElementById("reset-btn"),
    deckContainer: document.getElementById("deck-container"),
    cardsSection: document.getElementById("cards-section"),
    cardsContainer: document.getElementById("cards-container"),
    interpretBtn: document.getElementById("interpret-btn"),
    interpretationSection: document.getElementById("interpretation-section"),
    interpretationText: document.getElementById("interpretation-text"),
    copyResult: document.getElementById("copy-result"),
    saveResult: document.getElementById("save-result"),
    dailyCard: document.getElementById("daily-card"),
    refreshDaily: document.getElementById("refresh-daily"),
    historyList: document.getElementById("history-list"),
    clearHistory: document.getElementById("clear-history"),
    toast: document.getElementById("toast"),
};

const spreadFallbacks = {
    single_card: {
        name: "单牌指引",
        description: "适合快速确认当前问题的核心能量。",
        card_count: 1,
        positions: [{ name: "核心", meaning: "关键答案" }],
    },
    three_card: {
        name: "三牌牌阵",
        description: "用时间线看清背景、现状和可能方向。",
        card_count: 3,
        positions: [
            { name: "过去", meaning: "背景因素" },
            { name: "现在", meaning: "当前状态" },
            { name: "未来", meaning: "可能走向" },
        ],
    },
    celtic_cross: {
        name: "凯尔特十字",
        description: "适合复杂问题，覆盖内在、外部影响和结果趋势。",
        card_count: 10,
        positions: [],
    },
};

document.addEventListener("DOMContentLoaded", init);

async function init() {
    bindEvents();
    hydrateHistory();
    await Promise.all([loadSpreads(), loadDailyCard()]);
    updateQuestionCount();
    updateSpreadDetail();
    updateDrawButton();
}

function bindEvents() {
    els.question.addEventListener("input", () => {
        updateQuestionCount();
        updateDrawButton();
    });

    els.topic.addEventListener("change", () => {
        state.topic = els.topic.value;
    });

    els.tone.addEventListener("change", () => {
        state.tone = els.tone.value;
    });

    els.spreadOptions.addEventListener("click", (event) => {
        const button = event.target.closest(".spread-btn");
        if (!button) return;
        selectSpread(button.dataset.spread);
    });

    els.modeBtns.forEach((button) => {
        button.addEventListener("click", () => selectMode(button.dataset.mode));
    });

    els.drawBtn.addEventListener("click", drawCards);
    els.resetBtn.addEventListener("click", resetReading);
    els.interpretBtn.addEventListener("click", interpretCards);
    els.copyResult.addEventListener("click", copyInterpretation);
    els.saveResult.addEventListener("click", saveCurrentReading);
    els.refreshDaily.addEventListener("click", loadDailyCard);
    els.clearHistory.addEventListener("click", clearHistory);
}

async function loadSpreads() {
    try {
        const data = await requestJson("/api/spreads");
        if (data.success) {
            state.spreads = Object.fromEntries(data.spreads.map((spread) => [spread.id, spread]));
        }
    } catch (error) {
        console.warn("Spread metadata unavailable, using fallback.", error);
    }
}

async function loadDailyCard() {
    els.dailyCard.className = "mini-card loading-card";
    els.dailyCard.textContent = "星光校准中...";
    try {
        const data = await requestJson("/api/daily_card");
        if (!data.success) throw new Error(data.error || "获取今日一牌失败");
        const card = data.card;
        const meaning = card.reversed ? card.reversed_meaning : card.upright_meaning;
        els.dailyCard.className = "mini-card";
        els.dailyCard.innerHTML = `
            <strong>${escapeHtml(card.name)}</strong>
            <span>${card.reversed ? "逆位" : "正位"} · ${escapeHtml(card.date)}</span>
            <p>${escapeHtml(meaning)}</p>
        `;
    } catch (error) {
        els.dailyCard.className = "mini-card";
        els.dailyCard.textContent = error.message;
    }
}

function selectSpread(spread) {
    state.spread = spread;
    document.querySelectorAll(".spread-btn").forEach((button) => {
        button.classList.toggle("active", button.dataset.spread === spread);
    });
    state.selectedBlindIds = [];
    updateSpreadDetail();
    if (state.mode === "manual") loadBlindDeck();
    updateDrawButton();
}

function selectMode(mode) {
    state.mode = mode;
    els.modeBtns.forEach((button) => {
        button.classList.toggle("active", button.dataset.mode === mode);
    });
    state.selectedBlindIds = [];
    if (mode === "manual") {
        els.deckContainer.classList.add("visible");
        loadBlindDeck();
    } else {
        els.deckContainer.classList.remove("visible");
    }
    updateDrawButton();
}

function updateSpreadDetail() {
    const spread = getSpread();
    const positions = spread.positions || [];
    const positionText = positions.length
        ? positions.map((position) => `${position.index + 1}. ${position.name}`).join(" / ")
        : "牌位将在抽牌后显示";
    els.spreadDetail.innerHTML = `
        <strong>${escapeHtml(spread.name)}</strong>
        <span>${escapeHtml(spread.description)}</span>
        <small>${spread.card_count} 张牌 · ${escapeHtml(positionText)}</small>
    `;
}

async function loadBlindDeck() {
    els.deckContainer.innerHTML = `<p class="loading-text">正在洗牌...</p>`;
    try {
        const data = await requestJson("/api/blind_deck");
        if (!data.success) throw new Error(data.error || "加载牌组失败");
        state.blindDeck = data.cards;
        renderBlindDeck();
    } catch (error) {
        els.deckContainer.innerHTML = `<p class="loading-text">${escapeHtml(error.message)}</p>`;
    }
}

function renderBlindDeck() {
    const count = getCardCount();
    els.deckContainer.innerHTML = `
        <div class="deck-tools">
            <span id="selected-count">已选择 0 / ${count} 张</span>
            <button class="ghost-btn small" id="shuffle-btn">重新洗牌</button>
        </div>
        <div class="deck-grid"></div>
    `;
    els.deckContainer.querySelector("#shuffle-btn").addEventListener("click", shuffleDeck);
    const grid = els.deckContainer.querySelector(".deck-grid");
    state.blindDeck.forEach((card) => {
        const cardEl = document.createElement("button");
        cardEl.className = "deck-card";
        cardEl.type = "button";
        cardEl.dataset.blindId = card.blind_id;
        cardEl.title = `第 ${card.position} 张`;
        cardEl.addEventListener("click", () => toggleBlindSelection(card.blind_id, cardEl));
        grid.appendChild(cardEl);
    });
}

async function shuffleDeck() {
    try {
        const data = await requestJson("/api/shuffle", { method: "POST" });
        if (!data.success) throw new Error(data.error || "洗牌失败");
        state.selectedBlindIds = [];
        await loadBlindDeck();
        showToast("牌组已重新洗牌");
    } catch (error) {
        showToast(error.message);
    }
}

function toggleBlindSelection(blindId, element) {
    const count = getCardCount();
    const index = state.selectedBlindIds.indexOf(blindId);
    if (index >= 0) {
        state.selectedBlindIds.splice(index, 1);
        element.classList.remove("selected");
    } else if (state.selectedBlindIds.length < count) {
        state.selectedBlindIds.push(blindId);
        element.classList.add("selected");
    } else {
        showToast(`这个牌阵需要 ${count} 张牌`);
    }
    const selectedCount = document.getElementById("selected-count");
    if (selectedCount) selectedCount.textContent = `已选择 ${state.selectedBlindIds.length} / ${count} 张`;
    updateDrawButton();
}

async function drawCards() {
    const question = getQuestion();
    if (question.length < 5) {
        showToast("问题至少需要 5 个字符");
        els.question.focus();
        return;
    }

    setButtonLoading(els.drawBtn, "抽牌中...");
    try {
        const body = state.mode === "manual"
            ? { mode: "manual", spread_type: state.spread, blind_ids: state.selectedBlindIds }
            : { mode: "auto", spread_type: state.spread, count: getCardCount() };
        const data = await requestJson("/api/draw", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        if (!data.success) throw new Error(data.error || "抽牌失败");
        state.drawnCards = data.cards;
        state.drawnPositions = data.positions;
        state.interpretation = "";
        renderDrawnCards();
        els.interpretationSection.classList.remove("visible");
        els.cardsSection.classList.add("visible");
        els.cardsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
        showToast(error.message);
    } finally {
        setButtonReady(els.drawBtn, "开始占卜");
        updateDrawButton();
    }
}

function renderDrawnCards() {
    els.cardsContainer.innerHTML = "";
    state.drawnCards.forEach((card, index) => {
        const position = state.drawnPositions[index] || {};
        const wrapper = document.createElement("article");
        wrapper.className = "card-wrapper";
        const meaning = card.reversed ? card.reversed_meaning : card.upright_meaning;
        wrapper.innerHTML = `
            <div class="tarot-card ${card.reversed ? "reversed" : ""}">
                <span class="card-number">No. ${card.number}</span>
                <div class="card-art">${getSuitSymbol(card.suit, card.arcana)}</div>
                <div>
                    <div class="card-name">${escapeHtml(card.name)}</div>
                    <div class="card-meaning">${escapeHtml(meaning)}</div>
                </div>
                <span class="orientation-badge">${card.reversed ? "逆位" : "正位"}</span>
            </div>
            <div class="position-label">${escapeHtml(position.name || `位置 ${index + 1}`)}</div>
            <div class="position-meaning">${escapeHtml(position.meaning || "")}</div>
        `;
        els.cardsContainer.appendChild(wrapper);
    });
}

async function interpretCards() {
    if (!state.drawnCards.length) {
        showToast("请先抽牌");
        return;
    }

    setButtonLoading(els.interpretBtn, "解读中...");
    els.interpretationText.textContent = "星盘正在整理牌面线索...";
    els.interpretationSection.classList.add("visible");
    els.interpretationSection.scrollIntoView({ behavior: "smooth", block: "start" });

    try {
        const data = await requestJson("/api/interpret", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                cards: state.drawnCards,
                positions: state.drawnPositions,
                question: getQuestion(),
                spread_type: state.spread,
                topic: state.topic,
                tone: state.tone,
            }),
        });
        if (!data.success) throw new Error(data.error || "解读失败");
        state.interpretation = data.interpretation;
        els.interpretationText.textContent = data.interpretation;
    } catch (error) {
        els.interpretationText.textContent = error.message;
        showToast(error.message);
    } finally {
        setButtonReady(els.interpretBtn, "AI 解读");
    }
}

async function copyInterpretation() {
    if (!state.interpretation) {
        showToast("还没有可复制的解读");
        return;
    }
    await navigator.clipboard.writeText(buildShareText());
    showToast("解读已复制");
}

function saveCurrentReading() {
    if (!state.drawnCards.length) {
        showToast("请先完成一次抽牌");
        return;
    }
    const history = getHistory();
    const record = {
        id: Date.now().toString(),
        createdAt: new Date().toLocaleString("zh-CN"),
        question: getQuestion(),
        spread: state.spread,
        cards: state.drawnCards,
        positions: state.drawnPositions,
        cardSummary: state.drawnCards.map((card) => `${card.name}${card.reversed ? "逆位" : "正位"}`),
        interpretation: state.interpretation,
    };
    history.unshift(record);
    localStorage.setItem("tarotHistory", JSON.stringify(history.slice(0, 12)));
    hydrateHistory();
    showToast("记录已保存到本机浏览器");
}

function hydrateHistory() {
    const history = getHistory();
    if (!history.length) {
        els.historyList.className = "history-list empty";
        els.historyList.textContent = "还没有记录";
        return;
    }

    els.historyList.className = "history-list";
    els.historyList.innerHTML = "";
    history.forEach((record) => {
        const item = document.createElement("button");
        item.className = "history-item";
        item.type = "button";
        item.innerHTML = `
            <strong>${escapeHtml(record.question)}</strong>
            <span>${escapeHtml(record.createdAt)} · ${escapeHtml(getSpreadName(record.spread))}</span>
        `;
        item.addEventListener("click", () => {
            els.question.value = record.question;
            state.spread = record.spread || state.spread;
            state.drawnCards = normalizeHistoryCards(record.cards);
            state.drawnPositions = Array.isArray(record.positions) ? record.positions : [];
            state.interpretation = record.interpretation || "";
            if (state.drawnCards.length) {
                renderDrawnCards();
                els.cardsSection.classList.add("visible");
            }
            els.interpretationText.textContent = state.interpretation || "这条记录没有保存 AI 解读。";
            els.interpretationSection.classList.add("visible");
            updateQuestionCount();
            updateSpreadActiveState();
            updateSpreadDetail();
            els.cardsSection.scrollIntoView({ behavior: "smooth", block: "start" });
        });
        els.historyList.appendChild(item);
    });
}

function clearHistory() {
    localStorage.removeItem("tarotHistory");
    hydrateHistory();
    showToast("历史记录已清空");
}

function resetReading() {
    state.selectedBlindIds = [];
    state.drawnCards = [];
    state.drawnPositions = [];
    state.interpretation = "";
    els.cardsSection.classList.remove("visible");
    els.interpretationSection.classList.remove("visible");
    if (state.mode === "manual") loadBlindDeck();
    showToast("牌面已重置");
}

function updateQuestionCount() {
    els.questionCount.textContent = `${els.question.value.length} / 500`;
}

function updateDrawButton() {
    const enoughCards = state.mode !== "manual" || state.selectedBlindIds.length === getCardCount();
    els.drawBtn.disabled = !enoughCards;
    els.drawBtn.textContent = enoughCards ? "开始占卜" : `请选择 ${getCardCount()} 张牌`;
}

function getSpread() {
    return state.spreads[state.spread] || spreadFallbacks[state.spread] || spreadFallbacks.single_card;
}

function getCardCount() {
    return getSpread().card_count || 1;
}

function getSpreadName(spreadId) {
    return (state.spreads[spreadId] || spreadFallbacks[spreadId] || {}).name || spreadId;
}

function getQuestion() {
    return els.question.value.trim();
}

function getHistory() {
    try {
        return JSON.parse(localStorage.getItem("tarotHistory") || "[]");
    } catch {
        return [];
    }
}

function normalizeHistoryCards(cards) {
    if (!Array.isArray(cards)) return [];
    return cards.filter((card) => typeof card === "object" && card !== null && card.name);
}

function updateSpreadActiveState() {
    document.querySelectorAll(".spread-btn").forEach((button) => {
        button.classList.toggle("active", button.dataset.spread === state.spread);
    });
}

function getSuitSymbol(suit, arcana) {
    if (arcana === "major") return "☾";
    return {
        wands: "✦",
        cups: "◇",
        swords: "†",
        pentacles: "◎",
    }[suit] || "✧";
}

function buildShareText() {
    const cards = state.drawnCards
        .map((card, index) => `${index + 1}. ${card.name}（${card.reversed ? "逆位" : "正位"}）`)
        .join("\n");
    return `问题：${getQuestion()}\n牌阵：${getSpreadName(state.spread)}\n\n${cards}\n\n${state.interpretation}`;
}

async function requestJson(url, options = {}) {
    const response = await fetch(url, options);
    const text = await response.text();
    let data = {};

    if (text) {
        try {
            data = JSON.parse(text);
        } catch (error) {
            const shortText = text.replace(/\s+/g, " ").slice(0, 140);
            throw new Error(`接口返回了非 JSON 内容：${shortText || response.statusText}`);
        }
    }

    if (!response.ok) {
        throw new Error(data.error || `请求失败：${response.status} ${response.statusText}`);
    }

    if (!text) {
        throw new Error("接口返回为空，请检查服务是否部署成功");
    }

    return data;
}

function setButtonLoading(button, text) {
    button.dataset.originalText = button.textContent;
    button.textContent = text;
    button.disabled = true;
}

function setButtonReady(button, text) {
    button.textContent = text || button.dataset.originalText || button.textContent;
    button.disabled = false;
}

function showToast(message) {
    els.toast.textContent = message;
    els.toast.classList.add("visible");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => els.toast.classList.remove("visible"), 2600);
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
