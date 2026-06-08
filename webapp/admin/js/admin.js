const API_BASE = window.location.origin;

async function api(path, opts = {}) {
  const url = path.startsWith("http") ? path : `${API_BASE}/api${path.startsWith("/") ? "" : "/"}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...opts.headers },
    ...opts,
  });
  if (!res.ok) { const err = await res.json().catch(() => ({ error: "Request failed" })); throw new Error(err.error || `HTTP ${res.status}`); }
  return res.json();
}

function shorten(s, n=40) { return s?.length > n ? s.slice(0, n) + "..." : s || ""; }

const state = {
  navStack: [],
  currentPage: 'dashboard',
  _orderFilter: 'Pending',
  _debtFilter: 'active',
  _editingItem: null,
  _refreshTimer: null,
};

function getStatusBadge(status) {
  const colors = {
    Pending: "background:#f59e0b;color:#000",
    Accepted: "background:#3b82f6;color:#fff",
    Ready: "background:#f97316;color:#fff",
    Delivered: "background:#8BC34A;color:#000",
    Declined: "background:#ba1a1a;color:#fff",
    Cancelled: "background:#6b7280;color:#fff",
  };
  const style = colors[status] || "background:#6b7280;color:#fff";
  return `<span class="inline-block px-2 py-0.5 border-2 border-ink-black rounded-full text-xs font-label-mono" style="${style}">${status || "Unknown"}</span>`;
}

const REFRESH_INTERVAL = 15000;
const autoRefreshPages = ["dashboard", "orders", "menu", "stock", "debt", "payments", "users", "feedback", "referred"];

function stopAutoRefresh() {
  if (state._refreshTimer) { clearInterval(state._refreshTimer); state._refreshTimer = null; }
}

function startAutoRefresh(page) {
  stopAutoRefresh();
  if (!autoRefreshPages.includes(page)) return;
  state._refreshTimer = setInterval(() => {
    const params = Object.fromEntries(new URLSearchParams(window.location.hash.split("?")[1] || ""));
    initPage(state.currentPage, params);
  }, REFRESH_INTERVAL);
}

const $ = id => document.getElementById(id);
const tg = window.Telegram?.WebApp || null;

// --- Router ---
function navigateTo(page, params) {
  if (state.navStack[state.navStack.length - 1] !== page) state.navStack.push(page);
  showPage(page);
  initPage(page, params || {});
  const hash = params ? `${page}?${new URLSearchParams(params)}` : page;
  if (window.location.hash !== `#${hash}`) window.location.hash = hash;
}

function showPage(page) {
  stopAutoRefresh();
  state.currentPage = page;
  document.querySelectorAll(".page").forEach(p => p.classList.add("hidden"));
  const el = $(`page-${page}`);
  if (el) el.classList.remove("hidden");
  document.querySelectorAll(".nav-item").forEach(n => {
    n.classList.toggle("nav-active", n.dataset.page === page);
  });
  const backBtn = $("admin-back");
  backBtn.classList.toggle("hidden", state.navStack.length <= 1);
  if (tg) tg.BackButton.isVisible = state.navStack.length > 1;
  window.scrollTo(0, 0);
}

function initRouter() {
  function handleHash() {
    const hash = window.location.hash.slice(1) || "dashboard";
    const [page, qs] = hash.split("?");
    const params = Object.fromEntries(new URLSearchParams(qs));
    if (state.navStack[state.navStack.length - 1] !== page) state.navStack = [page];
    if (state.currentPage !== page) {
      showPage(page);
      initPage(page, params);
    }
  }
  window.addEventListener("hashchange", handleHash);
  handleHash();
}

function initPage(page, params) {
  switch (page) {
    case "dashboard": renderDashboard(); break;
    case "orders": renderOrders(); break;
    case "order-detail": renderOrderDetail(params?.og); break;
    case "menu": renderMenu(); break;
    case "stock": renderStock(); break;
    case "debt": renderDebt(); break;
    case "debt-allow": break;
    case "payments": renderPayments(); break;
    case "broadcast": loadUserCount(); break;
    case "users": renderUsers(); break;
    case "feedback": renderFeedback(); break;
    case "referred": renderReferred(); break;
  }
  startAutoRefresh(page);
}

