(() => {
  const root = document.documentElement;
  const storageKey = "engineering-reads-theme";
  const systemDark = window.matchMedia("(prefers-color-scheme: dark)");

  function restoreTheme() {
    try {
      const theme = localStorage.getItem(storageKey);
      if (theme === "light" || theme === "dark") {
        root.dataset.theme = theme;
      } else {
        delete root.dataset.theme;
      }
    } catch {
      // The browser may block local storage.
    }
  }

  // Restore the chosen palette before the stylesheet is applied.
  restoreTheme();

  document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector("[data-theme-toggle]");

    function isDark() {
      return root.dataset.theme ? root.dataset.theme === "dark" : systemDark.matches;
    }

    function updateToggle() {
      const label = isDark() ? "日间" : "夜间";
      toggle.textContent = label;
      toggle.setAttribute("aria-label", `切换到${label}模式`);
    }

    toggle.addEventListener("click", () => {
      const theme = isDark() ? "light" : "dark";
      root.dataset.theme = theme;
      updateToggle();
      try {
        localStorage.setItem(storageKey, theme);
      } catch {
        // The theme still applies to the current page.
      }
    });

    window.addEventListener("pageshow", event => {
      if (event.persisted) {
        restoreTheme();
        updateToggle();
      }
    });
    systemDark.addEventListener("change", updateToggle);
    updateToggle();
    toggle.hidden = false;
  });
})();
