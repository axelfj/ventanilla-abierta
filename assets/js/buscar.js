// Buscador de guías. Lee el índice que genera Jekyll (buscar.json) y busca en el navegador, sin servidor.
(function () {
  var script = document.currentScript;
  var entrada = document.getElementById("q");
  var resumen = document.getElementById("resumen");
  var lista = document.getElementById("resultados");
  var indice = null;

  // Minúsculas y sin tildes, para que "credito" encuentre "crédito".
  // Cambia cada letra por una sola, así las posiciones calzan con el texto original (para el extracto).
  function normalizar(texto) {
    return (texto || "").replace(/[^\u0000-\u007f]/g, function (c) { return c.normalize("NFD")[0]; }).toLowerCase();
  }

  function extracto(texto, termino) {
    var i = normalizar(texto).indexOf(termino);
    if (i < 0) return texto.slice(0, 160) + "…";
    var inicio = Math.max(0, i - 60);
    return (inicio > 0 ? "…" : "") + texto.slice(inicio, inicio + 180) + "…";
  }

  function buscar(consulta) {
    var terminos = normalizar(consulta).split(/\s+/).filter(function (t) { return t.length > 1; });
    lista.textContent = "";
    if (!terminos.length) { resumen.textContent = ""; return; }

    var resultados = indice.map(function (g) {
      var titulo = normalizar(g.titulo), texto = normalizar(g.texto), puntos = 0;
      for (var k = 0; k < terminos.length; k++) {
        var t = terminos[k];
        var enTitulo = titulo.indexOf(t) >= 0;
        var veces = texto.split(t).length - 1;
        if (!enTitulo && !veces) return null; // cada palabra tiene que aparecer en algún lado
        puntos += (enTitulo ? 20 : 0) + Math.min(veces, 10);
      }
      return { guia: g, puntos: puntos };
    }).filter(Boolean).sort(function (a, b) { return b.puntos - a.puntos; });

    resumen.textContent = resultados.length
      ? resultados.length + (resultados.length === 1 ? " guía encontrada." : " guías encontradas.")
      : "No encontramos guías con esas palabras. Probá con otras o pedí un trámite nuevo.";

    resultados.forEach(function (r) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = r.guia.url;
      a.textContent = r.guia.titulo;
      var nota = document.createElement("span");
      nota.className = "nota";
      nota.textContent = r.guia.estado === "planeado"
        ? "📝 Planeado: todavía no hay guía. Entrá a la categoría para pedirla o ayudar a escribirla."
        : (r.guia.estado === "verificado" ? "✅ " : "⚠️ ") + extracto(r.guia.texto, terminos[0]);
      li.appendChild(a);
      li.appendChild(nota);
      lista.appendChild(li);
    });
  }

  var inicial = new URLSearchParams(location.search).get("q") || "";
  entrada.value = inicial;
  resumen.textContent = "Cargando…";

  fetch(script.getAttribute("data-indice"))
    .then(function (r) { return r.json(); })
    .then(function (datos) {
      indice = datos.filter(Boolean); // el índice termina en null para que el JSON sea válido
      resumen.textContent = "";
      buscar(entrada.value);
      var espera;
      entrada.addEventListener("input", function () {
        clearTimeout(espera);
        espera = setTimeout(function () {
          buscar(entrada.value);
          history.replaceState(null, "", entrada.value ? "?q=" + encodeURIComponent(entrada.value) : location.pathname);
        }, 150);
      });
      entrada.form.addEventListener("submit", function (e) { e.preventDefault(); buscar(entrada.value); });
    })
    .catch(function () { resumen.textContent = "No se pudo cargar el buscador. Probá recargar la página."; });
})();