// --- Dashboard ---
async function renderDashboard() {
  const el = $("dash-stats");
  el.innerHTML = '<div class="col-span-4 text-center py-8"><div class="skeleton h-16 w-full mb-2"></div><div class="skeleton h-16 w-full"></div></div>';
  try {
    const d = await api("/admin/dashboard");
    el.innerHTML = `
      <div class="bg-white border-2 border-ink-black hard-shadow p-3 text-center"><p class="font-label-mono text-label-mono text-on-surface-variant">Pending</p><p class="font-headline-xl text-headline-xl text-primary">${d.pending_orders}</p></div>
      <div class="bg-white border-2 border-ink-black hard-shadow p-3 text-center"><p class="font-label-mono text-label-mono text-on-surface-variant">Today</p><p class="font-headline-xl text-headline-xl text-ink-black">${d.today_orders}</p></div>
      <div class="bg-white border-2 border-ink-black hard-shadow p-3 text-center"><p class="font-label-mono text-label-mono text-on-surface-variant">Users</p><p class="font-headline-xl text-headline-xl text-kelp-green">${d.total_users}</p></div>
      <div class="bg-white border-2 border-ink-black hard-shadow p-3 text-center"><p class="font-label-mono text-label-mono text-on-surface-variant">Profit</p><p class="font-headline-xl text-headline-xl text-secondary">${d.today_profit.toFixed(0)}</p></div>
    `;
  } catch(e) { el.innerHTML = '<div class="col-span-4 text-center py-8 text-error">Failed to load stats</div>'; }
}

// --- Orders ---
async function renderOrders() {
  const list = $("orders-list");
  list.innerHTML = '<div class="text-center py-8"><div class="skeleton h-24 w-full mb-3"></div></div>';
  try {
    const status = state._orderFilter;
    const url = status === "all" ? "/admin/orders?today_only=1" : `/admin/orders?status=${status}`;
    const orders = await api(url);
    if (!orders.length) { list.innerHTML = '<div class="text-center py-12 font-headline-lg-mobile text-on-surface-variant">No orders</div>'; return; }
    list.innerHTML = orders.map(g => `
      <div class="bg-white border-4 border-ink-black hard-shadow p-4 cursor-pointer hover:rotate-0 transition-transform" style="transform:rotate(${(Math.random()*2-1).toFixed(2)}deg)" data-og="${g.order_group}">
        <div class="flex justify-between items-start gap-2 mb-2">
          <div class="min-w-0 flex-1">
            <p class="font-label-mono text-label-mono text-tertiary truncate">${g.order_group}</p>
            <p class="font-headline-lg-mobile text-headline-lg-mobile truncate">${g.user_name || "Unknown"}</p>
          </div>
          <span class="status-badge-${g.status.toLowerCase()} px-3 py-1 border-2 border-ink-black rounded-full font-label-mono text-label-mono text-xs whitespace-nowrap">${g.status}</span>
        </div>
        <div class="border-t-2 border-dashed border-ink-black pt-2 flex justify-between items-center">
          <p class="font-body-md text-body-md text-on-surface-variant truncate">${g.items.map(i => `${i.qty}x ${i.item}`).join(", ")}</p>
          <span class="font-label-mono text-label-mono text-primary">${g.total.toFixed(2)}</span>
        </div>
      </div>
    `).join("");
    list.querySelectorAll("[data-og]").forEach(c => c.addEventListener("click", () => navigateTo("order-detail", { og: c.dataset.og })));
  } catch(e) { list.innerHTML = '<div class="text-center py-12 text-error">Failed to load orders</div>'; }
}

