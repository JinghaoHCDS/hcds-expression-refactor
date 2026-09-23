// Rasterize authored SVG frames. Install @resvg/resvg-js in a temporary prefix;
// pass its absolute module path to avoid adding runtime dependencies to the Skill.
const fs = require('node:fs');
const path = require('node:path');
const { Resvg } = require(process.argv[2]);
const { execFileSync } = require('node:child_process');
const crypto = require('node:crypto');
let font = {loadSystemFonts: true, defaultFontFamily: 'PingFang SC'};
try {
  const fonts = ['PingFang SC', 'Helvetica Neue'].map(name =>
    execFileSync('fc-match', ['-f', '%{file}', name], {encoding: 'utf8'}).trim());
  if (fonts.every(file => fs.existsSync(file))) font = {
    loadSystemFonts: false, fontFiles: [...new Set(fonts)], defaultFontFamily: 'PingFang SC'
  };
} catch (_) { /* System discovery remains the portable fallback. */ }
const cache = new Map();
// Outline each unique phrase once for rasterization. SVG deliverables retain text.
// The generated frames use only simple <text> nodes (no tspans or text paths).
const textCache = new Map();
function outlineText(svg) {
  return svg.replace(/<text\b([^>]*)>([^<]*)<\/text>/g, (_, attrs, value) => {
    const get = name => attrs.match(new RegExp('(?:^|\\s)' + name + '="([^"]*)"'))?.[1];
    const x = get('x') || '0', y = get('y') || '0';
    const transform = get('transform') || '', opacity = get('opacity') || '1';
    const stable = attrs.replace(/(?:^|\s)(?:x|y|transform|opacity)="[^"]*"/g, '');
    const key = stable + value;
    let geometry = textCache.get(key);
    if (!geometry) {
      const specimen = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620"><g font-family="PingFang SC, Helvetica Neue, sans-serif"><text x="0" y="0" ${stable}>${value}</text></g></svg>`;
      geometry = new Resvg(specimen, {font}).toString().replace(/^<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '');
      textCache.set(key, geometry);
    }
    return `<g transform="${transform}" opacity="${opacity}"><g transform="translate(${x} ${y})">${geometry}</g></g>`;
  });
}
const source = process.argv[3];
const target = process.argv[4];
fs.mkdirSync(target, {recursive: true});
for (const file of fs.readdirSync(source).filter(f => f.endsWith('.svg')).sort()) {
  const svg = fs.readFileSync(path.join(source, file), 'utf8');
  const hash = crypto.createHash('sha256').update(svg).digest('hex');
  let png = cache.get(hash);
  if (!png) {
    png = new Resvg(outlineText(svg), {font: {loadSystemFonts: false}}).render().asPng();
    cache.set(hash, png);
  }
  fs.writeFileSync(path.join(target, file.replace(/\.svg$/, '.png')), png);
}
