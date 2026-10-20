/* ===== C2C Streetwear — datos y utilidades compartidas (mockup) ===== */
const U = (id) => `https://images.unsplash.com/${id}?auto=format&fit=crop&w=800&q=60`;

const SELLERS = {
  '@DiegoVendedor':     { initial: 'D', rating: '4.9', sales: 37, zone: 'Santiago Centro' },
  '@CataColeccionista': { initial: 'C', rating: '4.7', sales: 21, zone: 'Providencia' },
  '@RetroKicks':        { initial: 'R', rating: '5.0', sales: 64, zone: 'Viña del Mar' }
};

const PRODUCTS = [
  { id: 1, brand: 'Nike', title: 'Dunk Low "Panda"', cat: 'Zapatillas', size: 'US 10', sizeGroup: 'L', cond: 'Usado', price: 120000, stock: 2,
    seller: '@DiegoVendedor', img: U('photo-1595950653106-6c9ebd614d3a'),
    imgs: [U('photo-1595950653106-6c9ebd614d3a'), U('photo-1608231387042-66d1773070a5'), U('photo-1588850561407-ed78c282e89b')],
    desc: 'Colorway blanco/negro en muy buen estado, usadas 3 veces. Incluye caja original y cordones de repuesto.' },
  { id: 2, brand: 'Stüssy', title: 'Basic Logo Hoodie', cat: 'Polerones', size: 'L', sizeGroup: 'L', cond: 'Nuevo', price: 85000, stock: 1,
    seller: '@CataColeccionista', img: U('photo-1556821840-3a63f95609a7'),
    imgs: [U('photo-1556821840-3a63f95609a7'), U('photo-1588850561407-ed78c282e89b')],
    desc: 'Polerón con etiquetas, comprado en tienda oficial y nunca usado. Algodón pesado, fit relajado.' },
  { id: 3, brand: 'Jordan', title: 'Air Jordan 1 Retro High', cat: 'Zapatillas', size: 'US 9.5', sizeGroup: 'M', cond: 'Usado', price: 190000, stock: 1,
    seller: '@RetroKicks', img: U('photo-1608231387042-66d1773070a5'),
    imgs: [U('photo-1608231387042-66d1773070a5'), U('photo-1595950653106-6c9ebd614d3a')],
    desc: 'Retro High en buen estado, suela con desgaste leve. Autenticidad verificable con boleta.' },
  { id: 4, brand: 'Supreme', title: 'Camp Cap Black', cat: 'Gorros', size: 'Única', sizeGroup: 'Única', cond: 'Nuevo', price: 65000, stock: 3,
    seller: '@DiegoVendedor', img: U('photo-1588850561407-ed78c282e89b'),
    imgs: [U('photo-1588850561407-ed78c282e89b'), U('photo-1556821840-3a63f95609a7')],
    desc: 'Camp Cap negro, nuevo con etiqueta. Ajuste trasero regulable.' }
];

/* ---------- Utilidades ---------- */
const fmt = (n) => '$' + Math.round(n).toLocaleString('es-CL');
const getProduct = (id) => PRODUCTS.find(p => p.id === Number(id));

function load(key, fallback) {
  try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch (e) { return fallback; }
}
function save(key, val) { try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) {} }

/* ---------- Mockup de Autenticación (RF1 y RF2) ---------- */
const Auth = {
  getUser() { return load('c2c_active_user', null); },
  
  getDB() { return load('c2c_users_db', { 
    'test@c2c.cl': { name: 'Diego Fuentes', email: 'test@c2c.cl', pass: '123' } 
  });},

  login(email, pass) {
    const db = Auth.getDB();
    if (db[email] && db[email].pass === pass) {
      save('c2c_active_user', db[email]);
      return true;
    }
    return false;
  },

  register(name, email, pass) {
    const db = Auth.getDB();
    if (db[email]) return false; 
    db[email] = { name, email, pass };
    save('c2c_users_db', db);
    save('c2c_active_user', db[email]); 
    return true;
  },

  logout() { localStorage.removeItem('c2c_active_user'); }
};

