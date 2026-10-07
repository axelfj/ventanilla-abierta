---
title: "Decisión 0002: fuentes de buses"
---

# Decisión 0002: de dónde salen los datos de buses

Fecha: 2026-10-07. Estado: aceptada para la primera versión.

## Contexto

Queremos mostrar rutas, horarios y tarifas de buses de Costa Rica y, más adelante, de Centroamérica. El formato estándar para esto es GTFS. Revisamos el 2026-10-07 qué existe, con qué licencia y si se puede leer automáticamente.

## Qué encontramos

| Fuente | Qué tiene | Formato | Licencia | Decisión |
|---|---|---|---|---|
| ARESEP, pliego tarifario de autobús ([ficha](https://aresep.go.cr/datos-abiertos/tarifas-autobus/)) | Todas las rutas con ramal, tramo, kilómetros, tarifa regular y de adulto mayor, resolución, Gaceta, fecha de vigencia y empresa | JSON (servicio de datos abiertos) | Publicado como dato abierto; la ficha no indica licencia | **Se usa**: buscador de tarifas en `/buses/`, actualizado a diario |
| ARESEP, rutas de autobuses ([ficha](https://aresep.go.cr/datos-abiertos/rutas-autobuses/)) | Origen, destino, distancia; también un servicio de mapas | JSON y WFS | No indicada | Pendiente: datos de 2015 a 2018; sirve para un mapa más adelante |
| INCOFER, GTFS del tren ([Mobility Database](https://mobilitydatabase.org/feeds/gtfs/mdb-3480), publicado por SIMOVI de la UCR) | Horarios del tren urbano, con servicio hasta el 31/12/2026 | GTFS | No indicada | Pendiente: aclarar la licencia con SIMOVI antes de redistribuir. Por ahora, enlace al INCOFER |
| CTP ([visor](https://visortp.ctp.go.cr/), portal Junar) | Rutas y concesiones | Visor y tableros | El CTP pide solicitud escrita para datos geográficos | No se usa. No publica horarios descargables |
| Plataforma nacional CTP, UCR, MOPT, ARESEP e INCOFER ([anuncio de agosto de 2026](https://delfino.cr/2026/08/ctp-anuncia-creacion-de-sistema-nacional-con-informacion-de-rutas-horarios-y-tarifas-de-transporte-publico)) | Rutas, paradas, horarios y tarifas en GTFS | GTFS (anunciado) | Sin definir | Vigilar. Cuando se publique, es la fuente principal de horarios |
| OpenStreetMap | Recorridos de rutas | OSM, licencia ODbL | ODbL | Pendiente. En Costa Rica hay muy pocas rutas de bus mapeadas; la wiki de OSM enlaza solo dos |
| Tracopa, Tica Bus, Transnica | Horarios interurbanos e internacionales | Páginas web con derechos reservados | Derechos reservados | Solo enlace. No copiamos sus tablas |
| Moovit, Google Maps | Rutas y horarios | Privado | Prohibido reutilizar | No se usa |
| Nicaragua: MapaNica | Rutas de Managua y Estelí, con horarios | GTFS y OSM | Horarios CC BY-SA 4.0, mapa ODbL | Pendiente: los horarios de Managua son de 2020 a 2021 |
| Panamá, Guatemala, El Salvador, Honduras | — | — | — | No encontramos GTFS público de buses |

## Decisión

1. Empezamos por lo que existe como dato abierto oficial: **las tarifas de la ARESEP**. Responden una pregunta diaria ("¿cuánto cuesta el bus?") con el dato que fija la ley.
2. El recolector (`scripts/recolectores/tarifas_bus.py`) baja el JSON una vez al día y guarda una versión compacta en la rama `datos`. Cada tramo lleva la resolución y la Gaceta que fijaron la tarifa.
3. Para horarios, la página `/buses/` enlaza a quien los publica. No copiamos tablas con derechos reservados.

## Qué falta y cómo seguir

- Pedir a SIMOVI (UCR) la licencia del GTFS del INCOFER para mostrar los horarios del tren.
- Seguir la plataforma nacional del CTP y cambiar a su GTFS cuando exista.
- Un mapa de rutas con los datos de rutas de la ARESEP y OpenStreetMap.
- Centroamérica: empezar por los datos de MapaNica si se actualizan.
