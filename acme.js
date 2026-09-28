// Acme Home Ergonomics: provider directory, assessment findings and marketplace.
// Data comes from data.js (CREDENTIALS, PROVIDERS, DIRECTORIES, FINDINGS, PRODUCTS).

var state = {
  findings: {},   // finding key -> true
  cart: {},       // product id -> quantity
  budget: 750
};

function $(sel) { return document.querySelector(sel); }
function money(n) { return "$" + n.toLocaleString(); }
function esc(s) {
  return String(s).replace(/[&<>"]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
  });
}

// =============================== tabs ===============================

function showTab(name) {
  document.querySelectorAll(".tab").forEach(function (t) {
    t.classList.toggle("active", t.id === name);
  });
  document.querySelectorAll("#tabs button").forEach(function (b) {
    b.classList.toggle("active", b.dataset.tab === name);
  });
}

// =========================== credentials ============================

function renderCredentials() {
  $("#credentials").innerHTML = CREDENTIALS.map(function (c) {
    var link = c.registry ? '<a href="' + c.registry + '" target="_blank" rel="noopener">Verify / registry ↗</a>' : "";
    return '<div class="card">' +
      '<span class="badge ' + c.tier + '">' + esc(c.tier) + '</span>' +
      '<h4>' + esc(c.code) + ' · ' + esc(c.name) + '</h4>' +
      '<p class="muted">' + esc(c.issuer) + '</p>' +
      '<p>' + esc(c.requires) + '</p>' + link +
      '</div>';
  }).join("");

  $("#f-cred").innerHTML += CREDENTIALS.map(function (c) {
    return '<option>' + esc(c.code) + '</option>';
  }).join("");
}

// ============================ providers =============================

function renderProviders() {
  var mode = $("#f-mode").value;
  var cred = $("#f-cred").value;
  var list = PROVIDERS.filter(function (p) {
    return (!mode || p.modes.includes(mode)) && (!cred || p.credentials.includes(cred));
  });

  $("#providers").innerHTML = list.length ? list.map(function (p) {
    return '<div class="card">' +
      '<h4><a href="' + p.url + '" target="_blank" rel="noopener">' + esc(p.name) + ' ↗</a></h4>' +
      '<p>' + p.modes.map(function (m) { return '<span class="tag">' + m + '</span>'; }).join(" ") +
      ' ' + p.credentials.map(function (c) { return '<span class="tag cred">' + esc(c) + '</span>'; }).join(" ") + '</p>' +
      '<p><strong>Coverage:</strong> ' + esc(p.coverage) + '</p>' +
      '<p><strong>Best for:</strong> ' + esc(p.bestFor) + '</p>' +
      '<p class="muted">' + esc(p.notes) + '</p>' +
      '</div>';
  }).join("") : '<p class="muted">No providers match those filters.</p>';

  $("#directories").innerHTML = DIRECTORIES.map(function (d) {
    return '<li><a href="' + d.url + '" target="_blank" rel="noopener">' + esc(d.name) + ' ↗</a></li>';
  }).join("");
}

// ============================= findings =============================

function renderFindings() {
  $("#findings").innerHTML = Object.keys(FINDINGS).map(function (k) {
    return '<label><input type="checkbox" value="' + k + '"' + (state.findings[k] ? " checked" : "") + '> ' +
      esc(FINDINGS[k]) + '</label>';
  }).join("");
}

function isRecommended(product) {
  return product.fixes.some(function (f) { return state.findings[f]; });
}

// ============================ marketplace ===========================

function renderProducts() {
  var onlyRec = $("#only-rec").checked;
  var byCat = {};
  PRODUCTS.forEach(function (p) {
    if (onlyRec && !isRecommended(p)) return;
    (byCat[p.category] = byCat[p.category] || []).push(p);
  });

  var html = Object.keys(byCat).map(function (cat) {
    return '<h3>' + esc(cat) + '</h3><div class="grid">' + byCat[cat].map(function (p) {
      var rec = isRecommended(p);
      var why = p.fixes.filter(function (f) { return state.findings[f]; })
        .map(function (f) { return FINDINGS[f]; }).join("; ");
      return '<div class="card product' + (rec ? " rec" : "") + '">' +
        (rec ? '<span class="badge expert">Recommended</span>' : "") +
        '<h4>' + esc(p.name) + '</h4>' +
        '<p class="price">~' + money(p.price) + '</p>' +
        '<p class="muted">e.g. ' + esc(p.examples) + '</p>' +
        (why ? '<p class="why">Addresses: ' + esc(why) + '</p>' : "") +
        '<button data-add="' + p.id + '">Add to cart</button>' +
        '</div>';
    }).join("") + '</div>';
  }).join("");

  $("#products").innerHTML = html || '<p class="muted">No recommended items yet. Record findings in step 3.</p>';
}

