"""Regression checks for indexable static routes and progressive enhancement."""
import json, re, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dist'
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.links=[];self.ids=[];self.meta={};self.canonical=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if tag=='meta':self.meta[a.get('name',a.get('property',''))]=a.get('content')
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
album=json.loads((OUT/'album.json').read_text());titles=[]
for t in album['tracks']:
    slug=t.get('slug') or re.sub('[^a-z0-9]+','-',t['title'].lower()).strip('-')
    route=f'/zhuang-zhuang/{slug}/';text=(OUT/route.strip('/')/'index.html').read_text();p=Page(text)
    assert len(p.ids)==len(set(p.ids)),route
    assert p.canonical==['https://jackzebranotes.com'+route]
    assert p.meta['og:url']==p.canonical[0] and p.meta['description']
    assert not p.meta.get('robots','').startswith('noindex')
    from html import escape
    assert f'<h1 id="song-title">{escape(t["title"])}</h1>' in text
    assert len(re.findall('data-line="',text))==len(t['lyrics'])
    for line in t['lyrics']:
        # Phrase links can split the text, but raw HTML text must preserve every lyric.
        raw=__import__('html').unescape(re.sub('<[^>]+>','',text))
        assert line['zh'] in raw and line['en'] in raw
    for note in t['notes']:assert escape(note['body'],quote=True) in text
    assert escape(t['intro'],quote=True) in text
    for context in album['researchContext']:assert escape(context['body'],quote=True) in text
    assert len([link for link in p.links if link.startswith('/zhuang-zhuang/')])>=56
    for link in p.links:
        target=urlsplit(link)
        if target.scheme or target.netloc:continue
        if target.path:
            local=OUT/target.path.lstrip('/')
            assert local.is_file() or (local/'index.html').is_file(),(route,link)
        elif target.fragment:assert unquote(target.fragment) in p.ids,(route,link)
    title=re.search('<title>(.*?)</title>',text)[1];assert title not in titles;titles.append(title)
    schema=json.loads(re.search(r'<script id="page-schema" type="application/ld\+json">(.*?)</script>',text)[1]);assert schema['about']['isrcCode']==t['isrc']
urls=[n.text for n in ET.parse(OUT/'sitemap.xml').findall('.//{*}loc')]
assert len(urls)==57 and len(set(urls))==57
assert (OUT/'CNAME').read_text().strip()=='jackzebranotes.com'
assert 'Sitemap: https://jackzebranotes.com/sitemap.xml' in (OUT/'robots.txt').read_text()
assert not re.search(r'<h2>\$\{esc\(n.title\)',(OUT/'app.js').read_text())
assert 'n.type' not in (OUT/'app.js').read_text()
print('PASS: 55 static song pages; complete bilingual lyrics and notes; unique metadata; valid links, sitemap, and canonical URLs.')
