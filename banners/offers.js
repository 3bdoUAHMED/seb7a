// =====================================================================
//  بيانات العروض — عدّل هنا فقط
//  Offer data — this is the only file you need to edit
// =====================================================================
//
//  - كل عرض بيطلع منه 8 بنرات: (3 موبايل + 1 ديسكتوب) × (عربي + إنجليزي)
//  - Each offer produces 8 banners: (3 mobile + 1 desktop) × (EN + AR)
//
//  صور المنتجات: حط الصورة (PNG بخلفية شفافة أفضل) في فولدر banners/products
//  واكتب اسمها في image، مثال: image: "products/omega3.png"
//  لو image فاضية بيترسم شكل مؤقت (placeholder) مكان المنتج.
//
//  Product images: drop a PNG (transparent background works best) into
//  banners/products and set image: "products/<file>.png". Leave it empty
//  to draw a placeholder bottle.
//
//  ⚠️ النصوص والمنتجات اللي تحت دي أمثلة مؤقتة — غيّرها ببيانات عروضك.
//  ⚠️ The texts and products below are placeholders — replace them.
//  (Offer 1 = Up to 40% OFF is confirmed; offers 2 & 3 texts are still placeholders.)

const BRAND = {
  logo: "products/bioxcin-logo.png", // white logo for dark backgrounds — empty = text logo below
  name: { en: "", ar: "" }, // e.g. { en: "My Store", ar: "اسم المتجر" } — empty = no logo
};

// How the numbers in the headline look: "plain" | "tilt" | "tag" | "sticker"
const HEADLINE_STYLE = "plain";

// Background pattern: "blackfriday" | "studio" (plain + product pedestals) | "circles" | "waves" | "leaves" | "glow"
const PATTERN = "blackfriday";

// Show the round BLACK FRIDAY sticker (replaces the pill badge)
const STICKER = false;

// "Big number" hero concept: a giant 3D discount number with the products in front of it.
const HERO = false;

// "Arc" concept: products fanned out along a half circle with motion arcs behind them.
const ARC = false;

