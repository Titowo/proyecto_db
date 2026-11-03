/* ===== C2C Streetwear — datos y utilidades compartidas (mockup) ===== */
const U = (id) => `https://images.unsplash.com/${id}?auto=format&fit=crop&w=800&q=60`;
const fullName = (u) =>
  [u.nombre1, u.nombre2, u.apellido1, u.apellido2].filter(Boolean).join(' ') || u.name || "";

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
    desc: 'Camp Cap negro, nuevo con etiqueta. Ajuste trasero regulable.' },
    { id: 5, brand: 'Nike', title: 'Air Force 1 Low White', cat: 'Zapatillas', size: 'US 9', sizeGroup: 'M', cond: 'Usado', price: 95000, stock: 1,
    seller: '@RetroKicks', img: U('photo-1595950653106-6c9ebd614d3a'), imgs: [U('photo-1595950653106-6c9ebd614d3a')],
    desc: 'Blancas clásicas, uso moderado y suela limpia. Incluyen caja.' },
  { id: 6, brand: 'Supreme', title: 'Box Logo Hoodie Grey', cat: 'Polerones', size: 'L', sizeGroup: 'L', cond: 'Nuevo', price: 180000, stock: 1,
    seller: '@CataColeccionista', img: U('photo-1556821840-3a63f95609a7'), imgs: [U('photo-1556821840-3a63f95609a7')],
    desc: 'Polerón gris con box logo bordado, nuevo con etiquetas.' },
  { id: 7, brand: 'Stüssy', title: 'Stock Logo Cap', cat: 'Gorros', size: 'Única', sizeGroup: 'Única', cond: 'Nuevo', price: 45000, stock: 4,
    seller: '@DiegoVendedor', img: U('photo-1588850561407-ed78c282e89b'), imgs: [U('photo-1588850561407-ed78c282e89b')],
    desc: 'Jockey con logo bordado, ajuste regulable. Nuevo con etiqueta.' },
  { id: 8, brand: 'Jordan', title: 'Air Jordan 4 Military Black', cat: 'Zapatillas', size: 'US 10', sizeGroup: 'L', cond: 'Usado', price: 220000, stock: 1,
    seller: '@RetroKicks', img: U('photo-1608231387042-66d1773070a5'), imgs: [U('photo-1608231387042-66d1773070a5')],
    desc: 'Muy buen estado, con caja y boleta. Autenticidad verificable.' },
  { id: 9, brand: 'Nike', title: 'Tech Fleece Hoodie', cat: 'Polerones', size: 'S', sizeGroup: 'S', cond: 'Usado', price: 70000, stock: 2,
    seller: '@CataColeccionista', img: U('photo-1556821840-3a63f95609a7'), imgs: [U('photo-1556821840-3a63f95609a7')],
    desc: 'Polerón tech fleece negro, usado pocas veces, sin manchas.' },
  { id: 10, brand: 'Supreme', title: 'Box Logo Beanie', cat: 'Gorros', size: 'Única', sizeGroup: 'Única', cond: 'Nuevo', price: 55000, stock: 2,
    seller: '@DiegoVendedor', img: U('photo-1588850561407-ed78c282e89b'), imgs: [U('photo-1588850561407-ed78c282e89b')],
    desc: 'Gorro de lana con box logo, nuevo.' }
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
  
    getDB() {
    const SEED = {
      'test@c2c.cl':  { nombre1: 'Diego', nombre2: '', apellido1: 'Fuentes', apellido2: '',
                        username: '@DiegoVendedor', email: 'test@c2c.cl', pass: '123', rol: 'usuario' },
      'admin@c2c.cl': { nombre1: 'Admin', nombre2: '', apellido1: 'C2C', apellido2: '',
                        username: '@AdminC2C', email: 'admin@c2c.cl', pass: 'admin123', rol: 'admin' }
    };
    return { ...SEED, ...load('c2c_users_db', {}) };
  },

  login(email, pass) {
    email = email.trim().toLowerCase();
    const db = Auth.getDB();
    if (db[email] && db[email].pass === pass) { save('c2c_active_user', db[email]); return true; }
    return false;
  },

  register(d) {
    const db = Auth.getDB();
    const email = d.email.trim().toLowerCase();
    let username = d.username.trim();
    if (!username.startsWith('@')) username = '@' + username;

    if (!d.nombre1 || !d.apellido1)
      return { ok: false, error: 'El primer nombre y el primer apellido son obligatorios' };
    if (!/^@[A-Za-z0-9_.]{3,29}$/.test(username))
      return { ok: false, error: '@usuario: de 3 a 29 caracteres (letras, números, _ o .)' };
    if (db[email])
      return { ok: false, error: 'Ese correo ya está registrado' };
    if (Object.values(db).some(u => (u.username || '').toLowerCase() === username.toLowerCase()))
      return { ok: false, error: 'Ese @usuario ya está en uso' };

    db[email] = { nombre1: d.nombre1, nombre2: d.nombre2, apellido1: d.apellido1, apellido2: d.apellido2,
                  username, email, pass: d.pass, rol: 'usuario', fecha_registro: new Date().toISOString() };
    save('c2c_users_db', db);
    save('c2c_active_user', db[email]);
    return { ok: true };
  },


  /* Exige sesión. Si no hay, avisa y manda a login recordando a dónde volver */
  require(msg = 'Inicia sesión para continuar') {
    if (Auth.getUser()) return true;
    toast(msg);
    const next = location.pathname.split('/').pop() + location.search + location.hash;
    setTimeout(() => { location.href = 'login.html?next=' + encodeURIComponent(next); }, 900);
    return false;
  },

  requireAdmin() {
    const u = Auth.getUser();
    if (u && u.rol === 'admin') return true;
    if (!u) return Auth.require('Inicia sesión como administrador');
    toast('Acceso restringido a administradores');
    setTimeout(() => { location.href = 'catalogo.html'; }, 900);
    return false;
  },
  logout() { localStorage.removeItem('c2c_active_user'); }
};

