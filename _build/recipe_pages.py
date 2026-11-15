"""Generate a static page per recipe + a recipes index, for Google and for sharing."""
import json, os, subprocess, html
from PIL import Image

URL = 'https://ugabehaftaha.com/'
SIZES = {}
GROUPS = [
    ('keren', 'המתכונים של קרן אגם', 'מתכונים שקרן אגם תרמה לעמותה, רובם ללא סוכר.'),
    ('grandma', 'המתכונים שלכם', 'הקשישות והקשישים שאנחנו מבקרים שיתפו את העוגות שליוו אותם כל החיים.'),
    ('volunteer', 'עוגות שעושים בקלי קלות', 'העוגות שהמתנדבים שלנו הכי אוהבים להביא לביקור. פשוטות, מהירות ובטוח יצליחו.'),
    ('memory', 'אופים לזכרם', 'ספר המתכונים מוקדש לזכרה של אלקה ריינס אברמוביץ ז״ל. כאן אופים גם לזכרם של מי שנפלו.'),
]
GROUPS_EN = [
    ('keren', 'Keren Agam’s recipes', 'Recipes that Keren Agam donated to Surprise Cake, most of them sugar-free.'),
    ('grandma', 'Your recipes', 'The seniors we visit shared the cakes that have been with them all their lives.'),
    ('volunteer', 'Cakes that are a piece of cake', 'The cakes our volunteers love to bring on a visit. Simple, quick and sure to work.'),
    ('memory', 'Baking in their memory', 'This recipe book is dedicated to the memory of Elka Reines Abramovitz. Here we also bake in memory of the fallen.'),
]
GNAME = {g: n for g, n, _ in GROUPS}
GNAME_EN = {g: n for g, n, _ in GROUPS_EN}
ORG = {'he': 'עוגה בהפתעה', 'en': 'Surprise Cake'}

S = {
 'he': dict(dir='rtl', locale='he_IL', pre='', home='/', how='/#how', skip='דלג לתוכן הראשי', nav='ניווט', book='ספר המתכונים',
            volunteer='אני רוצה להתנדב', crumbs='פירורי לחם', sugar='ללא סוכר', ing='מצרכים', steps='אופן ההכנה', storyh='הסיפור שמאחורי המתכון',
            share='שיתוף בוואטסאפ', copy='העתקת קישור', copied='הקישור הועתק', about='על העמותה', more='עוד מ',
            cta_h='רוצים להביא עוגה כזאת לקשיש בחג?',
            cta_p='בעוגה בהפתעה מתנדבים אופים עוגה בבית ומגיעים לביקור אצל קשישים וניצולי שואה, בראש השנה, חנוכה, פורים ושבועות, ב־14 ערים ברחבי הארץ.',
            video_p='קרן הכינה את המתכון הזה בסרטון.', video_b='לצפייה במתכון באינסטגרם', full_b='למתכון המלא אצל קרן',
            tagline='מפיגים את הבדידות של קשישים וניצולי שואה, באמצעות עוגות.', a11y='הצהרת נגישות', a11y_href='/?a11y=1',
            switch='English', step='שלב', wa_suffix='מתכון מספר המתכונים של עוגה בהפתעה', site_title='ספר המתכונים של עוגה בהפתעה'),
 'en': dict(dir='ltr', locale='en_US', pre='en/', home='/?lang=en', how='/?lang=en#how', skip='Skip to main content', nav='Navigation', book='Recipe book',
            volunteer='I want to volunteer', crumbs='Breadcrumbs', sugar='Sugar-free', ing='Ingredients', steps='Instructions', storyh='The story behind the recipe',
            share='Share on WhatsApp', copy='Copy link', copied='Link copied', about='About us', more='More from ',
            cta_h='Want to bring a cake like this to a senior for the holidays?',
            cta_p='At Surprise Cake, volunteers bake a cake at home and visit seniors and Holocaust survivors on Rosh Hashanah, Hanukkah, Purim and Shavuot, in 14 cities across Israel.',
            video_p='Keren made this recipe in a video.', video_b='Watch the recipe on Instagram', full_b='See Keren’s full recipe',
            tagline='Easing the loneliness of seniors and Holocaust survivors, one cake at a time.', a11y='Accessibility statement', a11y_href='/?lang=en&a11y=1',
            switch='עברית', step='Step', wa_suffix='a recipe from the Surprise Cake recipe book', site_title='The Surprise Cake recipe book'),
}