const OFFERS = [
  {
    id: "offer-1",
    theme: { from: "#0a0a0a", to: "#1a1a1a", accent: "#f2c94c", glow: "#d63447", text: "#ffffff" },
    stickerBadge: { en: "40%|OFF", ar: "40%|OFF" }, // round badge on the BLACK FRIDAY sticker ("|" = new line)
    bigNum: { pre: { en: "", ar: "" }, num: "", image: "", post: { en: "", ar: "" } }, // image = your 3D artwork (e.g. "products/40-3d.png"); empty = blank space
    badge: { en: "BLACK FRIDAY", ar: "بلاك فرايداي" },
    headline: { en: "Up to 40% OFF", ar: "خصم يصل إلى 40%" },
    sub: { en: "On Bioxcin hair care favourites", ar: "على منتجات بيوكسين للعناية بالشعر" },
    cta: { en: "Shop Now", ar: "تسوّق الآن" },
    code: { en: "", ar: "" },
    products: [
      { name: { en: "Eyelash & Eyebrow Serum", ar: "سيروم الرموش والحواجب" }, image: "products/bioxcin-eyelash-serum.png", scale: 0.8, price: "", oldPrice: "" },
      { name: { en: "Forte Herbal Shampoo", ar: "شامبو فورت العشبي" }, image: "products/bioxcin-forte-shampoo.png", scale: 1, price: "", oldPrice: "" },
      { name: { en: "Forte Herbal Serum", ar: "سيروم فورت العشبي" }, image: "products/bioxcin-forte-serum.png", scale: 0.86, price: "", oldPrice: "" },
      { name: { en: "Quantum Bio-Activ Serum", ar: "سيروم كوانتم بيو أكتيف" }, image: "products/bioxcin-quantum-serum.png", scale: 0.78, zoom: 1.35, price: "", oldPrice: "" },
    ],
 },
  {
    id: "offer-2",
    theme: { from: "#0a0a0a", to: "#1a1a1a", accent: "#f2c94c", glow: "#b23a55", text: "#ffffff" },
    stickerBadge: { en: "BUY 2|GET 2", ar: "BUY 2|GET 2" }, // round badge on the BLACK FRIDAY sticker ("|" = new line)
    badge: { en: "BLACK FRIDAY", ar: "بلاك فرايداي" },
    headline: { en: "Buy 2 Get 2", ar: "اشترِ 2 واحصل على 2" },
    sub: { en: "On Bioxcin hair care favourites", ar: "على منتجات بيوكسين للعناية بالشعر" },
    cta: { en: "Shop Now", ar: "تسوّق الآن" },
    code: { en: "", ar: "" },
    // Grouped: serum + the three 300ml shampoos (white, blue, red), then the two anti-dandruff
    // shampoos side by side, then eyelash serum + Quantum box. "scale" = height vs the tallest;
    // "zoom" enlarges a product beyond its slot (used for the wide Quantum box).
    products: [
      { name: { en: "Forte Herbal Serum", ar: "سيروم فورت العشبي" }, image: "products/bioxcin-forte-serum.png", scale: 0.72, price: "", oldPrice: "" },
      { name: { en: "Black Garlic Shampoo", ar: "شامبو الثوم الأسود" }, image: "products/bioxcin-black-garlic-shampoo.png", scale: 0.86, price: "", oldPrice: "" },
      { name: { en: "Quantum Bio-Activ Shampoo", ar: "شامبو كوانتم بيو أكتيف" }, image: "products/bioxcin-quantum-shampoo.png", scale: 0.86, price: "", oldPrice: "" },
      { name: { en: "Forte Herbal Shampoo", ar: "شامبو فورت العشبي" }, image: "products/bioxcin-forte-shampoo.png", scale: 0.86, price: "", oldPrice: "" },
      { name: { en: "Anti-Dandruff Thermal Shampoo", ar: "شامبو حراري ضد القشرة" }, image: "products/bioxcin-anti-dandruff-shampoo.png", scale: 1, price: "", oldPrice: "" },
      { name: { en: "Anti-Dandruff DS Shampoo", ar: "شامبو DS المكثف ضد القشرة" }, image: "products/bioxcin-anti-dandruff-ds-shampoo.png", scale: 0.8, price: "", oldPrice: "" },
      { name: { en: "Eyelash & Eyebrow Serum", ar: "سيروم الرموش والحواجب" }, image: "products/bioxcin-eyelash-serum.png", scale: 0.78, price: "", oldPrice: "" },
      { name: { en: "Quantum Bio-Activ Serum", ar: "سيروم كوانتم بيو أكتيف" }, image: "products/bioxcin-quantum-serum.png", scale: 0.62, zoom: 1.4, price: "", oldPrice: "" },
    ],
  },
  {
    id: "offer-3",
    theme: { from: "#0a0a0a", to: "#1a1a1a", accent: "#f2c94c", glow: "#2f5fd0", text: "#ffffff" },
    stickerBadge: { en: "50%|OFF", ar: "50%|OFF" }, // round badge on the BLACK FRIDAY sticker ("|" = new line)
    badge: { en: "BLACK FRIDAY", ar: "بلاك فرايداي" },
    headline: { en: "Buy 1 Get 50% OFF", ar: "اشترِ 1 واحصل على خصم 50%" },
    sub: { en: "", ar: "" },
    cta: { en: "Shop Now", ar: "تسوّق الآن" },
    code: { en: "", ar: "" },
    products: [
      { name: { en: "Forte Herbal Serum", ar: "سيروم فورت العشبي" }, image: "products/bioxcin-forte-serum.png", scale: 0.85, price: "", oldPrice: "" },
      { name: { en: "Quantum Bio-Activ Serum", ar: "سيروم كوانتم بيو أكتيف" }, image: "products/bioxcin-quantum-serum.png", scale: 0.62, zoom: 1.4, price: "", oldPrice: "" },
      { name: { en: "Eyelash & Eyebrow Serum", ar: "سيروم الرموش والحواجب" }, image: "products/bioxcin-eyelash-serum.png", scale: 0.95, price: "", oldPrice: "" },
    ],
  },
];

// Banner slots from the upload screen. maxProducts = max products shown (layouts handle 1-8).
const SIZES = [
  { id: "mobile-vertical-hero", device: "mobile", label: "Vertical Hero Banner", w: 800, h: 1200, maxProducts: 8 },
  { id: "mobile-hero", device: "mobile", label: "Hero Banner", w: 706, h: 320, maxProducts: 8 },
  { id: "mobile-slim", device: "mobile", label: "Slim Banner", w: 800, h: 200, maxProducts: 8 },
  { id: "desktop-hero", device: "desktop", label: "Hero Banner", w: 1440, h: 300, maxProducts: 8 },
];

const LANGS = ["en", "ar"];
