(() => {
  const form = document.querySelector("[data-article-search]");
  const input = form.querySelector("input");
  const clear = form.querySelector('button[type="reset"]');
  const browse = document.querySelector("[data-search-browse]");
  const results = document.querySelector("[data-search-results]");
  const status = results.querySelector('[role="status"]');
  const list = results.querySelector("ul");
  const normalize = text => text.normalize("NFKC").toLowerCase();

  let index;
  let revision = 0;
  let timer;

  function loadIndex() {
    if (!index) {
      index = fetch("/search-index.json").then(async response => {
        if (!response.ok) throw new Error("Search index unavailable");
        const articles = await response.json();
        return articles.map(article => ({
          ...article,
          searchable: normalize([
            article.title, article.originalTitle, article.body, article.summary, article.source,
            ...article.topics,
          ].join(" ")),
        }));
      }).catch(error => {
        index = undefined;
        throw error;
      });
    }
    return index;
  }

  function renderArticle(article) {
    const item = document.createElement("li");
    item.className = "entry";

    const time = document.createElement("time");
    time.className = "entry-date";
    time.dateTime = article.date;
    time.textContent = article.date;

    const details = document.createElement("article");
    const heading = document.createElement("h2");
    heading.className = "entry-title";
    const link = document.createElement("a");
    link.href = article.url;
    link.textContent = article.title;
    heading.append(link);

    const source = document.createElement("p");
    source.className = "entry-source";
    source.textContent = article.source;
    const summary = document.createElement("p");
    summary.className = "entry-summary";
    summary.textContent = article.summary;

    details.append(heading, source, summary);
    item.append(time, details);
    return item;
  }

  async function search() {
    const current = ++revision;
    const query = normalize(input.value.trim());
    clear.hidden = !query;
    results.hidden = !query;
    list.replaceChildren();
    if (!query) {
      browse.hidden = false;
      status.textContent = "";
      return;
    }

    try {
      browse.hidden = true;
      status.textContent = "正在搜索…";
      const articles = await loadIndex();
      if (current !== revision) return;
      const terms = query.split(/\s+/);
      const matches = articles.filter(article => terms.every(term => article.searchable.includes(term)));
      list.replaceChildren(...matches.map(renderArticle));
      status.textContent = matches.length ? `找到 ${matches.length} 篇文章` : "没有找到匹配的文章。";
    } catch {
      if (current !== revision) return;
      browse.hidden = false;
      status.textContent = "暂时无法搜索，请重试。";
    }
  }

  function searchSoon() {
    window.clearTimeout(timer);
    timer = window.setTimeout(search, 150);
  }

  form.addEventListener("submit", event => {
    event.preventDefault();
    window.clearTimeout(timer);
    search();
  });
  form.addEventListener("reset", event => {
    event.preventDefault();
    input.value = "";
    window.clearTimeout(timer);
    search();
    input.focus();
  });
  input.addEventListener("input", event => {
    if (!event.isComposing) searchSoon();
  });
  input.addEventListener("compositionend", searchSoon);
  form.hidden = false;
})();