def rurl(lang, slug=''):
    return f"{URL}{S[lang]['pre']}recipes/{slug + '/' if slug else ''}"


def rpath(lang, slug=''):
    return f"/{S[lang]['pre']}recipes/{slug + '/' if slug else ''}"

e = lambda s: html.escape(str(s or ''), quote=True)


def load(site):
    js = "global.window={};require(process.argv[1]);process.stdout.write(JSON.stringify(window.RECIPES))"
    return json.loads(subprocess.check_output(['node', '-e', js, os.path.abspath(f'{site}/recipes.js')]))


def by_line(r, lang='he'):
    d = r[lang]
    if lang == 'en':
        if r['group'] == 'volunteer':
            return f"Recipe by {d['by']}"
        if r['group'] == 'keren':
            return 'A recipe by Keren Agam'
        if r['group'] == 'memory':
            return d['by']
        return '' if d['by'] in d['title'] else d['by']
    if r['group'] == 'volunteer':
        return f"המתכון של {d['by']}"
    if r['group'] == 'keren':
        return 'מתכון של קרן אגם'
    if r['group'] == 'memory':
        return d['by']
    return '' if d['by'] in d['title'] else d['by']


def full_title(r, lang='he'):
    d = r[lang]
    if lang == 'en':
        if r['group'] == 'volunteer':
            return f"{d['title']} – recipe by {d['by']}"
        if r['group'] == 'keren':
            return f"{d['title']} – a recipe by Keren Agam"
        if r['group'] == 'memory':
            return f"{d['title']} – {d['by']}"
        return d['title']
    if r['group'] == 'volunteer':
        return f"{d['title']} – המתכון של {d['by']}"
    if r['group'] == 'keren':
        return f"{d['title']} – מתכון של קרן אגם"
    if r['group'] == 'memory':
        return f"{d['title']} {d['by']}"
    return d['title']


def describe(r, lang='he'):
    d = r[lang]
    base = d.get('intro') or ''
    if not base and lang == 'en':
        kind = 'sugar-free ' if r.get('sugarFree') and r['group'] != 'memory' else ''
        base = f"A {kind}recipe for {d['title']} from the Surprise Cake recipe book"
        if r['group'] == 'volunteer':
            base += f", shared by {d['by']}, one of our volunteers"
        if r['group'] == 'memory':
            base += f", {d['by'][0].lower() + d['by'][1:]}"
        base += '.'
        if d.get('ing'):
            base += ' Ingredients: ' + ', '.join(i.split('(')[0].strip() for i in d['ing'][:4]) + '.'
    if not base:
        kind = 'ללא סוכר, ' if r.get('sugarFree') and r['group'] != 'memory' else ''
        base = f"מתכון {kind}ל{d['title']} מתוך ספר המתכונים של עוגה בהפתעה"
        if r['group'] == 'volunteer':
            base += f", באדיבות {d['by']}, מתנדבת בעמותה"
        if r['group'] == 'memory':
            base += f", {d['by']}"
        base += '.'
        if d.get('ing'):
            base += ' מצרכים: ' + ', '.join(i.split('(')[0].strip() for i in d['ing'][:4]) + '.'
    return base[:300]


