"""Regenerate the checked-in pinyin layer; normal builds need no extra dependency.

Run with pypinyin==0.55.0. Chinese source text and timing remain authoritative.
Phrase readings are sliced from the converted full line, not converted separately.
"""
import json
import re
from pathlib import Path
from pypinyin import Style, lazy_pinyin

ROOT = Path(__file__).resolve().parents[1]
HAN = re.compile(r'[\u3400-\u9fff\uf900-\ufaff\U00020000-\U000323af]')
OVERRIDES = json.loads((ROOT / 'scripts/pinyin-readings.json').read_text())
PUNCTUATION = str.maketrans('，。！？；：（）', ',.!?;:()')

def romanize(text):
    syllables = lazy_pinyin(text, style=Style.TONE, errors=lambda s: list(s))
    assert len(syllables) == len(text), text
    # Apply reviewed phrases after dictionary segmentation; longer context wins.
    for phrase, reading in sorted(OVERRIDES.items(), key=lambda item: len(item[0])):
        tokens = reading.split()
        assert len(tokens) == len(phrase), phrase
        for match in re.finditer(re.escape(phrase), text):
            syllables[match.start():match.end()] = tokens
    out = ''; offsets = []
    for i, (char, syllable) in enumerate(zip(text, syllables)):
        previous = text[i-1] if i else ''
        if i and ((HAN.fullmatch(previous) and char.isalnum()) or
                  (HAN.fullmatch(char) and (previous.isalnum() or previous in ',.!?;:，。！？；：'))):
            out += ' '
        start = len(out)
        out += syllable.translate(PUNCTUATION)
        offsets.append((start, len(out)))
    assert not HAN.search(out), text
    return out, offsets

def generate():
    path = ROOT / 'dist/album.json'
    album = json.loads(path.read_text())
    for track in album['tracks']:
        offsets = []
        for line in track['lyrics']:
            line['pinyin'], positions = romanize(line['zh'])
            offsets.append(positions)
        for note in track['notes']:
            source = note['phrase'].get('zh')
            if source:
                index = note['anchorLine']; line = track['lyrics'][index]
                start = line['zh'].index(source); end = start + len(source)
                note['pinyinOffset'] = offsets[index][start][0]
                note['phrase']['pinyin'] = line['pinyin'][note['pinyinOffset']:offsets[index][end-1][1]]
            note['pinyinLabel'] = note['phrase'].get('pinyin') or romanize(note.get('original') or note['phrase'].get('en') or 'Note')[0]
    album['romanization'] = {'method': 'pypinyin 0.55.0 with reviewed contextual readings',
                            'style': 'Tone marks; syllable spacing; original non-Chinese text retained'}
    path.write_text(json.dumps(album, ensure_ascii=False, indent=2) + '\n')
    print(f'Generated pinyin for {sum(len(t["lyrics"]) for t in album["tracks"])} rows across {len(album["tracks"])} songs.')

if __name__ == '__main__':
    generate()
