(() => {
  document.querySelectorAll('[data-print]').forEach(button => button.addEventListener('click', () => window.print()));
  const input = document.getElementById('guide-search');
  if (input) {
    document.querySelector('[data-search-ui]').hidden = false;
    const cards = [...document.querySelectorAll('.guide-card')];
    const status = document.getElementById('search-status');
    function filter() {
      const query = input.value.trim().toLocaleLowerCase(); let visible = 0;
      cards.forEach(card => { const match = !query || card.textContent.toLocaleLowerCase().includes(query); card.hidden = !match; if(match) visible++; });
      status.textContent = query ? `${visible} ${visible === 1 ? 'guide' : 'guides'} found.` : '';
      document.getElementById('no-results').hidden = visible > 0;
    }
    input.addEventListener('input', filter);
    document.getElementById('clear-search').addEventListener('click', () => { input.value = ''; filter(); input.focus(); });
    window.addEventListener('pageshow', filter);
  }
})();