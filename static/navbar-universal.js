(() => {
  const NAVBAR_CONTAINER_ID = "navbar-container";
  const NAVBAR_COMPONENT_URL = "/static/modern-navbar-component.html";

  function ensureNavbarContainer() {
    let container = document.getElementById(NAVBAR_CONTAINER_ID);
    if (!container) {
      container = document.createElement("div");
      container.id = NAVBAR_CONTAINER_ID;
      document.body.prepend(container);
    }
    return container;
  }

  function removeLegacyNavbars() {
    const selectors = [
      ".floating-navbar-container",
      "nav.navbar:not(.modern-navbar)",
      "nav.floating-navbar:not(.modern-navbar)",
    ];
    selectors.forEach((selector) => {
      document.querySelectorAll(selector).forEach((el) => {
        if (!el.closest(".modern-navbar")) {
          el.remove();
        }
      });
    });
  }

  async function loadUniversalNavbar() {
    const container = ensureNavbarContainer();
    if (container.querySelector(".modern-navbar")) {
      return;
    }

    removeLegacyNavbars();

    try {
      const resp = await fetch(NAVBAR_COMPONENT_URL, { cache: "no-cache" });
      if (!resp.ok) {
        throw new Error(`Navbar fetch failed: ${resp.status}`);
      }
      container.innerHTML = await resp.text();
    } catch (err) {
      console.error("Failed to load universal navbar:", err);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadUniversalNavbar);
  } else {
    loadUniversalNavbar();
  }
})();