async function renderOrderDetail(og) {
  if (!og) return;
  try {
    const d = await api(`/orders/group/${og}`);
    $("od-ref").textContent = `REF: ${og}`;
    const statusEl = $("od-status");
    statusEl.textContent = d.status || "Pending";
    statusEl.className = `status-badge-${(d.status||"pending").toLowerCase()} px-3 py-1 border-2 border-ink-black rounded-full font-label-mono text-label-mono text-xs`;
    $("od-user").textContent = d.user_name ? `👤 ${d.user_name}` : "";
    $("od-date").textContent = d.created_at ? new Date(d.created_at).toLocaleString() : "";
    $("od-items").innerHTML = (d.items || []).map(i => `<div class="flex justify-between py-1 border-b border-dashed border-ink-black"><span>${i.qty}x ${i.item}</span></div>`).join("");
    $("od-total").textContent = `${(d.total || 0).toFixed(2)} Birr`;
    $("od-comment").textContent = d.comment || "None";
    const actions = $("od-actions");
    if (d.status === "Pending") {
      actions.innerHTML = `
        <button class="w-full bg-kelp-green text-white py-3 border-2 border-ink-black font-headline-lg-mobile uppercase hard-shadow active:translate-x-1 active:translate-y-1 active:shadow-none transition-all" onclick="acceptOrder('${og}')">Accept</button>
        <input id="decline-reason" class="w-full bg-surface-container-low border-2 border-ink-black p-3 font-body-md focus:outline-none" placeholder="Decline reason..." />
        <button class="w-full bg-error text-on-error py-3 border-2 border-ink-black font-headline-lg-mobile uppercase hard-shadow active:translate-x-1 active:translate-y-1 active:shadow-none transition-all" onclick="declineOrder('${og}')">Decline</button>
      `;
    } else if (d.status === "Accepted") {
      actions.innerHTML = `<button class="w-full bg-ocean-blue text-white py-3 border-2 border-ink-black font-headline-lg-mobile uppercase hard-shadow active:translate-x-1 active:translate-y-1 active:shadow-none transition-all" onclick="markReady('${og}')">Mark Ready</button>`;
    } else if (d.status === "Ready") {
      actions.innerHTML = `
        <p class="font-body-md text-body-md text-center mb-2">Delivered as:</p>
        <div class="flex gap-2">
          <button class="flex-1 bg-kelp-green text-white py-3 border-2 border-ink-black font-headline-lg-mobile uppercase hard-shadow active:translate-x-1 active:translate-y-1 active:shadow-none transition-all" onclick="deliverPaid('${og}')">Paid</button>
          <button class="flex-1 bg-secondary text-on-secondary py-3 border-2 border-ink-black font-headline-lg-mobile uppercase hard-shadow active:translate-x-1 active:translate-y-1 active:shadow-none transition-all" onclick="deliverDebt('${og}')">Debt</button>
        </div>
      `;
    } else { actions.innerHTML = ""; }
  } catch(e) { $("od-ref").textContent = "Error loading"; }
}

async function acceptOrder(og) { try { await api(`/admin/orders/${og}/accept`, { method: "POST" }); navigateTo("orders"); } catch(e) { alert("Failed: " + e.message); } }
async function declineOrder(og) { const r = $("decline-reason")?.value; if (!r) return alert("Enter a reason"); try { await api(`/admin/orders/${og}/decline`, { method: "POST", body: JSON.stringify({ reason: r }) }); navigateTo("orders"); } catch(e) { alert("Failed: " + e.message); } }
async function markReady(og) { try { await api(`/admin/orders/${og}/ready`, { method: "POST" }); navigateTo("orders"); } catch(e) { alert("Failed: " + e.message); } }
async function deliverPaid(og) { try { await api(`/admin/orders/${og}/deliver`, { method: "POST", body: JSON.stringify({ type: "paid" }) }); navigateTo("orders"); } catch(e) { alert("Failed: " + e.message); } }
async function deliverDebt(og) { try { await api(`/admin/orders/${og}/deliver`, { method: "POST", body: JSON.stringify({ type: "debt" }) }); navigateTo("orders"); } catch(e) { alert("Failed: " + e.message); } }

// --- Menu ---
let _menuData = [];