def default_image(out):
    os.makedirs(f'{out}/img/og', exist_ok=True)
    dst = f'{out}/img/og/recipe-default.jpg'
    if not os.path.exists(dst):
        W, H = 1200, 1200
        bg = Image.new('RGB', (W, H), (251, 252, 254))
        from PIL import ImageDraw
        dr = ImageDraw.Draw(bg)
        for i in range(H):
            t = i / H
            dr.line([(0, i), (W, i)], fill=(int(234 + 17 * t), int(245 + 7 * t), int(253 + 1 * t)))
        logo = Image.open(f'{out}/img/logo.webp').convert('RGBA')
        logo.thumbnail((620, 620))
        bg.paste(logo, ((W - logo.width) // 2, (H - logo.height) // 2), logo)
        bg.save(dst, quality=88)
    return URL + 'img/og/recipe-default.jpg'


def og_image(site, out, r):
    if not r.get('img'):
        return default_image(out)
    os.makedirs(f'{out}/img/og', exist_ok=True)
    dst = f"img/og/{r['slug']}.jpg"
    im = Image.open(f"{site}/{r['img']}").convert('RGB')
    W, H = 1200, 630
    sc = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    x = (im.width - W) // 2
    y = int((im.height - H) * 0.5)
    im.crop((x, y, x + W, y + H)).save(f'{out}/{dst}', quality=84)
    return URL + dst


def head(lang, title, desc, url, ogtype, ogtitle, image, ld, alt_url=None):
    t = S[lang]
    other = 'en' if lang == 'he' else 'he'
    alts = ''
    if alt_url:
        he_u, en_u = (url, alt_url) if lang == 'he' else (alt_url, url)
        alts = (f'<link rel="alternate" hreflang="he" href="{he_u}">\n<link rel="alternate" hreflang="en" href="{en_u}">\n'
                f'<link rel="alternate" hreflang="x-default" href="{he_u}">\n')
    switch = f'<a class="nl" href="{alt_url.replace(URL, "/")}" lang="{other}">{t["switch"]}</a>' if alt_url else ''
    return f"""<!doctype html>
<html lang="{lang}" dir="{t['dir']}" translate="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google" content="notranslate">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
{alts}<link rel="icon" href="/img/logo.webp" type="image/webp">
<meta name="theme-color" content="#5A3824">
<meta property="og:type" content="{ogtype}">
<meta property="og:locale" content="{t['locale']}">
<meta property="og:site_name" content="{ORG[lang]}">
<meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{image}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;800;900&display=swap">
<link rel="stylesheet" href="/assets/recipe.css">
{ld}
</head>
<body>
<a class="skip" href="#main">{t['skip']}</a>
<header class="top"><div class="wrap">
  <a class="brand" href="{t['home']}"><img src="/img/logo.webp" alt="" width="40" height="40"><span>{ORG[lang]}</span></a>
  <nav aria-label="{t['nav']}">
    <a class="nl" href="{rpath(lang)}">{t['book']}</a>
    {switch}
    <a class="btn" href="{t['how']}">{t['volunteer']}</a>
  </nav>
</div></header>
<main id="main" tabindex="-1">
"""


def foot(lang):
    t = S[lang]
    return f"""</main>
<footer><div class="wrap">
  <a class="brand" href="{t['home']}"><img src="/img/logo.webp" alt="" width="40" height="40"><span>{ORG[lang]}</span></a>
  <p>{t['tagline']} <a href="mailto:ugabehaftaha@gmail.com">ugabehaftaha@gmail.com</a></p>
  <p class="small"><a href="{t['a11y_href']}">{t['a11y']}</a></p>
</div></footer>
</body>
</html>
"""


def card(r, lang='he'):
    d = r[lang]
    ph = (f'<img src="/{e(r["img"])}" alt="{e(d["title"])}" loading="lazy" style="object-position:{e(r.get("pos") or "center 50%")}">'
          if r.get('img') else '<span class="noimg" aria-hidden="true"></span>')
    b = by_line(r, lang)
    tag = f'<span class="tag">{S[lang]["sugar"]}</span>' if r.get('sugarFree') and r['group'] != 'keren' else ''
    return (f'<a class="rcard" href="{rpath(lang, r["slug"])}"><span class="ph">{ph}{tag}</span>'
            f'<span class="body"><strong>{e(d["title"])}</strong>{f"<span>{e(b)}</span>" if b else ""}</span></a>')


def recipe_ld(r, image, url, desc, lang='he'):
    d = r[lang]
    t = S[lang]
    gname = (GNAME if lang == 'he' else GNAME_EN)[r['group']]
    if r['group'] == 'memory':
        author = {'@type': 'Organization', 'name': ORG[lang]}
    elif r['group'] == 'keren':
        author = {'@type': 'Person', 'name': 'קרן אגם' if lang == 'he' else 'Keren Agam'}
    else:
        author = {'@type': 'Person', 'name': d['by']}
    ld = {
        '@context': 'https://schema.org', '@type': 'Recipe', 'name': d['title'], 'description': desc,
        'image': [image], 'author': author, 'inLanguage': lang, 'url': url,
        'publisher': {'@type': 'Organization', 'name': ORG[lang], 'url': URL, 'logo': URL + 'img/logo.webp'},
        'recipeCategory': 'קינוח' if lang == 'he' else 'Dessert', 'recipeCuisine': 'ישראלית' if lang == 'he' else 'Israeli',
        'keywords': ', '.join(filter(None, [d['title'], t['sugar'] if r.get('sugarFree') else '', ORG[lang],
                                            'מתכון ביתי' if lang == 'he' else 'homemade cake', gname])),
        'recipeIngredient': d['ing'],
        'recipeInstructions': [{'@type': 'HowToStep', 'name': f"{t['step']} {i + 1}", 'text': st, 'url': f'{url}#step-{i + 1}'}
                               for i, st in enumerate(d['steps'])],
    }
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': ORG[lang], 'item': URL if lang == 'he' else URL + '?lang=en'},
        {'@type': 'ListItem', 'position': 2, 'name': t['book'], 'item': rurl(lang)},
        {'@type': 'ListItem', 'position': 3, 'name': d['title'], 'item': url}]}
    return ld, crumbs


