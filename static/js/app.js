const STORAGE_KEY = "tarotHistory";
const REVIEW_KEY = "tarotReviews";
const JOURNAL_KEY = "tarotCompanionJournals";
const AI_FRONTEND_TIMEOUT = 70000;

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
    intentCharged: false,
    dailyCard: null,
    deckInfo: [],
    focusIndex: 0,
    relationshipCards: [],
    learnIndex: -1,
    latestJournal: null,
};

const els = {
    tabs: document.querySelectorAll(".tab-btn"),
    tabPanels: document.querySelectorAll(".tab-panel"),
    question: document.getElementById("question"),
    questionCount: document.getElementById("question-count"),
    topic: document.getElementById("topic"),
    tone: document.getElementById("tone"),
    ritualGuide: document.getElementById("ritual-guide"),
    intentBtn: document.getElementById("intent-btn"),
    spreadOptions: document.getElementById("spread-options"),
    spreadDetail: document.getElementById("spread-detail"),
    modeBtns: document.querySelectorAll(".mode-btn"),
    drawBtn: document.getElementById("draw-btn"),
    resetBtn: document.getElementById("reset-btn"),
    deckContainer: document.getElementById("deck-container"),
    cardsSection: document.getElementById("cards-section"),
    cardsContainer: document.getElementById("cards-container"),
    interpretBtn: document.getElementById("interpret-btn"),
    saveCards: document.getElementById("save-cards"),
    interpretationSection: document.getElementById("interpretation-section"),
    interpretationText: document.getElementById("interpretation-text"),
    copyResult: document.getElementById("copy-result"),
    saveResult: document.getElementById("save-result"),
    dailyCard: document.getElementById("daily-card"),
    dailyAdvice: document.getElementById("daily-advice"),
    dailyOracle: document.getElementById("daily-oracle"),
    historyList: document.getElementById("history-list"),
    clearHistory: document.getElementById("clear-history"),
    metricTotal: document.getElementById("metric-total"),
    metricReview: document.getElementById("metric-review"),
    metricFit: document.getElementById("metric-fit"),
    topCards: document.getElementById("top-cards"),
    reviewList: document.getElementById("review-list"),
    generateReport: document.getElementById("generate-report"),
    monthlyReport: document.getElementById("monthly-report"),
    personA: document.getElementById("person-a"),
    personB: document.getElementById("person-b"),
    relationType: document.getElementById("relation-type"),
    relationshipBtn: document.getElementById("relationship-btn"),
    relationshipAiBtn: document.getElementById("relationship-ai-btn"),
    relationshipResult: document.getElementById("relationship-result"),
    relationshipAiResult: document.getElementById("relationship-ai-result"),
    learnCard: document.getElementById("learn-card"),
    nextLearnCard: document.getElementById("next-learn-card"),
    journalInput: document.getElementById("journal-input"),
    journalBtn: document.getElementById("journal-btn"),
    saveJournal: document.getElementById("save-journal"),
    journalList: document.getElementById("journal-list"),
    clearJournals: document.getElementById("clear-journals"),
    journalResponse: document.getElementById("journal-response"),
    toast: document.getElementById("toast"),
};

const spreadFallbacks = {
    single_card: {
        name: "单牌指引",
        description: "适合快速确认当前问题的核心能量。",
        card_count: 1,
        positions: [{ index: 0, name: "核心", meaning: "关键答案" }],
    },
    three_card: {
        name: "三牌牌阵",
        description: "用时间线看清背景、现状和可能方向。",
        card_count: 3,
        positions: [
            { index: 0, name: "过去", meaning: "背景因素" },
            { index: 1, name: "现在", meaning: "当前状态" },
            { index: 2, name: "未来", meaning: "可能走向" },
        ],
    },
    celtic_cross: {
        name: "凯尔特十字",
        description: "适合复杂问题，覆盖内在、外部影响和结果趋势。",
        card_count: 10,
        positions: [],
    },
};

const ritualGuides = [
    "深呼吸，把问题在心里默念三遍。",
    "把注意力放在此刻，不急着寻找标准答案。",
    "想象问题变成一束光，落在你即将抽出的牌上。",
    "先问自己：我真正想理解的是哪一部分？",
];

const topicWords = {
    general: ["方向", "选择", "节奏", "边界", "自我照顾"],
    love: ["犹豫", "等待", "沟通不足", "靠近", "安全感"],
    career: ["规划", "行动", "机会", "专注", "协作"],
    wealth: ["取舍", "稳定", "风险", "耐心", "积累"],
    growth: ["觉察", "蜕变", "信念", "休整", "勇气"],
};

document.addEventListener("DOMContentLoaded", init);

async function init() {
    bindEvents();
    hydrateHistory();
    hydrateProfile();
    hydrateJournals();
    await Promise.all([loadSpreads(), loadDailyCard(), loadDeckInfo()]);
    updateQuestionCount();
    updateSpreadDetail();
    updateDrawButton();
    renderLearnCard();
}

