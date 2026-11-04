"""Build the site. Edit _build/index.src.html (page) and recipes.js (recipes), add images to img/, then run:
    python3 _build/build.py
It regenerates index.html, recipes/, assets/, sitemap.xml, robots.txt and _redirects in the repo root."""
import re,shutil,os,json,sys
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
OUT=os.path.dirname(HERE);SITE=OUT;URL='https://ugabehaftaha.com/'
for n in ['index.html','recipes','assets','sitemap.xml','robots.txt','_redirects','img/og','README.md']:
    q=os.path.join(OUT,n)
    if os.path.isdir(q): shutil.rmtree(q)
    elif os.path.exists(q): os.remove(q)
s=open(f'{HERE}/index.src.html').read();r=open(f'{SITE}/recipes.js').read()
refs=set(re.findall(r"img/[A-Za-z0-9_\-./]+\.(?:webp|png|jpg|jpeg|svg)",s+r))
missing=[x for x in refs if not os.path.exists(f'{SITE}/'+x)]
if missing: sys.exit('Missing images: '+', '.join(missing))
from PIL import Image
im=Image.open(f'{SITE}/img/hero-elka-tal.webp').convert('RGB');w,h=im.size;W,H=1200,630;sc=max(W/w,H/h)
im=im.resize((int(w*sc),int(h*sc)));x=(im.width-W)//2;y=int((im.height-H)*.3);im.crop((x,y,x+W,y+H)).save(f'{OUT}/img/og.jpg',quality=85)
ld={"@context":"https://schema.org","@type":"NGO","name":"עוגה בהפתעה","alternateName":["Surprise Cake","Uga BeHafta'ah"],
 "url":URL,"logo":URL+"img/logo.webp","image":URL+"img/og.jpg","email":"ugabehaftaha@gmail.com","foundingDate":"2020","areaServed":"IL",
 "description":"עמותה שמפיגה את הבדידות של קשישים וניצולי שואה: מתנדבים אופים עוגה ומגיעים לביקור בחגים, ב־14 ערים ברחבי הארץ.",
 "sameAs":["https://www.instagram.com/uga_behaftaha/","https://www.tiktok.com/@uga_behaftaha","https://www.linkedin.com/in/surprise-cake-a3336b285"]}
title='עוגה בהפתעה | התנדבות עם קשישים וניצולי שואה בחגים'
desc='עוגה בהפתעה מפיגה בדידות של קשישים וניצולי שואה. מתנדבים אופים עוגה ומגיעים לביקור בראש השנה, חנוכה, פורים ושבועות, ב־14 ערים ברחבי הארץ. בואו להתנדב.'
head=f'''<!doctype html>
<html lang="he" dir="rtl" translate="no">
<head>
<meta charset="utf-8">
<meta name="google" content="notranslate">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="עוגה בהפתעה, התנדבות, התנדבות עם קשישים, התנדבות בחגים, ניצולי שואה, בדידות קשישים, התנדבות משפחתית, התנדבות לילדים, עמותה, ביקור קשישים, מתכוני עוגות, Surprise Cake, volunteering Israel">
<link rel="preload" as="image" href="img/hero-elka-tal.webp" fetchpriority="high">
<link rel="canonical" href="{URL}">
<link rel="icon" href="img/logo.webp" type="image/webp">
<link rel="apple-touch-icon" href="img/logo.webp">
<meta name="theme-color" content="#5A3824">
<meta property="og:type" content="website">
<meta property="og:locale" content="he_IL">
<meta property="og:site_name" content="עוגה בהפתעה">
<meta property="og:title" content="{title}">
<meta property="og:description" content="מתנדבים אופים עוגה ומבקרים קשישים וניצולי שואה בחגים, ב־14 ערים. בואו להצטרף.">
<meta property="og:image" content="{URL}img/og.jpg">
<meta property="og:url" content="{URL}">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
'''
body=re.sub(r'^<title>.*?</title>\n','',s,count=1)
body=body.replace('<meta name="claude:viewport-fit-sides" content="cover">\n','',1)
body=re.sub(r'<meta name="description"[^>]*>\n','',body,count=1)
i=body.index('</style>')+len('</style>')
open(f'{OUT}/index.html','w').write(head+body[:i]+'\n</head>\n<body>\n'+body[i:]+'\n</body>\n</html>\n')
open(f'{OUT}/robots.txt','w').write(f'User-agent: *\nAllow: /\nDisallow: /_build/\nSitemap: {URL}sitemap.xml\n')
import recipe_pages
RURLS=recipe_pages.build(SITE,OUT)
open(f'{OUT}/sitemap.xml','w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>{URL}</loc><lastmod>{__import__('datetime').date.today().isoformat()}</lastmod><changefreq>monthly</changefreq><priority>1.0</priority></url>\n'+''.join(f'  <url><loc>{u}</loc><lastmod>{__import__("datetime").date.today().isoformat()}</lastmod></url>\n' for u in RURLS)+'</urlset>\n')
open(f'{OUT}/README.md','w').write('# עוגה בהפתעה\nהאתר של עמותת עוגה בהפתעה – ugabehaftaha.com\n\nTo change the site: edit `_build/index.src.html` or `recipes.js`, add images to `img/`, run `python3 _build/build.py`, commit and push. Netlify deploys automatically.\n')
print('built',len(refs),'images')

open(f'{OUT}/_redirects','w').write("""# old Wix addresses -> new site
/en            /?lang=en           301
/en/*          /?lang=en           301
/he            /                   301
/he/*          /                   301
/recipes/*     /recipes/           301
/*             /                   301
""")
