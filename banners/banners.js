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
  const [w1, w2] = offer.sticker ?? ["BLACK", "FRIDAY"];
  const yellow = w1 === "YELLOW";
  const c1 = yellow ? "#f5c518" : "#d42a2a", c2 = yellow ? "#111" : "#d42a2a";
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
          <path d="M28 168 l14 26 29 4 -21 20 5 29 -27 -14 -26 14 5 -29 -21 -20 29 -4z" fill="${c1}"/>
          <path d="M100 70 H370 L346 112 L370 154 H100 Z" fill="${c1}"/>
          <text x="220" y="128" text-anchor="middle" font-family="Poppins, sans-serif" font-weight="600" font-size="56" fill="#111" ${w1.length > 5 ? `textLength="220" lengthAdjust="spacingAndGlyphs"` : ""}>${w1}</text>
          <path d="M120 146 q 18 -16 36 0 t 36 0 t 36 0 t 36 0 t 36 0 t 36 0" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round"/>
          <path d="M80 160 H330 Q340 200 332 240 H86 Q92 220 76 204 Q92 186 80 160 Z" fill="#fff"/>
          <text x="208" y="222" text-anchor="middle" font-family="Poppins, sans-serif" font-weight="600" font-size="54" fill="${c2}" ${w2.length > 6 ? `textLength="228" lengthAdjust="spacingAndGlyphs"` : ""}>${w2}</text>
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
      <div class="arc-item" style="left:${xc.toFixed(1)}px;top:${y.toFixed(1)}px;height:${h.toFixed(0)}px;transform:translate(-50%,-100%) rotate(${(a * 0.5).toFixed(1)}deg)">
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

// Geometry of the arc stage per banner size (LTR coordinates; mirrored for RTL).
const ARC_STAGE = {
  "mobile-vertical-hero": { x: 30, w: 740, top: 720, base: 340, maxA: 30, slot: { y: 770, h: 210, w: 620 } },
  "desktop-hero": { x: 560, w: 700, top: 206, base: 175, maxA: 16, slot: { y: 210, h: 84, w: 330 } },
  "mobile-hero": { x: 300, w: 400, top: 222, base: 175, maxA: 24, slot: { y: 226, h: 88, w: 260 } },
  "mobile-slim": { x: 330, w: 400, top: 136, base: 118, maxA: 20, slot: { y: 140, h: 56, w: 220 } },
};

function decoHTML(size, lang, rtl) {
  // red curly ribbons (confetti) + a SALE ribbon
  const curl = (x, y, r, sc) =>
    `<path transform="translate(${x} ${y}) rotate(${r}) scale(${sc})" d="M0 0 C 20 -30 50 -30 60 0 S 100 30 120 0" fill="none" stroke="#d42a2a" stroke-width="14" stroke-linecap="round"/>`;
  const bits = {
    "mobile-vertical-hero": [curl(90, 920, 20, 0.6), curl(620, 1000, -30, 0.55), curl(30, 1130, 10, 0.5), curl(690, 1150, -60, 0.45), curl(700, 300, 40, 0.35)],
    "desktop-hero": [curl(540, 40, 30, 0.3), curl(1250, 270, -20, 0.3)],
    "mobile-hero": [curl(300, 20, 20, 0.25), curl(660, 290, -30, 0.25)],
    "mobile-slim": [curl(720, 170, -20, 0.2)],
  }[size.id] ?? [];
  const sale = size.id === "mobile-vertical-hero" ? `
    <g transform="translate(600 380) rotate(-14)">
      <path d="M0 0 H200 L180 34 L200 68 H0 Z" fill="#d42a2a"/>
      <path d="M0 68 L-26 92 L0 92 Z" fill="#7a0f0f"/>
      <text x="96" y="47" text-anchor="middle" font-family="${lang === "ar" ? "Cairo" : "Anton"}, sans-serif" font-weight="900" font-size="38" fill="#fff">${lang === "ar" ? "تخفيضات" : "SALE"}</text>
    </g>` : "";
  return `<svg class="arc-deco" viewBox="0 0 ${size.w} ${size.h}" width="${size.w}" height="${size.h}" ${rtl ? `style="transform:scaleX(-1)"` : ""}>${bits.join("")}</svg>
    ${sale ? `<svg class="arc-deco" viewBox="0 0 ${size.w} ${size.h}" width="${size.w}" height="${size.h}">${sale}</svg>` : ""}`;
}

