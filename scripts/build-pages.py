"""Generate crawlable HTML for every song; browser JS progressively adds playback."""
import hashlib, html, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
ALBUM=json.loads((OUT/'album.json').read_text())
ORIGIN='https://jackzebranotes.com'
ALBUM_PATH='/zhuang-zhuang/'
e=lambda v:html.escape(str(v),quote=True)
def slug(t):return t.get('slug') or re.sub(r'[^a-z0-9]+','-',t['title'].lower()).strip('-')
def path(t):return ALBUM_PATH+slug(t)+'/'
def fmt(n):return f'{int(n)//60}:{int(n)%60:02}'
def title(t):return f'Jackzebra — {t["title"]}'+(f' ({t["originalTitle"]})' if t.get('originalTitle') else '')+': Lyrics & English Translation | Jackzebra Notes'
def description(t):return f'Read {t["title"]} by Jackzebra from Zhuang Zhuang Mixtape: original lyrics, English translation, and notes on language, references, and meaning.'
def version(name):return '/'+name+'?v='+hashlib.sha256((OUT/name).read_bytes()).hexdigest()[:10]
def links(active=None):
    return ''.join(f'<a class="track-row {"active" if t["id"]==active else ""}" href="{path(t)}" data-track="{t["id"]}" aria-current="{"true" if t["id"]==active else "false"}" aria-label="{e(str(t["id"])+". "+t["title"]+", lyrics available")}"><span class="num">{t["id"]:02}</span><span class="track-name">{e(t["title"])}</span><span class="track-time">{fmt(t["duration"])}</span></a>' for t in ALBUM['tracks'])
def replace_inner(doc,tag,id,value):
    result,n=re.subn(r'(<'+tag+r'\b[^>]*\bid="'+id+r'"[^>]*>).*?(</'+tag+r'>)',lambda m:m[1]+value+m[2],doc,flags=re.S)
    assert n==1,(tag,id,n)
    return result
def phrase(text,notes,lang):
    ranges=[]
    for n in notes:
        p=n.get('phrase',{}).get(lang)
        if p and p in text:ranges.append((text.index(p),text.index(p)+len(p),n))
    ranges.sort(key=lambda r:r[0]);out='';cursor=0
    for start,end,n in ranges:
        out+=e(text[cursor:start])+f'<a class="phrase-note" href="#note-{e(n["id"])}" aria-label="Explain {e(text[start:end])}">{e(text[start:end])}</a>';cursor=end
    return out+e(text[cursor:])
def lyrics(t):
    result=[]
    for i,l in enumerate(t['lyrics']):
        notes=[n for n in t['notes'] if n['anchorLine']==i or all(t['lyrics'][n['anchorLine']][k]==l[k] for k in ['zh','en'])]
        lang='ko' if re.search('[가-힣]',l['zh']) else 'zh' if re.search('[\u3400-\u9fff]',l['zh']) else 'en'
        classes='lyric-line'+(' lyric-section' if l.get('kind')=='section' else '')+(' same-text' if l['zh']==l['en'] else '')
        result.append(f'<div class="{classes}" id="line-{i}" data-line="{i}"><p class="chinese" lang="{lang}">{phrase(l["zh"],notes,"zh")}</p><p class="english">{phrase(l["en"],notes,"en")}</p></div>')
    return '\n'.join(result)
def notes(t):
    items=[]
    for n in t['notes']:
        label=n.get('phrase',{}).get('zh') or n.get('original') or 'Note'
        sources=''.join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["label"])}</a></li>' for s in n.get('sources',[]))
        items.append(f'<details id="note-{e(n["id"])}"><summary>{e(label)}</summary><p>{e(n["body"])}</p><ul>{sources}</ul></details>')
    sources=' · '.join(f'<a href="{e(s["url"])}">{e(s["label"])}</a>' for s in t['lyricSources'])
    return '<section class="static-notes" aria-label="Notes and sources"><h2>Notes</h2>'+''.join(items)+f'<p>Independent, AI-assisted English translation. Not artist-authorized. Sources: {sources}.</p></section>'
def head_metadata(page_title,desc,url,schema):
    return f'<link rel="canonical" href="{e(url)}"><meta property="og:type" content="website"><meta property="og:site_name" content="Jackzebra Notes"><meta property="og:title" content="{e(page_title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{e(url)}"><script id="page-schema" type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script>'
