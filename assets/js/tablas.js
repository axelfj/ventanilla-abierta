// Tablas anchas en celular: se deslizan hacia el lado, pero a simple vista no se nota.
// Si una tabla no cabe, se le agrega un aviso arriba y se deja enfocar con el teclado para poder deslizarla con las flechas.
(function () {
  var tablas = document.querySelectorAll("main table");
  if (!tablas.length) return;

  tablas.forEach(function (tabla, i) {
    tabla.nombre = "Tabla " + (i + 1) + ", se desliza hacia el lado";
    var aviso = document.createElement("p");
    aviso.className = "aviso-tabla";
    aviso.setAttribute("aria-hidden", "true");
    aviso.textContent = "↔ Deslizá la tabla hacia el lado para ver todas las columnas.";
    aviso.hidden = true;
    tabla.parentNode.insertBefore(aviso, tabla);
    tabla.aviso = aviso;
  });

  function revisar() {
    tablas.forEach(function (tabla) {
      var ancha = tabla.scrollWidth > tabla.clientWidth + 1;
      tabla.aviso.hidden = !ancha;
      if (ancha) {
        tabla.tabIndex = 0;
        tabla.setAttribute("role", "region");
        tabla.setAttribute("aria-label", tabla.nombre);
      } else {
        tabla.removeAttribute("tabindex");
        tabla.removeAttribute("role");
        tabla.removeAttribute("aria-label");
      }
    });
  }

  revisar();
  var espera;
  window.addEventListener("resize", function () {
    clearTimeout(espera);
    espera = setTimeout(revisar, 150);
  });
})();
