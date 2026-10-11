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
  logo: "", // e.g. "products/logo.png" — empty = text logo below
  name: { en: "", ar: "" }, // e.g. { en: "My Store", ar: "اسم المتجر" } — empty = no logo
};

const OFFERS = [
  {
    id: "offer-1",
    theme: { from: "#7a1e2c", to: "#d63447", accent: "#ffe66d", text: "#ffffff" },
    badge: { en: "LIMITED TIME", ar: "لفترة محدودة" },
    headline: { en: "Up to 40% OFF", ar: "خصم يصل إلى 40%" },
    sub: { en: "On Bioxcin hair care favourites", ar: "على منتجات بيوكسين للعناية بالشعر" },
    cta: { en: "Shop Now", ar: "تسوّق الآن" },
    code: { en: "", ar: "" },
    products: [
      { name: { en: "Forte Herbal Shampoo", ar: "شامبو فورت العشبي" }, image: "products/bioxcin-forte-shampoo.png", price: "", oldPrice: "" },
      { name: { en: "Forte Herbal Serum", ar: "سيروم فورت العشبي" }, image: "products/bioxcin-forte-serum.png", price: "", oldPrice: "" },
      { name: { en: "Quantum Bio-Activ Serum", ar: "سيروم كوانتم بيو أكتيف" }, image: "products/bioxcin-quantum-serum.png", price: "", oldPrice: "" },
      { name: { en: "Eyelash & Eyebrow Serum", ar: "سيروم الرموش والحواجب" }, image: "products/bioxcin-eyelash-serum.png", price: "", oldPrice: "" },
    ],
 },
  {
    id: "offer-2",
    theme: { from: "#0a1a4f", to: "#1d4ed8", accent: "#ffd166", text: "#ffffff" },
    badge: { en: "LIMITED TIME", ar: "لفترة محدودة" },
    headline: { en: "Buy 2 Get 2", ar: "اشترِ 2 واحصل على 2" },
    sub: { en: "On Bioxcin hair care favourites", ar: "على منتجات بيوكسين للعناية بالشعر" },
    cta: { en: "Shop Now", ar: "تسوّق الآن" },
    code: { en: "", ar: "" },
    products: [
      { name: { en: "Quantum Bio-Activ Shampoo", ar: "شامبو كوانتم بيو أكتيف" }, image: "products/bioxcin-quantum-shampoo.png", price: "", oldPrice: "" },
      { name: { en: "Forte Herbal Shampoo", ar: "شامبو فورت العشبي" }, image: "products/bioxcin-forte-shampoo.png", price: "", oldPrice: "" },
      { name: { en: "Forte Herbal Serum", ar: "سيروم فورت العشبي" }, image: "products/bioxcin-forte-serum.png", price: "", oldPrice: "" },
      { name: { en: "Quantum Bio-Activ Serum", ar: "سيروم كوانتم بيو أكتيف" }, image: "products/bioxcin-quantum-serum.png", price: "", oldPrice: "" },
      { name: { en: "Eyelash & Eyebrow Serum", ar: "سيروم الرموش والحواجب" }, image: "products/bioxcin-eyelash-serum.png", price: "", oldPrice: "" },
      { name: { en: "Black Garlic Shampoo", ar: "شامبو الثوم الأسود" }, image: "products/bioxcin-black-garlic-shampoo.png", price: "", oldPrice: "" },
      { name: { en: "Anti-Dandruff Thermal Shampoo", ar: "شامبو حراري ضد القشرة" }, image: "products/bioxcin-anti-dandruff-shampoo.png", price: "", oldPrice: "" },
      { name: { en: "Intensive Anti-Dandruff DS Shampoo", ar: "شامبو DS المكثف ضد القشرة" }, image: "products/bioxcin-anti-dandruff-ds-shampoo.png", price: "", oldPrice: "" },
    ],
  },
  {
    id: "offer-3",
    theme: { from: "#0f5132", to: "#198754", accent: "#ffc107", text: "#ffffff" },
    badge: { en: "BUNDLE & SAVE", ar: "باقات التوفير" },
    headline: { en: "Bundle Up & Save More", ar: "وفّر أكثر مع باقاتنا" },
    sub: { en: "Special bundle prices on top picks", ar: "أسعار حصرية على باقات مختارة" },
    cta: { en: "Shop Now", ar: "تسوّق الآن" },
    code: { en: "", ar: "" },
    products: [
      { name: { en: "Product 1", ar: "منتج 1" }, image: "", price: "", oldPrice: "" },
      { name: { en: "Product 2", ar: "منتج 2" }, image: "", price: "", oldPrice: "" },
      { name: { en: "Product 3", ar: "منتج 3" }, image: "", price: "", oldPrice: "" },
      { name: { en: "Product 4", ar: "منتج 4" }, image: "", price: "", oldPrice: "" },
    ],
  },
];

// Banner slots from the upload screen. maxProducts = how many products fit.
const SIZES = [
  { id: "mobile-vertical-hero", device: "mobile", label: "Vertical Hero Banner", w: 800, h: 1200, maxProducts: 8 },
  { id: "mobile-hero", device: "mobile", label: "Hero Banner", w: 706, h: 320, maxProducts: 3 },
  { id: "mobile-slim", device: "mobile", label: "Slim Banner", w: 800, h: 200, maxProducts: 3 },
  { id: "desktop-hero", device: "desktop", label: "Hero Banner", w: 1440, h: 300, maxProducts: 6 },
];

const LANGS = ["en", "ar"];
