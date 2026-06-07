const API = "https://shopbotshemsu-1.onrender.com/api";
const tg = window.Telegram?.WebApp;
const USER_ID = tg?.initDataUnsafe?.user?.id || 7598009952;
const USERNAME = tg?.initDataUnsafe?.user?.username || "adasbear";
const INIT_DATA = tg?.initData || "";
const PHOTO_URL = tg?.initDataUnsafe?.user?.photo_url || "";

let state = {
  cart: [],
  currentPage: "home",
  navStack: ["home"],
  user: null,
  menu: [],
  orders: [],
  debts: [],
  notifications: [],
  paymentAccounts: [],
};

function $(id) { return document.getElementById(id); }

async function api(path, opts = {}) {
  const url = `${API}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...opts.headers },
    ...opts,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: "Request failed" }));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

async function loadUser() {
  try {
    state.user = await api(`/user/profile?user_id=${USER_ID}`);
  } catch (e) {
    state.user = { user_id: USER_ID, username: USERNAME, full_name: "User" };
  }
  document.querySelector(".pf-name-side").textContent = state.user?.full_name?.split(" ")[0] || "Member";
  document.querySelector(".pf-username-side").textContent = `@${state.user?.username || USERNAME}`;
  if (PHOTO_URL) {
    document.querySelectorAll(".js-avatar").forEach((div) => {
      div.style.backgroundImage = `url(${PHOTO_URL})`;
      div.style.backgroundSize = "cover";
      div.style.backgroundPosition = "center";
      const icon = div.querySelector(".js-avatar-icon");
      if (icon) icon.style.display = "none";
    });
  }
}

async function loadMenu() {
  state.menu = await api(`/menu`);
  return state.menu;
}

async function loadOrders() {
  state.orders = await api(`/orders?user_id=${USER_ID}`);
  return state.orders;
}

async function loadDebts() {
  state.debts = await api(`/debts?username=${USERNAME}`);
  return state.debts;
}

async function loadNotifications() {
  state.notifications = await api(`/notifications?user_id=${USER_ID}`);
  return state.notifications;
}

async function loadPaymentAccounts() {
  state.paymentAccounts = await api(`/payment-accounts`);
  return state.paymentAccounts;
}

async function checkDebtAllow() {
  const r = await api(`/debt-allow-list/check?username=${USERNAME}`);
  return r.allowed;
}

async function getDebtTotal() {
  const r = await api(`/debts/active-total?username=${USERNAME}`);
  return r.active_total;
}

async function getOrderGroup(og) {
  return await api(`/orders/group/${og}`);
}

// --- Cart ---
function getCart() {
  const saved = localStorage.getItem("cart");
  state.cart = saved ? JSON.parse(saved) : [];
  return state.cart;
}
function saveCart() {
  localStorage.setItem("cart", JSON.stringify(state.cart));
}
function addToCart(item) {
  const existing = state.cart.find((i) => i.item === item.name);
  if (existing) {
    existing.qty++;
  } else {
    state.cart.push({ item: item.name, price: item.price, qty: 1, id: item.id });
  }
  saveCart();
  updateCartBadge();
}
function removeFromCart(itemName) {
  state.cart = state.cart.filter((i) => i.item !== itemName);
  saveCart();
  updateCartBadge();
}
function updateCartQty(itemName, delta) {
  const item = state.cart.find((i) => i.item === itemName);
  if (!item) return;
  item.qty += delta;
  if (item.qty <= 0) {
    removeFromCart(itemName);
  } else {
    saveCart();
  }
  updateCartBadge();
}
function getCartTotal() {
  return state.cart.reduce((sum, i) => sum + i.price * i.qty, 0);
}
function clearCart() {
  state.cart = [];
  saveCart();
  updateCartBadge();
}
function updateCartBadge() {
  document.querySelectorAll(".cart-badge").forEach((el) => {
    const total = state.cart.reduce((s, i) => s + i.qty, 0);
    el.textContent = total;
    el.classList.toggle("hidden", total === 0);
  });
}

// --- Router ---
function navigateTo(page, params) {
  if (state.navStack[state.navStack.length - 1] !== page) {
    state.navStack.push(page);
  }
  const hash = params ? `${page}?${new URLSearchParams(params)}` : page;
  window.location.hash = hash;
}

function showPage(page) {
  document.querySelectorAll(".page").forEach((p) => p.classList.add("hidden"));
  const el = $(`page-${page}`);
  if (el) el.classList.remove("hidden");
  document.querySelectorAll(".nav-item").forEach((n) => {
    const p = n.dataset.page;
    const isActive = p === page;
    n.classList.toggle("nav-active", isActive);
  });
  if (tg) {
    tg.BackButton.isVisible = state.navStack.length > 1;
  }
  window.scrollTo(0, 0);
}

function initRouter() {
  function handleHash() {
    const hash = window.location.hash.slice(1) || "home";
    const [page, qs] = hash.split("?");
    const params = Object.fromEntries(new URLSearchParams(qs));
    if (state.navStack[state.navStack.length - 1] !== page) {
      state.navStack = [page];
    }
    showPage(page);
    initPage(page, params);
  }
  window.addEventListener("hashchange", handleHash);
  handleHash();
}

// --- Page Init ---
async function initPage(page, params) {
  switch (page) {
    case "home": renderHome(); break;
    case "menu": renderMenu(); break;
    case "cart": renderCart(); break;
    case "orders": renderOrders(); break;
    case "order-detail": renderOrderDetail(params?.og); break;
    case "order-placed": renderOrderPlaced(params?.og); break;
    case "profile": renderProfile(); break;
    case "debt": renderDebt(); break;
    case "notifications": renderNotifications(); break;
    case "help": renderHelp(); break;
    case "contact": break;
    case "feedback": break;
  }
}

// --- Navigation Setup ---
function setupNavigation() {
  document.addEventListener("click", (e) => {
    const nav = e.target.closest("[data-nav]");
    if (nav) {
      e.preventDefault();
      navigateTo(nav.dataset.nav);
    }
  });
}

// --- Render Functions ---

function renderHome() {
  const el = $("page-home");
  if (!el) return;
  const name = state.user?.full_name || "User";
  el.querySelector(".welcome-name").textContent = `Hi ${name.split(" ")[0]} 👋`;
  loadDebtTotalForHome();
}

async function loadDebtTotalForHome() {
  try {
    const total = await getDebtTotal();
    const banner = document.querySelector(".debt-banner");
    if (banner) {
      if (total > 0) {
        banner.classList.remove("hidden");
        banner.querySelector(".debt-amount").textContent = `${total.toFixed(2)} Birr`;
      } else {
        banner.classList.add("hidden");
      }
    }
  } catch (e) {}
}

async function renderMenu() {
  const grid = $("menu-grid");
  if (!grid) return;
  grid.innerHTML = '<div class="col-span-full text-center py-12"><div class="skeleton h-48 w-48 mx-auto mb-4 rounded-full"></div><div class="skeleton h-4 w-48 mx-auto"></div></div>';
  try {
    const items = await loadMenu();
    const categories = items.filter((i) => i.price === 0);
    const subItems = items.filter((i) => i.price > 0);
    const cats = categories.length ? categories.map((c) => c.name) : ["All"];

    let catHtml = cats.map((c) =>
      `<button class="cat-btn flex-shrink-0 font-label-mono text-label-mono px-6 py-2 text-ink-black uppercase tracking-wider ${c === "All" ? "scribble-highlight" : "opacity-60 hover:opacity-100 hover:bg-paper-shadow"} transition-all" data-cat="${c}">${c}</button>`
    ).join("");
    $("menu-categories").innerHTML = catHtml;

    $("menu-categories").querySelectorAll(".cat-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        $("menu-categories").querySelectorAll(".cat-btn").forEach((b) => {
          b.classList.remove("scribble-highlight");
          b.classList.add("opacity-60");
        });
        btn.classList.add("scribble-highlight");
        btn.classList.remove("opacity-60");
        renderMenuItems(subItems, btn.dataset.cat);
      });
    });

    renderMenuItems(subItems, "All");
  } catch (e) {
    grid.innerHTML = `<div class="col-span-full text-center py-12"><p class="text-error font-headline-lg">Failed to load menu</p></div>`;
  }
}

function renderMenuItems(items, category) {
  const grid = $("menu-grid");
  const filtered = category === "All" ? items : items.filter((i) => i.parent === category);
  if (!filtered.length) {
    grid.innerHTML = `<div class="col-span-full text-center py-12"><p class="font-headline-lg text-on-surface-variant">No items in this category</p></div>`;
    return;
  }
  grid.innerHTML = filtered.map((item) => {
    const rot = (Math.random() * 2 - 1).toFixed(2);
    const img = item.image_url ? `<img src="${item.image_url}" alt="${item.name}" class="w-full h-full object-cover"/>` : `<span class="material-symbols-outlined text-5xl text-primary">restaurant</span>`;
    return `<div class="menu-item group bg-surface-container rough-border p-4 flex flex-col items-center text-center relative hover:scale-[1.02] transition-transform" style="transform:rotate(${rot}deg)">
      <div class="w-full aspect-square mb-4 bg-white/50 rough-border overflow-hidden flex items-center justify-center">
        ${img}
      </div>
      <span class="text-secondary font-headline-lg text-xl md:text-2xl mb-2">${item.price.toFixed(2)} Birr</span>
      <h3 class="font-headline-lg text-lg md:text-xl uppercase mb-4">${item.name}</h3>
      <button class="add-to-cart w-12 h-12 rounded-full bg-secondary-container text-on-secondary-container border-4 border-ink-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] flex items-center justify-center hover:scale-95 active:translate-x-0.5 active:translate-y-0.5 transition-all" data-item='${item.name}' data-price='${item.price}' data-id='${item.id}'>
        <span class="material-symbols-outlined font-bold">add</span>
      </button>
    </div>`;
  }).join("");

  grid.querySelectorAll(".add-to-cart").forEach((btn) => {
    btn.addEventListener("click", () => {
      addToCart({ name: btn.dataset.item, price: parseFloat(btn.dataset.price), id: parseInt(btn.dataset.id) });
      btn.innerHTML = '<span class="material-symbols-outlined font-bold fill">check</span>';
      setTimeout(() => { btn.innerHTML = '<span class="material-symbols-outlined font-bold">add</span>'; }, 1000);
    });
  });
}

function renderCart() {
  const items = $("cart-items");
  const subtotal = $("cart-subtotal");
  const totalEl = $("cart-total");
  const countEl = $("cart-count");
  if (!items) return;
  getCart();
  if (!state.cart.length) {
    items.innerHTML = '<div class="col-span-full text-center py-12"><span class="material-symbols-outlined text-6xl text-on-surface-variant">shopping_cart</span><p class="font-headline-lg mt-4">Your cart is empty</p><button class="mt-4 bg-primary text-white px-6 py-3 rough-border hard-shadow font-label-mono" data-nav="menu">Browse Menu</button></div>';
    subtotal.textContent = "0.00 Birr";
    totalEl.textContent = "0.00 Birr";
    countEl.textContent = "0 ITEMS";
    return;
  }
  items.innerHTML = state.cart.map((i) =>
    `<div class="cart-item bg-background border-4 border-ink-black p-4 flex gap-4 items-center hard-shadow hover:rotate-0 transition-transform" style="transform:rotate(${(Math.random()*2-1).toFixed(2)}deg)">
      <div class="w-20 h-20 bg-paper-shadow border-2 border-ink-black flex-shrink-0 flex items-center justify-center">
        <span class="material-symbols-outlined text-3xl text-primary">restaurant</span>
      </div>
      <div class="flex-grow min-w-0">
        <h3 class="font-headline-lg text-headline-lg-mobile text-ink-black mb-1 truncate">${i.item.toUpperCase()}</h3>
        <p class="font-label-mono text-label-mono text-primary">${i.price.toFixed(2)} Birr</p>
      </div>
      <div class="flex items-center gap-2 bg-secondary-container border-2 border-ink-black p-1 px-2 rounded-xl">
        <button class="qty-minus w-7 h-7 flex items-center justify-center font-bold hover:scale-110" data-item="${i.item}">−</button>
        <span class="font-label-mono text-headline-lg-mobile w-6 text-center">${i.qty}</span>
        <button class="qty-plus w-7 h-7 flex items-center justify-center font-bold hover:scale-110" data-item="${i.item}">+</button>
      </div>
      <button class="cart-remove text-error hover:scale-110 transition-transform p-1" data-item="${i.item}">
        <span class="material-symbols-outlined">delete_forever</span>
      </button>
    </div>`
  ).join("");

  const total = getCartTotal();
  subtotal.textContent = `${total.toFixed(2)} Birr`;
  totalEl.textContent = `${(total + (total > 0 ? 80 : 0)).toFixed(2)} Birr`;
  countEl.textContent = `${state.cart.reduce((s, i) => s + i.qty, 0)} ITEMS`;

  items.querySelectorAll(".qty-minus").forEach((btn) => {
    btn.addEventListener("click", () => { updateCartQty(btn.dataset.item, -1); renderCart(); });
  });
  items.querySelectorAll(".qty-plus").forEach((btn) => {
    btn.addEventListener("click", () => { updateCartQty(btn.dataset.item, 1); renderCart(); });
  });
  items.querySelectorAll(".cart-remove").forEach((btn) => {
    btn.addEventListener("click", () => { removeFromCart(btn.dataset.item); renderCart(); });
  });

  loadPaymentAccountsUI();
}

async function renderOrders() {
  const list = $("orders-list");
  if (!list) return;
  list.innerHTML = '<div class="text-center py-12"><div class="skeleton h-24 w-full mb-4"></div><div class="skeleton h-24 w-full"></div></div>';
  try {
    const orders = await loadOrders();
    const grouped = {};
    orders.forEach((o) => {
      if (!grouped[o.order_group]) grouped[o.order_group] = [];
      grouped[o.order_group].push(o);
    });
    const groups = Object.entries(grouped);
    if (!groups.length) {
      list.innerHTML = '<div class="text-center py-12"><span class="material-symbols-outlined text-6xl text-on-surface-variant">receipt_long</span><p class="font-headline-lg mt-4">No orders yet</p><button class="mt-4 bg-primary text-white px-6 py-3 rough-border hard-shadow font-label-mono" data-nav="menu">Order Now</button></div>';
      return;
    }
    list.innerHTML = groups.map(([og, items]) =>
      `<div class="order-card cursor-pointer bg-white border-4 border-ink-black hard-shadow p-4 md:p-6 hover:rotate-0 transition-transform" style="transform:rotate(${(Math.random()*2-1).toFixed(2)}deg)" data-og="${og}">
        <div class="flex justify-between items-start gap-4 mb-3">
          <div class="min-w-0 flex-1">
            <p class="font-label-mono text-label-mono text-tertiary mb-1 truncate">REF: ${og}</p>
            <h3 class="font-headline-lg-mobile text-headline-lg-mobile truncate">${items[0].item}${items.length > 1 ? ` +${items.length - 1} more` : ""}</h3>
          </div>
          <div class="flex flex-col items-end gap-1 flex-shrink-0">
            <span class="inline-block status-badge-${items[0].status.toLowerCase()} px-3 py-1 border-2 border-ink-black rounded-full font-label-mono text-label-mono text-xs">${items[0].status}</span>
            <p class="font-label-mono text-label-mono text-xs">${new Date(items[0].timestamp).toLocaleDateString()}</p>
          </div>
        </div>
        <div class="border-t-2 border-dashed border-ink-black pt-3 flex justify-between items-center">
          <p class="font-label-mono text-xs truncate">${items.map(i => `${i.qty}x ${i.item}`).join(", ")}</p>
          <span class="material-symbols-outlined text-primary flex-shrink-0">chevron_right</span>
        </div>
      </div>`
    ).join("");
    list.querySelectorAll(".order-card").forEach((card) => {
      card.addEventListener("click", () => navigateTo("order-detail", { og: card.dataset.og }));
    });
  } catch (e) {
    list.innerHTML = `<div class="text-center py-12"><p class="text-error font-headline-lg">Failed to load orders</p></div>`;
  }
}

async function renderOrderDetail(og) {
  const el = $("page-order-detail");
  if (!el || !og) return;
  try {
    const data = await getOrderGroup(og);
    el.querySelector(".od-ref").textContent = `REF: ${og}`;
    const statusEl = el.querySelector(".od-status");
    statusEl.textContent = data.status || "Pending";
    statusEl.className = `od-status status-badge-${(data.status||"pending").toLowerCase()} px-4 py-1 border-2 border-ink-black rounded-full font-label-mono text-label-mono`;
    el.querySelector(".od-date").textContent = data.created_at ? new Date(data.created_at).toLocaleString() : "";
    el.querySelector(".od-items").innerHTML = (data.items || []).map(i =>
      `<div class="flex justify-between items-center py-2 border-b border-dashed border-ink-black font-body-md">
        <span>${i.qty}x ${i.item}</span>
      </div>`
    ).join("");
    el.querySelector(".od-total").textContent = `${data.total.toFixed(2)} Birr`;
    const commentEl = el.querySelector(".od-comment");
    commentEl.textContent = data.comment || "None";
    commentEl.classList.toggle("text-on-surface-variant", !data.comment);
    const declineSection = el.querySelector(".od-decline");
    declineSection.classList.toggle("hidden", !data.decline_reason);
    if (data.decline_reason) {
      el.querySelector(".od-decline-reason").textContent = data.decline_reason;
    }
    const cancelBtn = el.querySelector(".od-cancel");
    cancelBtn.classList.toggle("hidden", data.status !== "Pending");
    cancelBtn.onclick = async () => {
      if (!confirm("Cancel this order?")) return;
      try {
        await api(`/orders/${og}`, { method: "DELETE" });
        navigateTo("orders");
      } catch(e) { alert("Failed to cancel: " + e.message); }
    };
  } catch (e) {
    el.querySelector(".od-ref").textContent = "Error loading order";
  }
}

function renderOrderPlaced(og) {
  const el = $("page-order-placed");
  if (!el) return;
  el.querySelector(".op-ref").textContent = og || "APP-UNKNOWN";
}

async function renderProfile() {
  await loadUser();
  const el = $("page-profile");
  if (!el) return;
  el.querySelector(".pf-name").textContent = state.user?.full_name || "User";
  el.querySelector(".pf-username").textContent = `@${state.user?.username || USERNAME}`;
}

async function renderDebt() {
  const list = $("debt-list");
  const totalEl = $("debt-total");
  if (!list) return;
  list.innerHTML = '<div class="text-center py-12"><div class="skeleton h-16 w-full mb-4"></div><div class="skeleton h-16 w-full"></div></div>';
  try {
    const debts = await loadDebts();
    const activeTotal = await getDebtTotal();
    totalEl.textContent = `${activeTotal.toFixed(2)} Birr`;
    if (!debts.length) {
      list.innerHTML = '<div class="text-center py-12"><p class="font-headline-lg">No debts found</p></div>';
      return;
    }
    list.innerHTML = debts.map(d =>
      `<div class="bg-white border-4 border-ink-black p-4 hard-shadow" style="transform:rotate(${(Math.random()*2-1).toFixed(2)}deg)">
        <div class="flex justify-between items-center">
          <div>
            <p class="font-label-mono text-label-mono text-tertiary">${new Date(d.created_at).toLocaleDateString()}</p>
            <p class="font-headline-lg text-xl text-ink-black">${d.amount.toFixed(2)} Birr</p>
          </div>
          <span class="status-badge-${d.status} px-3 py-1 border-2 border-ink-black rounded-full font-label-mono text-label-mono text-xs">${d.status.toUpperCase()}</span>
        </div>
      </div>`
    ).join("");
  } catch (e) {
    list.innerHTML = `<div class="text-center py-12"><p class="text-error font-headline-lg">Failed to load debts</p></div>`;
  }
}

async function renderNotifications() {
  const list = $("notif-list");
  if (!list) return;
  try {
    const notifs = await loadNotifications();
    if (!notifs.length) {
      list.innerHTML = '<div class="text-center py-12"><span class="material-symbols-outlined text-6xl text-on-surface-variant">notifications_off</span><p class="font-headline-lg mt-4">No notifications</p></div>';
      return;
    }
    list.innerHTML = notifs.map(n =>
      `<div class="notif-item bg-white border-4 border-ink-black p-4 hard-shadow ${n.read ? "opacity-60" : ""}" data-id="${n.id}">
        <div class="flex justify-between items-start gap-4">
          <div class="flex-1 min-w-0">
            <h4 class="font-headline-lg-mobile text-headline-lg-mobile">${n.title}</h4>
            <p class="font-body-md text-body-md mt-1">${n.body}</p>
          </div>
          <div class="flex flex-col items-end gap-2 flex-shrink-0">
            <p class="font-label-mono text-[10px] text-tertiary">${new Date(n.created_at).toLocaleDateString()}</p>
            ${n.read ? "" : '<span class="w-3 h-3 bg-secondary rounded-full border border-ink-black"></span>'}
          </div>
        </div>
      </div>`
    ).join("");
    list.querySelectorAll(".notif-item:not(.opacity-60)").forEach((item) => {
      item.addEventListener("click", async () => {
        const id = item.dataset.id;
        try {
          await api(`/notifications/${id}/read`, { method: "PUT" });
          item.classList.add("opacity-60");
          item.querySelector(".w-3.h-3")?.remove();
        } catch (e) {}
      });
    });
  } catch (e) {
    list.innerHTML = `<div class="text-center py-12"><p class="text-error font-headline-lg">Failed to load notifications</p></div>`;
  }
}

function renderHelp() {
  const list = $("help-list");
  if (!list) return;
  const faqs = [
    { q: "How do I place an order?", a: "Browse the menu, add items to your cart, and checkout. Choose a payment method and confirm." },
    { q: "Can I cancel my order?", a: "Yes, you can cancel pending orders before 6PM UTC on the same day." },
    { q: "What payment methods are accepted?", a: "We accept bank transfers to our registered accounts. Paste your SMS confirmation after payment." },
    { q: "What is the debt system?", a: "Eligible users can order on debt. The amount is added to your debt balance which you can pay later." },
    { q: "How do I pay my debt?", a: "Go to My Debt, select 'Pay Now', choose a payment method, and paste your SMS confirmation." },
  ];
  list.innerHTML = faqs.map((f, i) =>
    `<div class="faq-item bg-white border-4 border-ink-black hard-shadow" style="transform:rotate(${(Math.random()*2-1).toFixed(2)}deg)">
      <button class="faq-toggle w-full p-4 text-left flex justify-between items-center gap-4" data-idx="${i}">
        <span class="font-headline-lg-mobile text-headline-lg-mobile flex-1">${f.q}</span>
        <span class="material-symbols-outlined transition-transform">expand_more</span>
      </button>
      <div class="faq-answer hidden px-4 pb-4 border-t-2 border-dashed border-ink-black pt-3">
        <p class="font-body-md text-body-md">${f.a}</p>
      </div>
    </div>`
  ).join("");
  list.querySelectorAll(".faq-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const answer = btn.parentElement.querySelector(".faq-answer");
      const icon = btn.querySelector(".material-symbols-outlined");
      answer.classList.toggle("hidden");
      icon.classList.toggle("rotate-180");
    });
  });
}

// --- Place Order ---
async function placeOrder(comment) {
  if (!state.cart.length) return { error: "Cart is empty" };
  const paymentMethod = _selectedPayment.method;
  const paymentAccountId = _selectedPayment.accountId;
  const confirmation = $("payment-confirmation")?.value?.trim() || "";
  if (paymentMethod !== "debt" && !paymentAccountId) {
    return { error: "Please select a bank or payment method." };
  }
  if (paymentMethod === "debt" && !_debtAllowed) {
    return { error: "You are not on the debt allow list." };
  }
  try {
    const result = await api("/orders", {
      method: "POST",
      body: JSON.stringify({
        user_id: USER_ID,
        username: USERNAME,
        full_name: state.user?.full_name || USERNAME,
        items: state.cart.map((i) => ({ item: i.item, qty: i.qty })),
        payment_method: paymentMethod === "debt" ? "debt" : paymentMethod,
        payment_account_id: paymentAccountId,
        confirmation: confirmation,
        comment: comment || "",
      }),
    });
    if (result.success) {
      clearCart();
      navigateTo("order-placed", { og: result.order_group });
    }
    return result;
  } catch (e) {
    return { error: e.message };
  }
}

// --- Payment Accounts UI ---
let _selectedPayment = { method: "bank", accountId: null, account: null };
let _debtAllowed = false;

async function loadPaymentAccountsUI() {
  try {
    const accounts = await loadPaymentAccounts();
    const methodsEl = $("payment-methods");
    if (!methodsEl) return;
    _debtAllowed = await checkDebtAllow();
    methodsEl.innerHTML = `
      <button class="pay-method-btn flex flex-col items-center justify-center p-3 border-2 border-ink-black hard-shadow-sm hover:scale-95 transition-transform bg-secondary text-on-secondary" data-method="bank">
        <span class="material-symbols-outlined mb-1">account_balance</span>
        <span class="font-label-mono text-[10px]">BANK</span>
      </button>
      <button class="pay-method-btn flex flex-col items-center justify-center p-3 border-2 border-ink-black hard-shadow-sm hover:scale-95 transition-transform bg-white text-ink-black" data-method="telebirr">
        <span class="material-symbols-outlined mb-1">smartphone</span>
        <span class="font-label-mono text-[10px]">TELEBIRR</span>
      </button>
      <button class="pay-method-btn flex flex-col items-center justify-center p-3 border-2 border-ink-black hard-shadow-sm hover:scale-95 transition-transform bg-white text-ink-black ${_debtAllowed ? '' : 'opacity-40'}" data-method="debt">
        <span class="material-symbols-outlined mb-1">${_debtAllowed ? 'payments' : 'lock'}</span>
        <span class="font-label-mono text-[10px]">${_debtAllowed ? 'DEBT' : 'DEBT (LOCKED)'}</span>
      </button>`;
    methodsEl.querySelectorAll(".pay-method-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        if (btn.dataset.method === "debt" && !_debtAllowed) {
          alert("You are not on the debt allow list. Contact admin to be added.");
          return;
        }
        methodsEl.querySelectorAll(".pay-method-btn").forEach(b => { b.classList.remove("bg-secondary", "text-on-secondary"); b.classList.add("bg-white", "text-ink-black"); });
        btn.classList.add("bg-secondary", "text-on-secondary"); btn.classList.remove("bg-white", "text-ink-black");
        _selectedPayment.method = btn.dataset.method;
        _selectedPayment.accountId = null;
        _selectedPayment.account = null;
        renderPaymentSection(accounts);
      });
    });
    _selectedPayment = { method: "bank", accountId: null, account: null };
    renderPaymentSection(accounts);
  } catch(e) {}
}

function renderPaymentSection(accounts) {
  const el = $("payment-accounts");
  if (!el) return;
  const confirmSection = $("payment-confirmation-section");
  if (_selectedPayment.method === "debt") {
    el.innerHTML = '<p class="font-label-mono text-label-mono text-on-surface-variant p-2">Debt option selected. Amount will be added to your debt balance.</p>';
    if (confirmSection) confirmSection.style.display = "none";
    return;
  }
  if (confirmSection) confirmSection.style.display = "";
  if (_selectedPayment.method === "telebirr") {
    const tb = accounts.find(a => a.bank_name?.toLowerCase() === "telebirr");
    if (tb) {
      _selectedPayment.accountId = tb.id;
      _selectedPayment.account = tb;
      el.innerHTML = `
        <div class="p-3 bg-background border-2 border-ink-black space-y-1">
          <p class="font-headline-lg-mobile text-headline-lg-mobile">Telebirr</p>
          <p class="font-label-mono text-label-mono text-primary text-lg">${tb.number}</p>
          <p class="font-label-mono text-label-mono text-on-surface-variant">Name: ${tb.holder_name}</p>
        </div>`;
    } else {
      el.innerHTML = '<p class="font-label-mono text-label-mono text-on-surface-variant p-2">No Telebirr account configured.</p>';
    }
    return;
  }
  const bankAccounts = accounts.filter(a => a.bank_name?.toLowerCase() !== "telebirr");
  const uniqueBanks = [...new Set(bankAccounts.map(a => a.bank_name))];
  let html = `<select id="bank-select" class="w-full bg-white border-2 border-ink-black p-3 font-label-mono text-label-mono focus:outline-none hard-shadow-sm mb-3">`;
  html += `<option value="">-- Select Bank --</option>`;
  uniqueBanks.forEach(b => {
    html += `<option value="${b}" ${_selectedPayment.account?.bank_name === b ? 'selected' : ''}>${b}</option>`;
  });
  html += `</select><div id="bank-account-info"></div>`;
  el.innerHTML = html;
  const select = $("bank-select");
  if (select) {
    select.addEventListener("change", () => {
      const selected = bankAccounts.find(a => a.bank_name === select.value);
      const info = $("bank-account-info");
      if (selected) {
        _selectedPayment.accountId = selected.id;
        _selectedPayment.account = selected;
        info.innerHTML = `
          <div class="p-3 bg-background border-2 border-ink-black space-y-1">
            <p class="font-headline-lg-mobile text-headline-lg-mobile">${selected.bank_name}</p>
            <p class="font-label-mono text-label-mono text-primary text-lg">${selected.number}</p>
            <p class="font-label-mono text-label-mono text-on-surface-variant">Name: ${selected.holder_name}</p>
          </div>`;
      } else {
        _selectedPayment.accountId = null;
        _selectedPayment.account = null;
        info.innerHTML = '<p class="font-label-mono text-label-mono text-on-surface-variant">Select a bank to see account details.</p>';
      }
    });
    if (_selectedPayment.account) {
      select.value = _selectedPayment.account.bank_name;
      select.dispatchEvent(new Event("change"));
    } else if (bankAccounts.length > 0) {
      select.value = bankAccounts[0].bank_name;
      select.dispatchEvent(new Event("change"));
    } else {
      $("bank-account-info").innerHTML = '<p class="font-label-mono text-label-mono text-on-surface-variant">No bank accounts configured.</p>';
    }
  }
}

// --- Form Handlers ---
function setupForms() {
  const contactBtn = $("contact-submit");
  if (contactBtn) {
    contactBtn.addEventListener("click", async () => {
      const msg = $("contact-message")?.value.trim();
      if (!msg) return;
      try {
        await api("/contact", { method: "POST", body: JSON.stringify({ user_id: USER_ID, username: USERNAME, message: msg }) });
        $("contact-message").value = "";
        $("contact-success").classList.remove("hidden");
        contactBtn.disabled = true;
      } catch(e) { alert("Failed to send: " + e.message); }
    });
  }

  const feedbackBtn = $("feedback-submit");
  if (feedbackBtn) {
    feedbackBtn.addEventListener("click", async () => {
      const msg = $("feedback-msg")?.value.trim();
      if (!msg) return;
      try {
        await api("/feedback", { method: "POST", body: JSON.stringify({ user_id: USER_ID, msg }) });
        $("feedback-msg").value = "";
        $("feedback-success").classList.remove("hidden");
        feedbackBtn.disabled = true;
      } catch(e) { alert("Failed to submit: " + e.message); }
    });
  }

  const placeOrderBtn = $("place-order-btn");
  if (placeOrderBtn) {
    placeOrderBtn.addEventListener("click", async () => {
      placeOrderBtn.disabled = true;
      placeOrderBtn.textContent = "PLACING...";
      const comment = $("cart-comment")?.value || "";
      const result = await placeOrder(comment);
      if (result.error) {
        $("order-error").textContent = result.error;
        $("order-error").classList.remove("hidden");
        placeOrderBtn.disabled = false;
        placeOrderBtn.textContent = "PLACE ORDER!";
      }
    });
  }
}

// --- Telegram WebApp ---
if (tg) {
  tg.ready();
  tg.expand();
  tg.BackButton.onClick(() => {
    if (state.navStack.length > 1) {
      state.navStack.pop();
      const prev = state.navStack[state.navStack.length - 1];
      window.location.hash = prev;
    } else {
      window.location.hash = "home";
    }
  });
}

// --- Init ---
async function init() {
  await loadUser();
  updateCartBadge();
  setupNavigation();
  setupForms();
  initRouter();
}

document.addEventListener("DOMContentLoaded", init);
