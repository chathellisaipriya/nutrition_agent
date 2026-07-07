/* ─────────────────────────────────────────────────────────────────────────
   NutriSage AI  —  app.js
   Handles: dark/light mode toggle, active nav highlighting, global alerts.
   Page-specific logic lives in each template's {% block scripts %} section.
   ───────────────────────────────────────────────────────────────────────── */

/* ── Dark / Light mode ────────────────────────────────────────────────────── */
(function () {
  const html       = document.documentElement;
  const toggleBtn  = document.getElementById("themeToggle");
  const themeIcon  = document.getElementById("themeIcon");
  const STORAGE_KEY = "nutrisage-theme";

  function applyTheme(theme) {
    html.setAttribute("data-bs-theme", theme);
    if (themeIcon) {
      themeIcon.className = theme === "dark"
        ? "bi bi-sun-fill"
        : "bi bi-moon-stars-fill";
    }
    localStorage.setItem(STORAGE_KEY, theme);
  }

  // Initialise from storage or system preference
  const saved = localStorage.getItem(STORAGE_KEY);
  const preferred = window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark" : "light";
  applyTheme(saved || preferred);

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const current = html.getAttribute("data-bs-theme");
      applyTheme(current === "dark" ? "light" : "dark");
    });
  }
})();

/* ── Active nav link ──────────────────────────────────────────────────────── */
(function () {
  const path  = window.location.pathname.replace(/\/$/, "") || "/";
  document.querySelectorAll("#mainNav .nav-link").forEach(link => {
    const href = link.getAttribute("href").replace(/\/$/, "") || "/";
    if (href === path || (href !== "/" && path.startsWith(href))) {
      link.classList.add("active");
    }
  });
})();

/* ── Global helpers ───────────────────────────────────────────────────────── */
function showAlert(message, type = "info", autoDismiss = 5000) {
  const area = document.getElementById("alertArea");
  if (!area) return;
  const id  = "alert-" + Date.now();
  const div = document.createElement("div");
  div.id    = id;
  div.className = `alert alert-${type} alert-dismissible fade show`;
  div.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
  area.appendChild(div);
  if (autoDismiss) setTimeout(() => {
    const el = document.getElementById(id);
    if (el) el.remove();
  }, autoDismiss);
}