async function renderMenu() {
  const tree = $("menu-tree");
  tree.innerHTML = '<div class="text-center py-8"><div class="skeleton h-16 w-full mb-2"></div></div>';
  try {
    _menuData = await api("/admin/menu");
    const cats = _menuData.filter(i => !i.parent);
    tree.innerHTML = cats.map(c => {
      const subs = _menuData.filter(i => i.parent === c.name);
      return `<div class="bg-white border-4 border-ink-black hard-shadow-lg p-4">
        <div class="flex justify-between items-center gap-2 mb-2">
          <h3 class="font-headline-lg-mobile text-headline-lg-mobile truncate">${c.name.toUpperCase()}</h3>
          <div class="flex gap-1 flex-shrink-0">
            <button class="bg-error text-on-error px-2 py-1 border-2 border-ink-black font-label-mono text-label-mono text-xs hard-shadow active:translate-x-0.5 active:translate-y-0.5 active:shadow-none transition-all" onclick="deleteMenuItem('${c.name}')">Del</button>
          </div>
        </div>
        ${subs.map(s => `
          <div class="flex items-center justify-between gap-2 py-2 border-t border-dashed border-ink-black">
            <div class="flex items-center gap-2 min-w-0 flex-1">
              ${s.image_url ? `<img src="${s.image_url}" class="w-8 h-8 border border-ink-black object-cover flex-shrink-0" />` : `<span class="material-symbols-outlined text-primary flex-shrink-0">restaurant</span>`}
              <span class="font-body-md text-body-md truncate">${s.name}</span>
              <span class="font-label-mono text-label-mono text-primary flex-shrink-0">${s.price.toFixed(2)}</span>
            </div>
            <div class="flex gap-1 flex-shrink-0">
              <button class="bg-secondary-fixed text-ink-black px-2 py-1 border-2 border-ink-black font-label-mono text-label-mono text-xs hard-shadow active:translate-x-0.5 active:translate-y-0.5 active:shadow-none transition-all" onclick="editMenuItem('${s.name}')">Edit</button>
              <button class="bg-error text-on-error px-2 py-1 border-2 border-ink-black font-label-mono text-label-mono text-xs hard-shadow active:translate-x-0.5 active:translate-y-0.5 active:shadow-none transition-all" onclick="deleteMenuItem('${s.name}')">Del</button>
            </div>
          </div>
        `).join("")}
        <button class="w-full mt-2 bg-secondary text-on-secondary py-2 border-2 border-ink-black font-headline-lg-mobile uppercase hard-shadow active:translate-x-1 active:translate-y-1 active:shadow-none transition-all" onclick="showAddSubItem('${c.name}')">+ Sub-Item</button>
      </div>`;
    }).join("");
  } catch(e) { tree.innerHTML = '<div class="text-center py-12 text-error">Failed to load menu</div>'; }
}

function _menuModalReset() {
  $("menu-input-name").value = "";
  $("menu-input-price").value = "";
  $("menu-input-image").value = "";
  $("menu-parent-wrap").classList.remove("hidden");
}

async function showAddItem() { state._editingItem = null; _menuModalReset(); $("menu-modal-title").textContent = "Add Item"; $("menu-parent-wrap").classList.add("hidden"); $("menu-modal").classList.remove("hidden"); }
async function showAddCategory() { state._editingItem = null; _menuModalReset(); $("menu-modal-title").textContent = "Add Category"; $("menu-input-price").value = "0"; $("menu-parent-wrap").classList.add("hidden"); $("menu-modal").classList.remove("hidden"); }
function editMenuItem(name) { const item = _menuData.find(i => i.name === name); if (!item) return; state._editingItem = name; _menuModalReset(); $("menu-modal-title").textContent = "Edit Item"; $("menu-input-name").value = item.name; $("menu-input-price").value = item.price; $("menu-input-image").value = item.image_url || ""; populateParentSelect(item.parent); $("menu-input-parent").value = item.parent || ""; $("menu-modal").classList.remove("hidden"); }
async function showAddSubItem(cat) { state._editingItem = null; _menuModalReset(); $("menu-modal-title").textContent = `Add to ${cat}`; await populateParentSelect(cat); $("menu-input-parent").value = cat; $("menu-modal").classList.remove("hidden"); }

async function populateParentSelect(selected) {
  const sel = $("menu-input-parent");
  sel.innerHTML = '<option value="">Top-level (category)</option>';
  const cats = _menuData.filter(i => !i.parent);
  cats.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c.name; opt.textContent = c.name;
    if (c.name === selected) opt.selected = true;
    sel.appendChild(opt);
  });
}

async function saveMenuItem() {
  const name = $("menu-input-name").value.trim();
  const price = parseFloat($("menu-input-price").value);
  const parent = $("menu-parent-wrap").classList.contains("hidden") ? null : ($("menu-input-parent").value || null);
  const image_url = $("menu-input-image").value.trim() || null;
  if (!name) return alert("Name required");
  try {
    if (state._editingItem) {
      await api(`/admin/menu/${encodeURIComponent(state._editingItem)}`, { method: "PUT", body: JSON.stringify({ name, price, parent, image_url }) });
    } else {
      await api("/admin/menu", { method: "POST", body: JSON.stringify({ name, price, parent, image_url }) });
    }
    closeMenuModal(); renderMenu();
  } catch(e) { alert("Failed: " + e.message); }
}