function bindEvents() {
    const on = (element, eventName, handler, options) => {
        if (element) element.addEventListener(eventName, handler, options);
    };

    els.tabs.forEach((button) => {
        button.addEventListener("click", () => selectTab(button.dataset.tab));
    });

    on(els.question, "input", () => {
        updateQuestionCount();
        updateDrawButton();
    });

    on(els.topic, "change", () => {
        state.topic = els.topic.value;
        renderDailyOracle();
    });

    on(els.tone, "change", () => {
        state.tone = els.tone.value;
    });

    on(els.spreadOptions, "click", (event) => {
        const button = event.target.closest(".spread-btn");
        if (!button) return;
        selectSpread(button.dataset.spread);
    });

    els.modeBtns.forEach((button) => {
        button.addEventListener("click", () => selectMode(button.dataset.mode));
    });

    let chargeTimer = null;
    const startCharge = () => {
        els.intentBtn.textContent = "正在注入...";
        chargeTimer = window.setTimeout(() => {
            state.intentCharged = true;
            els.intentBtn.textContent = "问题已注入";
            document.querySelector(".ritual-box").classList.add("charged");
            showToast("仪式感已完成，可以抽牌了");
        }, 650);
    };
    const cancelCharge = () => {
        window.clearTimeout(chargeTimer);
        if (!state.intentCharged) els.intentBtn.textContent = "长按注入问题";
    };
    const completeCharge = () => {
        if (state.intentCharged) return;
        window.clearTimeout(chargeTimer);
        state.intentCharged = true;
        els.intentBtn.textContent = "问题已注入";
        document.querySelector(".ritual-box").classList.add("charged");
        showToast("仪式感已完成，可以抽牌了");
    };
    on(els.intentBtn, "mousedown", startCharge);
    on(els.intentBtn, "touchstart", startCharge, { passive: true });
    on(els.intentBtn, "click", completeCharge);
    ["mouseup", "mouseleave", "touchend", "touchcancel"].forEach((eventName) => {
        on(els.intentBtn, eventName, cancelCharge);
    });

    on(els.drawBtn, "click", drawCards);
    on(els.resetBtn, "click", resetReading);
    on(els.interpretBtn, "click", interpretCards);
    on(els.saveCards, "click", saveCurrentReading);
    on(els.copyResult, "click", copyInterpretation);
    on(els.saveResult, "click", saveCurrentReading);
    on(els.clearHistory, "click", clearHistory);
    on(els.generateReport, "click", renderMonthlyReport);
    on(els.relationshipBtn, "click", renderRelationshipReading);
    on(els.relationshipAiBtn, "click", renderRelationshipAiReading);
    on(els.nextLearnCard, "click", renderLearnCard);
    on(els.journalBtn, "click", renderJournalResponse);
    on(els.saveJournal, "click", saveJournalEntry);
    on(els.clearJournals, "click", clearJournals);
}

function selectTab(tabName) {
    els.tabs.forEach((button) => button.classList.toggle("active", button.dataset.tab === tabName));
    els.tabPanels.forEach((panel) => panel.classList.toggle("active", panel.id === `tab-${tabName}`));
    if (tabName === "profile") hydrateProfile();
}

async function loadSpreads() {
    try {
        const data = await requestJson("/api/spreads");
        if (data.success) {
            state.spreads = Object.fromEntries(data.spreads.map((spread) => [spread.id, localizeSpread(spread)]));
        }
    } catch (error) {
        console.warn("Spread metadata unavailable, using fallback.", error);
    }
}

async function loadDeckInfo() {
    try {
        const data = await requestJson("/api/deck");
        if (data.success) state.deckInfo = data.cards;
    } catch (error) {
        console.warn("Deck metadata unavailable.", error);
    }
}

async function loadDailyCard() {
    els.dailyCard.className = "mini-card loading-card";
    els.dailyCard.textContent = "星光校准中...";
    els.dailyAdvice.textContent = "";
    try {
        const data = await requestJson("/api/daily_card");
        if (!data.success) throw new Error(data.error || "获取今日能量卡失败");
        const card = data.card;
        state.dailyCard = card;
        const meaning = card.reversed ? card.reversed_meaning : card.upright_meaning;
        els.dailyCard.className = "mini-card";
        els.dailyCard.innerHTML = `
            <strong>${escapeHtml(card.name)}</strong>
            <span>${card.reversed ? "逆位" : "正位"} · ${escapeHtml(card.date)}</span>
            <p>${escapeHtml(meaning)}</p>
        `;
        els.dailyAdvice.textContent = data.advice ? stripThinking(data.advice) : buildLocalDailyAdvice(card);
        renderDailyOracle();
    } catch (error) {
        els.dailyCard.className = "mini-card";
        els.dailyCard.textContent = error.message;
        renderDailyOracle();
    }
}

