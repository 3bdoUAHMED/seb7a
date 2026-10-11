# بنرات العروض · Offer Banners

بيطلّع لكل عرض ٨ بنرات (عربي + إنجليزي) بالمقاسات المطلوبة في شاشة الرفع:

| الجهاز | المقاس | النوع |
|---|---|---|
| Mobile | 800 x 1200 | Vertical Hero Banner |
| Mobile | 706 x 320 | Hero Banner |
| Mobile | 800 x 200 | Slim Banner |
| Desktop | 1440 x 300 | Hero Banner |

٣ عروض × ٤ مقاسات × لغتين = **٢٤ بنر** في فولدر `output/`.

## الخطوات

1. **صور المنتجات:** حط صور المنتجات في `products/` بنفس الأسماء المكتوبة في `offers.js`.
   لو الصور بخلفية بيضاء، شيل الخلفية وقصّها بالأمر ده:
   ```bash
   python3 prepare-products.py path/to/photos/*.jpg --out products
   ```
2. **النصوص والمنتجات:** عدّل `offers.js` (العنوان، الوصف، الزرار، الكود، الألوان، المنتجات والأسعار).
3. **المعاينة:** افتح `index.html` في المتصفح.
4. **التصدير PNG:**
   ```bash
   npm install
   npm run render
   ```
   الملفات بتطلع في `output/<offer-id>/<device>-<lang>-<W>x<H>.png`،
   مثال: `output/offer-1/mobile-ar-800x1200.png`.

لو صورة منتج مش موجودة بيترسم مكانها شكل مؤقت لحد ما تضيفها.