function closeMenuModal() { $("menu-modal").classList.add("hidden"); }
async function deleteMenuItem(name) { if (!confirm(`Delete "${name}"?`)) return; try { await api(`/admin/menu/${encodeURIComponent(name)}`, { method: "DELETE" }); renderMenu(); } catch(e) { alert("Failed: " + e.message); } }

// --- Stock ---
async function renderStock() {
  const list = $("stock-list");
  list.innerHTML = '<div class="text-center py-8"><div class="skeleton h-16 w-full mb-2"></div></div>';
  try {
    const items = await api("/admin/menu");
    const stocks = await api("/admin/stock");
    const stockMap = {};
    (stocks || []).forEach(s => stockMap[s.name] = s);
    const orderable = items.filter(i => i.price > 0);
    list.innerHTML = orderable.map(i => {
      const st = stockMap[i.name];
      const status = st ? (st.locked ? "🔒 Locked" : `${st.remaining}/${st.max_qty}`) : "Unlimited";
      return `<div class="bg-white border-4 border-ink-black hard-shadow p-4">
        <div class="flex justify-between items-center gap-2">
          <div class="min-w-0 flex-1">
            <p class="font-headline-lg-mobile text-headline-lg-mobile truncate">${i.name}</p>
            <p class="font-label-mono text-label-mono text-xs ${st?.locked ? 'text-error' : ''}">${status}</p>
          </div>
          <div class="flex gap-1 flex-shrink-0">
            <button class="bg-primary text-on-primary px-2 py-1 border-2 border-ink-black font-label-mono text-label-mono text-xs hard-shadow active:translate-x-0.5 active:translate-y-0.5 active:shadow-none transition-all" onclick="showSetStock('${i.name}')">Limit</button>
            ${!st?.locked ? `<button class="bg-secondary-fixed text-ink-black px-2 py-1 border-2 border-ink-black font-label-mono text-label-mono text-xs hard-shadow active:translate-x-0.5 active:translate-y-0.5 active:shadow-none transition-all" onclick="toggleLock('${i.name}')">Lock</button>` : ""}
            ${st ? `<button class="bg-error text-on-error px-2 py-1 border-2 border-ink-black font-label-mono text-label-mono text-xs hard-shadow active:translate-x-0.5 active:translate-y-0.5 active:shadow-none transition-all" onclick="clearStock('${i.name}')">Clear</button>` : ""}
          </div>
        </div>
      </div>`;
    }).join("");
  } catch(e) { list.innerHTML = '<div class="text-center py-12 text-error">Failed to load stock</div>'; }
}

let _stockEditing = null;
function showSetStock(name) { _stockEditing = name; $("stock-modal-title").textContent = `Limit for ${name}`; $("stock-input-qty").value = ""; $("stock-modal").classList.remove("hidden"); }
function closeStockModal() { $("stock-modal").classList.add("hidden"); }
async function saveStockLimit() { const qty = parseInt($("stock-input-qty").value); if (!qty || qty < 1) return alert("Enter valid qty"); try { await api(`/admin/stock/${encodeURIComponent(_stockEditing)}`, { method: "PUT", body: JSON.stringify({ max_qty: qty }) }); closeStockModal(); renderStock(); } catch(e) { alert("Failed: " + e.message); } }
async function toggleLock(name) { try { await api(`/admin/stock/${encodeURIComponent(name)}/toggle-lock`, { method: "POST" }); renderStock(); } catch(e) { alert("Failed: " + e.message); } }
async function clearStock(name) { try { await api(`/admin/stock/${encodeURIComponent(name)}`, { method: "DELETE" }); renderStock(); } catch(e) { alert("Failed: " + e.message); } }
async function unlockAll() { if (!confirm("Unlock all items?")) return; try { await api("/admin/stock/unlock-all", { method: "POST" }); renderStock(); } catch(e) { alert("Failed: " + e.message); } }

