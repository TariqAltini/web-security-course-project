// ============================================================
// MAISON — main.js
// ============================================================

let cartCount = 0;

function handleQuickBuy(btn) {
  // Update button state
  const originalText = btn.querySelector('.btn-text').textContent;
  btn.querySelector('.btn-text').textContent = 'Added!';
  btn.classList.add('added');
  btn.disabled = true;

  // Increment cart count
  cartCount++;
  const countEl = document.querySelector('.cart-count');
  countEl.textContent = cartCount;
  countEl.classList.add('bump');
  setTimeout(() => countEl.classList.remove('bump'), 350);

  // Show toast
  showToast('Added to cart!');

  // Reset button after 2s
  setTimeout(() => {
    btn.querySelector('.btn-text').textContent = originalText;
    btn.classList.remove('added');
    btn.disabled = false;
  }, 2000);
}

function showToast(message) {
  const toast = document.getElementById('toast');
  toast.querySelector('.toast-msg').textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2800);
}

// Mobile menu toggle
const toggle = document.querySelector('.navbar__mobile-toggle');
const links  = document.querySelector('.navbar__links');

if (toggle && links) {
  toggle.addEventListener('click', () => {
    links.classList.toggle('open');
    toggle.textContent = links.classList.contains('open') ? '✕' : '☰';
  });
}