/* ---------- Mockup de Reportes y Valoraciones (RF12 y RF13) ---------- */
const Moderation = {
  saveReport(articleId, reason) {
    const reps = load('c2c_reports', []);
    reps.push({ id: Date.now(), articleId, reason, date: new Date().toLocaleDateString('es-CL'), status: 'Pendiente' });
    save('c2c_reports', reps);
  },
  saveReview(seller, stars, comment) {
    const revs = load('c2c_reviews', []);
    revs.push({ id: Date.now(), seller, stars, comment, date: new Date().toLocaleDateString('es-CL') });
    save('c2c_reviews', revs);
  }
};

/* Carrito: { productId: cantidad } */
const Store = {
  cart() { return load('c2c_cart', { 1: 1, 4: 1, 2: 1 }); },
  favs() { return load('c2c_favs', [3]); },
  setCart(c) { save('c2c_cart', c); Store.updateBadges(); },
  setFavs(f) { save('c2c_favs', f); Store.updateBadges(); },
  addToCart(id, qty = 1) {
    const c = Store.cart(); const p = getProduct(id);
    c[id] = Math.min((c[id] || 0) + qty, p.stock); Store.setCart(c);
  },
  toggleFav(id) {
    let f = Store.favs();
    f = f.includes(Number(id)) ? f.filter(x => x !== Number(id)) : [...f, Number(id)];
    Store.setFavs(f); return f.includes(Number(id));
  },
  isFav(id) { return Store.favs().includes(Number(id)); },
  updateBadges() {
    const c = document.getElementById('badge-cart'), f = document.getElementById('badge-fav');
    if (c) c.textContent = Object.values(Store.cart()).reduce((a, b) => a + b, 0);
    if (f) f.textContent = Store.favs().length;
  }
};

/* ---------- Header compartido ---------- */
function renderHeader(active) {
  const el = document.getElementById('app-header');
  if (!el) return;
  const cls = (n) => (n === active ? 'active' : '');
  
  const user = Auth.getUser();
  const authButtons = user 
    ? `<a href="perfil.html" class="btn-login">Mi Perfil</a>
       <button onclick="Auth.logout(); window.location.href='catalogo.html';" class="link-btn" style="margin-left:12px; font-weight:bold;">Salir</button>`
    : `<a href="login.html" class="btn-login">Iniciar Sesión</a>`;

  el.outerHTML = `
  <header class="site-header">
    <a class="logo" href="catalogo.html">C2C <span>Streetwear</span></a>
    <form class="search-bar" action="catalogo.html" method="GET">
      <input type="text" placeholder="Buscar zapatillas, polerones, marcas..." name="q">
      <button type="submit">Buscar</button>
    </form>
    <nav class="nav-links">
      <a href="catalogo.html" class="${cls('catalogo')}">Catálogo</a>
      <a href="carrito.html#favoritos" class="${cls('favoritos')}">Favoritos<span class="badge" id="badge-fav">0</span></a>
      <a href="carrito.html" class="${cls('carrito')}">Carrito<span class="badge" id="badge-cart">0</span></a>
      <a href="chat.html" class="${cls('chat')}">Mensajes</a>
      ${authButtons}
    </nav>
  </header>`;
  Store.updateBadges();
}

function toast(msg) {
  let t = document.getElementById('toast');
  if (!t) { t = document.createElement('div'); t.id = 'toast'; t.className = 'toast'; document.body.appendChild(t); }
  t.textContent = msg; t.classList.add('show');
  clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove('show'), 2200);
}

/* Tarjeta de producto reutilizable */
function productCard(p) {
  return `
  <a class="product-card" href="producto.html?id=${p.id}">
    <button class="fav-btn ${Store.isFav(p.id) ? 'on' : ''}" data-fav="${p.id}" title="Favorito">${Store.isFav(p.id) ? '♥' : '♡'}</button>
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

document.addEventListener('click', (e) => {
  const b = e.target.closest('[data-fav]');
  if (!b) return;
  e.preventDefault(); e.stopPropagation();
  const on = Store.toggleFav(b.dataset.fav);
  b.classList.toggle('on', on); b.textContent = on ? '♥' : '♡';
  toast(on ? 'Agregado a favoritos' : 'Quitado de favoritos');
  if (typeof onFavChange === 'function') onFavChange();
});