function arcStageHTML(offer, size, lang) {
  const g = ARC_STAGE[size.id];
  const rtl = lang === "ar";
  const products = offer.products.slice(0, size.maxProducts);
  const n = products.length;
  const x0 = rtl ? size.w - g.x - g.w : g.x;
  const cx = x0 + g.w / 2;
  const half = g.w * 0.4;
  const R = half / Math.sin((g.maxA * Math.PI) / 180);
  const cy = g.top + R;
  const id = `${offer.id}-${size.id}-${lang}`;
  // Size each product, then lay them side by side along the arc so none overlap
  // and all stay inside the stage. Shrink everything if they don't fit.
  const sizes = products.map((p, i) => {
    const t = n === 1 ? 0 : -1 + (2 * i) / (n - 1);
    const h = g.base * (1 - 0.3 * Math.abs(t)) * (p.scale ?? 1);
    const w = Math.max(h * 0.7, (g.w * 0.8 / n) * 1.1) * (p.zoom ?? 1);
    return { p, h, w };
  });
  const gap = g.w * 0.02;
  const avail = g.w * 0.96;
  let total = sizes.reduce((sum, it) => sum + it.w, 0) + gap * (n - 1);
  const k2 = Math.min(1, avail / total);
  sizes.forEach((it) => { it.w *= k2; it.h *= k2; });
  total = total * k2;
  let cursor = cx - total / 2;
  const items = sizes.map(({ p, h, w }) => {
    const x = cursor + w / 2;
    cursor += w + gap * k2;
    const a = (Math.asin(Math.max(-1, Math.min(1, (x - cx) / R))) * 180) / Math.PI;
    const y = cy - Math.sqrt(Math.max(0, R * R - (x - cx) ** 2));
    return `<div class="arc-item" style="left:${x.toFixed(1)}px;top:${(y + 4).toFixed(1)}px;height:${h.toFixed(0)}px;width:${w.toFixed(0)}px;transform:translate(-50%,-100%) rotate(${(a * 0.5).toFixed(1)}deg)">
        ${p.image ? `<img src="${esc(p.image)}" alt="">` : ""}</div>`;
  }).join("");
  const arc = (r, w, op, dash) =>
    `<path d="M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}" fill="none" stroke="url(#arcg-${id})" stroke-width="${w}" stroke-opacity="${op}" stroke-linecap="round" ${dash ? `stroke-dasharray="${dash}"` : ""}/>`;
  const k = g.base / 340; // scale line spacing to banner size
  const slot = offer.bigNum?.image
    ? `<img class="arc-slot" src="${esc(offer.bigNum.image)}" style="left:${cx - g.slot.w / 2}px;top:${g.slot.y}px;width:${g.slot.w}px;height:${g.slot.h}px" alt="">`
    : `<div class="arc-slot" style="left:${cx - g.slot.w / 2}px;top:${g.slot.y}px;width:${g.slot.w}px;height:${g.slot.h}px"></div>`;
  return `
    <svg class="arc-lines" viewBox="0 0 ${size.w} ${size.h}" width="${size.w}" height="${size.h}">
      <defs>
        <linearGradient id="arcg-${id}" x1="0" x2="1">
          <stop offset="0" stop-color="#f2c94c" stop-opacity="0"/><stop offset=".5" stop-color="#f2c94c"/><stop offset="1" stop-color="#f2c94c" stop-opacity="0"/>
        </linearGradient>
        <radialGradient id="dome-${id}" cx="50%" cy="0%" r="90%">
          <stop offset="0" stop-color="${offer.theme.glow}" stop-opacity=".6"/><stop offset=".6" stop-color="#0a0a0a" stop-opacity=".2"/><stop offset="1" stop-color="#0a0a0a" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <path d="M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy} Z" fill="url(#dome-${id})"/>
      ${arc(R, Math.max(2, 4 * k), 0.9)}
      ${arc(R + 40 * k, Math.max(1, 2 * k), 0.55, `${160 * k} ${40 * k} ${60 * k} ${40 * k}`)}
      ${arc(R + 80 * k, 1.2, 0.35, `${60 * k} ${30 * k}`)}
      ${arc(R - 46 * k, Math.max(1, 2 * k), 0.4, `${220 * k} ${60 * k}`)}
    </svg>
    ${decoHTML(size, lang, rtl)}
    ${items}
    ${slot}`;
}

