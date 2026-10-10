#!/usr/bin/env bash
# Publica una carpeta de datos en la rama `datos`, sin tocar las demás carpetas de esa rama.
# La rama se reescribe con un solo commit para que no acumule historial.
#
# Uso (dentro de GitHub Actions): scripts/recolectores/publicar-datos.sh CARPETA_NUEVA NOMBRE_EN_LA_RAMA
# Necesita GITHUB_TOKEN y GITHUB_REPOSITORY en el entorno.
set -euo pipefail
nueva="$1"
nombre="$2"
raiz="$(cd "$(dirname "$0")/../.." && pwd)"
tmp="$(mktemp -d)"

# Si la rama ya existe, se parte de lo que tiene. Si no se puede leer (por ejemplo, un fallo de red),
# se aborta en vez de publicar sin las otras carpetas.
if git ls-remote -q --exit-code --heads origin datos >/dev/null; then
  git fetch -q --depth 1 origin datos
  git archive origin/datos | tar -x -C "$tmp"
else
  codigo=$?
  if [ "$codigo" -ne 2 ]; then
    echo "No se pudo leer la rama datos (código $codigo); no se publica." >&2
    exit 1
  fi
fi
rm -rf "${tmp:?}/$nombre"
cp -r "$nueva" "$tmp/$nombre"
cp "$raiz/scripts/recolectores/LEEME-datos.md" "$tmp/LEEME.md"

cd "$tmp"
git init -q -b datos
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -A
git commit -q -m "Datos: $nombre $(date -u +%Y-%m-%dT%H:%MZ)"
git push -q --force "${DATOS_REMOTO:-https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git}" HEAD:datos
echo "Publicado $nombre en la rama datos"
