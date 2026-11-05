/* ===== C2C Streetwear — utilidades compartidas ===== */

/* Formatea número como moneda chilena */
const fmt = (n) => '$' + Math.round(n).toLocaleString('es-CL');

/* Toast global */
function toast(msg) {
  let t = document.getElementById('toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast';
    t.className = 'toast';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => t.classList.remove('show'), 2200);
}

/* Header compartido */
function renderHeader(active) {
  const el = document.getElementById('app-header');
  if (!el) return;
  
  const user = window.currentUser || null;
  const cls = (...names) => (names.includes(active) ? 'active' : '');

  const userNav = user ? `
      <div class="dropdown" id="menu-dd">
        <button type="button" class="dd-btn ${cls('favoritos', 'carrito', 'chat', 'publicar', 'admin')}" id="menu-btn" aria-haspopup="true" aria-expanded="false">Menú ▾<span class="badge" id="badge-menu">0</span></button>
        <div class="dd-menu" id="menu-list" role="menu">
          <a href="/carrito.html#favoritos" role="menuitem" class="${cls('favoritos')}">♡ Favoritos <span class="count" id="badge-fav">0</span></a>
          <a href="/carrito.html" role="menuitem" class="${cls('carrito')}">Carrito <span class="count" id="badge-cart">0</span></a>
          <a href="/chat.html" role="menuitem" class="${cls('chat')}">Mensajes</a>
          <a href="/publicar.html" role="menuitem" class="${cls('publicar')}">Publicar artículo</a>
          <a href="#" role="menuitem" class="dd-only-mobile" onclick="window.location.href='/login/'; return false;">Cerrar sesión</a>
        </div>
      </div>
      <a href="/perfil.html" class="btn-login">Mi Perfil</a>
      <button type="button" class="link-btn logout">Cerrar sesión</button>`
    : `<a href="/login/" class="btn-login">Iniciar Sesión</a>`;

  el.outerHTML = `
  <header class="site-header">
    <a class="logo" href="/">C2C <span>Streetwear</span></a>
    <form class="search-bar" action="/" method="GET">
      <input type="text" name="q" placeholder="Buscar zapatillas, polerones...">
      <button type="submit">Buscar</button>
    </form>
    <nav class="nav-links">
      <a href="/" class="${cls('catalogo')}">Catálogo</a>
      ${userNav}
    </nav>
  </header>`;
}

/* Tarjeta de producto reutilizable */
function productCard(p) {
  return `
  <a class="product-card" href="/producto?id=${p.id}">
    <button class="fav-btn" data-fav="${p.id}" title="Favorito">♡</button>
    <img src="${p.img}" alt="${p.title}" class="product-image">
    <div class="product-info">
      <div class="brand">${p.brand}</div>
      <h2 class="product-title">${p.title}</h2>
      <div class="product-meta"><span>Talla: ${p.size}</span><span>${p.cond}</span></div>
      <div class="price">${fmt(p.price)}</div>
      <div class="seller-line">Vende ${p.seller}</div>
    </div>
  </a>`;
}

/* Menú desplegable */
function closeMenu() {
  const dd = document.getElementById('menu-dd'), b = document.getElementById('menu-btn');
  if (dd) dd.classList.remove('open');
  if (b) b.setAttribute('aria-expanded', 'false');
}
document.addEventListener('click', (e) => {
  const dd = document.getElementById('menu-dd');
  if (!dd) return;
  const btn = e.target.closest('#menu-btn');
  if (btn) {
    const open = dd.classList.toggle('open');
    btn.setAttribute('aria-expanded', open);
    return;
  }
  if (!e.target.closest('#menu-list')) closeMenu();
});
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });