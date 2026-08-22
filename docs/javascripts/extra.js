(function () {
  "use strict";

  /* Legacy article links used *.md — redirect to canonical MkDocs URLs. */
  if (/\.md$/i.test(location.pathname) && location.pathname.includes("/articles/")) {
    location.replace(
      location.pathname.replace(/\.md$/i, "/") + location.search + location.hash
    );
    return;
  }

  function enhanceLayout() {
    const path = document.location.pathname.replace(/\/$/, "");
    const isArticle = path.includes("/articles/") && !path.endsWith("/articles");
    const isBlogIndex = path.endsWith("/articles") || path.endsWith("/articles/index");

    if (isArticle || isBlogIndex) {
      document.body.classList.add("kl-article-page");
    }

    document.querySelectorAll(".md-nav--secondary .md-nav__title").forEach(function (el) {
      const text = (el.textContent || "").trim();
      if (text === "Table of contents" || text.includes("Table of contents")) {
        el.lastChild && (el.lastChild.textContent = " On this page");
        if (!el.lastChild) el.textContent = "On this page";
      }
    });

    const header = document.querySelector(".md-header__inner");
    if (header && !document.querySelector(".kl-header-cta")) {
      const cta = document.createElement("a");
      cta.href = "https://github.com/kramlipi/code-agent-binaries/releases";
      cta.className = "kl-header-cta";
      cta.textContent = "Download";
      cta.title = "Download code-agent binary";
      const repo = header.querySelector(".md-header__source");
      if (repo) header.insertBefore(cta, repo);
      else header.appendChild(cta);
    }
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(function () {
      enhanceLayout();
      if (typeof mermaid !== "undefined") {
        mermaid.initialize({ startOnLoad: true, theme: "dark" });
      }
    });
  } else {
    document.addEventListener("DOMContentLoaded", enhanceLayout);
  }
})();
