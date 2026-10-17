(function () {
  var toggle = document.querySelector(".nav-toggle");
  var menu = document.querySelector(".menu");
  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      var open = menu.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  document.querySelectorAll("[data-acc]").forEach(function (item) {
    var btn = item.querySelector("button");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var was = item.classList.contains("open");
      item.parentElement.querySelectorAll("[data-acc]").forEach(function (el) {
        el.classList.remove("open");
      });
      if (!was) item.classList.add("open");
    });
  });

  document.querySelectorAll("[data-paths]").forEach(function (box) {
    var buttons = box.querySelectorAll(".paths button");
    var panels = box.querySelectorAll("[data-panel]");
    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        var id = button.getAttribute("data-for");
        buttons.forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
        button.setAttribute("aria-pressed", "true");
        panels.forEach(function (panel) {
          panel.hidden = panel.getAttribute("data-panel") !== id;
        });
      });
    });
  });

  document.querySelectorAll("form[data-lead]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var note = form.querySelector(".note");
      if (note) note.classList.add("show");
      form.querySelectorAll("input, select, textarea, button").forEach(function (el) {
        if (el.type !== "button") el.disabled = el.tagName !== "BUTTON" ? false : false;
      });
    });
  });
})();
