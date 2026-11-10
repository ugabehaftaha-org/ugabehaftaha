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
GNAME = {g: n for g, n, _ in GROUPS}

e = lambda s: html.escape(str(s or ''), quote=True)


def load(site):
    js = "global.window={};require(process.argv[1]);process.stdout.write(JSON.stringify(window.RECIPES))"
    return json.loads(subprocess.check_output(['node', '-e', js, os.path.abspath(f'{site}/recipes.js')]))


def by_line(r):
    d = r['he']
    if r['group'] == 'volunteer':
        return f"המתכון של {d['by']}"
    if r['group'] == 'keren':
        return 'מתכון של קרן אגם'
    if r['group'] == 'memory':
        return d['by']
    return '' if d['by'] in d['title'] else d['by']


def full_title(r):
    d = r['he']
    if r['group'] == 'volunteer':
        return f"{d['title']} – המתכון של {d['by']}"
    if r['group'] == 'keren':
        return f"{d['title']} – מתכון של קרן אגם"
    if r['group'] == 'memory':
        return f"{d['title']} {d['by']}"
    return d['title']


def describe(r):
    d = r['he']
    base = d.get('intro') or ''
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


HEAD = '''<!doctype html>
<html lang="he" dir="rtl" translate="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google" content="notranslate">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/img/logo.webp" type="image/webp">
<meta name="theme-color" content="#5A3824">
<meta property="og:type" content="{ogtype}">
<meta property="og:locale" content="he_IL">
<meta property="og:site_name" content="עוגה בהפתעה">
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
<a class="skip" href="#main">דלג לתוכן הראשי</a>
<header class="top"><div class="wrap">
  <a class="brand" href="/"><img src="/img/logo.webp" alt="" width="40" height="40"><span>עוגה בהפתעה</span></a>
  <nav aria-label="ניווט">
    <a class="nl" href="/recipes/">ספר המתכונים</a>
    <a class="btn" href="/#how">אני רוצה להתנדב</a>
  </nav>
</div></header>
<main id="main" tabindex="-1">
'''

FOOT = '''</main>
<footer><div class="wrap">
  <a class="brand" href="/"><img src="/img/logo.webp" alt="" width="40" height="40"><span>עוגה בהפתעה</span></a>
  <p>מפיגים את הבדידות של קשישים וניצולי שואה, באמצעות עוגות. <a href="mailto:ugabehaftaha@gmail.com">ugabehaftaha@gmail.com</a></p>
  <p class="small"><a href="/?a11y=1">הצהרת נגישות</a></p>
</div></footer>
</body>
</html>
'''


def card(r):
    d = r['he']
    ph = (f'<img src="/{e(r["img"])}" alt="{e(d["title"])}" loading="lazy" style="object-position:{e(r.get("pos") or "center 50%")}">'
          if r.get('img') else '<span class="noimg" aria-hidden="true"></span>')
    b = by_line(r)
    tag = '<span class="tag">ללא סוכר</span>' if r.get('sugarFree') and r['group'] != 'keren' else ''
    return (f'<a class="rcard" href="/recipes/{e(r["slug"])}/"><span class="ph">{ph}{tag}</span>'
            f'<span class="body"><strong>{e(d["title"])}</strong>{f"<span>{e(b)}</span>" if b else ""}</span></a>')


def recipe_ld(r, image, url, desc):
    d = r['he']
    author = {'@type': 'Organization', 'name': 'עוגה בהפתעה'} if r['group'] == 'memory' else \
        {'@type': 'Person', 'name': d['by'].replace('המתכון של ', '')}
    ld = {
        '@context': 'https://schema.org', '@type': 'Recipe', 'name': d['title'], 'description': desc,
        'image': [image], 'author': author, 'inLanguage': 'he', 'url': url,
        'publisher': {'@type': 'Organization', 'name': 'עוגה בהפתעה', 'url': URL, 'logo': URL + 'img/logo.webp'},
        'recipeCategory': 'קינוח', 'recipeCuisine': 'ישראלית',
        'keywords': ', '.join(filter(None, [d['title'], 'ללא סוכר' if r.get('sugarFree') else '', 'עוגה בהפתעה', 'מתכון ביתי', GNAME[r['group']]])),
        'recipeIngredient': d['ing'],
        'recipeInstructions': [{'@type': 'HowToStep', 'text': s} for s in d['steps']],
    }
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'עוגה בהפתעה', 'item': URL},
        {'@type': 'ListItem', 'position': 2, 'name': 'ספר המתכונים', 'item': URL + 'recipes/'},
        {'@type': 'ListItem', 'position': 3, 'name': d['title'], 'item': url}]}
    return ld, crumbs


