(() => {
  'use strict';
  const archives = new Set(['downloadgameps3.net', 'www.downloadgameps3.net']);
  const sourceHosts = new Set(['dlpsgame.com', 'www.dlpsgame.com']);
  const originals = new WeakMap();
  const captured = new WeakMap();
  const blockedExtensions = /\.(?:pkg|iso|rar|zip|7z|exe|msi)(?:$|[?#])/i;
  let timer, panel, panelBody, currentSignature = '', repaired = 0;

  function safeURL(value, base = location.href) {
    try {
      const u = new URL(value, base);
      if (!['https:', 'http:'].includes(u.protocol) || u.username || u.password) return null;
      if (/^(localhost|127\.|0\.0\.0\.0|\[::1\])/.test(u.hostname)) return null;
      return u;
    } catch { return null; }
  }

  function unwrap(value) {
    const u = safeURL(value);
    if (!u || !['clk.sh', 'www.clk.sh'].includes(u.hostname) || !/^\/full\/?$/.test(u.pathname)) return null;
    // Raw query extraction preserves '+' used by the Base64 encoding in the public script.
    const match = u.search.match(/[?&]url=([^&]*)/);
    if (!match) return null;
    try {
      const bytes = Uint8Array.from(atob(decodeURIComponent(match[1])), c => c.charCodeAt(0));
      const destination = safeURL(new TextDecoder('utf-8', { fatal: true }).decode(bytes));
      if (!destination || ['clk.sh', 'www.clk.sh'].includes(destination.hostname)) return null;
      return destination;
    } catch { return null; }
  }

  const currentDestination = unwrap(location.href);
  if (currentDestination && archives.has(currentDestination.hostname) && /^\/archives\/\d+\/?$/.test(currentDestination.pathname)) {
    location.replace(currentDestination.href);
    return;
  }

  function decode(value) {
    try {
      const bytes = Uint8Array.from(atob(value), c => c.charCodeAt(0));
      // Template contents are inert: no insertion of the site's decoded HTML into the live document.
      const template = document.createElement('template');
      template.innerHTML = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
      return template.content;
    } catch { return null; }
  }

  function rememberPayload(node, value) {
    if (!(node instanceof Element) || !value || !node.matches('.secure-data')) return;
    const content = decode(value);
    if (content) captured.set(node, content);
  }

  function repair(anchor, oldValue) {
    if (!anchor.matches('a[href]')) return;
    const current = anchor.getAttribute('href');
    const previous = safeURL(oldValue);
    if (!originals.has(anchor) && previous && unwrap(current) && !unwrap(previous.href)) {
      // Only keep a previous href when it agrees with the wrapper's documented destination.
      if (unwrap(current).href === previous.href) originals.set(anchor, previous.href);
    }
    const destination = unwrap(current);
    if (!destination) return;
    anchor.setAttribute('href', destination.href);
    originals.set(anchor, destination.href);
    repaired++;
    anchor.title = 'Destino público recuperado do parâmetro Base64 de clk.sh';
  }

  function scan(node) {
    if (!(node instanceof Element)) return;
    if (node.matches('.secure-data[data-payload]')) rememberPayload(node, node.getAttribute('data-payload'));
    for (const n of node.querySelectorAll('.secure-data[data-payload]')) rememberPayload(n, n.getAttribute('data-payload'));
    if (node.matches('a[href]')) repair(node);
    for (const a of node.querySelectorAll('a[href]')) repair(a);
  }

  function text(node) { return node?.textContent?.replace(/\s+/g, ' ').trim() || ''; }
  function element(tag, value) {
    const e = document.createElement(tag);
    if (value !== undefined) e.textContent = value;
    return e;
  }

  function collect() {
    const root = document.querySelector('.entry-content') || document.querySelector('article') || document;
    const options = [];
    for (const spoiler of root.querySelectorAll('.su-spoiler')) {
      const button = text(spoiler.querySelector('.su-spoiler-title'));
      if (!/link\s+(download|mirror)/i.test(button)) continue;
      let heading = '';
      for (let n = spoiler.previousElementSibling; n; n = n.previousElementSibling) {
        if (!n.classList.contains('su-spoiler') && /\bCUSA\d+\b/.test(text(n))) { heading = text(n); break; }
      }
      const secure = spoiler.querySelector('.secure-data');
      const content = (secure && captured.get(secure)) || spoiler.querySelector('.su-spoiler-content') || spoiler;
      const rows = [];
      for (const row of content.querySelectorAll('p,li,tr')) {
        const label = text(row).split(':')[0].trim();
        if (!/^(game\b|base game\b|update\b|dlc\b)/i.test(label)) continue;
        const links = [];
        for (const anchor of row.querySelectorAll('a[href]')) {
          const raw = anchor.getAttribute('href');
          const url = unwrap(raw) || safeURL(raw);
          if (url) links.push({ label: text(anchor) || url.hostname, url: url.href });
        }
        if (links.length) rows.push({ label, links });
      }
      if (rows.length) options.push({ heading: heading || 'Edição não informada', button, rows });
    }
    return options;
  }

  function update() {
    if (!document.body) return;
    const options = collect();
    const isSource = sourceHosts.has(location.hostname);
    // At the destination, unwrap links in place. Do not mistake a generic page for a confirmed game identity.
    if (!isSource || !options.length) return;
    const signature = JSON.stringify(options);
    if (signature === currentSignature && panel?.isConnected) return;
    currentSignature = signature;
    if (!panel?.isConnected) {
      panel = element('div');
      panel.id = 'dlps-direct-links-extension';
      const shadow = panel.attachShadow({ mode: 'open' });
      shadow.addEventListener('click', event => event.stopPropagation());
      shadow.addEventListener('auxclick', event => event.stopPropagation());
      const style = element('style', `
        :host{all:initial;position:fixed;bottom:16px;right:16px;z-index:2147483647;font:14px/1.5 system-ui,sans-serif;color:#17202a}
        details.outer{width:min(470px,calc(100vw - 32px));background:#fff;border:2px solid #137752;border-radius:12px;box-shadow:0 8px 35px #0004}
        summary{cursor:pointer;padding:12px;font-weight:700} .body{max-height:65vh;overflow:auto;padding:0 14px 14px}
        p{margin:8px 0}small{display:block;color:#48545d}.edition{border-top:1px solid #ddd;margin-top:12px} .edition summary{padding:10px 0}
        h4{margin:12px 0 4px}a{display:inline-block;color:#075caa;margin:2px 12px 2px 0;overflow-wrap:anywhere}a:focus{outline:2px solid #137752}
      `);
      shadow.append(style);
      const outer = element('details'); outer.className = 'outer';
      outer.append(element('summary', 'DLPS · Links diretos'));
      panelBody = element('div'); panelBody.className = 'body'; outer.append(panelBody);
      shadow.append(outer); document.body.append(panel);
    }
    panelBody.replaceChildren();
    panelBody.append(element('p', `${options.length} opções recuperadas do conteúdo público da página.`));
    panelBody.append(element('small', 'Vínculo declarado pela origem. Disponibilidade e identidade no destino não verificadas. Cloudflare ou CAPTCHA no destino ainda podem aparecer.'));
    for (const option of options) {
      const section = element('details'); section.className = 'edition';
      section.append(element('summary', `${option.heading} · ${option.button}`));
      for (const row of option.rows) {
        section.append(element('h4', row.label));
        for (const link of row.links) {
          const a = element('a', link.label); a.href = link.url; a.target = '_blank'; a.rel = 'noopener noreferrer';
          a.title = `${link.url}\nEvidência: botão ${option.button} → ${row.label} → href publicado`;
          if (blockedExtensions.test(link.url)) a.title += '\nAtenção: URL aparenta ser de arquivo; abrir pode iniciar download.';
          section.append(a);
        }
      }
      panelBody.append(section);
    }
  }

  const observer = new MutationObserver(records => {
    let relevant = false;
    for (const record of records) {
      if (record.target === panel) continue;
      if (record.type === 'attributes') {
        if (record.attributeName === 'href') { repair(record.target, record.oldValue); relevant = true; }
        if (record.attributeName === 'data-payload') {
          rememberPayload(record.target, record.target.getAttribute('data-payload') || record.oldValue); relevant = true;
        }
      } else {
        for (const node of record.addedNodes) if (node !== panel) { scan(node); relevant = true; }
      }
    }
    if (relevant) { clearTimeout(timer); timer = setTimeout(update, 120); }
  });
  observer.observe(document, { subtree: true, childList: true, attributes: true, attributeOldValue: true, attributeFilter: ['href', 'data-payload'] });
  // Capture handler runs before the site's usual click handlers; default navigation keeps modifiers and mouse behavior.
  document.addEventListener('click', event => {
    const a = event.target instanceof Element ? event.target.closest('a[href]') : null;
    if (!a) return;
    const target = unwrap(a.href);
    if (target) { a.href = target.href; originals.set(a, target.href); }
    if (target || originals.has(a)) event.stopImmediatePropagation();
  }, true);
  if (document.documentElement) scan(document.documentElement);
  document.addEventListener('DOMContentLoaded', update, { once: true });
  timer = setTimeout(update, 120);
})();