function arcBannerHTML(offer, size, lang, cls, style) {
  const rtl = lang === "ar";
  const cta = `<span class="cta">${txt(offer.cta[lang])}<span class="arrow">${rtl ? "←" : "→"}</span></span>`;
  const vertical = size.id === "mobile-vertical-hero";
  const sticker = vertical || size.id === "desktop-hero";
  return `
    <div class="banner arcb ${cls} ${sticker ? "has-sticker" : ""}" dir="${rtl ? "rtl" : "ltr"}" lang="${lang}"
         data-file="${offer.id}/${size.device}-${lang}-${size.w}x${size.h}.png" style="${style}">
      ${sticker ? stickerHTML({ ...offer, stickerBadge: null }, lang) : ""}
      ${arcStageHTML(offer, size, lang)}
      ${vertical ? `
        <div class="arc-top">
          ${logoHTML(lang)}
          <h2 class="headline">${txt(offer.headline[lang], "hl-num")}</h2>
          ${offer.sub[lang] ? `<p class="sub">${txt(offer.sub[lang])}</p>` : ""}
        </div>
        <div class="arc-cta">${cta}</div>` : `
        <div class="copy">
          ${logoHTML(lang)}
          <div class="badge">${txt(offer.badge[lang])}</div>
          <h2 class="headline">${txt(offer.headline[lang], "hl-num")}</h2>
          ${offer.sub[lang] ? `<p class="sub">${txt(offer.sub[lang])}</p>` : ""}
          <div class="actions">${cta}</div>
        </div>`}
    </div>`;
}

// 3D word: white face (or red) with a stacked extrusion.
function word3d(t, cls) {
  return `<span class="w3d ${cls}" data-t="${esc(t)}">${esc(t)}</span>`;
}

// Offer-3 wide banners: scale/offset of the original photo inside each banner (see make-wide-bg.py).
const STUDIO_GEO = {
  "mobile-slim": { k: 1, ox: 0, oy: 0 },
  "desktop-hero": { k: 1.5, ox: 240, oy: 0 },
  "mobile-hero": { k: 1.25, ox: 0, oy: 70, logo: true },
  "mobile-vertical-hero": { k: 1, ox: 0, oy: 0, noProducts: true },
};

// "Scene" layout: photo wall, stone ledge, products standing on it, 3D "50% OFF".
function sceneBannerHTML(offer, size, lang, style) {
  const rtl = lang === "ar";
  const big = `
    <div class="sc-big" dir="ltr">
      <i class="sc-line red"></i>
      ${rtl ? `<span class="ar-lock">${word3d(offer.big.word.ar, "red ar")}${word3d(offer.big.num, "white")}</span>`
            : `${word3d(offer.big.num, "white")}${word3d(offer.big.word.en, "red")}`}
      <i class="sc-line white"></i>
    </div>`;
  if (offer.studio && STUDIO_GEO[size.id]) {
    const g = STUDIO_GEO[size.id];
    // product spots in the original 800x200 photo: [centre x, bottom y, height]
    const spots = [[288, 188, 176], [418, 184, 134], [536, 186, 164]];
    const prods = g.noProducts ? "" : offer.products.map((p, i) => {
      const [cx, by, h] = spots[i];
      return `<img class="st-abs" src="${esc(p.image)}" alt=""
        style="left:${g.ox + cx * g.k}px;top:${g.oy + by * g.k}px;height:${h * g.k}px">`;
    }).join("");
    return `
    <div class="banner scene studio ${offer.id} ${size.id}" dir="${rtl ? "rtl" : "ltr"}" lang="${lang}"
         data-file="${offer.id}/${size.device}-${lang}-${size.w}x${size.h}.png"
         style="${style};background:url('products/offer3-bg-${size.w}x${size.h}.jpg') 0 0/100% 100%">
      ${prods}
      ${g.logo ? `<img class="st-logo" src="products/bioxcin-logo-red.png" alt="BIOXCIN">` : ""}
      ${stickerHTML({ ...offer, stickerBadge: null }, lang)}
      <div class="ph-copy">
        ${big}
        <span class="st-cta">${txt(offer.cta[lang])}
          <svg viewBox="0 0 24 24"><path d="${rtl ? "M15 6l-6 6 6 6" : "M9 6l6 6-6 6"}" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
      </div>
    </div>`;
  }
  const prods = offer.products.map((p) =>
    `<img class="sc-p" style="--h:${p.h}" src="${esc(p.image)}" alt="">`).join("");
  return `
    <div class="banner scene ${offer.id} ${size.id}" dir="${rtl ? "rtl" : "ltr"}" lang="${lang}"
         data-file="${offer.id}/${size.device}-${lang}-${size.w}x${size.h}.png" style="${style}">
      <div class="sc-wall"></div>
      <div class="sc-ledge"><div class="sc-top"></div><div class="sc-face"></div><div class="sc-floor"></div></div>
      <div class="sc-products">${prods}</div>
      ${stickerHTML({ ...offer, stickerBadge: null }, lang)}
      <div class="sc-copy">
        ${logoHTML(lang)}
        ${big}
        <span class="cta">${txt(offer.cta[lang])}<span class="arrow">${rtl ? "←" : "→"}</span></span>
      </div>
    </div>`;
}