// --- Debt ---
async function renderDebt() {
  const list = $("debt-list");
  list.innerHTML = '<div class="text-center py-8"><div class="skeleton h-16 w-full mb-2"></div></div>';
  try {
    const debts = await api(`/admin/debts?filter=${state._debtFilter}`);
    if (!debts.length) { list.innerHTML = '<div class="text-center py-12 font-headline-lg-mobile text-on-surface-variant">No debts</div>'; return; }
    list.innerHTML = debts.map(d => `
      <div class="bg-white border-4 border-ink-black hard-shadow p-4">
        <div class="flex justify-between items-start gap-2 mb-2">
          <div>
            <p class="font-headline-lg-mobile text-headline-lg-mobile">${d.full_name || d.username}</p>
            <p class="font-label-mono text-label-mono text-tertiary">@${d.username}</p>
          </div>
          <span class="status-badge-${d.status} px-3 py-1 border-2 border-ink-black rounded-full font-label-mono text-label-mono text-xs">${d.status.toUpperCase()}</span>
        </div>
        <div class="border-t-2 border-dashed border-ink-black pt-2 flex justify-between items-center">
          <p class="font-label-mono text-label-mono text-on-surface-variant">${d.description || d.order_group || ""}</p>
          <span class="font-headline-lg-mobile text-headline-lg-mobile text-primary">${d.amount.toFixed(2)}</span>
        </div>
        ${d.status === "active" ? `<div class="flex gap-2 mt-2"><button class="flex-1 bg-kelp-green text-white py-2 border-2 border-ink-black font-label-mono text-label-mono uppercase hard-shadow active:translate-x-0.5 active:translate-y-0.5 active:shadow-none transition-all" onclick="markDebtPaid(${d.id})">Paid</button><button class="flex-1 bg-tertiary text-on-tertiary py-2 border-2 border-ink-black font-label-mono text-label-mono uppercase hard-shadow active:translate-x-0.5 active:translate-y-0.5 active:shadow-none transition-all" onclick="waiveDebt(${d.id})">Waive</button></div>` : ""}
      </div>
    `).join("");
  } catch(e) { list.innerHTML = '<div class="text-center py-12 text-error">Failed to load debts</div>'; }
}

async function markDebtPaid(id) { try { await api(`/admin/debts/${id}/pay`, { method: "POST" }); renderDebt(); } catch(e) { alert("Failed: " + e.message); } }
async function waiveDebt(id) { if (!confirm("Waive this debt?")) return; try { await api(`/admin/debts/${id}/waive`, { method: "POST" }); renderDebt(); } catch(e) { alert("Failed: " + e.message); } }

async function showAllowList() {
  navigateTo("debt-allow");
  const list = $("allow-list");
  list.innerHTML = '<div class="text-center py-8"><div class="skeleton h-16 w-full"></div></div>';
  try {
    const entries = await api("/admin/debt-allow-list");
    if (!entries.length) { list.innerHTML = '<p class="text-center font-body-md text-on-surface-variant">No one on allow list</p>'; return; }
    list.innerHTML = entries.map(e => `
      <div class="flex justify-between items-center bg-surface-container-low p-3 border-2 border-ink-black">
        <span class="font-headline-lg-mobile">@${e.username}</span>
        <button class="bg-error text-on-error px-3 py-1 border-2 border-ink-black font-label-mono text-label-mono text-xs hard-shadow active:translate-x-0.5 active:translate-y-0.5 active:shadow-none transition-all" onclick="removeAllow('${e.username}')">Remove</button>
      </div>
    `).join("");
  } catch(e) { list.innerHTML = '<div class="text-center py-12 text-error">Failed to load</div>'; }
}

function showAddAllow() {
  const username = prompt("Enter username to allow (without @):");
  if (!username) return;
  api("/admin/debt-allow-list", { method: "POST", body: JSON.stringify({ username }) }).then(() => { showAllowList(); }).catch(e => alert("Failed: " + e.message));
}
async function removeAllow(username) { try { await api(`/admin/debt-allow-list/${encodeURIComponent(username)}`, { method: "DELETE" }); showAllowList(); } catch(e) { alert("Failed: " + e.message); } }

// --- Payments ---
async function renderPayments() {
  const list = $("payments-list");
  list.innerHTML = '<div class="text-center py-8"><div class="skeleton h-16 w-full mb-2"></div></div>';
  try {
    const accounts = await api("/payment-accounts");
    if (!accounts.length) { list.innerHTML = '<div class="text-center py-12 font-body-md text-on-surface-variant">No payment accounts</div>'; return; }
    list.innerHTML = accounts.map(a => `
      <div class="bg-white border-4 border-ink-black hard-shadow p-4">
        <div class="flex justify-between items-center">
          <div>
            <p class="font-headline-lg-mobile text-headline-lg-mobile">${a.bank_name}</p>
            <p class="font-label-mono text-label-mono text-tertiary">${a.number}</p>
            <p class="font-body-md text-body-md text-on-surface-variant">${a.holder_name}</p>
          </div>
          <button class="bg-error text-on-error px-3 py-2 border-2 border-ink-black font-label-mono text-label-mono text-xs hard-shadow active:translate-x-0.5 active:translate-y-0.5 active:shadow-none transition-all" onclick="deletePayment(${a.id})">Delete</button>
        </div>
      </div>
    `).join("");
  } catch(e) { list.innerHTML = '<div class="text-center py-12 text-error">Failed to load</div>'; }
}

