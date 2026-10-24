# Datos de Ventanilla Abierta

Esta rama la escriben solos los workflows de https://github.com/axelfj/ventanilla-abierta. No la edités a mano: se reescribe en cada corrida.

- `alertas/activas.json`: alertas vigentes (cortes de luz, clima, sismos, desastres). Cada alerta enlaza al aviso oficial en `fuente.url`. Se actualiza cada hora.
- `alertas/estado.json`: qué fuentes respondieron en la última corrida.
- `buses/tarifas.json`: tarifas de autobús del pliego tarifario de la ARESEP. Se actualiza una vez al día.

El dato que vale es siempre el de la institución que lo publica. Cómo se eligieron las fuentes: `docs/decisiones/` en la rama `main`.
