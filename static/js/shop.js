/* ============================================================
   MAISON — Unified JS
   Handles: cart state, shop page, product page, cart page, nav
   ============================================================ */

/* ----------------------------------------------------------
   CSRF helper — reads Django's csrftoken cookie
   ---------------------------------------------------------- */
function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : '';
}

/* ----------------------------------------------------------
   ADD TO CART — POST to Django backend
   POST /cart/add/<product_id>/  with field: quantity
   The view redirects back to the product page on success,
   so for quick-buy on the shop page we use fetch() to stay
   on the page and just show a toast instead.
   ---------------------------------------------------------- */
function postAddToCart(productId, quantity, { redirect = false } = {}) {
  const url = `/cart/add/${productId}/`;

  if (redirect) {
    // Let the browser follow the view's redirect naturally (product page form submit)
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = url;

    const csrfInput = document.createElement('input');
    csrfInput.type  = 'hidden';
    csrfInput.name  = 'csrfmiddlewaretoken';
    csrfInput.value = getCsrfToken();

    const qtyInput = document.createElement('input');
    qtyInput.type  = 'hidden';
    qtyInput.name  = 'quantity';
    qtyInput.value = quantity;

    form.appendChild(csrfInput);
    form.appendChild(qtyInput);
    document.body.appendChild(form);
    form.submit();
    return;
  }

  // fetch() — stay on page (shop quick-buy)
  return fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCsrfToken(),
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `quantity=${quantity}`,
    credentials: 'same-origin',
  });
}

/* ----------------------------------------------------------
   CART COUNT — kept in a data attribute set by the template.
   The count badge is server-rendered; bump animation only.
   ---------------------------------------------------------- */
function syncCartCount() {
  // No-op: count is rendered server-side.
  // Call this after a fetch-based add to animate the badge.
  document.querySelectorAll('.cart-count').forEach(el => {
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

  // Route to page init
  if (document.querySelector('.product-list')) initShopPage();
  if (document.querySelector('.product-detail')) initProductPage();
  if (document.querySelector('.cart-layout'))   initCartPage();
  if (document.querySelector('.login-form'))    initLoginPage();
});

/* ----------------------------------------------------------
   SHOP PAGE — quick buy buttons
   Posts to backend via fetch() so the user stays on the
   shop page. Requires data-product-id on each .product-card.
   ---------------------------------------------------------- */
function initShopPage() {
  document.querySelectorAll('.quick-buy-btn').forEach(btn => {
    btn.addEventListener('click', async e => {
      e.stopPropagation();
      const card      = btn.closest('.product-card');
      const productId = card.dataset.productId;

      if (!productId) {
        console.warn('Quick Buy: missing data-product-id on .product-card');
        return;
      }

      btn.disabled = true;

      try {
        const res = await postAddToCart(productId, 1);
        if (res.ok || res.redirected) {
          showToast('Added to cart!');
          syncCartCount();
          btn.classList.add('added');
          btn.querySelector('.btn-text').textContent = 'Added!';
          setTimeout(() => {
            btn.classList.remove('added');
            btn.querySelector('.btn-text').textContent = 'Quick Buy';
            btn.disabled = false;
          }, 1800);
        } else if (res.status === 302 || res.status === 403) {
          // Unauthenticated — redirect to login
          window.location.href = '/secure/login';
        } else {
          showToast('Could not add to cart.');
          btn.disabled = false;
        }
      } catch {
        showToast('Network error.');
        btn.disabled = false;
      }
    });
  });
}

/* legacy inline handler still referenced in some cards */
async function handleQuickBuy(btn) {
  const card      = btn.closest('.product-card');
  const productId = card.dataset.productId;

  if (!productId) {
    console.warn('Quick Buy: missing data-product-id on .product-card');
    return;
  }

  btn.disabled = true;

  try {
    const res = await postAddToCart(productId, 1);
    if (res.ok || res.redirected) {
      showToast('Added to cart!');
      syncCartCount();
      btn.classList.add('added');
      btn.querySelector('.btn-text').textContent = 'Added!';
      setTimeout(() => {
        btn.classList.remove('added');
        btn.querySelector('.btn-text').textContent = 'Quick Buy';
        btn.disabled = false;
      }, 1800);
    } else {
      window.location.href = '/secure/login';
    }
  } catch {
    showToast('Network error.');
    btn.disabled = false;
  }
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
      const productId = atcBtn.dataset.productId;
      if (!productId) {
        console.warn('Add to Cart: missing data-product-id on button');
        return;
      }
      // Submit as a real form POST — view handles redirect back to product page
      postAddToCart(productId, qty, { redirect: true });
    });
  }

  // Accordion
  document.querySelectorAll('.accordion__trigger').forEach(trigger => {
    trigger.addEventListener('click', () => {
      const expanded = trigger.getAttribute('aria-expanded') === 'true';
      trigger.setAttribute('aria-expanded', String(!expanded));
      const icon = trigger.querySelector('.accordion__icon');
      if (icon) icon.textContent = expanded ? '+' : '−';
      const body = trigger.nextElementSibling;
      if (body) body.classList.toggle('accordion__body--open', !expanded);
    });
  });

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
   The cart page is server-rendered by Django. JS here only
   handles the remove / qty-change buttons if they are wired
   to their own backend views. Toast is shown via Django
   messages rendered into data-toast on the body tag.
   ---------------------------------------------------------- */
function initCartPage() {
  // Show Django message as toast if present (add data-toast="{{ messages|first }}" to <body>)
  const msg = document.body.dataset.toast;
  if (msg) showToast(msg);
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