function showAddPayment() { $("payment-modal").classList.remove("hidden"); }
function closePaymentModal() { $("payment-modal").classList.add("hidden"); }
async function savePaymentAccount() {
  const bank_name = $("pay-input-bank").value.trim();
  const number = $("pay-input-number").value.trim();
  const holder_name = $("pay-input-holder").value.trim();
  if (!bank_name || !number) return alert("Bank name and number required");
  try { await api("/admin/payment-accounts", { method: "POST", body: JSON.stringify({ bank_name, number, holder_name }) }); closePaymentModal(); renderPayments(); } catch(e) { alert("Failed: " + e.message); }
}
async function deletePayment(id) { if (!confirm("Delete this account?")) return; try { await api(`/admin/payment-accounts/${id}`, { method: "DELETE" }); renderPayments(); } catch(e) { alert("Failed: " + e.message); } }

// --- Broadcast ---
async function loadUserCount() {
  try {
    const users = await api("/admin/users");
    $("broadcast-count").textContent = `${users.length} users will receive this`;
  } catch(e) {}
}

async function sendBroadcast() {
  const msg = $("broadcast-msg").value.trim();
  if (!msg) return alert("Enter a message");
  const btn = event.target; btn.disabled = true; btn.textContent = "SENDING...";
  try {
    const res = await api("/admin/broadcast", { method: "POST", body: JSON.stringify({ message: msg }) });
    $("broadcast-result").textContent = `Sent to ${res.sent} users`;
    $("broadcast-result").classList.remove("hidden");
    $("broadcast-msg").value = "";
  } catch(e) { alert("Failed: " + e.message); }
  btn.disabled = false; btn.textContent = "Send Broadcast";
}

// --- Users ---
async function renderUsers() {
  const list = $("users-list");
  try {
    const users = await api("/admin/users");
    const q = ($("users-search")?.value || "").toLowerCase();
    const filtered = users.filter(u => (u.full_name || "").toLowerCase().includes(q) || (u.username || "").toLowerCase().includes(q));
    list.innerHTML = filtered.map(u => `
      <div class="flex justify-between items-center bg-surface-container-low p-3 border-2 border-ink-black ${u.banned ? 'opacity-50' : ''}">
        <div class="min-w-0 flex-1">
          <p class="font-headline-lg-mobile text-headline-lg-mobile truncate">${u.full_name || "Unknown"}</p>
          <p class="font-label-mono text-label-mono text-tertiary">@${u.username || "no username"} ${u.banned ? '🚫 BANNED' : ''}</p>
        </div>
        <div class="flex gap-1 flex-shrink-0">
          ${u.banned ? `<button class="bg-kelp-green text-white px-3 py-1 border-2 border-ink-black font-label-mono text-label-mono text-xs hard-shadow active:translate-x-0.5 active:translate-y-0.5 active:shadow-none transition-all" onclick="unbanUser(${u.user_id})">Unban</button>` : `<button class="bg-error text-on-error px-3 py-1 border-2 border-ink-black font-label-mono text-label-mono text-xs hard-shadow active:translate-x-0.5 active:translate-y-0.5 active:shadow-none transition-all" onclick="banUser(${u.user_id})">Ban</button>`}
        </div>
      </div>
    `).join("");
  } catch(e) { list.innerHTML = '<div class="text-center py-12 text-error">Failed to load</div>'; }
}

async function banUser(id) { if (!confirm("Ban this user?")) return; try { await api(`/admin/users/${id}/ban`, { method: "POST" }); renderUsers(); } catch(e) { alert("Failed: " + e.message); } }
async function unbanUser(id) { try { await api(`/admin/users/${id}/unban`, { method: "POST" }); renderUsers(); } catch(e) { alert("Failed: " + e.message); } }

