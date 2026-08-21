if (typeof document$ !== "undefined") {
  document$.subscribe(function () {
    if (typeof mermaid !== "undefined") {
      mermaid.initialize({ startOnLoad: true, theme: "neutral" });
    }
  });
}