function renderDailyOracle() {
    const words = topicWords[state.topic] || topicWords.general;
    const seed = state.dailyCard?.number || new Date().getDate();
    const keyword = words[seed % words.length];
    const luckyNumber = (seed % 9) + 1;
    els.dailyOracle.innerHTML = `
        <div class="oracle-tile">
            <span class="tile-title">今日关键词</span>
            <strong class="tile-value">${escapeHtml(keyword)}</strong>
        </div>
        <div class="oracle-tile">
            <span class="tile-title">今日宜做</span>
            <strong class="tile-value">整理计划</strong>
        </div>
        <div class="oracle-tile">
            <span class="tile-title">今日忌做</span>
            <strong class="tile-value">脑补过多</strong>
        </div>
        <div class="oracle-tile">
            <span class="tile-title">幸运提示</span>
            <strong class="tile-value">${luckyNumber} · 浅紫银</strong>
        </div>
    `;
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
        ? positions.map((position, index) => `${(position.index ?? index) + 1}. ${position.name}`).join(" / ")
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
    state.focusIndex = 0;
    els.deckContainer.innerHTML = `
        <div class="deck-tools">
            <span id="selected-count">已选择 0 / ${count} 张</span>
            <button class="ghost-btn small" id="shuffle-btn">重新洗牌</button>
        </div>
        <div class="deck-picker" id="deck-picker">
            <button class="icon-btn picker-nav" id="prev-card" type="button" aria-label="上一张">‹</button>
            <button class="focus-card" id="focus-card" type="button" aria-label="选择当前牌">
                <span class="focus-card-mark">☽</span>
                <span class="focus-card-index">第 1 张</span>
            </button>
            <button class="icon-btn picker-nav" id="next-card" type="button" aria-label="下一张">›</button>
        </div>
        <div class="picker-actions">
            <button class="ghost-btn small" id="random-card" type="button">随机换一张</button>
            <button class="primary-btn small" id="pick-focus-card" type="button">选择这张</button>
        </div>
        <div class="selected-tray" id="selected-tray"></div>
        <div class="deck-dots" id="deck-dots" aria-hidden="true"></div>
        <div class="deck-grid" id="deck-grid">
            <div class="deck-strip"></div>
        </div>
    `;
    els.deckContainer.querySelector("#shuffle-btn").addEventListener("click", shuffleDeck);
    els.deckContainer.querySelector("#prev-card").addEventListener("click", () => moveFocus(-1));
    els.deckContainer.querySelector("#next-card").addEventListener("click", () => moveFocus(1));
    els.deckContainer.querySelector("#random-card").addEventListener("click", randomFocusCard);
    els.deckContainer.querySelector("#pick-focus-card").addEventListener("click", pickFocusedCard);
    els.deckContainer.querySelector("#focus-card").addEventListener("click", pickFocusedCard);
    els.deckContainer.querySelector("#deck-picker").addEventListener("keydown", (event) => {
        if (event.key === "ArrowLeft" || event.key === "ArrowUp") moveFocus(-1);
        if (event.key === "ArrowRight" || event.key === "ArrowDown") moveFocus(1);
        if (event.key === "Enter" || event.key === " ") pickFocusedCard();
    });
    const strip = els.deckContainer.querySelector(".deck-strip");
    state.blindDeck.forEach((card) => {
        const cardEl = document.createElement("button");
        cardEl.className = "deck-card";
        cardEl.type = "button";
        cardEl.dataset.blindId = card.blind_id;
        cardEl.dataset.deckIndex = String(card.position - 1);
        cardEl.title = `选择第 ${card.position} 张`;
        cardEl.addEventListener("click", () => {
            state.focusIndex = card.position - 1;
            updatePicker();
        });
        strip.appendChild(cardEl);
    });
    updatePicker();
}

function wrapIndex(index, length) {
    return ((index % length) + length) % length;
}

function moveFocus(direction) {
    state.focusIndex = wrapIndex(state.focusIndex + direction, state.blindDeck.length);
    updatePicker();
}

function randomFocusCard() {
    if (!state.blindDeck.length) return;
    let nextIndex = Math.floor(Math.random() * state.blindDeck.length);
    if (state.blindDeck.length > 1 && nextIndex === state.focusIndex) {
        nextIndex = wrapIndex(nextIndex + 1, state.blindDeck.length);
    }
    state.focusIndex = nextIndex;
    updatePicker();
}

function pickFocusedCard() {
    const focused = state.blindDeck[state.focusIndex];
    if (!focused) return;
    const element = els.deckContainer.querySelector(`.deck-card[data-blind-id="${focused.blind_id}"]`);
    toggleBlindSelection(focused.blind_id, element);
}

function updatePicker() {
    const focused = state.blindDeck[state.focusIndex];
    if (!focused) return;
    const focusCard = els.deckContainer.querySelector("#focus-card");
    const focusIndex = els.deckContainer.querySelector(".focus-card-index");
    const tray = els.deckContainer.querySelector("#selected-tray");
    const dots = els.deckContainer.querySelector("#deck-dots");
    const cards = [...els.deckContainer.querySelectorAll(".deck-card")];
    const focusSelected = state.selectedBlindIds.includes(focused.blind_id);

    focusIndex.textContent = `第 ${focused.position} 张`;
    focusCard.classList.toggle("selected", focusSelected);

    cards.forEach((cardEl) => {
        const deckIndex = Number(cardEl.dataset.deckIndex);
        const offset = Math.abs(deckIndex - state.focusIndex);
        cardEl.classList.toggle("is-focus", deckIndex === state.focusIndex);
        cardEl.classList.toggle("selected", state.selectedBlindIds.includes(Number(cardEl.dataset.blindId)));
        cardEl.hidden = offset > 5;
    });

    tray.innerHTML = state.selectedBlindIds.length
        ? state.selectedBlindIds.map((blindId, index) => `
            <button class="selected-chip" type="button" data-remove-blind-id="${blindId}">
                第 ${index + 1} 张 · 取消
            </button>
        `).join("")
        : `<span>选中的牌会出现在这里</span>`;
    tray.querySelectorAll("[data-remove-blind-id]").forEach((button) => {
        button.addEventListener("click", () => {
            const blindId = Number(button.dataset.removeBlindId);
            const cardEl = els.deckContainer.querySelector(`.deck-card[data-blind-id="${blindId}"]`);
            toggleBlindSelection(blindId, cardEl);
        });
    });

    const dotCount = 9;
    const half = Math.floor(dotCount / 2);
    dots.innerHTML = Array.from({ length: dotCount }, (_, index) => {
        const cardIndex = wrapIndex(state.focusIndex + index - half, state.blindDeck.length);
        const active = index === half ? "active" : "";
        return `<button class="deck-dot ${active}" type="button" data-dot-index="${cardIndex}"></button>`;
    }).join("");
    dots.querySelectorAll("[data-dot-index]").forEach((button) => {
        button.addEventListener("click", () => {
            state.focusIndex = Number(button.dataset.dotIndex);
            updatePicker();
        });
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
        element?.classList.remove("selected");
    } else if (state.selectedBlindIds.length < count) {
        state.selectedBlindIds.push(blindId);
        element?.classList.add("selected");
    } else {
        showToast(`这个牌阵需要 ${count} 张牌`);
    }
    const selectedCount = document.getElementById("selected-count");
    if (selectedCount) selectedCount.textContent = `已选择 ${state.selectedBlindIds.length} / ${count} 张`;
    updatePicker();
    updateDrawButton();
}

async function drawCards() {
    const question = getQuestion();
    if (question.length < 5) {
        showToast("问题至少需要 5 个字符");
        els.question.focus();
        return;
    }

    if (!state.intentCharged) {
        els.ritualGuide.textContent = ritualGuides[Math.floor(Math.random() * ritualGuides.length)];
        showToast("建议先长按注入问题，再开始抽牌");
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
        wrapper.style.animationDelay = `${index * 80}ms`;
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
        state.interpretation = stripThinking(data.interpretation);
        els.interpretationText.textContent = state.interpretation;
    } catch (error) {
        state.interpretation = buildLocalInterpretation();
        els.interpretationText.textContent = state.interpretation;
        showToast("AI 暂不可用，已生成本地反思版解读");
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
    const now = new Date();
    const history = getHistory();
    const record = {
        id: Date.now().toString(),
        createdAt: now.toLocaleString("zh-CN"),
        createdAtISO: now.toISOString(),
        reviewDueAt: addDays(now, getReviewDays()).toISOString(),
        reviewWindow: getReviewDays(),
        question: getQuestion(),
        topic: state.topic,
        spread: state.spread,
        cards: state.drawnCards,
        positions: state.drawnPositions,
        cardSummary: state.drawnCards.map((card) => `${card.name}${card.reversed ? "逆位" : "正位"}`),
        interpretation: state.interpretation,
    };
    history.unshift(record);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history.slice(0, 80)));
    hydrateHistory();
    hydrateProfile();
    showToast(`记录已保存，${record.reviewWindow} 天后可回访验证`);
}