// --- Feedback ---
async function renderFeedback() {
  const list = $("feedback-list");
  list.innerHTML = '<div class="text-center py-8"><div class="skeleton h-16 w-full mb-2"></div></div>';
  try {
    const feedback = await api("/admin/feedback");
    if (!feedback.length) { list.innerHTML = '<div class="text-center py-12 font-headline-lg-mobile text-on-surface-variant">No feedback</div>'; return; }
    list.innerHTML = feedback.map(f => `
      <div class="bg-white border-4 border-ink-black hard-shadow p-4">
        <div class="flex justify-between items-start gap-2 mb-2">
          <p class="font-headline-lg-mobile text-headline-lg-mobile">${f.name || "Unknown"}</p>
          <p class="font-label-mono text-label-mono text-tertiary text-xs">${new Date(f.created_at).toLocaleDateString()}</p>
        </div>
        <p class="font-body-md text-body-md text-on-surface-variant">${f.msg}</p>
      </div>
    `).join("");
  } catch(e) { list.innerHTML = '<div class="text-center py-12 text-error">Failed to load</div>'; }
}

// --- Referred Purchases ---
async function renderReferred() {
  const list = $("referred-list");
  list.innerHTML = '<div class="text-center py-8"><div class="skeleton h-16 w-full mb-2"></div></div>';
  try {
    const earnings = await api("/admin/referrals/earnings");
    if (!earnings.length) { list.innerHTML = '<div class="text-center py-12 font-headline-lg-mobile text-on-surface-variant">No referred purchases yet</div>'; return; }
    list.innerHTML = earnings.map(e => `
      <div class="bg-white border-4 border-ink-black hard-shadow p-4">
        <div class="flex justify-between items-start gap-2 mb-2">
          <p class="font-headline-lg-mobile text-headline-lg-mobile">${e.referred_name || e.referred_username || "Unknown"}</p>
          <p class="font-label-mono text-label-mono text-tertiary text-xs">${new Date(e.earned_at).toLocaleDateString()}</p>
        </div>
        <div class="font-label-mono text-label-mono text-on-surface-variant mb-1">
          <span class="text-kelp-green">Referred by:</span> ${e.referrer_name || e.referrer_username || "Unknown"}
        </div>
        <div class="font-label-mono text-label-mono text-on-surface-variant mb-1">
          <span class="text-primary">Order:</span> <a href="#/order-detail?og=${e.order_group}" class="underline">${e.order_group}</a>
          ${getStatusBadge(e.status)}
        </div>
        <p class="font-body-md text-body-md text-on-surface-variant">${e.items}</p>
      </div>
    `).join("");
  } catch(e) { list.innerHTML = '<div class="text-center py-12 text-error">Failed to load</div>'; }
}

// --- Setup ---
function setupNavigation() {
  document.addEventListener("click", (e) => {
    const nav = e.target.closest("[data-nav], [data-page]");
    if (nav) { e.preventDefault(); navigateTo(nav.dataset.nav || nav.dataset.page); }
  });
  document.querySelectorAll(".order-tab").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".order-tab").forEach(b => { b.className = "order-tab bg-white text-ink-black px-4 py-2 border-2 border-ink-black font-label-mono text-label-mono uppercase hard-shadow active:translate-x-1 active:translate-y-1 active:shadow-none transition-all"; });
      btn.className = "order-tab bg-primary text-on-primary px-4 py-2 border-2 border-ink-black font-label-mono text-label-mono uppercase hard-shadow active:translate-x-1 active:translate-y-1 active:shadow-none transition-all";
      state._orderFilter = btn.dataset.status;
      renderOrders();
    });
  });
  document.querySelectorAll(".debt-tab").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".debt-tab").forEach(b => { b.className = "debt-tab bg-white text-ink-black px-4 py-2 border-2 border-ink-black font-label-mono text-label-mono uppercase hard-shadow active:translate-x-1 active:translate-y-1 active:shadow-none transition-all"; });
      btn.className = "debt-tab bg-primary text-on-primary px-4 py-2 border-2 border-ink-black font-label-mono text-label-mono uppercase hard-shadow active:translate-x-1 active:translate-y-1 active:shadow-none transition-all";
      state._debtFilter = btn.dataset.filter;
      renderDebt();
    });
  });
  $("admin-back").addEventListener("click", () => {
    if (state.navStack.length > 1) { state.navStack.pop(); navigateTo(state.navStack.pop()); }
    else navigateTo("dashboard");
  });
}

// --- Init ---
function init() {
  setupNavigation();
  initRouter();
}

document.addEventListener("DOMContentLoaded", init);
