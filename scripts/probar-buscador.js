#!/usr/bin/env node
// Prueba el buscador con frases como las escribe la gente (scripts/busquedas-de-prueba.json).
// Uso: node scripts/probar-buscador.js _site/buscar.json
// Cada búsqueda tiene que mostrar, entre los 3 primeros resultados, una guía cuyo título contenga el texto esperado.
"use strict";
const fs = require("fs");
const path = require("path");
const buscador = require("../assets/js/buscar.js");

const indice = buscador.preparar(JSON.parse(fs.readFileSync(process.argv[2] || "_site/buscar.json", "utf8")));
const pruebas = JSON.parse(fs.readFileSync(path.join(__dirname, "busquedas-de-prueba.json"), "utf8"));
const enActions = process.env.GITHUB_ACTIONS === "true";

let fallas = 0;
for (const [consulta, esperado] of pruebas) {
  const primeros = buscador.buscar(indice, consulta).slice(0, 3).map((r) => r.guia.titulo);
  const n = buscador.normalizar(esperado);
  if (!primeros.some((t) => buscador.normalizar(t).includes(n))) {
    fallas++;
    const msg = `"${consulta}" no muestra "${esperado}" entre los 3 primeros. Muestra: ${primeros.join(" | ") || "nada"}`;
    console.log(enActions ? `::error file=scripts/busquedas-de-prueba.json::${msg}` : `FALLA  ${msg}`);
  }
}
const bien = pruebas.length - fallas;
console.log(`${bien} de ${pruebas.length} búsquedas encuentran la guía esperada.`);
// Meta de la versión 1: al menos 9 de cada 10.
process.exit(bien / pruebas.length >= 0.9 ? 0 : 1);