function getReviewDays() {
    const count = getCardCount();
    if (count >= 10) return 30;
    if (count >= 3) return 7;
    return 3;
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
    history.slice(0, 12).forEach((record) => {
        const item = document.createElement("button");
        item.className = "history-item";
        item.type = "button";
        item.innerHTML = `
            <strong>${escapeHtml(record.question)}</strong>
            <span>${escapeHtml(record.createdAt)} · ${escapeHtml(getSpreadName(record.spread))}</span>
            <span>${escapeHtml((record.cardSummary || []).slice(0, 3).join(" / "))}</span>
        `;
        item.addEventListener("click", () => restoreReading(record));
        els.historyList.appendChild(item);
    });
}

function restoreReading(record) {
    selectTab("reading");
    els.question.value = record.question;
    state.spread = record.spread || state.spread;
    state.topic = record.topic || state.topic;
    els.topic.value = state.topic;
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
}

function clearHistory() {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(REVIEW_KEY);
    hydrateHistory();
    hydrateProfile();
    showToast("历史记录已清空");
}

function hydrateProfile() {
    const history = getHistory();
    const reviews = getReviews();
    const now = Date.now();
    const due = history.filter((record) => !reviews[record.id] && new Date(record.reviewDueAt || record.createdAtISO || 0).getTime() <= now);
    const rated = Object.values(reviews).filter((review) => Number.isFinite(review.rating));
    const average = rated.length ? (rated.reduce((sum, review) => sum + review.rating, 0) / rated.length).toFixed(1) : "--";

    els.metricTotal.textContent = history.length;
    els.metricReview.textContent = due.length;
    els.metricFit.textContent = average;
    renderTopCards(history);
    renderReviewList(history, reviews, due);
}

function renderTopCards(history) {
    const cutoff = addDays(new Date(), -90).getTime();
    const counts = new Map();
    history
        .filter((record) => new Date(record.createdAtISO || record.createdAt || 0).getTime() >= cutoff)
        .flatMap((record) => record.cards || [])
        .forEach((card) => counts.set(card.name, (counts.get(card.name) || 0) + 1));

    const top = [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5);
    if (!top.length) {
        els.topCards.className = "tag-cloud empty";
        els.topCards.textContent = "保存占卜后会生成趋势";
        return;
    }
    els.topCards.className = "tag-cloud";
    els.topCards.innerHTML = top.map(([name, count]) => `<span class="tag">${escapeHtml(name)} · ${count}</span>`).join("");
}

function renderReviewList(history, reviews, due) {
    const reviewable = due.length ? due : history.slice(0, 3).filter((record) => !reviews[record.id]);
    if (!reviewable.length) {
        els.reviewList.className = "review-list empty";
        els.reviewList.textContent = "还没有需要回访的占卜";
        return;
    }

    els.reviewList.className = "review-list";
    els.reviewList.innerHTML = "";
    reviewable.forEach((record) => {
        const item = document.createElement("article");
        item.className = "review-item";
        item.innerHTML = `
            <strong>${escapeHtml(record.question)}</strong>
            <span>${escapeHtml(record.createdAt)} · 回访周期 ${record.reviewWindow || 3} 天</span>
            <div class="review-form">
                <textarea class="question-input small" maxlength="240" placeholder="事情后来怎么样了？当时的牌准在哪里？AI 建议有没有用？"></textarea>
                <div class="rating-row">
                    ${[1, 2, 3, 4, 5].map((value) => `<button class="ghost-btn small" data-rating="${value}">${value}</button>`).join("")}
                </div>
            </div>
        `;
        item.querySelectorAll("[data-rating]").forEach((button) => {
            button.addEventListener("click", () => saveReview(record.id, Number(button.dataset.rating), item.querySelector("textarea").value));
        });
        els.reviewList.appendChild(item);
    });
}

function saveReview(recordId, rating, note) {
    const reviews = getReviews();
    reviews[recordId] = {
        rating,
        note: note.trim(),
        reviewedAt: new Date().toISOString(),
    };
    localStorage.setItem(REVIEW_KEY, JSON.stringify(reviews));
    hydrateProfile();
    showToast(`已记录契合度 ${rating}/5`);
}