def page(r, all_r, image):
    d = r['he']
    url = f"{URL}recipes/{r['slug']}/"
    desc = describe(r)
    title = f"{full_title(r)} | ספר המתכונים של עוגה בהפתעה"
    lds = []
    if d.get('ing'):
        ld, crumbs = recipe_ld(r, image, url, desc)
        lds = [ld, crumbs]
    ldtxt = '\n'.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    out = HEAD.format(title=e(title), desc=e(desc), url=url, ogtype='article', ogtitle=e(full_title(r)), image=image, ld=ldtxt)
    b = by_line(r)
    mem = r['group'] == 'memory'
    out += f'''<article class="wrap recipe{' memory' if mem else ''}">
  <nav class="crumbs" aria-label="פירורי לחם"><a href="/">עוגה בהפתעה</a> <span aria-hidden="true">›</span> <a href="/recipes/">ספר המתכונים</a> <span aria-hidden="true">›</span> <a href="/recipes/#{r['group']}">{e(GNAME[r['group']])}</a></nav>
  <header class="rhead">
    <h1>{e(d['title'])}</h1>
    {f'<p class="by">{e(b)}</p>' if b else ''}
    {'<p class="tag">ללא סוכר</p>' if r.get('sugarFree') and not mem else ''}
    {f'<p class="credit">{e(d.get("credit"))}</p>' if d.get('credit') else ''}
  </header>
'''
    if r.get('img') and not mem:
        out += f'  <figure class="hero"><img src="/{e(r["img"])}" alt="{e(d["title"])}" width="{SIZES.get(r['img'],(1200,900))[0]}" height="{SIZES.get(r['img'],(1200,900))[1]}" fetchpriority="high"></figure>\n'
    if mem and d.get('story'):
        out += f'  <div class="storybox memorybox"><p>{e(d["story"])}</p></div>\n'
    if d.get('intro'):
        out += f'  <p class="intro">{e(d["intro"])}</p>\n'
    if d.get('video') and r.get('link'):
        out += f'  <p>קרן הכינה את המתכון הזה בסרטון.</p><p><a class="btn" href="{e(r["link"])}" target="_blank" rel="noopener">לצפייה במתכון באינסטגרם</a></p>\n'
    if d.get('ing'):
        out += '  <div class="cols">\n    <section><h2>מצרכים</h2><ul>' + ''.join(f'<li>{e(i)}</li>' for i in d['ing']) + '</ul></section>\n'
        out += '    <section><h2>אופן ההכנה</h2><ol>' + ''.join(f'<li>{e(s)}</li>' for s in d['steps']) + '</ol></section>\n  </div>\n'
    if d.get('note'):
        out += f'  <p class="note">{e(d["note"])}</p>\n'
    if r.get('link') and not d.get('video'):
        out += f'  <p><a class="btn ghost" href="{e(r["link"])}" target="_blank" rel="noopener">למתכון המלא אצל קרן</a></p>\n'
    if r.get('img2'):
        out += f'  <img class="img2" src="/{e(r["img2"])}" alt="" loading="lazy">\n'
    if d.get('story') and not mem:
        out += f'  <div class="storybox"><h2>הסיפור שמאחורי המתכון</h2><p>{e(d["story"])}</p></div>\n'
    wa = 'https://wa.me/?text=' + __import__('urllib.parse', fromlist=['quote']).quote(f"{full_title(r)} – מתכון מספר המתכונים של עוגה בהפתעה\n{url}")
    out += f'''  <div class="share"><a class="btn ghost" href="{wa}" target="_blank" rel="noopener">שיתוף בוואטסאפ</a><button class="btn ghost" type="button" data-copy="{url}">העתקת קישור</button></div>
  <aside class="cta">
    <h2>רוצים להביא עוגה כזאת לקשיש בחג?</h2>
    <p>בעוגה בהפתעה מתנדבים אופים עוגה בבית ומגיעים לביקור אצל קשישים וניצולי שואה, בראש השנה, חנוכה, פורים ושבועות, ב־14 ערים ברחבי הארץ.</p>
    <p><a class="btn" href="/#how">אני רוצה להתנדב</a> <a class="btn ghost light" href="/">על העמותה</a></p>
  </aside>
'''
    more = [x for x in all_r if x['group'] == r['group'] and x['slug'] != r['slug']][:4]
    if more:
        out += f'  <section class="more"><h2>עוד מ{e(GNAME[r["group"]])}</h2><div class="grid">' + ''.join(card(x) for x in more) + '</div></section>\n'
    out += '</article>\n<script>document.querySelectorAll("[data-copy]").forEach(b=>b.addEventListener("click",async()=>{try{await navigator.clipboard.writeText(b.dataset.copy);b.textContent="הקישור הועתק";setTimeout(()=>b.textContent="העתקת קישור",1600)}catch(e){}}))</script>\n'
    return out + FOOT


