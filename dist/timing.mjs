// Keep lyric highlights inside the aligned vocal interval, including after seeking.
export function activeLyricIndex(lyrics, seconds) {
  let candidate = -1;
  for (let i = 0; i < lyrics.length; i++) {
    const line = lyrics[i];
    if (line.kind === 'section' || !Number.isFinite(line.start)) continue;
    if (line.start > seconds) break;
    candidate = i;
  }
  if (candidate < 0) return -1;
  const line = lyrics[candidate];
  return Number.isFinite(line.end) && seconds >= line.end ? -1 : candidate;
}
