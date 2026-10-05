import assert from 'node:assert/strict';
import { activeLyricIndex } from '../dist/timing.mjs';

const lyrics = [
  { kind: 'section', start: null },
  { start: 2.4, end: 4.1 },
  { start: 4.5, end: 6.2 },
  { start: null, end: null },
  { start: 12, end: 13.4 },
];
assert.equal(activeLyricIndex(lyrics, 0), -1, 'instrumental intro');
assert.equal(activeLyricIndex(lyrics, 2.4), 1, 'exact line onset');
assert.equal(activeLyricIndex(lyrics, 4.1), -1, 'vocal end is exclusive');
assert.equal(activeLyricIndex(lyrics, 5), 2, 'normal playback');
assert.equal(activeLyricIndex(lyrics, 9), -1, 'instrumental or unresolved gap');
assert.equal(activeLyricIndex(lyrics, 12.5), 4, 'seek forward across a gap');
assert.equal(activeLyricIndex(lyrics, 3), 1, 'seek backward');
assert.equal(activeLyricIndex(lyrics, 20), -1, 'outro');
assert.equal(activeLyricIndex([{ start: 2 }, { start: 4 }], 3), 0, 'legacy start-only timing');
console.log('Timing playback checks passed.');

// Exercise every imported onset through the actual playback lookup, including
// backward seeks and mixed-language/section rows.
const { readFileSync } = await import('node:fs');
const album = JSON.parse(readFileSync(new URL('../dist/album.json', import.meta.url)));
let checked = 0;
for (const track of album.tracks) {
  for (let i = track.lyrics.length - 1; i >= 0; i--) {
    const line = track.lyrics[i];
    if (!Number.isFinite(line.start)) continue;
    assert.equal(activeLyricIndex(track.lyrics, line.start + .001), i, `track ${track.id}, line ${i}`);
    checked++;
  }
}
assert.ok(checked > 3000, 'album timing coverage');
console.log(`${checked} imported lyric onsets resolve to the correct row.`);