def index_page(all_r):
    url = URL + 'recipes/'
    desc = 'ספר המתכונים של עוגה בהפתעה: מתכונים ללא סוכר של קרן אגם, עוגות של סבתא שהקשישים שלנו שיתפו, עוגות קלות של המתנדבים ומתכונים לזכרם של הנופלים.'
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'ספר המתכונים של עוגה בהפתעה', 'url': url, 'description': desc,
          'isPartOf': {'@type': 'WebSite', 'name': 'עוגה בהפתעה', 'url': URL},
          'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f"{URL}recipes/{r['slug']}/"} for i, r in enumerate(all_r)]}}
    out = HEAD.format(title='ספר המתכונים של עוגה בהפתעה | מתכוני עוגות ביתיות וללא סוכר', desc=e(desc), url=url, ogtype='website',
                      ogtitle='ספר המתכונים של עוגה בהפתעה', image=URL + 'img/og.jpg',
                      ld=f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')
    out += '''<div class="wrap">
  <nav class="crumbs" aria-label="פירורי לחם"><a href="/">עוגה בהפתעה</a> <span aria-hidden="true">›</span> ספר המתכונים</nav>
  <header class="rhead"><h1>ספר המתכונים של עוגה בהפתעה</h1>
  <p class="lead">לאורך השנים והחגים המתנדבים שלנו יצרו קשרים מיוחדים עם הקשישים, ומתוכם נולד ספר מתכונים של עוגה בהפתעה. תודה לכל מי שאפה, סיפר ושיתף.</p>
  <p class="jump">''' + ' '.join(f'<a href="#{g}">{e(n)}</a>' for g, n, _ in GROUPS) + '''</p></header>
'''
    for g, n, sub in GROUPS:
        rs = [r for r in all_r if r['group'] == g]
        out += f'  <section class="group" id="{g}"><h2>{e(n)}</h2><p>{e(sub)}</p><div class="grid">' + ''.join(card(r) for r in rs) + '</div></section>\n'
    out += '''  <aside class="cta"><h2>רוצים להביא עוגה לקשיש בחג?</h2><p>אופים עוגה בבית, מגיעים לביקור, ומשמחים מישהו שמחכה לחברה.</p><p><a class="btn" href="/#how">אני רוצה להתנדב</a></p></aside>
</div>
'''
    return out + FOOT


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
        if r.get('img'): SIZES[r['img']] = Image.open(f"{site}/{r['img']}").size
        img = og_image(site, out, r)
        d = f"{out}/recipes/{r['slug']}"
        os.makedirs(d, exist_ok=True)
        open(f'{d}/index.html', 'w').write(page(r, rs, img))
        urls.append(f"{URL}recipes/{r['slug']}/")
    os.makedirs(f'{out}/recipes', exist_ok=True)
    open(f'{out}/recipes/index.html', 'w').write(index_page(rs))
    return [URL + 'recipes/'] + urls


def not_found_page():
    out = HEAD.format(title='העמוד לא נמצא | עוגה בהפתעה', desc='העמוד שחיפשתם לא נמצא באתר של עוגה בהפתעה.', url=URL, ogtype='website',
                      ogtitle='עוגה בהפתעה', image=URL + 'img/og.jpg', ld='<meta name="robots" content="noindex">')
    out += """<div class="wrap" style="text-align:center;padding:60px 20px 20px">
  <h1>אופס, העמוד הזה לא נמצא</h1>
  <p class="lead" style="margin:12px auto 26px">ייתכן שהגעתם מקישור ישן. בנינו אתר חדש, והכול נמצא בו:</p>
  <p class="jump" style="justify-content:center"><a href="/">לדף הבית</a><a href="/#how">אני רוצה להתנדב</a><a href="/recipes/">ספר המתכונים</a><a href="/#faq">שאלות נפוצות</a></p>
</div>
<script>if(/^\/recipes\//.test(location.pathname))location.replace('/recipes/')</script>
"""
    return out + FOOT
