// Alertas. Lee el JSON que el workflow "Recolectar alertas" publica en la rama `datos`
// y lo muestra en el navegador, sin servidor. La provincia elegida se guarda solo en este navegador.
(function () {
  var script = document.currentScript;
  var lista = document.getElementById("alertas");
  var resumen = document.getElementById("alertas-resumen");
  var fuentes = document.getElementById("alertas-fuentes");
  var filtroTipo = document.getElementById("filtro-tipo");
  var filtroProvincia = document.getElementById("filtro-provincia");
  var base = script.getAttribute("data-base");
  var datos = [];

  var NOMBRES = {
    imn: "IMN (avisos del clima)", rsn: "Red Sismológica Nacional (sismos sentidos)", usgs: "USGS (sismos fuertes)",
    gdacs: "GDACS (desastres)", cnfl: "CNFL (cortes de luz)", jasec: "JASEC (cortes de luz en Cartago)"
  };
  var ICONOS = { agua: "💧", luz: "💡", carretera: "🚧", sismo: "🌎", clima: "🌧️", volcan: "🌋", otro: "⚠️" };

  function fecha(iso) {
    if (!iso) return "";
    return new Date(iso).toLocaleString("es-CR", { timeZone: "America/Costa_Rica", dateStyle: "medium", timeStyle: "short" });
  }

  function hace(iso) {
    var min = Math.round((Date.now() - new Date(iso)) / 60000);
    if (min < 60) return "hace " + min + " min";
    var h = Math.round(min / 60);
    return h < 48 ? "hace " + h + " h" : "hace " + Math.round(h / 24) + " días";
  }

  function el(etiqueta, clase, texto) {
    var e = document.createElement(etiqueta);
    if (clase) e.className = clase;
    if (texto) e.textContent = texto;
    return e;
  }

  function guardar(clave, valor) { try { localStorage.setItem(clave, valor); } catch (e) {} }
  function leer(clave) { try { return localStorage.getItem(clave) || ""; } catch (e) { return ""; } }

  function mostrar() {
    var tipo = filtroTipo.value, provincia = filtroProvincia.value;
    guardar("alertas-provincia", provincia);
    var visibles = datos.filter(function (a) {
      // Las alertas sin provincia (sismos, avisos nacionales) se muestran siempre.
      return (!tipo || a.tipo === tipo) && (!provincia || !a.zona.provincia || a.zona.provincia === provincia);
    });
    lista.textContent = "";
    resumen.textContent = visibles.length ? visibles.length + (visibles.length === 1 ? " alerta" : " alertas") : "No hay alertas activas con ese filtro en las fuentes que revisamos.";
    visibles.forEach(function (a) {
      var li = el("li", "alerta alerta-" + (a.severidad || "na"));
      var enlace = el("a", null, (ICONOS[a.tipo] || "⚠️") + " " + a.titulo);
      enlace.href = a.fuente.url;
      enlace.rel = "noopener";
      li.appendChild(enlace);
      var cuando = a.inicio ? fecha(a.inicio) + (a.fin ? " a " + fecha(a.fin) : "") : "";
      if (cuando) li.appendChild(el("span", "nota", cuando));
      if (a.descripcion) li.appendChild(el("span", "nota", a.descripcion));
      li.appendChild(el("span", "nota", "Fuente: " + (NOMBRES[a.fuente.institucion] || a.fuente.institucion) + ". Tocá el título para ver el aviso oficial."));
      lista.appendChild(li);
    });
  }

  function mostrarFuentes(estado) {
    fuentes.textContent = "";
    Object.keys(estado.fuentes).forEach(function (k) {
      var e = estado.fuentes[k];
      fuentes.appendChild(el("li", null, (e.ok ? "✅ " : "❌ ") + (NOMBRES[k] || k) + ": " +
        (e.ok ? "revisada " + hace(e.revisado) : "no respondió en la última revisión (" + hace(e.revisado) + ")")));
    });
  }

  function json(url) {
    return fetch(url, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    });
  }

  filtroProvincia.value = leer("alertas-provincia");
  filtroTipo.addEventListener("change", mostrar);
  filtroProvincia.addEventListener("change", mostrar);

  json(base + "activas.json").then(function (d) {
    datos = d.alertas;
    mostrar();
    resumen.textContent += ". Actualizado " + hace(d.generado) + ".";
  }).catch(function () {
    resumen.textContent = "No pudimos cargar las alertas en este momento. Revisá los sitios oficiales de abajo.";
  });
  json(base + "estado.json").then(mostrarFuentes).catch(function () {});
})();