/* ---------- Mockup de Reportes y Valoraciones (RF12 y RF13) ---------- */
const SEED_REPORTS = [
  { id: 1, articleId: 1, reason: 'Contenido sospechoso o fraude - Detalles: la etiqueta interior no corresponde a un par original.',
    reporter: '@CataColeccionista', date: '23-9-2026', status: 'Pendiente' },
  { id: 2, articleId: 3, reason: 'Información engañosa o falsa',
    reporter: '@MatiStreet', date: '21-9-2026', status: 'Revisado' },
  { id: 3, articleId: 4, reason: 'Artículo prohibido o falsificado',
    reporter: '@NachoKicks', date: '19-9-2026', status: 'Descartado' }
];

const Moderation = {
  getReports() { return load('c2c_reports', SEED_REPORTS); },
  saveReport(articleId, reason) {
    const reps = Moderation.getReports();
    reps.push({ id: Date.now(), articleId, reason,
      reporter: (Auth.getUser() || {}).username || 'anónimo',
      date: new Date().toLocaleDateString('es-CL'), status: 'Pendiente' });
    save('c2c_reports', reps);
  },
  setReportStatus(id, status) {
    const reps = Moderation.getReports();
    const r = reps.find(x => x.id === id);
    if (!r) return;
    r.status = status;
    r.reviewedBy = (Auth.getUser() || {}).username;
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
    const c = document.getElementById('badge-cart'), f = document.getElementById('badge-fav'),
          m = document.getElementById('badge-menu');
    const nc = Object.values(Store.cart()).reduce((a, b) => a + b, 0), nf = Store.favs().length;
    if (c) c.textContent = nc;
    if (f) f.textContent = nf;
    if (m) m.textContent = nc + nf;
  }
};

/* ---------- Header compartido ---------- */
function renderHeader(active) {
  const el = document.getElementById('app-header');
  if (!el) return;
  const cls = (...names) => (names.includes(active) ? 'active' : '');
  const user = Auth.getUser();

  const userNav = user ? `
      <div class="dropdown" id="menu-dd">
        <button type="button" class="dd-btn ${cls('favoritos', 'carrito', 'chat', 'admin')}" id="menu-btn" aria-haspopup="true" aria-expanded="false">Menú ▾<span class="badge" id="badge-menu">0</span></button>
        <div class="dd-menu" id="menu-list" role="menu">
          <a href="carrito.html#favoritos" role="menuitem" class="${cls('favoritos')}">♡ Favoritos <span class="count" id="badge-fav">0</span></a>
          <a href="carrito.html" role="menuitem" class="${cls('carrito')}">Carrito <span class="count" id="badge-cart">0</span></a>
          <a href="chat.html" role="menuitem" class="${cls('chat')}">Mensajes</a>
          ${user.rol === 'admin' ? `<a href="admin.html" role="menuitem" class="${cls('admin')}">Reportes</a>` : ''}
        </div>
      </div>
      <a href="perfil.html" class="btn-login">Mi Perfil</a>
      <button type="button" class="link-btn logout" onclick="Auth.logout(); window.location.href='catalogo.html';">Cerrar sesión</button>`
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
      ${userNav}
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
  if (!Auth.require('Inicia sesión para guardar favoritos')) return;
  const on = Store.toggleFav(b.dataset.fav);
  b.classList.toggle('on', on); b.textContent = on ? '♥' : '♡';
  toast(on ? 'Agregado a favoritos' : 'Quitado de favoritos');
  if (typeof onFavChange === 'function') onFavChange();
});


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
  if (btn) { const open = dd.classList.toggle('open'); btn.setAttribute('aria-expanded', open); return; }
  if (!e.target.closest('#menu-list')) closeMenu();
});
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });
