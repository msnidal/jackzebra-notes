import json, re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
album=json.loads((root/'dist/album.json').read_text())
assert len(album['tracks'])==55
assert [t['id'] for t in album['tracks']]==list(range(1,56))
assert len({t['isrc'] for t in album['tracks']})==55
covered=[]
for t in album['tracks']:
    times=[l['start'] for l in t['lyrics'] if l['start'] is not None]
    assert t['lyrics'],t['title']
    assert all(l['start'] is None or isinstance(l['start'],(float,int)) for l in t['lyrics'])
    assert times==sorted(times),t['title']
    assert all(0<=s<t['duration'] for s in times),t['title']
    for row in t['lyrics']:
        if row.get('kind')=='section':
            assert row['start'] is None and row.get('end') is None,(t['title'],'timed section')
        if row.get('end') is not None:
            assert row['start'] is not None and row['start']<row['end']<=t['duration']+.01,(t['title'],'invalid vocal interval')
    if t.get('timing'):
        timing=t['timing'];lyrics=[l for l in t['lyrics'] if l.get('kind')!='section']
        assert timing['lyricLines']==len(lyrics)
        assert timing['timedLines']==len(times)
        assert timing['unresolvedLines']==len(lyrics)-len(times)
        assert timing['communityFallbackLines']==sum(l.get('timingSource')=='community' for l in lyrics)
        assert timing['method'] and timing['models'] and timing['generatedAt']
        assert all(l.get('timingSource') in ['ai','community','unresolved'] for l in lyrics)
    assert all(l['en'].strip() and l['zh'].strip() for l in t['lyrics']),t['title']
    assert all(0<=n['anchorLine']<len(t['lyrics']) for n in t['notes']),t['title']
    assert len({n['id'] for n in t['notes']})==len(t['notes'])
    if t['lyrics']:
        assert t['sourceUrl'].startswith('https://')
        assert t['translationStatus']
        assert t['audioReview']=='Not independently audio-verified'
        assert all(s['url'].startswith('https://') for s in t['lyricSources'])
        covered.append(t['title'])
    for n in t['notes']:
        assert all(s['url'].startswith('https://') for s in n.get('sources',[]))
        assert n.get('phrase') and any(n['phrase'].values()),(t['title'],n['id'],'missing phrase')
        for lang,phrase in n['phrase'].items():
            assert lang in ['zh','en'] and phrase and phrase in t['lyrics'][n['anchorLine']][lang],(t['title'],n['id'],lang)
    for row in t['lyrics']:
        notes=[n for n in t['notes'] if all(t['lyrics'][n['anchorLine']][lang]==row[lang] for lang in ['zh','en'])]
        for lang in ['zh','en']:
            ranges=[]
            for n in notes:
                phrase=n['phrase'].get(lang)
                if not phrase:continue
                start=row[lang].index(phrase);end=start+len(phrase)
                assert not any(start<b and end>a for a,b in ranges),(t['title'],n['id'],'overlapping phrases')
                ranges.append((start,end))
for f in (root/'dist').rglob('*'):
    assert f.suffix.lower() not in ['.flac','.mp3','.m4a','.wav','.zip'],str(f)
html=(root/'dist/zhuang-zhuang/sunshine/index.html').read_text()
ids=re.findall(r'\bid="([^"]+)"',html)
assert len(ids)==len(set(ids))
for src in re.findall(r'(?:src|href)="([^"]+)"',html):
    if src.startswith(('http','#','data:')):continue
    target=root/'dist'/src.split('?',1)[0].lstrip('/')
    assert target.is_file() or (target/'index.html').is_file(),src
print(json.dumps({'tracks':55,'translated_tracks':len(covered),'tracks_with_approximate_timing':sum(any(l['start'] is not None for l in t['lyrics']) for t in album['tracks']),'lyric_rows':sum(len(t['lyrics']) for t in album['tracks']),'notes':sum(len(t['notes']) for t in album['tracks']),'audio_in_deployment':False}))
