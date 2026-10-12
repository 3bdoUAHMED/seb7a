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

// BLACK FRIDAY ribbon sticker: red "BLACK" flag, white "FRIDAY" ribbon,
// a star and a round badge with the offer's discount.
function stickerHTML(offer, lang) {
  const [l1, l2 = ""] = (offer.stickerBadge?.[lang] ?? "").split("|");
  const badgeFont = /[\u0600-\u06ff]/.test(l1 + l2) ? "Cairo" : "Anton";
  const long = Math.max(l1.length, l2.length) > 5;
  const fs = long ? 22 : 34;
  const gid = `bfg-${offer.id}-${lang}`;
  // Extruded 3D text: stacked dark copies under a white face.
  const line3d = (t, x, y, size) => {
    const attrs = `text-anchor="middle" font-family="${badgeFont}, sans-serif" font-weight="900" font-size="${size}"`;
    let out = "";
    for (let d = 5; d >= 1; d--) out += `<text x="${x + d * 0.7}" y="${y + d}" ${attrs} fill="#3a0505">${esc(t)}</text>`;
    return out + `<text x="${x}" y="${y}" ${attrs} fill="#fff" stroke="#ffe3b0" stroke-width=".6">${esc(t)}</text>`;
  };
  return `
    <div class="bf-sticker">
      <svg viewBox="0 0 450 350" xmlns="http://www.w3.org/2000/svg">
        <g transform="rotate(-24 210 170)">
          <path d="M28 168 l14 26 29 4 -21 20 5 29 -27 -14 -26 14 5 -29 -21 -20 29 -4z" fill="#d42a2a"/>
          <path d="M100 70 H370 L346 112 L370 154 H100 Z" fill="#d42a2a"/>
          <text x="220" y="128" text-anchor="middle" font-family="Poppins, sans-serif" font-weight="500" font-size="56" fill="#111">BLACK</text>
          <path d="M120 146 q 18 -16 36 0 t 36 0 t 36 0 t 36 0 t 36 0 t 36 0" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round"/>
          <path d="M80 160 H330 Q340 200 332 240 H86 Q92 220 76 204 Q92 186 80 160 Z" fill="#fff"/>
          <text x="208" y="222" text-anchor="middle" font-family="Poppins, sans-serif" font-weight="500" font-size="54" fill="#d42a2a">FRIDAY</text>
        </g>
        ${l1 ? `
        <defs>
          <radialGradient id="${gid}" cx="38%" cy="30%" r="75%">
            <stop offset="0" stop-color="#ff5a4f"/><stop offset=".55" stop-color="#c41f1f"/><stop offset="1" stop-color="#7a0f0f"/>
          </radialGradient>
        </defs>
        <g transform="rotate(-20 368 250)">
          <circle cx="374" cy="261" r="74" fill="#4a0707"/>
          <circle cx="368" cy="250" r="74" fill="url(#${gid})" stroke="#ffd5c2" stroke-opacity=".5" stroke-width="2"/>
          <ellipse cx="346" cy="212" rx="38" ry="17" fill="#fff" opacity=".22"/>
          ${line3d(l1, 368, l2 ? 245 : 262, fs + 8)}
          ${l2 ? line3d(l2, 368, 245 + fs + 8, fs + 2) : ""}
        </g>` : ""}
      </svg>
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

// Giant glossy 3D number (red face, black extruded body).
function bigNumHTML(offer, lang) {
  const b = offer.bigNum;
  return `
    <div class="bn">
      ${b.pre[lang] ? `<div class="bn-pre">${txt(b.pre[lang])}</div>` : ""}
      <div class="bn-row" dir="ltr">
        ${b.image ? `<img class="bn-img" src="${esc(b.image)}" alt="">`
          : b.num ? `<span class="bn-num" data-t="${esc(b.num)}">${esc(b.num)}</span>`
          : `<span class="bn-space"></span>`}
        ${b.post[lang] ? `<span class="bn-post">${esc(b.post[lang])}</span>` : ""}
      </div>
    </div>`;
}

function heroVerticalHTML(offer, size, lang, cls, style) {
  const products = offer.products.slice(0, size.maxProducts);
  return `
    <div class="banner hero ${cls}" dir="${lang === "ar" ? "rtl" : "ltr"}" lang="${lang}"
         data-file="${offer.id}/${size.device}-${lang}-${size.w}x${size.h}.png" style="${style}">
      ${stickerHTML({ ...offer, stickerBadge: null }, lang)}
      <div class="hero-top">${logoHTML(lang)}</div>
      ${bigNumHTML(offer, lang)}
      <div class="hero-products">
        ${products.map((p, i) => productHTML(p, offer, lang, i, false)).join("")}
      </div>
      <div class="hero-bottom">
        <p class="hero-sub">${txt(offer.headlineSub?.[lang] ?? offer.sub[lang] ?? "")}</p>
        <span class="cta">${txt(offer.cta[lang])}<span class="arrow">${lang === "ar" ? "←" : "→"}</span></span>
      </div>
    </div>`;
}

// Products fanned along a half circle (dome). Each product stands on the arc,
// tilted outward; the middle ones are biggest. Gold arcs behind suggest motion.
function arcVerticalHTML(offer, size, lang, cls, style) {
  const products = offer.products.slice(0, size.maxProducts);
  const n = products.length;
  const cx = size.w / 2, cy = 1240, R = 520;
  const maxA = n > 5 ? 38 : 30;
  const base = n > 5 ? 260 : 340;
  const items = products.map((p, i) => {
    const a = n === 1 ? 0 : -maxA + (2 * maxA * i) / (n - 1);
    const rad = (a * Math.PI) / 180;
    const x = cx + R * Math.sin(rad), y = cy - R * Math.cos(rad);
    const h = base * (1 - 0.32 * Math.abs(a) / maxA) * (p.scale ?? 1);
    return `
      <div class="arc-item" style="left:${x.toFixed(1)}px;top:${y.toFixed(1)}px;height:${h.toFixed(0)}px;transform:translate(-50%,-100%) rotate(${(a * 0.5).toFixed(1)}deg)">
        ${p.image ? `<img src="${esc(p.image)}" alt="${esc(p.name?.[lang] ?? "")}">` : ""}
      </div>`;
  }).join("");
  // concentric motion arcs (upper half circles)
  const arc = (r, w, op, dash) =>
    `<path d="M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}" fill="none" stroke="url(#arcg-${offer.id}-${lang})" stroke-width="${w}" stroke-opacity="${op}" stroke-linecap="round" ${dash ? `stroke-dasharray="${dash}"` : ""}/>`;
  const svg = `
    <svg class="arc-lines" viewBox="0 0 ${size.w} ${size.h}" width="${size.w}" height="${size.h}">
      <defs><linearGradient id="arcg-${offer.id}-${lang}" x1="0" x2="1">
        <stop offset="0" stop-color="#f2c94c" stop-opacity="0"/><stop offset=".5" stop-color="#f2c94c"/><stop offset="1" stop-color="#f2c94c" stop-opacity="0"/>
      </linearGradient>
      <radialGradient id="dome-${offer.id}-${lang}" cx="50%" cy="0%" r="90%">
        <stop offset="0" stop-color="${offer.theme.glow || "#d63447"}" stop-opacity=".55"/><stop offset=".6" stop-color="#0a0a0a" stop-opacity=".2"/><stop offset="1" stop-color="#0a0a0a" stop-opacity="0"/>
      </radialGradient></defs>
      <path d="M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy} Z" fill="url(#dome-${offer.id}-${lang})"/>
      ${arc(R, 4, 0.9)}
      ${arc(R + 40, 2, 0.55, "160 40 60 40")}
      ${arc(R + 80, 1.5, 0.35, "60 30")}
      ${arc(R - 46, 2, 0.4, "220 60")}
      ${arc(R + 130, 1, 0.25)}
    </svg>`;
  return `
    <div class="banner arc ${cls}" dir="${lang === "ar" ? "rtl" : "ltr"}" lang="${lang}"
         data-file="${offer.id}/${size.device}-${lang}-${size.w}x${size.h}.png" style="${style}">
      ${stickerHTML({ ...offer, stickerBadge: null }, lang)}
      ${svg}
      <div class="arc-glow" style="left:${cx}px;top:${cy}px"></div>
      <div class="arc-top">
        ${logoHTML(lang)}
        <h2 class="headline">${txt(offer.headline[lang], "hl-num")}</h2>
        ${offer.sub[lang] ? `<p class="sub">${txt(offer.sub[lang])}</p>` : ""}
      </div>
      ${items}
      <div class="arc-cta"><span class="cta">${txt(offer.cta[lang])}<span class="arrow">${lang === "ar" ? "←" : "→"}</span></span></div>
    </div>`;
}

function bannerHTML(offer, size, lang) {
  const t = offer.theme;
  const products = offer.products.slice(0, size.maxProducts);
  const showNames = size.id === "mobile-vertical-hero" || size.id === "desktop-hero";
  const code = offer.code?.[lang];
  if ((window.ARC_OVERRIDE ?? ARC) && size.id === "mobile-vertical-hero") {
    return arcVerticalHTML(offer, size, lang, `${offer.id} ${size.id} hl-${window.HL_STYLE || HEADLINE_STYLE} pat-${window.PATTERN_OVERRIDE || PATTERN} n${products.length}`,
      `width:${size.w}px;height:${size.h}px;--from:${t.from};--to:${t.to};--accent:${t.accent};--glow:${t.glow || t.to};--text:${t.text}`);
  }
  if ((window.HERO_OVERRIDE ?? HERO) && offer.bigNum && size.id === "mobile-vertical-hero") {
    const t2 = offer.theme;
    return heroVerticalHTML(offer, size, lang, `${offer.id} ${size.id} pat-${window.PATTERN_OVERRIDE || PATTERN} n${products.length}`,
      `width:${size.w}px;height:${size.h}px;--from:${t2.from};--to:${t2.to};--accent:${t2.accent};--glow:${t2.glow || t2.to};--text:${t2.text}`);
  }
  return `
    <div class="banner ${offer.id} ${size.id} ${(window.STICKER_OVERRIDE ?? STICKER) ? "has-sticker" : ""} hl-${window.HL_STYLE || HEADLINE_STYLE} pat-${window.PATTERN_OVERRIDE || PATTERN} n${products.length}${products.length >= 5 ? " many" : ""}" dir="${lang === "ar" ? "rtl" : "ltr"}" lang="${lang}"
         data-file="${offer.id}/${size.device}-${lang}-${size.w}x${size.h}.png"
         style="width:${size.w}px;height:${size.h}px;--from:${t.from};--to:${t.to};--accent:${t.accent};--glow:${t.glow || t.to};--text:${t.text}">
      ${(window.STICKER_OVERRIDE ?? STICKER) ? stickerHTML(offer, lang) : ""}<div class="deco deco-1"></div><div class="deco deco-2"></div><div class="deco deco-3"></div>
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
