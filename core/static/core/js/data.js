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
          <a href="/carrito/#favoritos" role="menuitem" class="${cls('favoritos')}">♡ Favoritos <span class="count" id="badge-fav">0</span></a>
          <a href="/carrito" role="menuitem" class="${cls('carrito')}">Carrito <span class="count" id="badge-cart">0</span></a>
          <a href="/chat" role="menuitem" class="${cls('chat')}">Mensajes</a>
          <a href="/publicar" role="menuitem" class="${cls('publicar')}">Publicar artículo</a>
          <a href="#" role="menuitem" class="dd-only-mobile" onclick="window.location.href='/logout/'; return false;">Cerrar sesión</a>
          ${user.rol === 'admin' ? `<a href="/admin" role="menuitem" class="${cls('admin')}">Reportes</a>` : ''}
        </div>
      </div>
      <a href="/perfil" class="btn-login">Mi Perfil</a>
      <button type="button" class="link-btn logout">Cerrar sesión</button>`
    : `<a href="/login/" class="btn-login">Iniciar Sesión</a>`;

  el.outerHTML = `
  <header class="site-header">
    <a class="logo" href="/catalogo">C2C <span>Streetwear</span></a>
    <form class="search-bar" action="/catalogo" method="GET">
      <input type="text" name="q" placeholder="Buscar zapatillas, polerones...">
      <button type="submit">Buscar</button>
    </form>
    <nav class="nav-links">
      <a href="/catalogo" class="${cls('catalogo')}">Catálogo</a>
      ${userNav}
    </nav>
  </header>`;
  Store.updateBadges();
}

/* Tarjeta de producto reutilizable */
function productCard(p) {
  const imgs = window.productImgs ? window.productImgs[p.id] || [p.img || p.url_imagen] : [p.img || p.url_imagen, p.img_2, p.img_3, p.img_4];
  return `
  <a class="product-card" href="/producto/${p.id}">
    <button class="fav-btn ${Store.isFav(p.id) ? 'on' : ''}" data-fav="${p.id}" title="Favorito">${Store.isFav(p.id) ? '♥' : '♡'}</button>
    <img src="${imgs[0]}" alt="${p.title || p.nombre}" class="product-image">
    <div class="product-info">
      <div class="brand">${p.brand || p.marca}</div>
      <h2 class="product-title">${p.title || p.nombre}</h2>
      <div class="product-meta"><span>Talla: ${p.size || p.talla}</span><span>${p.cond || p.estado_conservacion}</span></div>
      <div class="price">${fmt(p.price || p.precio)}</div>
      <div class="seller-line">Vende ${(p.seller || {}).nombre_usuario || (p.vendedor ? p.vendedor.nombre_usuario : 'Vendedor')}</div>
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