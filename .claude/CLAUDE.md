# Surprise Cake (עוגה בהפתעה) website — ugabehaftaha.com

- Hosting: Netlify, auto-deploys every push to `main`. Domain is registered at Wix; Wix DNS has A @ → 75.2.60.5 and CNAME www → papaya-biscuit-1eaa95.netlify.app. Do not touch MX/TXT records.
- Never edit the generated files (index.html, recipes/, assets/, sitemap.xml, robots.txt, _redirects) by hand.
- Edit `_build/index.src.html` (home page, Hebrew + English via `data-t` and the `T.en` dictionary) and `recipes.js` (recipe data; every recipe needs a unique `slug`). Put images in `img/`.
- Then run `python3 _build/build.py` (needs Python with Pillow, and Node), check the result, commit and push.
- Each recipe gets a page at /recipes/<slug>/ with Recipe structured data; the sitemap is regenerated automatically.
- Style: white and light, brown text and buttons (#5A3824), logo-blue accents, Heebo font. The owner dislikes kitsch, heavy colors and cartoon illustrations.
- Accessibility (Israeli standard 5568) is required: keep the skip link, the accessibility menu and the accessibility statement.