function renderMonthlyReport() {
    const history = getHistory();
    const now = new Date();
    const month = now.getMonth();
    const year = now.getFullYear();
    const monthRecords = history.filter((record) => {
        const date = new Date(record.createdAtISO || record.createdAt || 0);
        return date.getFullYear() === year && date.getMonth() === month;
    });
    const source = monthRecords.length ? monthRecords : history.slice(0, 8);
    if (!source.length) {
        els.monthlyReport.textContent = "本月还没有足够记录。完成并保存几次占卜后再来生成报告。";
        return;
    }

    const cards = source.flatMap((record) => record.cards || []);
    const majors = cards.filter((card) => card.arcana === "major").length;
    const topCard = mostCommon(cards.map((card) => card.name)) || "尚未形成重复牌";
    const topTopic = mostCommon(source.map((record) => record.topic || "general"));
    const keywords = topicWords[topTopic] || topicWords.general;
    const theme = keywords[(cards.length + source.length) % keywords.length];

    els.monthlyReport.innerHTML = `
        <div class="tag-cloud">
            <span class="chip">本月能量主题：${escapeHtml(theme)}</span>
            <span class="chip">重复出现最多：${escapeHtml(topCard)}</span>
            <span class="chip">大阿卡那出现：${majors} 次</span>
        </div>
        <p><strong>感情/关系关键词：</strong>${escapeHtml(keywords.slice(0, 3).join("、"))}</p>
        <p><strong>学业/事业提醒：</strong>把注意力放回可执行的下一步，少用想象替代沟通和行动。</p>
        <p><strong>给本月的你：</strong>这个月的牌面提醒你，不必急着给所有事情定性。先看见自己的反应，再决定要投入多少能量。真正重要的答案，通常会在你愿意诚实记录之后慢慢浮现。</p>
    `;
}

async function renderRelationshipReading() {
    const a = els.personA.value.trim() || "我";
    const b = els.personB.value.trim() || "TA";
    const relation = els.relationType.value;
    setButtonLoading(els.relationshipBtn, "抽取关系牌...");
    try {
        const data = await requestJson("/api/draw", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode: "auto", spread_type: "celtic_cross", count: 5 }),
        });
        if (!data.success) throw new Error(data.error || "关系占卜失败");
        const labels = [`${a} 怎么看 ${b}`, `${b} 怎么看 ${a}`, "隐藏情绪", "关系走向", "建议"];
        state.relationshipCards = data.cards;
        els.relationshipResult.innerHTML = `
            <h2>${escapeHtml(a)} × ${escapeHtml(b)} 的${escapeHtml(relation)}能量图</h2>
            <div class="relationship-cards">
                ${data.cards.map((card, index) => `
                    <div class="energy-card">
                        <strong>${escapeHtml(labels[index])}</strong>
                        <span>${escapeHtml(card.name)} · ${card.reversed ? "逆位" : "正位"}</span>
                        <p>${escapeHtml(card.reversed ? card.reversed_meaning : card.upright_meaning)}</p>
                    </div>
                `).join("")}
            </div>
        `;
    } catch (error) {
        showToast(error.message);
    } finally {
        setButtonReady(els.relationshipBtn, "生成关系能量图");
    }
}

async function renderRelationshipAiReading() {
    if (!state.relationshipCards.length) {
        showToast("请先生成关系能量图");
        return;
    }
    const a = els.personA.value.trim() || "我";
    const b = els.personB.value.trim() || "TA";
    const relation = els.relationType.value;
    setButtonLoading(els.relationshipAiBtn, "解读关系中...");
    els.relationshipAiResult.innerHTML = "<p>AI 正在整理这段关系里的能量流向...</p>";
    try {
        const labels = [`${a} 怎么看 ${b}`, `${b} 怎么看 ${a}`, "隐藏情绪", "关系走向", "建议"];
        const positions = labels.map((name, index) => ({ index, name, meaning: name }));
        const data = await withTimeout(requestJson("/api/interpret", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                cards: state.relationshipCards,
                positions,
                question: `${a} 和 ${b} 的${relation}，现在最需要理解什么？`,
                spread_type: "relationship",
                topic: "love",
                tone: state.tone,
            }),
        }), AI_FRONTEND_TIMEOUT);
        if (!data.success) throw new Error(data.error || "关系解读失败");
        els.relationshipAiResult.innerHTML = `<pre class="interpretation-text">${escapeHtml(stripThinking(data.interpretation))}</pre>`;
    } catch (error) {
        els.relationshipAiResult.innerHTML = `<pre class="interpretation-text">${escapeHtml(buildLocalRelationshipInterpretation(a, b, relation))}</pre>`;
        showToast("AI 暂不可用，已生成本地关系反思版");
    } finally {
        setButtonReady(els.relationshipAiBtn, "AI 解读关系");
    }
}

function renderLearnCard() {
    const cards = state.deckInfo.length ? state.deckInfo : [
        { name: "The Fool", arcana: "major", suit: "major_arcana", number: 1 },
        { name: "The Moon", arcana: "major", suit: "major_arcana", number: 19 },
        { name: "Nine of Swords", arcana: "minor", suit: "swords", number: 59 },
    ];
    state.learnIndex = wrapIndex(state.learnIndex + 1, cards.length);
    const card = cards[state.learnIndex];
    const lesson = buildLearnLesson(card);
    els.learnCard.innerHTML = `
        <strong>${escapeHtml(card.name)}</strong>
        <span>${card.arcana === "major" ? "大阿卡那" : "小阿卡那"} · ${escapeHtml(card.suit)}</span>
        <p>正位速记：${escapeHtml(lesson.upright)}</p>
        <p>逆位速记：${escapeHtml(lesson.reversed)}</p>
        <p>小测：${escapeHtml(lesson.quiz)}</p>
        <button class="ghost-btn small quiz-answer-btn" type="button">显示答案</button>
        <p class="quiz-answer" hidden>参考答案：${escapeHtml(lesson.answer)}</p>
    `;
    els.learnCard.querySelector(".quiz-answer-btn").addEventListener("click", (event) => {
        const answer = els.learnCard.querySelector(".quiz-answer");
        answer.hidden = !answer.hidden;
        event.currentTarget.textContent = answer.hidden ? "显示答案" : "收起答案";
    });
}

