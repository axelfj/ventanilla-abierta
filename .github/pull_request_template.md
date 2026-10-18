## Qué cambia

<!-- Una o dos frases: qué guía o parte del sitio cambia y por qué. -->

## Fuentes oficiales

<!-- Un enlace por dato que agregaste o cambiaste, con la fecha en que lo abriste (AAAA-MM-DD).
     Solo fuentes oficiales: leyes (SCIJ), sitios de instituciones públicas, La Gaceta, tablas de tarifas. -->

- [Nombre de la fuente](https://...), consultada AAAA-MM-DD

## Lista antes de pedir revisión

- [ ] Cada dato nuevo o cambiado tiene su fuente oficial en la sección **Fuentes** de la guía.
- [ ] Actualicé `ultima_verificacion` en la guía con la fecha en que revisé las fuentes.
- [ ] Lo que no pude confirmar quedó marcado `⚠️ Por verificar` y la guía sigue en `estado: borrador`.
- [ ] No recomiendo despachos, empresas ni servicios pagos.
- [ ] Corrí `python3 scripts/validar.py` y no da errores.

## Si la guía pasa a ✅ verificada

Una guía solo pasa a `estado: verificado` cuando **al menos dos personas, además de quien la escribió**,
abrieron cada fuente y confirmaron que la guía dice lo mismo. Cada una deja su revisión en este pull request
y su usuario de GitHub va en `revisado_por`, que el sitio muestra al pie de la guía.

- [ ] Primera persona que revisó: @
- [ ] Segunda persona que revisó: @
- [ ] Agregué los dos usuarios a `revisado_por` en el front matter.
