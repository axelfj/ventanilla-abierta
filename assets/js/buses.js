// Buscador de tarifas de bus. Lee el pliego tarifario de la ARESEP que el workflow
// "Recolectar tarifas de bus" guarda en la rama `datos` y busca en el navegador, sin servidor.
(function () {
  var script = document.currentScript;
  var entrada = document.getElementById("q-bus");
  var resumen = document.getElementById("bus-resumen");
  var lista = document.getElementById("bus-resultados");
  var fuente = document.getElementById("bus-fuente");
  var rutas = [];
  var MAX = 30;

  function normalizar(texto) {
    return (texto || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }

  function colones(n) {
    return n == null ? "sin dato" : "₡" + n.toLocaleString("es-CR", { maximumFractionDigits: 2 });
  }

  function fecha(iso) {
    if (!iso) return "";
    var p = iso.split("-");
    return p[2] + "/" + p[1] + "/" + p[0];
  }

  // "SAN JOSE-HEREDIA POR TIBAS" -> "San Jose-Heredia por Tibas". Los datos de la ARESEP vienen en mayúsculas.
  var MENORES = ["de", "del", "la", "las", "los", "el", "por", "y", "a", "en"];
  function nombre(texto) {
    return texto.toLowerCase().replace(/(^|[\s\-(\/.])([a-zñáéíóú]+)/g, function (m, antes, palabra) {
      return antes + (antes === " " && MENORES.indexOf(palabra) >= 0 ? palabra : palabra[0].toUpperCase() + palabra.slice(1));
    });
  }

  function el(etiqueta, clase, texto) {
    var e = document.createElement(etiqueta);
    if (clase) e.className = clase;
    if (texto) e.textContent = texto;
    return e;
  }

  // Agrupa los tramos por número de ruta, para mostrar una tarjeta por ruta.
  function agrupar(tramos) {
    var porRuta = {};
    tramos.forEach(function (t) {
      var r = porRuta[t.ruta];
      if (!r) {
        r = porRuta[t.ruta] = { ruta: t.ruta, nombre: t.nombre, operadores: [], tramos: [], texto: "" };
        rutas.push(r);
      }
      t.operadores.forEach(function (o) { if (r.operadores.indexOf(o) < 0) r.operadores.push(o); });
      r.tramos.push(t);
      r.texto += " " + [t.ruta, t.nombre, t.ramal, t.tramo, t.operadores.join(" ")].join(" ");
    });
    rutas.forEach(function (r) { r.texto = normalizar(r.texto); r.codigo = normalizar(r.ruta); });
  }

  function buscar() {
    var consulta = normalizar(entrada.value).trim();
    var terminos = consulta.split(/\s+/).filter(function (t) { return t.length > 1 || /\d/.test(t); });
    lista.textContent = "";
    if (!terminos.length) { resumen.textContent = rutas.length + " rutas con tarifa. Escribí un lugar, un número de ruta o una empresa."; return; }
    var hallados = rutas.filter(function (r) {
      return terminos.every(function (t) { return r.texto.indexOf(t) >= 0; });
    });
    // El número de ruta exacto va primero.
    hallados.sort(function (a, b) { return (b.codigo === consulta) - (a.codigo === consulta); });
    resumen.textContent = hallados.length ? hallados.length + (hallados.length === 1 ? " ruta" : " rutas") + (hallados.length > MAX ? "; se muestran las primeras " + MAX + ". Agregá otra palabra para afinar." : ".") : "No encontramos rutas con esas palabras. Probá con el nombre del cantón o del distrito.";
    hallados.slice(0, MAX).forEach(function (r) {
      var li = el("li", "ruta");
      li.appendChild(el("strong", null, "Ruta " + r.ruta + ": " + nombre(r.nombre)));
      if (r.operadores.length) li.appendChild(el("span", "nota", "Empresa: " + r.operadores.map(nombre).join(", ")));
      var tabla = el("table");
      var cab = el("tr");
      ["Tramo", "Tarifa", "Adulto mayor", "Vigente desde"].forEach(function (c) { cab.appendChild(el("th", null, c)); });
      tabla.appendChild(cab);
      r.tramos.forEach(function (t) {
        var fila = el("tr");
        var desc = nombre(t.tramo || t.ramal);
        if (t.ramal && t.ramal !== t.tramo && t.ramal !== r.nombre) desc += " (ramal " + nombre(t.ramal) + ")";
        fila.appendChild(el("td", null, desc));
        fila.appendChild(el("td", null, colones(t.tarifa)));
        fila.appendChild(el("td", null, colones(t.adulto_mayor)));
        var vig = el("td", null, fecha(t.vigente_desde));
        vig.title = "Resolución " + t.resolucion + (t.gaceta ? ", La Gaceta " + t.gaceta + " del " + fecha(t.fecha_gaceta) : "");
        fila.appendChild(vig);
        tabla.appendChild(fila);
      });
      li.appendChild(tabla);
      var res = r.tramos.map(function (t) { return t.resolucion; }).filter(function (v, i, a) { return v && a.indexOf(v) === i; });
      if (res.length) li.appendChild(el("span", "nota", "Fijada por la ARESEP en la resolución " + res.join(", ") + "."));
      lista.appendChild(li);
    });
  }

  fetch(script.getAttribute("data-tarifas"), { cache: "no-cache" }).then(function (r) {
    if (!r.ok) throw new Error(r.status);
    return r.json();
  }).then(function (d) {
    agrupar(d.tramos);
    fuente.textContent = "Datos del pliego tarifario de la ARESEP, descargados el " +
      new Date(d.fuente.recuperado).toLocaleDateString("es-CR", { timeZone: "America/Costa_Rica" }) + ".";
    entrada.disabled = false;
    var q = new URLSearchParams(location.search).get("q");
    if (q) entrada.value = q;
    buscar();
  }).catch(function () {
    resumen.textContent = "No pudimos cargar las tarifas en este momento. Podés consultarlas directo en el sitio de la ARESEP (enlace abajo).";
  });

  // Enter no recarga la página: la búsqueda ya corre mientras se escribe.
  entrada.form.addEventListener("submit", function (e) { e.preventDefault(); buscar(); });

  var espera;
  entrada.addEventListener("input", function () { clearTimeout(espera); espera = setTimeout(buscar, 150); });
})();