function productById(id) {
  return PRODUCTS.find(function (p) { return p.id === id; });
}

function cartTotal() {
  return Object.keys(state.cart).reduce(function (sum, id) {
    return sum + productById(id).price * state.cart[id];
  }, 0);
}

function renderCart() {
  var ids = Object.keys(state.cart);
  var count = ids.reduce(function (n, id) { return n + state.cart[id]; }, 0);
  $("#cart-count").textContent = count;

  $("#cart-items").innerHTML = ids.length ? ids.map(function (id) {
    var p = productById(id);
    return '<li><span>' + esc(p.name) + (state.cart[id] > 1 ? " ×" + state.cart[id] : "") + '</span>' +
      '<span>' + money(p.price * state.cart[id]) + ' <button class="x" data-remove="' + id + '" aria-label="Remove">×</button></span></li>';
  }).join("") : '<li class="muted">Empty</li>';

  var total = cartTotal();
  var over = total > state.budget;
  var pct = state.budget ? Math.min(100, Math.round(total / state.budget * 100)) : 100;
  $("#budget-bar").style.width = pct + "%";
  $("#budget-bar").classList.toggle("over", over);
  $("#cart-total").innerHTML = '<strong>' + money(total) + '</strong> of ' + money(state.budget) + ' stipend' +
    (over ? ' <span class="warn">(' + money(total - state.budget) + ' over, so HR will need to approve the difference)</span>'
          : ' (' + money(state.budget - total) + ' left)');
  $("#submit").disabled = !ids.length;
}

function addToCart(id) {
  state.cart[id] = (state.cart[id] || 0) + 1;
  renderCart();
}

function submitOrder() {
  var order = {
    submitted: new Date().toISOString(),
    findings: Object.keys(state.findings).map(function (k) { return FINDINGS[k]; }),
    items: Object.keys(state.cart).map(function (id) {
      var p = productById(id);
      return { item: p.name, qty: state.cart[id], estimate: p.price * state.cart[id] };
    }),
    estimatedTotal: cartTotal(),
    stipend: state.budget,
    needsExceptionApproval: cartTotal() > state.budget
  };
  $("#order").hidden = false;
  $("#order").textContent = "Request ready for HR:\n" + JSON.stringify(order, null, 2);
}

// ============================== wiring ==============================

document.addEventListener("DOMContentLoaded", function () {
  renderCredentials();
  renderProviders();
  renderFindings();
  renderProducts();
  renderCart();

  $("#tabs").addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (b) showTab(b.dataset.tab);
  });
  $("#budget").addEventListener("input", function (e) {
    state.budget = Math.max(0, Number(e.target.value) || 0);
    renderCart();
  });
  $("#f-mode").addEventListener("change", renderProviders);
  $("#f-cred").addEventListener("change", renderProviders);

  $("#findings").addEventListener("change", function (e) {
    if (e.target.checked) state.findings[e.target.value] = true;
    else delete state.findings[e.target.value];
    renderProducts();
  });
  $("#to-shop").addEventListener("click", function () {
    $("#only-rec").checked = Object.keys(state.findings).length > 0;
    renderProducts();
    showTab("shop");
  });

  $("#only-rec").addEventListener("change", renderProducts);
  $("#add-rec").addEventListener("click", function () {
    PRODUCTS.filter(isRecommended).forEach(function (p) {
      if (!state.cart[p.id]) state.cart[p.id] = 1;
    });
    renderCart();
  });
  $("#products").addEventListener("click", function (e) {
    var id = e.target.dataset.add;
    if (id) addToCart(id);
  });
  $("#cart-items").addEventListener("click", function (e) {
    var id = e.target.dataset.remove;
    if (!id) return;
    if (--state.cart[id] <= 0) delete state.cart[id];
    renderCart();
  });
  $("#submit").addEventListener("click", submitOrder);
});
