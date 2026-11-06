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


/* ===== Store: carrito y favoritos contra el servidor ===== */
function getCookie(name) {
  const m = document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith(name + '='));
  return m ? decodeURIComponent(m.substring(name.length + 1)) : null;
}

const Store = {
  _favs: new Set(), _cart: 0, _favCount: 0, logged: false,

  async _post(url, body) {
    try {
      const r = await fetch(url, {
        method: 'POST', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') || '' },
        body: JSON.stringify(body)
      });
      const d = await r.json().catch(() => ({ success: false, error: 'Respuesta inválida del servidor' }));
      if (!d.success) toast(d.error || 'Ocurrió un error');
      return d;
    } catch (e) {
      toast('Error de conexión');
      return { success: false };
    }
  },

  async init() {
    try {
      const d = await (await fetch('/api/estado/', { credentials: 'same-origin' })).json();
      this.logged = d.logged;
      this._favs = new Set((d.favs || []).map(String));
      this.updateBadges(d.total_carrito, d.total_favs);
    } catch (e) {}
    this.refreshHearts();
  },

  isFav(id) { return this._favs.has(String(id)); },

  async toggleFav(id) {
    const d = await this._post('/api/favoritos/toggle/', { id: String(id) });
    if (!d.success) return null;
    d.is_fav ? this._favs.add(String(id)) : this._favs.delete(String(id));
    this.updateBadges(d.total_carrito, d.total_favs);
    this.refreshHearts();
    document.dispatchEvent(new CustomEvent('store:favs', { detail: { id: String(id), isFav: d.is_fav } }));
    return d.is_fav;
  },

  async addToCart(id, qty = 1) {
    const d = await this._post('/api/carrito/add/', { id: String(id), qty });
    if (d.success) this.updateBadges(d.total_carrito, d.total_favs);
    return d.success;
  },
  async setQty(id, qty) {
    const d = await this._post('/api/carrito/set/', { id: String(id), qty });
    if (d.success) this.updateBadges(d.total_carrito, d.total_favs);
    return d;
  },
  async removeFromCart(id, toFav = false) {
    const d = await this._post('/api/carrito/remove/', { id: String(id), to_fav: toFav });
    if (d.success) {
      if (toFav) this._favs.add(String(id));
      this.updateBadges(d.total_carrito, d.total_favs);
    }
    return d;
  },
  async clearCart(ids) {
    const d = await this._post('/api/carrito/clear/', { ids });
    if (d.success) this.updateBadges(d.total_carrito, d.total_favs);
    return d;
  },

  refreshHearts() {
    document.querySelectorAll('.fav-btn[data-fav]').forEach(b => {
      const on = this.isFav(b.dataset.fav);
      b.classList.toggle('on', on);
      b.textContent = on ? '♥' : '♡';
    });
  },

  updateBadges(cart, fav) {
    if (typeof cart === 'number') this._cart = cart;
    if (typeof fav === 'number') this._favCount = fav;
    const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
    set('badge-cart', this._cart);
    set('badge-fav', this._favCount);
    set('badge-menu', this._cart + this._favCount);
  }
};

/* Corazones de cualquier tarjeta (funciona aunque se re-rendericen) */
document.addEventListener('click', async (e) => {
  const b = e.target.closest('.fav-btn[data-fav]');
  if (!b) return;
  e.preventDefault(); e.stopPropagation();
  await Store.toggleFav(b.dataset.fav);
});

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => Store.init());
else Store.init();