/* ============================================================
   MAISON — Unified JS
   Handles: cart state, shop page, product page, cart page, nav
   ============================================================ */

/* ----------------------------------------------------------
   CART STATE  (localStorage-backed)
   Structure: [{ id, name, price, image, qty }, ...]
   ---------------------------------------------------------- */
const CART_KEY = 'maison_cart';

function getCart() {
  try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; }
  catch { return []; }
}

function saveCart(cart) {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
  syncCartCount();
}

function addToCart(item) {
  const cart = getCart();
  const existing = cart.find(i => i.id === item.id);
  if (existing) {
    existing.qty += item.qty;
  } else {
    cart.push(item);
  }
  saveCart(cart);
}

function removeFromCart(id) {
  saveCart(getCart().filter(i => i.id !== id));
}

function updateQty(id, qty) {
  const cart = getCart();
  const item = cart.find(i => i.id === id);
  if (item) {
    item.qty = Math.max(1, qty);
    saveCart(cart);
  }
}

function cartTotal() {
  return getCart().reduce((sum, i) => sum + i.price * i.qty, 0);
}

function syncCartCount() {
  const total = getCart().reduce((sum, i) => sum + i.qty, 0);
  document.querySelectorAll('.cart-count').forEach(el => {
    el.textContent = total;
    el.classList.add('bump');
    setTimeout(() => el.classList.remove('bump'), 350);
  });
}

/* ----------------------------------------------------------
   TOAST
   ---------------------------------------------------------- */
let toastTimer = null;

function showToast(msg) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  const msgEl = toast.querySelector('.toast-msg');
  if (msgEl) msgEl.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2500);
}

/* ----------------------------------------------------------
   NAVBAR — mobile toggle
   ---------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {

  // Mobile toggle
  const toggle = document.querySelector('.navbar__mobile-toggle');
  const links  = document.querySelector('.navbar__links');
  if (toggle && links) {
    toggle.addEventListener('click', () => links.classList.toggle('open'));
  }

  // Sync count on every page load
  syncCartCount();

  // Route to page init
  if (document.querySelector('.product-list')) initShopPage();
  if (document.querySelector('.product-detail')) initProductPage();
  if (document.querySelector('.cart-layout'))   initCartPage();
  if (document.querySelector('.login-form'))    initLoginPage();
});

/* ----------------------------------------------------------
   SHOP PAGE — quick buy buttons
   ---------------------------------------------------------- */
function initShopPage() {
  document.querySelectorAll('.quick-buy-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      const card = btn.closest('.product-card');
      const name  = card.querySelector('.product-card__name').textContent.trim();
      const price = parseFloat(card.querySelector('.product-card__price').textContent.replace('$', ''));
      const image = card.querySelector('.product-card__image')?.src || '';
      const id    = name.toLowerCase().replace(/\s+/g, '-');

      addToCart({ id, name, price, image, qty: 1 });
      showToast('Added to cart!');

      btn.classList.add('added');
      btn.querySelector('.btn-text').textContent = 'Added!';
      setTimeout(() => {
        btn.classList.remove('added');
        btn.querySelector('.btn-text').textContent = 'Quick Buy';
      }, 1800);
    });
  });
}

/* legacy inline handler still referenced in some cards */
function handleQuickBuy(btn) {
  const card = btn.closest('.product-card');
  const name  = card.querySelector('.product-card__name').textContent.trim();
  const price = parseFloat(card.querySelector('.product-card__price').textContent.replace('$', ''));
  const image = card.querySelector('.product-card__image')?.src || '';
  const id    = name.toLowerCase().replace(/\s+/g, '-');

  addToCart({ id, name, price, image, qty: 1 });
  showToast('Added to cart!');

  btn.classList.add('added');
  btn.querySelector('.btn-text').textContent = 'Added!';
  setTimeout(() => {
    btn.classList.remove('added');
    btn.querySelector('.btn-text').textContent = 'Quick Buy';
  }, 1800);
}

/* ----------------------------------------------------------
   PRODUCT PAGE
   ---------------------------------------------------------- */
