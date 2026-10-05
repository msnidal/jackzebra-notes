// Preserve shared links from the earlier prototype without making fragments the route.
const id=Number(new URLSearchParams(location.hash.slice(1)).get('track'));
const song=document.querySelector(`.catalog-tracks [data-track="${id}"]`);
if(song)location.replace(song.getAttribute('href')+location.search);