function buildLearnLesson(card) {
    if (card.arcana === "major") {
        const majorLessons = {
            "The Fool": ["开始、信任、轻装上路", "鲁莽、逃避准备、过度天真", "愚人出现在建议位时，最该先做什么？", "迈出第一步，但给自己一个最小安全检查。"],
            "The Magician": ["资源整合、主动创造、表达意图", "分心、空想、工具没有用起来", "魔术师提醒你把哪种资源用起来？", "列出手上已有的人、时间、技能或信息，并立刻使用其中一个。"],
            "The High Priestess": ["直觉、观察、暂不揭晓", "压抑感受、信息不透明、过度沉默", "女祭司建议你先问自己什么？", "先确认自己的真实感受，再决定是否需要更多信息。"],
            "The Empress": ["滋养、创造、身体感受", "过度付出、依赖舒适、失去边界", "皇后在建议位会让你照顾什么？", "照顾身体和情绪，同时把付出的边界说清楚。"],
            "The Emperor": ["秩序、规则、稳定掌控", "僵硬、控制欲、害怕失序", "皇帝会建议你建立什么？", "建立一个清晰规则或时间表，而不是靠情绪硬撑。"],
            "The Lovers": ["选择、关系、价值一致", "犹豫、讨好、价值冲突", "恋人牌的小测重点是什么？", "选择前先确认：这是否符合你真正重视的东西。"],
            "The Chariot": ["推进、意志、方向感", "用力过猛、失控、目标冲突", "战车提醒你如何行动？", "把目标收束成一个方向，再集中推进。"],
            "Strength": ["温柔的力量、耐心、自我安抚", "压抑怒气、硬撑、失去耐心", "力量牌的关键词不是强硬，而是什么？", "用稳定和耐心驯服情绪，而不是压住情绪。"],
            "The Hermit": ["独处、反思、内在答案", "孤立、逃避连接、过度封闭", "隐士出现时适合做什么？", "给自己安静时间，但不要完全切断必要沟通。"],
            "Wheel of Fortune": ["周期、转机、变化", "抗拒变化、反复无常、赌运气", "命运之轮提醒你看见什么？", "看见事情处在变化周期里，顺势调整计划。"],
            "Justice": ["公平、事实、因果", "偏见、逃避责任、不平衡", "正义牌建议你先检查什么？", "先核对事实和责任边界，再做判断。"],
            "The Hanged Man": ["暂停、换角度、等待", "停滞、牺牲感、迟迟不动", "倒吊人为什么不是失败？", "它是在提醒你换角度，等待不是放弃。"],
            "Death": ["结束、更新、转化", "抓住旧状态、害怕告别", "死神牌要你放下什么？", "放下已经失效的模式，给新阶段腾位置。"],
            "Temperance": ["调和、节制、慢慢融合", "失衡、极端、急着见效", "节制牌建议的节奏是什么？", "慢慢调配，不用一次到位。"],
            "The Devil": ["欲望、束缚、看见依赖", "沉迷、恐惧、被习惯控制", "恶魔牌要你识别什么？", "识别让你失去自由的欲望或恐惧。"],
            "The Tower": ["破局、真相显露、重建", "害怕崩塌、维持假稳定", "高塔后的第一步是什么？", "先承认真相，再重建更稳的结构。"],
            "The Star": ["希望、疗愈、长期信念", "失望、能量低、看不见未来", "星星牌给你的提醒是什么？", "把希望落到长期的小行动里。"],
            "The Moon": ["潜意识、迷雾、敏感", "焦虑脑补、误解、不确定", "月亮牌出现时不要急着做什么？", "不要急着下结论，先分清事实和想象。"],
            "The Sun": ["清晰、快乐、被看见", "过度乐观、幼稚、忽略细节", "太阳牌建议你如何表达？", "坦诚明亮地表达，同时保留基本细节检查。"],
            "Judgement": ["召唤、复盘、醒来", "自责、拒绝回应、旧事缠绕", "审判牌让你复盘什么？", "复盘过去的选择，并回应新的召唤。"],
            "The World": ["完成、整合、阶段成果", "未收尾、缺最后一步、空转", "世界牌的小测答案通常是什么？", "完成收尾，把经验整合成下一阶段的起点。"],
        };
        const picked = majorLessons[card.name] || ["关键课题、转化、成长", "课题受阻、需要放慢理解", "这张大阿卡那在提醒你面对什么人生课题？", "把牌义当成阶段提醒，找出你正在学习的一件事。"];
        return { upright: picked[0], reversed: picked[1], quiz: picked[2], answer: picked[3] };
    }

    const suitLessons = {
        wands: ["行动、热情、创造力", "急躁、分散、动力不足", "权杖牌出现时，建议位通常推动你做什么？", "把想法变成行动，但先确认优先级。"],
        cups: ["情绪、关系、感受流动", "情绪泛滥、逃避表达、依赖", "圣杯牌会提醒你照顾哪一层面？", "照顾感受并真诚表达，不用把情绪包装成理性。"],
        swords: ["思考、沟通、判断", "过度分析、焦虑、语言伤人", "宝剑牌在建议位最常提醒什么？", "把想法说清楚，也检查自己是否想太多。"],
        pentacles: ["现实、资源、稳定积累", "拖延、匮乏感、现实压力", "星币牌会让你把注意力放回哪里？", "回到现实资源、时间安排和可执行步骤。"],
    };
    const rank = card.name.split(" of ")[0] || card.name;
    const suit = suitLessons[card.suit] || ["现实经验、具体行动", "能量受阻、需要调整", "这张牌在建议位提醒什么？", "把牌义落到一个具体行动。"];
    return {
        upright: `${rank}：${suit[0]}`,
        reversed: `${rank} 的阻滞：${suit[1]}`,
        quiz: `${card.name} 出现在“建议”位置时，你会提醒自己做哪一步？`,
        answer: suit[3],
    };
}

