// Buscador de guías. Lee el índice que genera Jekyll (buscar.json) y busca en el navegador, sin servidor.
// Entiende frases como las escribe la gente: ignora palabras vacías ("me", "de"), compara por raíz
// ("despidieron" encuentra "despido") y usa los sinónimos de _data/sinonimos.yml ("la Caja" = CCSS).
// La parte de búsqueda no toca la página, así scripts/probar-buscador.js la prueba con Node.
(function () {
  "use strict";

  var VACIAS = (
    "a al ante bajo con contra de del desde el en entre es esta este hay la las le les lo los me mi mis muy " +
    "nos o para pero por que se si sin sobre su sus te tu tus un una unas uno unos y ya yo vos usted no " +
    "como cual cuales cuando cuanto cuanta cuantos cuantas donde quien quiero quiere quieren necesito " +
    "necesita tengo tiene tienen puedo puede debo debe hago hacer hacen toca tocan ser estoy esta estan algo"
  ).split(" ");

  var SUFIJOS = ["amientos", "imientos", "aciones", "iciones", "amiento", "imiento", "ieron", "aron", "iendo",
    "ando", "acion", "icion", "ados", "idos", "adas", "idas", "ado", "ido", "ada", "ida", "emos", "amos",
    "ar", "er", "ir", "es", "as", "os", "an", "en", "a", "e", "o", "s"];

  // Minúsculas y sin tildes, para que "credito" encuentre "crédito".
  // Cambia cada letra por una sola, así las posiciones calzan con el texto original (para el extracto).
  function normalizar(texto) {
    return (texto || "").replace(/[^\u0000-\u007f]/g, function (c) { return c.normalize("NFD")[0]; }).toLowerCase();
  }

  // Raíz aproximada de una palabra ya normalizada: "despidieron" y "despido" quedan en "despid".
  function raizDe(p) {
    p = p.replace(/(ar|er|ir)(me|te|se|lo|la|le|nos|los|las|les)$/, "$1"); // divorciarme -> divorciar
    for (var i = 0; i < SUFIJOS.length; i++) {
      var s = SUFIJOS[i];
      if (p.length - s.length >= 5 && p.slice(-s.length) === s) return p.slice(0, -s.length);
    }
    return p;
  }

  function escapar(t) { return t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

  // Una palabra suelta busca por raíz al inicio de palabra; una frase ("salida de menores") busca tal cual.
  function patron(termino) {
    termino = normalizar(termino).trim();
    var cuerpo = termino.indexOf(" ") >= 0 ? escapar(termino) : escapar(raizDe(termino));
    return new RegExp("(^|[^a-z0-9])" + cuerpo, "g");
  }

  function preparar(datos) {
    var sinonimos = (datos.sinonimos || []).map(function (s) {
      return { frase: " " + normalizar(s.frase).trim() + " ", buscar: s.buscar.map(patron), peso: normalizar(s.frase).trim().split(/\s+/).length };
    }).sort(function (a, b) { return b.frase.length - a.frase.length; }); // primero las frases largas
    var guias = (datos.guias || []).filter(Boolean).map(function (g) {
      return { guia: g, titulo: normalizar(g.titulo), texto: normalizar(g.texto) };
    });
    return { sinonimos: sinonimos, guias: guias };
  }

  // Convierte la consulta en "conceptos": cada uno se cumple si la guía tiene cualquiera de sus patrones.
  function conceptos(indice, consulta) {
    var q = " " + normalizar(consulta).replace(/[^a-z0-9ñ]+/g, " ").trim() + " ";
    var lista = [];
    indice.sinonimos.forEach(function (s) {
      if (q.indexOf(s.frase) >= 0) {
        lista.push({ patrones: s.buscar, peso: s.peso });
        q = q.split(s.frase).join(" ");
      }
    });
    q.split(/\s+/).forEach(function (p) {
      if (p.length > 1 && VACIAS.indexOf(p) < 0) lista.push({ patrones: [patron(p)], peso: 1 });
    });
    return lista;
  }

  function contar(re, texto) { re.lastIndex = 0; var n = 0; while (re.exec(texto)) n++; return n; }

  function buscar(indice, consulta) {
    var cs = conceptos(indice, consulta);
    if (!cs.length) return [];
    var resultados = indice.guias.map(function (g) {
      var cubre = 0, puntos = 0;
      cs.forEach(function (c) {
        var mejor = 0;
        c.patrones.forEach(function (re) {
          var enTitulo = contar(re, g.titulo) > 0;
          var veces = contar(re, g.texto);
          if (enTitulo || veces) mejor = Math.max(mejor, (enTitulo ? 20 : 0) + Math.min(veces, 10));
        });
        if (mejor) { cubre += c.peso; puntos += mejor * c.peso; }
      });
      if (g.guia.estado === "planeado") puntos -= 5; // a igual cobertura, primero lo que ya tiene guía
      return cubre ? { guia: g.guia, cubre: cubre, puntos: puntos } : null;
    }).filter(Boolean);
    var maximo = resultados.reduce(function (m, r) { return Math.max(m, r.cubre); }, 0);
    var minimo = maximo >= 3 ? maximo - 1 : maximo; // con consultas largas, perdonamos una palabra
    return resultados.filter(function (r) { return r.cubre >= minimo; })
      .sort(function (a, b) { return b.cubre - a.cubre || b.puntos - a.puntos; });
  }

  var api = { normalizar: normalizar, raizDe: raizDe, preparar: preparar, buscar: buscar };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; return; }

  // ---- Página /buscar.html ----
  var script = document.currentScript;
  var entrada = document.getElementById("q");
  var resumen = document.getElementById("resumen");
  var lista = document.getElementById("resultados");
  var indice = null;

  function extracto(texto, consulta) {
    var palabras = normalizar(consulta).split(/\s+/).filter(function (p) { return p.length > 1 && VACIAS.indexOf(p) < 0; });
    var t = normalizar(texto), i = -1;
    for (var k = 0; k < palabras.length && i < 0; k++) i = t.indexOf(raizDe(palabras[k]));
    if (i < 0) return texto.slice(0, 160) + "…";
    var inicio = Math.max(0, i - 60);
    return (inicio > 0 ? "…" : "") + texto.slice(inicio, inicio + 180) + "…";
  }

  function mostrar(consulta) {
    lista.textContent = "";
    if (!consulta.trim()) { resumen.textContent = ""; return; }
    var resultados = buscar(indice, consulta);
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
        : (r.guia.estado === "verificado" ? "✅ " : "⚠️ ") + extracto(r.guia.texto, consulta);
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
      indice = preparar(datos);
      resumen.textContent = "";
      mostrar(entrada.value);
      var espera;
      entrada.addEventListener("input", function () {
        clearTimeout(espera);
        espera = setTimeout(function () {
          mostrar(entrada.value);
          history.replaceState(null, "", entrada.value ? "?q=" + encodeURIComponent(entrada.value) : location.pathname);
        }, 150);
      });
      entrada.form.addEventListener("submit", function (e) { e.preventDefault(); mostrar(entrada.value); });
    })
    .catch(function () { resumen.textContent = "No se pudo cargar el buscador. Probá recargar la página."; });
})();
