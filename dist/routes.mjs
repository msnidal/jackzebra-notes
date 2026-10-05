export const albumPath='/zhuang-zhuang/';
export const slug=t=>t.slug||t.title.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
export const trackPath=t=>`${albumPath}${slug(t)}/`;
export const trackFromPath=(tracks,path)=>tracks.find(t=>trackPath(t)===path.replace(/\/?$/,'/'));
export const pageTitle=t=>`Jackzebra — ${t.title}${t.originalTitle?` (${t.originalTitle})`:''}: Lyrics & English Translation | Jackzebra Notes`;
export const pageDescription=t=>`Read ${t.title} by Jackzebra from Zhuang Zhuang Mixtape: original lyrics, English translation, and notes on language, references, and meaning.`;