def page(r, all_r, image, lang='he'):
    from urllib.parse import quote
    d = r[lang]
    t = S[lang]
    other = 'en' if lang == 'he' else 'he'
    gname = (GNAME if lang == 'he' else GNAME_EN)[r['group']]
    url = rurl(lang, r['slug'])
    desc = describe(r, lang)
    title = f"{full_title(r, lang)} | {t['site_title']}"
    lds = list(recipe_ld(r, image, url, desc, lang)) if d.get('ing') else []
    ldtxt = '\n'.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    out = head(lang, e(title), e(desc), url, 'article', e(full_title(r, lang)), image, ldtxt, alt_url=rurl(other, r['slug']))
    b = by_line(r, lang)
    mem = r['group'] == 'memory'
    out += f"""<article class="wrap recipe{' memory' if mem else ''}">
  <nav class="crumbs" aria-label="{t['crumbs']}"><a href="{t['home']}">{ORG[lang]}</a> <span aria-hidden="true">›</span> <a href="{rpath(lang)}">{t['book']}</a> <span aria-hidden="true">›</span> <a href="{rpath(lang)}#{r['group']}">{e(gname)}</a></nav>
  <header class="rhead">
    <h1>{e(d['title'])}</h1>
    {f'<p class="by">{e(b)}</p>' if b else ''}
    {f'<p class="tag">{t["sugar"]}</p>' if r.get('sugarFree') and not mem else ''}
    {f'<p class="credit">{e(d.get("credit"))}</p>' if d.get('credit') else ''}
  </header>
"""
    if r.get('img') and not mem:
        w, h = SIZES.get(r['img'], (1200, 900))
        out += f'  <figure class="hero"><img src="/{e(r["img"])}" alt="{e(d["title"])}" width="{w}" height="{h}" fetchpriority="high"></figure>\n'
    if mem and d.get('story'):
        out += f'  <div class="storybox memorybox"><p>{e(d["story"])}</p></div>\n'
    if d.get('intro'):
        out += f'  <p class="intro">{e(d["intro"])}</p>\n'
    if d.get('video') and r.get('link'):
        out += f'  <p>{t["video_p"]}</p><p><a class="btn" href="{e(r["link"])}" target="_blank" rel="noopener">{t["video_b"]}</a></p>\n'
    if d.get('ing'):
        out += f'  <div class="cols">\n    <section><h2>{t["ing"]}</h2><ul>' + ''.join(f'<li>{e(i)}</li>' for i in d['ing']) + '</ul></section>\n'
        out += (f'    <section><h2>{t["steps"]}</h2><ol>' + ''.join(f'<li id="step-{i + 1}">{e(st)}</li>' for i, st in enumerate(d['steps']))
                + '</ol></section>\n  </div>\n')
    if d.get('note'):
        out += f'  <p class="note">{e(d["note"])}</p>\n'
    if r.get('link') and not d.get('video'):
        out += f'  <p><a class="btn ghost" href="{e(r["link"])}" target="_blank" rel="noopener">{t["full_b"]}</a></p>\n'
    if r.get('img2'):
        out += f'  <img class="img2" src="/{e(r["img2"])}" alt="" loading="lazy">\n'
    if d.get('story') and not mem:
        out += f'  <div class="storybox"><h2>{t["storyh"]}</h2><p>{e(d["story"])}</p></div>\n'
    wa = 'https://wa.me/?text=' + quote(f"{full_title(r, lang)} – {t['wa_suffix']}\n{url}")
    out += f"""  <div class="share"><a class="btn ghost" href="{wa}" target="_blank" rel="noopener">{t['share']}</a><button class="btn ghost" type="button" data-copy="{url}">{t['copy']}</button></div>
  <aside class="cta">
    <h2>{t['cta_h']}</h2>
    <p>{t['cta_p']}</p>
    <p><a class="btn" href="{t['how']}">{t['volunteer']}</a> <a class="btn ghost light" href="{t['home']}">{t['about']}</a></p>
  </aside>
"""
    more = [x for x in all_r if x['group'] == r['group'] and x['slug'] != r['slug']][:4]
    if more:
        out += f'  <section class="more"><h2>{t["more"]}{e(gname)}</h2><div class="grid">' + ''.join(card(x, lang) for x in more) + '</div></section>\n'
    js = ('document.querySelectorAll("[data-copy]").forEach(b=>b.addEventListener("click",async()=>{try{await navigator.clipboard.writeText(b.dataset.copy);'
          'b.textContent="COPIED";setTimeout(()=>b.textContent="COPY",1600)}catch(e){}}))').replace('COPIED', t['copied']).replace('COPY', t['copy'])
    out += f'</article>\n<script>{js}</script>\n'
    return out + foot(lang)


