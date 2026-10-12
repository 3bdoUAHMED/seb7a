// Renders every offer × size × language banner into #app.
// Each banner is a .banner element at its exact pixel size, so render.mjs
// can screenshot it 1:1.

function esc(s) {
  return String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
}

// Escapes text and keeps numbers like "40%" left-to-right inside Arabic text.
// numClass styles those numbers (used to make the discount pop in headlines).
function txt(s, numClass = "") {
  const cls = numClass ? ` class="${numClass}"` : "";
  return esc(s).replace(/[0-9][0-9.,]*(?:\s?%)?/g, (m) => `<span dir="ltr"${cls}>${m}</span>`);
}

// Keeps "Bio-Activ" / "بيو أكتيف" from breaking across two lines.
function keepTogether(name) {
  return name.replace(/Bio-Activ/g, "Bio\u2011Activ").replace(/بيو أكتيف/g, "بيو\u00a0أكتيف");
}

// BLACK FRIDAY typographic sticker: outlined "BLACK" over a gold "FRIDAY" slab.
function stickerHTML(lang) {
  return `
    <div class="bf-sticker">
      <span class="bf-black">BLACK</span>
      <span class="bf-friday">FRIDAY</span>
      <span class="bf-sale">${lang === "ar" ? "عروض حصرية" : "SALE"}</span>
    </div>`;
}

// Simple bottle drawing used until a real product photo is set.

function placeholderProduct(name, theme, i) {
  const caps = [theme.accent, "#ffffff", theme.to, theme.from];
  const cap = caps[i % caps.length];
  return `
    <svg class="ph" viewBox="0 0 120 200" xmlns="http://www.w3.org/2000/svg" aria-label="${esc(name)}">
      <rect x="38" y="6" width="44" height="26" rx="5" fill="${cap}" stroke="rgba(0,0,0,.15)"/>
      <rect x="44" y="30" width="32" height="12" fill="#e9ecef"/>
      <path d="M30 42h60q14 0 14 16v124q0 12-12 12H28q-12 0-12-12V58q0-16 14-16z" fill="#ffffff"/>
      <rect x="16" y="80" width="88" height="74" fill="${theme.from}"/>
      <rect x="16" y="80" width="88" height="8" fill="${theme.accent}"/>
      <path d="M22 50q-6 6-6 20v100" stroke="rgba(0,0,0,.06)" stroke-width="6" fill="none"/>
    </svg>`;
}

function productHTML(p, offer, lang, i, showName) {
  const name = p.name?.[lang] ?? "";
  // If the image file is missing, fall back to the placeholder bottle.
  const media = p.image
    ? `<img src="${esc(p.image)}" alt="${esc(name)}" onerror="this.nextElementSibling.style.display='';this.remove()">
       <span style="display:none;height:100%;width:100%">${placeholderProduct(name, offer.theme, i)}</span>`
    : placeholderProduct(name, offer.theme, i);
  const price = p.price
    ? `<div class="price">${p.oldPrice ? `<s>${esc(p.oldPrice)}</s>` : ""}<b>${esc(p.price)}</b></div>`
    : "";
  return `
    <div class="product" style="--s:${p.scale ?? 1};--z:${p.zoom ?? 1}">
      <div class="product-media">${media}</div>
      ${showName ? `<div class="product-name">${txt(keepTogether(name))}</div>${price}` : ""}
    </div>`;
}

function logoHTML(lang) {
  if (!BRAND.logo && !BRAND.name[lang]) return "";
  return BRAND.logo
    ? `<img class="logo" src="${esc(BRAND.logo)}" alt="${esc(BRAND.name[lang])}">`
    : `<div class="logo logo-text">${esc(BRAND.name[lang])}</div>`;
}

function bannerHTML(offer, size, lang) {
  const t = offer.theme;
  const products = offer.products.slice(0, size.maxProducts);
  const showNames = size.id === "mobile-vertical-hero" || size.id === "desktop-hero";
  const code = offer.code?.[lang];
  return `
    <div class="banner ${offer.id} ${size.id} ${(window.STICKER_OVERRIDE ?? STICKER) ? "has-sticker" : ""} hl-${window.HL_STYLE || HEADLINE_STYLE} pat-${window.PATTERN_OVERRIDE || PATTERN} n${products.length}${products.length >= 5 ? " many" : ""}" dir="${lang === "ar" ? "rtl" : "ltr"}" lang="${lang}"
         data-file="${offer.id}/${size.device}-${lang}-${size.w}x${size.h}.png"
         style="width:${size.w}px;height:${size.h}px;--from:${t.from};--to:${t.to};--accent:${t.accent};--glow:${t.glow || t.to};--text:${t.text}">
      ${(window.STICKER_OVERRIDE ?? STICKER) ? stickerHTML(lang) : ""}<div class="deco deco-1"></div><div class="deco deco-2"></div><div class="deco deco-3"></div>
      <div class="copy">
        ${logoHTML(lang)}
        <div class="badge">${txt(offer.badge[lang])}</div>
        <h2 class="headline">${txt(offer.headline[lang], "hl-num")}</h2>
        ${offer.sub[lang] ? `<p class="sub">${txt(offer.sub[lang])}</p>` : ""}
        <div class="actions">
          <span class="cta">${txt(offer.cta[lang])}<span class="arrow">${lang === "ar" ? "←" : "→"}</span></span>
          ${code ? `<span class="code">${txt(code)}</span>` : ""}
        </div>
      </div>
      <div class="products">
        ${products.map((p, i) => productHTML(p, offer, lang, i, showNames)).join("")}
      </div>
      ${size.id === "mobile-vertical-hero" ? `
      <div class="footer-cta">
        <span class="cta">${txt(offer.cta[lang])}<span class="arrow">${lang === "ar" ? "←" : "→"}</span></span>
        ${code ? `<span class="code">${txt(code)}</span>` : ""}
      </div>` : ""}
    </div>`;
}

function render() {
  const app = document.getElementById("app");
  app.innerHTML = OFFERS.map((offer, oi) => `
    <section class="offer">
      <h2 class="offer-title">Offer ${oi + 1} · عرض ${oi + 1} <small>${esc(offer.headline.en)} — ${esc(offer.headline.ar)}</small></h2>
      ${SIZES.map((size) => `
        <div class="slot">
          <div class="slot-label">${size.device === "mobile" ? "📱 Mobile" : "🖥 Desktop"} · <b>${size.w} x ${size.h}</b> ${size.label}</div>
          <div class="pair">
            ${LANGS.map((lang) => `
              <figure>
                <figcaption>${lang === "en" ? "EN English Banner" : "AR Arabic Banner"}</figcaption>
                <div class="frame">${bannerHTML(offer, size, lang)}</div>
              </figure>`).join("")}
          </div>
        </div>`).join("")}
    </section>`).join("");
}

render();
