/* Deterministic, local-only picture-card renderer. No AI or external API calls. */
(() => {
  'use strict';
  if (window.AALPictureCard) return;

  const NAVY = '#173c4c';
  const PINE = '#2e513f';
  const PAPER = '#fffdf8';

  const clean = value => String(value || '').replace(/\s+/g, ' ').trim();
  const slugify = value => clean(value).toLocaleLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'picture-card';

  function loadImage(src) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.decoding = 'async';
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = src;
    });
  }

  function fitContain(img, x, y, w, h) {
    const ratio = Math.min(w / img.naturalWidth, h / img.naturalHeight);
    const dw = img.naturalWidth * ratio;
    const dh = img.naturalHeight * ratio;
    return { x: x + (w - dw) / 2, y: y + (h - dh) / 2, w: dw, h: dh };
  }

  function wrapLines(ctx, text, maxWidth, maxLines = 2) {
    const words = clean(text).split(' ').filter(Boolean);
    if (!words.length) return [''];
    const lines = [];
    let current = words.shift();
    for (const word of words) {
      const trial = current + ' ' + word;
      if (ctx.measureText(trial).width <= maxWidth || lines.length >= maxLines - 1) {
        current = trial;
      } else {
        lines.push(current);
        current = word;
      }
    }
    lines.push(current);
    if (lines.length > maxLines) {
      const overflow = lines.splice(maxLines - 1).join(' ');
      lines[maxLines - 1] = overflow;
    }
    return lines.slice(0, maxLines);
  }

  async function render({ image, label, place = '', description = '' }) {
    const src = clean(image);
    const word = clean(label);
    if (!src || !word) throw new Error('Picture and label are required.');

    const img = await loadImage(src);
    const canvas = document.createElement('canvas');
    canvas.width = 1200;
    canvas.height = 1200;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, 1200, 1200);

    ctx.strokeStyle = NAVY;
    ctx.lineWidth = 14;
    ctx.strokeRect(16, 16, 1168, 1168);

    ctx.strokeStyle = PINE;
    ctx.lineWidth = 3;
    ctx.strokeRect(34, 34, 1132, 1132);

    const imageBox = { x: 74, y: 72, w: 1052, h: 770 };
    ctx.fillStyle = PAPER;
    ctx.fillRect(imageBox.x, imageBox.y, imageBox.w, imageBox.h);
    const fitted = fitContain(img, imageBox.x, imageBox.y, imageBox.w, imageBox.h);
    ctx.drawImage(img, fitted.x, fitted.y, fitted.w, fitted.h);

    ctx.beginPath();
    ctx.moveTo(74, 878);
    ctx.lineTo(1126, 878);
    ctx.strokeStyle = NAVY;
    ctx.lineWidth = 3;
    ctx.stroke();

    const maxLabelWidth = 1010;
    let fontSize = word.length > 34 ? 58 : 74;
    let lines = [];
    for (; fontSize >= 46; fontSize -= 2) {
      ctx.font = `700 ${fontSize}px Arial, Helvetica, sans-serif`;
      lines = wrapLines(ctx, word, maxLabelWidth, 2);
      if (lines.every(line => ctx.measureText(line).width <= maxLabelWidth)) break;
    }

    ctx.fillStyle = NAVY;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const labelY = place ? 965 : 1005;
    const gap = fontSize * 1.05;
    const startY = labelY - ((lines.length - 1) * gap) / 2;
    lines.forEach((line, i) => ctx.fillText(line, 600, startY + i * gap));

    if (place) {
      ctx.font = '400 34px Arial, Helvetica, sans-serif';
      ctx.fillStyle = '#52656c';
      ctx.fillText(clean(place), 600, 1102);
    }

    canvas.setAttribute('aria-label', description ? `${word}: ${clean(description)}` : word);
    return canvas;
  }

  async function download(options) {
    const canvas = await render(options);
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
    if (!blob) throw new Error('Could not prepare PNG.');
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${slugify(options.label)}-picture-card.png`;
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
    return true;
  }

  window.AALPictureCard = { render, download, slugify };
})();
