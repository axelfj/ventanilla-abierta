// Filtra las tablas de carreras mientras la persona escribe. Ignora tildes y mayúsculas.
(function () {
  var campo = document.getElementById("q-carrera");
  if (!campo) return;
  var resumen = document.getElementById("carrera-resumen");
  var filas = Array.prototype.slice.call(document.querySelectorAll(".carreras tbody tr"));
  function limpiar(t) {
    return t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }
  filas.forEach(function (f) { f.setAttribute("data-texto", limpiar(f.textContent)); });
  campo.disabled = false;
  campo.addEventListener("input", function () {
    var palabras = limpiar(campo.value).split(/\s+/).filter(Boolean);
    var vistas = 0;
    filas.forEach(function (f) {
      var texto = f.getAttribute("data-texto");
      var ok = palabras.every(function (p) { return texto.indexOf(p) !== -1; });
      f.hidden = !ok;
      if (ok) vistas++;
    });
    document.querySelectorAll(".carreras").forEach(function (t) {
      var bloque = t.closest("details");
      if (bloque && palabras.length) bloque.open = !!t.querySelector("tbody tr:not([hidden])");
    });
    resumen.textContent = palabras.length ? vistas + " carrera(s) encontradas." : "";
  });
})();