// Offer 2 "podium" layout: podium photo + burgundy BUY 2 GET 2 FREE lockup.
function b2g2Lockup(lang) {
  if (lang === "en") return `<img class="pd-type" src="products/offer2-type-en.png" alt="Buy 2 Get 2 Free">`;
  return `
    <div class="pd-type ar" dir="rtl">
      <span class="q">”</span>
      <div class="ar-l1">اشترِ <b>2</b></div>
      <div class="ar-l2">واحصل على <b>2</b></div>
      <div class="ar-free">مجاناً</div>
      <span class="q end">“</span>
    </div>`;
}

function podiumBannerHTML(offer, size, lang, style) {
  const rtl = lang === "ar";
  const vertical = size.id === "mobile-vertical-hero";
  const cta = `<span class="st-cta">${txt(offer.cta[lang])}
          <svg viewBox="0 0 24 24"><path d="${rtl ? "M15 6l-6 6 6 6" : "M9 6l6 6-6 6"}" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>`;
  const sticker = stickerHTML({ ...offer, stickerBadge: null }, lang);
  if (vertical) {
    return `
    <div class="banner podium ${offer.id} ${size.id}" dir="${rtl ? "rtl" : "ltr"}" lang="${lang}"
         data-file="${offer.id}/${size.device}-${lang}-${size.w}x${size.h}.png"
         style="${style};background:url('products/offer2-podium.jpg') 0 0/100% 100%">
      <img class="pd-logo" src="products/bioxcin-logo-red.png" alt="BIOXCIN">
      ${sticker}
      <div class="pd-copy">${b2g2Lockup(lang)}${cta}</div>
    </div>`;
  }
  // wide: logo in the top corner, lockup (+ sticker on its corner) centred on the text side, no button
  return `
    <div class="banner podium pd3 ${offer.id} ${size.id}" dir="${rtl ? "rtl" : "ltr"}" lang="${lang}"
         data-file="${offer.id}/${size.device}-${lang}-${size.w}x${size.h}.png"
         style="${style};background:url('products/offer2-bg-${size.w}x${size.h}-${lang}.jpg') 0 0/100% 100%">
      <img class="pd3-logo" src="products/bioxcin-logo-red.png" alt="BIOXCIN">
      <div class="pd3-text"><div class="pd3-type">${b2g2Lockup(lang)}${sticker}</div></div>
    </div>`;
}

function bannerHTML(offer, size, lang) {
  const t = offer.theme;
  const products = offer.products.slice(0, size.maxProducts);
  const showNames = size.id === "mobile-vertical-hero" || size.id === "desktop-hero";
  const code = offer.code?.[lang];
  if (offer.layout === "podium") {
    return podiumBannerHTML(offer, size, lang, `width:${size.w}px;height:${size.h}px`);
  }
  if (offer.layout === "scene") {
    return sceneBannerHTML(offer, size, lang, `width:${size.w}px;height:${size.h}px;--accent:${t.accent}`);
  }
  if (offer.layout === "arc" && ARC_STAGE[size.id]) {
    return arcBannerHTML(offer, size, lang, `${offer.id} ${size.id} hl-${window.HL_STYLE || HEADLINE_STYLE} pat-${window.PATTERN_OVERRIDE || PATTERN} n${products.length}`,
      `width:${size.w}px;height:${size.h}px;--from:${t.from};--to:${t.to};--accent:${t.accent};--glow:${t.glow || t.to};--text:${t.text}`);
  }
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