async function renderJournalResponse() {
    const text = els.journalInput.value.trim();
    if (text.length < 4) {
        showToast("先写下一句今天的状态");
        return;
    }
    const card = state.dailyCard;
    const cardName = card?.name || "今日牌";
    const topic = inferJournalTopic(text);
    setButtonLoading(els.journalBtn, "生成中...");
    els.journalResponse.innerHTML = "<p>正在结合今日牌整理回应...</p>";
    let responseText = "";
    try {
        const data = await withTimeout(requestJson("/api/journal_reflect", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text,
                daily_card: card || {},
                topic,
            }),
        }), AI_FRONTEND_TIMEOUT);
        if (!data.success) throw new Error(data.error || "日记回应失败");
        responseText = stripThinking(data.response);
    } catch (error) {
        responseText = buildLocalJournalResponse(text, cardName, topic);
        showToast("AI 暂不可用，已生成本地陪伴回应");
    } finally {
        setButtonReady(els.journalBtn, "生成今日回应");
    }
    const responseHtml = formatJournalResponse(responseText, topic);
    state.latestJournal = {
        id: Date.now().toString(),
        createdAt: new Date().toLocaleString("zh-CN"),
        text,
        responseHtml,
        topic,
        title: makeJournalTitle(text),
        comments: [],
    };
    els.journalResponse.innerHTML = responseHtml;
}

async function saveJournalEntry() {
    if (!state.latestJournal) {
        const text = els.journalInput.value.trim();
        if (text.length < 4) {
            showToast("先生成一段今日回应再保存");
            return;
        }
        await renderJournalResponse();
    }
    const journals = getJournals();
    journals.unshift({ ...state.latestJournal, id: Date.now().toString() });
    localStorage.setItem(JOURNAL_KEY, JSON.stringify(journals.slice(0, 60)));
    hydrateJournals();
    showToast("日记已保存到私人空间");
}

function formatJournalResponse(responseText, topic) {
    const safeText = escapeHtml(responseText).replace(/\n{2,}/g, "</p><p>").replace(/\n/g, "<br>");
    return `
        <div class="journal-ai-text"><p>${safeText}</p></div>
        <span class="chip">自动归类：${escapeHtml(topic)}</span>
    `;
}

function buildLocalJournalResponse(text, cardName, topic) {
    const topicHint = {
        "感情": "关系里的真实感受",
        "学业/事业": "任务之外的身体负荷",
        "家庭": "亲近关系中的边界",
        "自我": "你对自己的要求",
    }[topic] || "你当下最需要被看见的部分";
    return `标题：${makeJournalTitle(text)}

结合 ${cardName}，这段日记更像是在提醒你看见：${topicHint}。你不需要立刻把所有情绪整理成答案，先承认此刻的疲惫和混乱，本身就是一种诚实。

反思问题：今天最消耗你的，是事情本身，还是你一直在心里反复推演它？

小行动：给自己十分钟，不解决问题，只把下一步能做的一件小事写下来。`;
}

function hydrateJournals() {
    if (!els.journalList) return;
    const journals = getJournals();
    if (!journals.length) {
        els.journalList.className = "journal-list empty";
        els.journalList.textContent = "还没有保存日记";
        return;
    }

    els.journalList.className = "journal-list";
    els.journalList.innerHTML = "";
    journals.forEach((entry) => {
        const item = document.createElement("article");
        item.className = "journal-entry";
        item.innerHTML = `
            <div class="journal-entry-head">
                <div>
                    <strong>${escapeHtml(entry.title || makeJournalTitle(entry.text))}</strong>
                    <span>${escapeHtml(entry.createdAt)} · ${escapeHtml(entry.topic || "自我")}</span>
                </div>
                <button class="text-btn" type="button" data-delete-journal="${entry.id}">删除</button>
            </div>
            <p>${escapeHtml(entry.text)}</p>
            <div class="journal-entry-response">${entry.responseHtml || ""}</div>
            <div class="journal-comments">
                ${(entry.comments || []).map((comment) => `
                    <div class="journal-comment">
                        <span>${escapeHtml(comment.createdAt)}</span>
                        <p>${escapeHtml(comment.text)}</p>
                    </div>
                `).join("")}
            </div>
            <div class="journal-comment-form">
                <input class="text-input" maxlength="160" placeholder="给这篇日记留一句评论">
                <button class="ghost-btn small" type="button" data-comment-journal="${entry.id}">评论</button>
            </div>
        `;
        item.querySelector("[data-delete-journal]").addEventListener("click", () => deleteJournal(entry.id));
        item.querySelector("[data-comment-journal]").addEventListener("click", () => {
            const input = item.querySelector(".journal-comment-form input");
            addJournalComment(entry.id, input.value);
        });
        els.journalList.appendChild(item);
    });
}

function getJournals() {
    try {
        return JSON.parse(localStorage.getItem(JOURNAL_KEY) || "[]");
    } catch {
        return [];
    }
}