template=(ROOT/'src/song.html').read_text()
for t in ALBUM['tracks']:
    doc=re.sub(r'<title>.*?</title>',lambda _:f'<title>{e(title(t))}</title>',template)
    doc=re.sub(r'<meta name="description"[^>]+>',lambda _:f'<meta name="description" content="{e(description(t))}">',doc)
    schema={'@context':'https://schema.org','@type':'WebPage','name':title(t),'url':ORIGIN+path(t),'inLanguage':['en','zh'],'about':{'@type':'MusicRecording','name':t['title'],'isrcCode':t['isrc'],'byArtist':{'@type':'MusicGroup','name':'Jackzebra'},'inAlbum':{'@type':'MusicAlbum','name':ALBUM['title']}}}
    doc=doc.replace('</head>',head_metadata(title(t),description(t),ORIGIN+path(t),schema)+'</head>')
    values=[('nav','track-list',links(t['id'])),('span','coverage-count','55 with lyrics'),('span','track-number',f'{t["id"]:02} / 55'),('span','track-length',fmt(t['duration'])),('h1','song-title',e(t['title'])),('p','song-original-title',e(t.get('originalTitle',''))),('span','song-credit',e(t['artist']+' · prod. '+t['producer'])),('strong','player-title',e(t['title'])),('span','duration',fmt(t['duration'])),('section','lyrics',lyrics(t))]
    for tag,id,value in values:doc=replace_inner(doc,tag,id,value)
    doc=doc.replace('<section id="lyrics" class="lyrics"','<section id="lyrics" data-language="both" class="lyrics"').replace('<main id="reader"','<main data-language="both" id="reader"')
    if t.get('originalTitle'):doc=doc.replace('id="song-original-title" lang="zh" hidden','id="song-original-title" lang="zh"')
    nxt=ALBUM['tracks'][t['id']%len(ALBUM['tracks'])]
    doc=replace_inner(doc,'a','next-song',f'<span>NEXT TRACK</span><strong>{e(nxt["title"])}</strong>')
    doc=re.sub(r'(<a id="next-song"[^>]*href=")[^"]+',lambda m:m[1]+path(nxt),doc)
    doc=doc.replace('<div class="song-end">',notes(t)+'<div class="song-end">')
    doc=doc.replace('href="/style.css"',f'href="{version("style.css")}"').replace('src="/app.js"',f'src="{version("app.js")}"')
    target=OUT/path(t).strip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(doc)

favicon=re.search(r'<link rel="icon"[^>]+>',template)[0]
def catalog(album=False):
    page_title='Zhuang Zhuang Mixtape: Lyrics & English Translations | Jackzebra Notes' if album else 'Jackzebra Notes — Lyrics, English Translations & Context'
    desc='Original lyrics, independent English translations, and phrase notes for all 55 songs on Jackzebra’s Zhuang Zhuang Mixtape. Read freely or listen with your own audio.'
    url=ORIGIN+(ALBUM_PATH if album else '/')
    schema={'@context':'https://schema.org','@type':'CollectionPage','name':page_title,'url':url,'about':{'@type':'MusicAlbum','name':ALBUM['title'],'byArtist':{'@type':'MusicGroup','name':'Jackzebra'}}}
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#151713"><title>{e(page_title)}</title><meta name="description" content="{e(desc)}">{favicon}<link rel="stylesheet" href="{version('style.css')}"><link rel="stylesheet" href="{version('catalog.css')}">{head_metadata(page_title,desc,url,schema)}</head><body class="catalog-page"><header class="masthead"><a href="/" class="wordmark">jackzebra notes</a><a class="catalog-support" href="https://surfgangrecords.bandcamp.com/album/zhuang-zhuang-mixtape" target="_blank" rel="noopener">Bandcamp ↗</a></header><main class="catalog-main"><section class="album-intro"><img src="/assets/cover.jpg" width="240" height="240" alt="Zhuang Zhuang Mixtape cover: a green praying mantis on a white railing"><div><p class="eyebrow">JACKZEBRA · OCTOBER 2, 2026</p><h1><a href="/zhuang-zhuang/">Zhuang Zhuang</a></h1><p class="album-kind">Mixtape · 55 tracks · 1 hr 47 min</p><p class="catalog-description">Original lyrics, English translations, and notes on the words in between.</p><p class="catalog-help">Choose a song. Read freely, or add your Bandcamp download to listen along.</p></div></section><nav class="catalog-tracks" aria-label="Zhuang Zhuang songs">{links()}</nav><footer class="catalog-footer"><p>Independent, AI-assisted translations and sourced notes. Not affiliated with Jackzebra or Surf Gang Records.</p><a href="https://jackzebra.org/" target="_blank" rel="noopener">Artist website ↗</a></footer></main><script type="module" src="{version('catalog.js')}"></script></body></html>'''
(OUT/'index.html').write_text(catalog())
(OUT/'zhuang-zhuang/index.html').write_text(catalog(True))
urls=['/',ALBUM_PATH]+[path(t) for t in ALBUM['tracks']]
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{ORIGIN+u}</loc></url>' for u in urls)+'</urlset>\n')
(OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {ORIGIN}/sitemap.xml\n')
(OUT/'CNAME').write_text('jackzebranotes.com\n')
(OUT/'.nojekyll').touch()
(OUT/'404.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Page not found | Jackzebra Notes</title><link rel="stylesheet" href="{version("style.css")}"></head><body><main><h1>That page isn’t here.</h1><p><a href="/">Find your song at Jackzebra Notes</a></p></main></body></html>')
print(json.dumps({'song_pages':len(ALBUM['tracks']),'sitemap_urls':len(urls),'domain':ORIGIN}))
