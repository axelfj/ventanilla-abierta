// Botón de sol y luna para cambiar entre modo claro y oscuro.
// Sin elección guardada, el sitio sigue el modo del sistema. Se carga en <head> para aplicar el modo antes de pintar.
(function () {
  var raiz = document.documentElement;
  var sistema = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  function guardado() {
    try { return localStorage.getItem("tema"); } catch (e) { return null; }
  }
  function actual() {
    return raiz.getAttribute("data-tema") || (sistema && sistema.matches ? "oscuro" : "claro");
  }

  var g = guardado();
  if (g === "claro" || g === "oscuro") raiz.setAttribute("data-tema", g);

  function pintarBoton(boton) {
    var oscuro = actual() === "oscuro";
    boton.textContent = oscuro ? "☀️" : "🌙";
    boton.setAttribute("aria-label", oscuro ? "Cambiar a modo claro" : "Cambiar a modo oscuro");
    boton.title = boton.getAttribute("aria-label");
  }

  document.addEventListener("DOMContentLoaded", function () {
    var boton = document.getElementById("cambiar-tema");
    if (!boton) return;
    pintarBoton(boton);
    boton.hidden = false;
    boton.addEventListener("click", function () {
      var nuevo = actual() === "oscuro" ? "claro" : "oscuro";
      raiz.setAttribute("data-tema", nuevo);
      try { localStorage.setItem("tema", nuevo); } catch (e) { /* modo privado: solo dura esta visita */ }
      pintarBoton(boton);
    });
    if (sistema && sistema.addEventListener) {
      sistema.addEventListener("change", function () { pintarBoton(boton); });
    }
  });
})();