function addJournalComment(entryId, text) {
    const trimmed = text.trim();
    if (!trimmed) {
        showToast("先写一句评论");
        return;
    }
    const journals = getJournals();
    const entry = journals.find((item) => item.id === entryId);
    if (!entry) return;
    entry.comments = entry.comments || [];
    entry.comments.unshift({
        id: Date.now().toString(),
        text: trimmed,
        createdAt: new Date().toLocaleString("zh-CN"),
    });
    localStorage.setItem(JOURNAL_KEY, JSON.stringify(journals));
    hydrateJournals();
    showToast("评论已保存");
}

function deleteJournal(entryId) {
    const journals = getJournals().filter((entry) => entry.id !== entryId);
    localStorage.setItem(JOURNAL_KEY, JSON.stringify(journals));
    hydrateJournals();
    showToast("日记已删除");
}

function clearJournals() {
    localStorage.removeItem(JOURNAL_KEY);
    hydrateJournals();
    showToast("陪伴日记已清空");
}

function resetReading() {
    state.selectedBlindIds = [];
    state.drawnCards = [];
    state.drawnPositions = [];
    state.interpretation = "";
    state.intentCharged = false;
    els.intentBtn.textContent = "长按注入问题";
    document.querySelector(".ritual-box").classList.remove("charged");
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
        return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    } catch {
        return [];
    }
}

function getReviews() {
    try {
        return JSON.parse(localStorage.getItem(REVIEW_KEY) || "{}");
    } catch {
        return {};
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
    if (arcana === "major") return "☉";
    return {
        wands: "✦",
        cups: "♡",
        swords: "⌁",
        pentacles: "◇",
    }[suit] || "✦";
}

function buildShareText() {
    const cards = state.drawnCards
        .map((card, index) => `${index + 1}. ${card.name}（${card.reversed ? "逆位" : "正位"}）`)
        .join("\n");
    return `问题：${getQuestion()}\n牌阵：${getSpreadName(state.spread)}\n\n${cards}\n\n${state.interpretation}`;
}

function buildLocalInterpretation() {
    const cards = state.drawnCards.map((card) => `${card.name}${card.reversed ? "逆位" : "正位"}`).join("、");
    const words = topicWords[state.topic] || topicWords.general;
    return `本次牌面：${cards}\n\n这组牌更像是在提醒你关注「${words.slice(0, 2).join("」和「")}」。先不要把它当成绝对预言，而是把它当成一次反思：现在最需要被看见的，是你的真实感受、行动节奏，以及你愿意承担的下一步。\n\n建议：写下一个 24 小时内可以完成的小动作，再观察事情是否因为这个动作出现新的反馈。`;
}

function buildLocalRelationshipInterpretation(a, b, relation) {
    const cards = state.relationshipCards
        .map((card) => `${card.name}${card.reversed ? "逆位" : "正位"}`)
        .join("、");
    return `关系主题：${a} 与 ${b} 的${relation}\n\n牌面线索：${cards}\n\n这段关系目前最值得看的不是谁对谁错，而是双方在靠近和自我保护之间的节奏差。隐藏情绪里可能有期待，也可能有不敢直接说出口的顾虑。\n\n建议：先用一个低压力的问题确认彼此真实状态，不急着把关系定性。把重点放在沟通是否清楚、边界是否舒服、行动是否一致。`;
}

function buildLocalDailyAdvice(card) {
    const direction = card.reversed ? "放慢反应，先处理内在阻力。" : "顺着当下的清晰感，做一个小决定。";
    return `${card.name} 提醒你：${direction}`;
}

function localizeSpread(spread) {
    const fallback = spreadFallbacks[spread.id];
    if (!fallback) return spread;
    return {
        ...spread,
        name: fallback.name,
        description: fallback.description,
        positions: spread.positions?.map((position, index) => fallback.positions[index] || position) || fallback.positions,
    };
}

function addDays(date, days) {
    const next = new Date(date);
    next.setDate(next.getDate() + days);
    return next;
}

function mostCommon(values) {
    const counts = new Map();
    values.filter(Boolean).forEach((value) => counts.set(value, (counts.get(value) || 0) + 1));
    return [...counts.entries()].sort((a, b) => b[1] - a[1])[0]?.[0];
}

function inferJournalTopic(text) {
    if (/喜欢|恋|暧昧|分手|前任|ta|TA/.test(text)) return "感情";
    if (/学习|考试|工作|项目|老板|同事|事业/.test(text)) return "学业/事业";
    if (/家|父母|亲人/.test(text)) return "家庭";
    return "自我";
}

function makeJournalTitle(text) {
    if (text.length <= 14) return text;
    return `${text.slice(0, 14)}...`;
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
        throw new Error("接口返回为空，请检查服务是否启动");
    }

    return data;
}

function withTimeout(promise, timeoutMs) {
    return Promise.race([
        promise,
        new Promise((_, reject) => {
            window.setTimeout(() => reject(new Error("AI 解读等待超时")), timeoutMs);
        }),
    ]);
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

function stripThinking(value) {
    return String(value ?? "")
        .replace(/<think\b[^>]*>[\s\S]*?<\/think>/gi, "")
        .replace(/<thinking\b[^>]*>[\s\S]*?<\/thinking>/gi, "")
        .replace(/<reasoning\b[^>]*>[\s\S]*?<\/reasoning>/gi, "")
        .replace(/<think\b[^>]*>[\s\S]*$/gi, "")
        .replace(/<thinking\b[^>]*>[\s\S]*$/gi, "")
        .replace(/<reasoning\b[^>]*>[\s\S]*$/gi, "")
        .replace(/<\/?(think|thinking|reasoning)[^>]*>/gi, "")
        .trim();
}