function initProductPage() {
  let qty = 1;
  const qtyValue = document.getElementById('qty-value');
  const minusBtn = document.getElementById('qty-minus');
  const plusBtn  = document.getElementById('qty-plus');
  const atcBtn   = document.getElementById('add-to-cart-btn');

  function renderQty() {
    if (qtyValue) qtyValue.textContent = qty;
    if (minusBtn) minusBtn.disabled = qty <= 1;
  }

  if (minusBtn) minusBtn.addEventListener('click', () => { if (qty > 1) { qty--; renderQty(); } });
  if (plusBtn)  plusBtn.addEventListener('click',  () => { qty++; renderQty(); });

  if (atcBtn) {
    atcBtn.addEventListener('click', () => {
      const name  = atcBtn.dataset.name;
      const price = parseFloat(atcBtn.dataset.price);
      const image = atcBtn.dataset.image || '';
      const id    = name.toLowerCase().replace(/\s+/g, '-');

      addToCart({ id, name, price, image, qty });
      showToast(`${qty > 1 ? qty + '× ' : ''}${name} added to cart!`);

      atcBtn.classList.add('added');
      atcBtn.querySelector('.btn-text').textContent = 'Added!';
      setTimeout(() => {
        atcBtn.classList.remove('added');
        atcBtn.querySelector('.btn-text').textContent = 'Add to Cart';
      }, 1800);
    });
  }

  // Thumbnail switching
  document.querySelectorAll('.product-detail__thumb').forEach(thumb => {
    thumb.addEventListener('click', () => {
      const mainImg = document.querySelector('.product-detail__main-image');
      if (mainImg) mainImg.src = thumb.querySelector('img').src;
      document.querySelectorAll('.product-detail__thumb').forEach(t => t.classList.remove('product-detail__thumb--active'));
      thumb.classList.add('product-detail__thumb--active');
    });
  });

  renderQty();
}

/* ----------------------------------------------------------
   CART PAGE
   ---------------------------------------------------------- */
function initCartPage() {
  renderCartPage();
}

function renderCartPage() {
  const cart       = getCart();
  const container  = document.getElementById('cart-items');
  const emptyState = document.getElementById('cart-empty');
  const summary    = document.getElementById('cart-summary');

  if (!container) return;

  if (cart.length === 0) {
    container.innerHTML = '';
    if (emptyState) emptyState.style.display = 'flex';
    if (summary)    summary.style.display    = 'none';
    return;
  }

  if (emptyState) emptyState.style.display = 'none';
  if (summary)    summary.style.display    = '';

  container.innerHTML = cart.map(item => `
    <div class="cart-item" data-id="${item.id}">
      <div class="cart-item__image-wrap">
        <img src="${item.image}" alt="${item.name}" class="cart-item__image" />
      </div>
      <div class="cart-item__info">
        <div class="cart-item__meta">
          <span class="product-card__category">Accessories</span>
        </div>
        <h3 class="cart-item__name">${item.name}</h3>
        <p class="cart-item__unit-price">$${item.price.toFixed(2)} each</p>
      </div>
      <div class="cart-item__controls">
        <div class="qty-selector">
          <button class="qty-btn cart-qty-minus" data-id="${item.id}" aria-label="Decrease">−</button>
          <span class="qty-value cart-qty-value">${item.qty}</span>
          <button class="qty-btn cart-qty-plus"  data-id="${item.id}" aria-label="Increase">+</button>
        </div>
        <p class="cart-item__line-price">$${(item.price * item.qty).toFixed(2)}</p>
        <button class="cart-item__remove" data-id="${item.id}" aria-label="Remove item">Remove</button>
      </div>
    </div>
  `).join('');

  // Bind controls
  container.querySelectorAll('.cart-qty-minus').forEach(btn => {
    btn.addEventListener('click', () => {
      const id   = btn.dataset.id;
      const item = getCart().find(i => i.id === id);
      if (item && item.qty > 1) { updateQty(id, item.qty - 1); renderCartPage(); }
      else if (item && item.qty === 1) { removeFromCart(id); showToast('Item removed.'); renderCartPage(); }
    });
  });

  container.querySelectorAll('.cart-qty-plus').forEach(btn => {
    btn.addEventListener('click', () => {
      const id   = btn.dataset.id;
      const item = getCart().find(i => i.id === id);
      if (item) { updateQty(id, item.qty + 1); renderCartPage(); }
    });
  });

  container.querySelectorAll('.cart-item__remove').forEach(btn => {
    btn.addEventListener('click', () => {
      removeFromCart(btn.dataset.id);
      showToast('Item removed.');
      renderCartPage();
    });
  });

  // Update summary
  const subtotal = cartTotal();
  const subtotalEl = document.getElementById('summary-subtotal');
  const totalEl    = document.getElementById('summary-total');
  const shippingEl = document.getElementById('summary-shipping');

  if (subtotalEl) subtotalEl.textContent = `$${subtotal.toFixed(2)}`;
  if (shippingEl) shippingEl.textContent = subtotal >= 250 ? 'Free' : 'Calculated at checkout';
  if (totalEl)    totalEl.textContent    = `$${subtotal.toFixed(2)}`;
}

/* ----------------------------------------------------------
   LOGIN PAGE — password toggle
   ---------------------------------------------------------- */
function initLoginPage() {
  const pwInput  = document.getElementById('password');
  const toggleBtn = document.getElementById('toggle-pw');
  const eyeIcon  = document.getElementById('eye-icon');

  if (toggleBtn && pwInput) {
    toggleBtn.addEventListener('click', () => {
      const hidden = pwInput.type === 'password';
      pwInput.type = hidden ? 'text' : 'password';
      if (eyeIcon) eyeIcon.textContent = hidden ? '🙈' : '👁';
    });
  }
}