def index_page(all_r, lang='he'):
    t = S[lang]
    other = 'en' if lang == 'he' else 'he'
    groups = GROUPS if lang == 'he' else GROUPS_EN
    url = rurl(lang)
    if lang == 'he':
        desc = 'ספר המתכונים של עוגה בהפתעה: מתכונים ללא סוכר של קרן אגם, עוגות של סבתא שהקשישים שלנו שיתפו, עוגות קלות של המתנדבים ומתכונים לזכרם של הנופלים.'
        title = 'ספר המתכונים של עוגה בהפתעה | מתכוני עוגות ביתיות וללא סוכר'
        lead = 'לאורך השנים והחגים המתנדבים שלנו יצרו קשרים מיוחדים עם הקשישים, ומתוכם נולד ספר מתכונים של עוגה בהפתעה. תודה לכל מי שאפה, סיפר ושיתף.'
        cta = ('רוצים להביא עוגה לקשיש בחג?', 'אופים עוגה בבית, מגיעים לביקור, ומשמחים מישהו שמחכה לחברה.')
    else:
        desc = ('The Surprise Cake recipe book: sugar-free cakes by Keren Agam, grandma’s cakes shared by the seniors we visit, '
                'easy cakes from our volunteers and recipes baked in memory of the fallen.')
        title = 'The Surprise Cake Recipe Book | Homemade and Sugar-Free Cake Recipes from Israel'
        lead = ('Over the years and holidays, our volunteers have formed special bonds with the seniors they visit, and out of those bonds '
                'came the Surprise Cake recipe book. Thank you to everyone who baked, told their story and shared.')
        cta = ('Want to bring a cake to a senior for the holidays?', 'Bake a cake at home, come for a visit, and make someone who has been waiting for company happy.')
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': t['site_title'], 'url': url, 'description': desc, 'inLanguage': lang,
          'isPartOf': {'@type': 'WebSite', 'name': ORG[lang], 'url': URL},
          'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': rurl(lang, r['slug'])}
                                                                    for i, r in enumerate(all_r)]}}
    out = head(lang, e(title), e(desc), url, 'website', e(t['site_title']), URL + 'img/og.jpg',
               f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>', alt_url=rurl(other))
    jump = ' '.join(f'<a href="#{g}">{e(n)}</a>' for g, n, _ in groups)
    out += f"""<div class="wrap">
  <nav class="crumbs" aria-label="{t['crumbs']}"><a href="{t['home']}">{ORG[lang]}</a> <span aria-hidden="true">›</span> {t['book']}</nav>
  <header class="rhead"><h1>{t['site_title']}</h1>
  <p class="lead">{lead}</p>
  <p class="jump">{jump}</p></header>
"""
    for g, n, sub in groups:
        rs = [r for r in all_r if r['group'] == g]
        out += f'  <section class="group" id="{g}"><h2>{e(n)}</h2><p>{e(sub)}</p><div class="grid">' + ''.join(card(r, lang) for r in rs) + '</div></section>\n'
    out += f"""  <aside class="cta"><h2>{cta[0]}</h2><p>{cta[1]}</p><p><a class="btn" href="{t['how']}">{t['volunteer']}</a></p></aside>
</div>
"""
    return out + foot(lang)


CSS = '''
:root{--ink:#3E2618;--soft:#6E5849;--brn:#5A3824;--blue:#1F6FA8;--sky:#EAF5FD;--line:#E7E1DA;--bg:#FBFCFE}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:Heebo,system-ui,sans-serif;font-weight:400;font-size:17px;line-height:1.75;-webkit-font-smoothing:antialiased}
a{color:var(--blue)}
img{max-width:100%;height:auto;display:block}
:focus-visible{outline:3px solid #6FB4E2;outline-offset:3px;border-radius:6px}
.skip{position:fixed;top:-60px;inset-inline-start:16px;z-index:9;background:var(--brn);color:#fff;padding:10px 18px;border-radius:12px;font-weight:700;text-decoration:none}
.skip:focus{top:12px}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
.top{position:sticky;top:0;z-index:5;background:rgba(255,255,255,.92);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:64px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;color:var(--ink);text-decoration:none;font-size:18px}
.top nav{display:flex;align-items:center;gap:16px}
.nl{color:var(--ink);text-decoration:none;font-weight:500}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;background:var(--brn);color:#fff;border:1px solid var(--brn);border-radius:999px;padding:.55em 1.2em;font:inherit;font-weight:700;font-size:15px;text-decoration:none;cursor:pointer}
.btn.ghost{background:#fff;color:var(--brn);border-color:var(--line)}
.btn.ghost.light{background:transparent;color:#fff;border-color:rgba(255,255,255,.5)}
main{display:block;padding-bottom:40px}
.crumbs{font-size:14px;color:var(--soft);margin:22px 0 6px}
.crumbs a{color:var(--soft)}
.rhead{margin:6px 0 22px}
h1{font-size:clamp(32px,5vw,52px);line-height:1.1;font-weight:900;letter-spacing:-.02em;margin:0 0 8px;color:var(--ink)}
h2{font-size:22px;font-weight:800;margin:0 0 10px;color:var(--ink)}
.by{margin:0;font-size:18px;font-weight:600;color:var(--soft)}
.tag{display:inline-block;margin:10px 0 0;background:var(--sky);color:var(--blue);font-weight:700;font-size:14px;padding:3px 12px;border-radius:999px}
.credit{margin:6px 0 0;font-size:14px;color:var(--soft)}
.lead{max-width:62ch;color:var(--soft);font-size:18px}
.jump{display:flex;flex-wrap:wrap;gap:8px}
.jump a{background:#fff;border:1px solid var(--line);border-radius:999px;padding:6px 14px;text-decoration:none;color:var(--ink);font-weight:600;font-size:15px}
.hero{margin:0 0 26px;border-radius:24px;overflow:hidden;border:1px solid var(--line);background:#fff}
.hero img{width:100%;max-height:560px;object-fit:cover}
.intro{font-size:18px}
.cols{display:grid;grid-template-columns:1fr 1.4fr;gap:28px;background:#fff;border:1px solid var(--line);border-radius:24px;padding:clamp(20px,3vw,32px)}
.cols ul,.cols ol{margin:0;padding-inline-start:1.2em}
.cols li{margin-bottom:6px}
.note{background:#FFF8EF;border-radius:16px;padding:12px 16px}
.img2{border-radius:18px;margin:20px 0}
.storybox{background:var(--sky);border-radius:20px;padding:18px 22px;margin:22px 0}
.storybox p{margin:0}
.memorybox{background:#F5F1EC}
.share{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0}
.cta{background:linear-gradient(160deg,#5A3824,#8A5A3B);color:#F6EAE0;border-radius:28px;padding:clamp(22px,4vw,40px);margin:34px 0}
.cta h2{color:#fff;font-size:clamp(22px,3vw,30px)}
.cta .btn{background:#fff;color:var(--brn);border-color:#fff}
.cta .btn.ghost.light{background:transparent;color:#fff;border-color:rgba(255,255,255,.5)}
.more,.group{margin:34px 0}
.group>p{color:var(--soft);margin:-4px 0 16px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.rcard{display:grid;grid-template-rows:auto 1fr;background:#fff;border:1px solid var(--line);border-radius:20px;overflow:hidden;text-decoration:none;color:var(--ink);transition:transform .2s,box-shadow .2s}
.rcard:hover{transform:translateY(-3px);box-shadow:0 18px 40px -24px rgba(40,70,100,.4)}
.rcard .ph{position:relative;display:block;aspect-ratio:4/3;background:linear-gradient(140deg,#F2F9FE,#DDEFFB)}
.rcard .ph img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.rcard .ph .tag{position:absolute;top:10px;inset-inline-start:10px;margin:0;background:#fff}
.rcard .noimg{position:absolute;inset:0}
.rcard .body{display:grid;gap:2px;padding:12px 14px 14px}
.rcard strong{font-weight:800;line-height:1.3}
.rcard .body span{font-size:14px;color:var(--soft);font-weight:600}
footer{border-top:1px solid var(--line);padding:30px 0 50px;color:var(--soft);font-size:15px}
footer .small{font-size:14px}
@media (max-width:820px){.grid{grid-template-columns:1fr 1fr}.cols{grid-template-columns:1fr}}
@media (max-width:480px){.brand span{display:none}.nl{font-size:15px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
'''


def build(site, out):
    rs = load(site)
    os.makedirs(f'{out}/assets', exist_ok=True)
    open(f'{out}/assets/recipe.css', 'w').write(CSS)
    urls = []
    for r in rs:
        if r.get('img'):
            SIZES[r['img']] = Image.open(f"{site}/{r['img']}").size
        img = og_image(site, out, r)
        for lang in ('he', 'en'):
            if not r.get(lang):
                continue
            d = f"{out}/{S[lang]['pre']}recipes/{r['slug']}"
            os.makedirs(d, exist_ok=True)
            open(f'{d}/index.html', 'w').write(page(r, rs, img, lang))
            urls.append(rurl(lang, r['slug']))
    for lang in ('he', 'en'):
        os.makedirs(f"{out}/{S[lang]['pre']}recipes", exist_ok=True)
        open(f"{out}/{S[lang]['pre']}recipes/index.html", 'w').write(index_page(rs, lang))
    return [rurl('he'), rurl('en')] + urls


def not_found_page():
    out = head('he', 'העמוד לא נמצא | עוגה בהפתעה', 'העמוד שחיפשתם לא נמצא באתר של עוגה בהפתעה.', URL, 'website',
               'עוגה בהפתעה', URL + 'img/og.jpg', '<meta name="robots" content="noindex">')
    out += """<div class="wrap" style="text-align:center;padding:60px 20px 20px">
  <h1>אופס, העמוד הזה לא נמצא</h1>
  <p class="lead" style="margin:12px auto 26px">ייתכן שהגעתם מקישור ישן. בנינו אתר חדש, והכול נמצא בו:</p>
  <p class="jump" style="justify-content:center"><a href="/">לדף הבית</a><a href="/#how">אני רוצה להתנדב</a><a href="/recipes/">ספר המתכונים</a><a href="/#faq">שאלות נפוצות</a></p>
  <p lang="en" dir="ltr" style="margin-top:28px;color:var(--soft)">Page not found. <a href="/?lang=en">Go to the English home page</a></p>
</div>
<script>if(location.pathname.startsWith('/en/recipes/'))location.replace('/en/recipes/');else if(location.pathname.startsWith('/recipes/'))location.replace('/recipes/')</script>
"""
    return out + foot('he')
