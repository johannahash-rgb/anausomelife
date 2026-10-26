'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const {parseHTML} = require('linkedom');
const source = fs.readFileSync(require.resolve('../assets/reading-ease.js'), 'utf8');

function setup(hash = '') {
  const {window, document} = parseHTML('<html><body><main><details id="outer" data-reading-ease="worksheet"><summary>Checklist</summary><details id="inner"><summary>Instructions</summary><h2 id="instructions">Instructions</h2></details></details><details id="related" data-reading-ease="related"><summary>Related topics</summary><p>More reading</p></details></main></body></html>');
  Object.defineProperty(window.HTMLElement.prototype, 'open', {configurable: true, get() {return this.hasAttribute('open');}, set(value) {this.toggleAttribute('open', value);}});
  window.HTMLElement.prototype.scrollIntoView = function() {this.scrolled = true;};
  window.HTMLElement.prototype.focus = function() {document._focus = this;};
  const events = {};
  vm.runInNewContext(source, {document, window: {addEventListener: (type, fn) => {events[type] = fn;}}, location: new URL('https://anausomelife.com/guide.html' + hash), requestAnimationFrame: fn => fn(), MutationObserver: window.MutationObserver, setTimeout});
  return {document, window, events, get: id => document.getElementById(id)};
}

test('a deep link reveals every enclosing disclosure and the requested heading', () => {
  const {get} = setup('#instructions');
  assert.equal(get('outer').open, true);
  assert.equal(get('inner').open, true);
  assert.equal(get('instructions').scrolled, true);
  assert.equal(get('related').open, false);
});

test('printing restores prior disclosure state; Escape returns focus to its summary', () => {
  const {document, window, events, get} = setup();
  get('outer').open = true;
  events.beforeprint();
  assert.equal(get('related').open, true);
  events.afterprint();
  assert.equal(get('outer').open, true);
  assert.equal(get('related').open, false);
  const key = new window.Event('keydown', {bubbles: true, cancelable: true});
  key.key = 'Escape';
  get('outer').dispatchEvent(key);
  assert.equal(get('outer').open, false);
  assert.equal(document._focus, get('outer').querySelector('summary'));
});
