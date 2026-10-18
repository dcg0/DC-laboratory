# Informe de revisión de seguridad — DC Laboratory

> **Naturaleza del informe:** síntesis de resultados de revisiones estáticas ya realizadas. No se volvió a investigar, ejecutar código, navegar a servicios externos ni reauditar archivos para elaborar este documento. No se modificó código.

## Resumen ejecutivo

La revisión estática consolidada cubre **14 páginas HTML**, el directorio raíz del repositorio, `_headers`, `SECURITY.md`, `.well-known/security.txt`, los workflows de GitHub Actions y referencias locales relevantes.

**No se confirmó una vulnerabilidad XSS explotable**, filtración concreta de secretos, compromiso de GitHub Actions, enlace `target="_blank"` sin `rel="noopener"`, URL `javascript:`, formulario remoto ni recurso local faltante salvo la imagen indicada en `dcking.html`. En las páginas con interacción, los resultados reportan inserción mediante `textContent`/nodos y no mediante sinks HTML inseguros.

Los hallazgos principales son de **configuración, efectividad de cabeceras y endurecimiento**:

1. **Prioridad alta — protección de cabeceras no garantizada en GitHub Pages.** En el despliegue descrito por `SECURITY.md`, los archivos `_headers` no demuestran que se emitan cabeceras HTTP. Además, `frame-ancestors` en una CSP declarada con `<meta>` no se aplica, y los metas no sustituyen cabeceras como `X-Content-Type-Options`, `Permissions-Policy`, HSTS, COOP o CORP. La protección anti-framing y otros controles de respuesta no quedan garantizados.
2. **Prioridad alta — corregir la documentación de seguridad.** `SECURITY.md` reconoce la limitación de GitHub Pages pero puede inducir a equiparar metadatos HTML y cabeceras HTTP. Debe diferenciar qué aplica un meta y qué exige una cabecera de respuesta efectiva.
3. **Prioridad media — corregir una integración de analítica actualmente bloqueada.** `dcm2000/index.html` carga `https://manus-analytics.com/umami`, mientras su CSP solo permite scripts de `'self'` e inline; el navegador la bloqueará. Es un problema funcional/CSP confirmado, no una intrusión confirmada.
4. **Prioridad media — suprimir `'unsafe-inline'` de `script-src` cuando sea viable.** La excepción se repite en las páginas revisadas; reduce la defensa en profundidad frente a una futura inyección. No constituye, por sí sola, evidencia de XSS.
5. **Prioridad baja — arreglar calidad y endurecimiento residual.** Incluye una imagen ausente, validar el puente `postMessage` de `dcm2000`, reforzar la detección de secretos y fijar acciones de GitHub por SHA.

## Alcance y criterio de prioridad

| Prioridad | Criterio aplicado | Elementos consolidados |
|---|---|---|
| **Alta** | Control de seguridad presentado/configurado pero no garantizado en el hosting descrito, o documentación que puede llevar a asumirlo. | Cabeceras HTTP/CSP anti-framing y precisión de `SECURITY.md`. |
| **Media** | Fallo funcional reproducible por configuración estática o mejora de exposición relevante. | Analítica bloqueada por CSP; retirada planificada de `'unsafe-inline'`. |
| **Baja** | Defensa en profundidad, cobertura o calidad; sin explotación confirmada. | `postMessage`, detector de secretos, pinning de Actions, hash de APK, recursos/navegación. |

## Hallazgos confirmados priorizados

### 1. Alta — Las cabeceras y la protección anti-framing no están garantizadas en GitHub Pages

**Hecho confirmado por la configuración documentada:** `_headers` contiene cabeceras como `Content-Security-Policy`, `X-Frame-Options`, HSTS, COOP y CORP, pero `SECURITY.md` indica que el sitio se publica en GitHub Pages y que dicho servicio no permite configurar cabeceras HTTP arbitrarias. Por ello, la mera existencia de `_headers` no acredita que esas cabeceras se entreguen en producción.

A esto se suma que las páginas incluyen `frame-ancestors 'none'` en una CSP suministrada mediante `<meta http-equiv>`. Los navegadores **no aplican `frame-ancestors` desde una meta CSP**. Asimismo, metas de `X-Content-Type-Options` y `Permissions-Policy` no sustituyen sus respectivas cabeceras de respuesta.

**Impacto:** no debe asumirse protección efectiva frente a framing/clickjacking ni la emisión de los demás encabezados de seguridad mientras la publicación sea GitHub Pages sin una capa que los inyecte.

**Arreglo recomendado:** publicar detrás de un CDN, proxy o hosting que emita las cabeceras HTTP en la respuesta y verificarlo en producción. Como mínimo, implementar una CSP de cabecera con `frame-ancestors 'none'` y `X-Frame-Options: DENY` para compatibilidad; aplicar también `X-Content-Type-Options: nosniff`, `Permissions-Policy`, HSTS (solo sobre HTTPS y dominio controlado), COOP y CORP cuando correspondan.

### 2. Alta — Documentación de seguridad potencialmente equívoca sobre metadatos y cabeceras

**Hecho confirmado:** `SECURITY.md` reconoce la limitación de cabeceras de GitHub Pages y, a la vez, alude a políticas equivalentes en metadatos HTML. Esta formulación requiere precisión: una meta CSP puede aplicar algunas directivas, pero no hace efectivo `frame-ancestors`; y metas de `X-Content-Type-Options`/`Permissions-Policy` no equivalen a cabeceras HTTP. HSTS, X-Frame-Options, COOP y CORP tampoco se establecen mediante los metas observados.

**Impacto:** mantenedores o usuarios pueden interpretar que controles de transporte, anti-embebido y aislamiento están activos cuando no se ha demostrado que lo estén.

**Arreglo recomendado:** actualizar `SECURITY.md` con una tabla de controles: **aplicable por meta**, **requiere cabecera HTTP** y **estado real según hosting**. Describir `_headers` únicamente como configuración para proveedores compatibles, no como garantía para GitHub Pages.

### 3. Media — La CSP bloquea el script de analítica de DCM2000

**Hecho confirmado:** `dcm2000/index.html` declara un script externo desde `https://manus-analytics.com/umami`, pero su `script-src` limita los scripts a `'self'` y `'unsafe-inline'`. Ese origen externo no está autorizado, por lo que la carga quedará bloqueada por CSP.

**Impacto:** analítica inoperante y posible ruido de errores CSP. No se revisó ni se ejecutó la analítica; no se deriva una exposición de datos de este hallazgo.

**Arreglo recomendado:** decidir explícitamente si la analítica es necesaria. Si lo es, validar la finalidad, privacidad e integridad del proveedor y permitir exclusivamente el origen indispensable en las directivas necesarias; si no lo es, retirar la etiqueta del script.

### 4. Media — Uso generalizado de `script-src 'unsafe-inline'`

**Hecho confirmado:** las CSP revisadas permiten scripts inline. Algunas páginas lo necesitan para scripts embebidos; otras no contienen scripts y conservan la excepción innecesariamente.

**Impacto:** disminuye la capacidad de CSP para contener una futura inyección HTML/JavaScript. **No se confirmó un vector XSS explotable** en esta revisión.

**Arreglo recomendado:** externalizar JavaScript y CSS locales cuando sea razonable y usar `script-src 'self'`; cuando deba mantenerse código estático inline, autorizarlo con hashes CSP. Para contenido dinámico generado en servidor, emplear nonces por respuesta. Retirar `'unsafe-inline'` solo después de probar las páginas afectadas.

### 5. Baja — Puente `postMessage` de DCM2000 sin validación visible de origen

**Hecho confirmado:** el runtime visible en `dcm2000/index.html` registra un listener de `message` y despacha según campos del mensaje, sin comprobación visible de `event.origin` ni `event.source`.

**Impacto:** si ese canal se usa en producción, una ventana no confiable podría intentar enviar mensajes al runtime. La revisión fue estática; no se confirmó un efecto explotable ni se probaron mensajes.

**Arreglo recomendado:** eliminar el canal si no es necesario. Si lo es, validar `event.origin` contra una lista permitida, verificar `event.source` y aplicar validación estricta y con esquema a `data`, `payload` y tipos antes de despachar.

### 6. Baja — Cobertura limitada de detección de secretos y endurecimiento de Actions

**Hechos confirmados:**

- El workflow `security.yml` usa patrones heurísticos para unas pocas familias de secretos y excluye `SECURITY.md` y el propio workflow. No es un detector general de credenciales; no se encontró filtración concreta.
- Las acciones se referencian por tags (`actions/checkout@v7`, `github/codeql-action/*@v4`) y no por SHA inmutable. `security.yml` conserva credenciales de checkout por defecto y descarga el historial completo.
- Los permisos están relativamente acotados: `security.yml` utiliza `contents: read`; CodeQL emplea permisos de lectura y `security-events: write`, coherente con la carga de hallazgos. No se identificó `pull_request_target` ni escritura de contenido.

**Arreglo recomendado:** incorporar un escáner de secretos mantenido, minimizar exclusiones mediante allowlists concretas y mantener la prevención del proveedor si está disponible. Fijar acciones a SHA verificadas y actualizadas mediante Dependabot; configurar `persist-credentials: false` y `fetch-depth: 1` cuando no se requieran credenciales ni historial completo.

### 7. Baja — Recursos, integridad y navegación

**Hechos confirmados:**

- `dcking.html` referencia `dcking-m2000-cover.png`, archivo que no estaba presente en la revisión reportada.
- Las descargas APK de `dcelm327.html` no muestran hashes SHA-256 junto a los enlaces. En contraste, se verificó que `downloads/DCA-ChromeOS.apk` coincide con su archivo `.sha256` publicado.
- `dcesp32.html` y `tallerrojo.html` no ofrecen un retorno visible directo al índice; el resto de retornos principales fueron comprobados como existentes.

**Arreglo recomendado:** añadir/corregir la imagen de `dcking.html`; publicar hashes SHA-256 verificables para cada APK junto a su enlace y a la fuente oficial; añadir un enlace visible al índice en las dos páginas señaladas si esa es la navegación esperada.

## Matriz breve por página HTML

| Página | Resultado estático consolidado | Configuración/hallazgos relevantes | Navegación, enlaces y recursos | Prioridad de actuación |
|---|---|---|---|---|
| `index.html` | Chat local: inserta respuestas con `textContent`; `innerHTML=''` es una cadena constante. Sin envío externo ni XSS confirmada. | Meta CSP con `frame-ancestors` inefectivo; script inline requiere o hereda `'unsafe-inline'`. | Anclas internas presentes; `target="_blank"` con `noopener`; Google Fonts e insignias HTTPS inventariados. | Alta: cabeceras reales. Media: CSP sin inline. |
| `admin.html` | Chat local con límite, normalización y limitación de frecuencia; sin API, almacenamiento ni sinks peligrosos. | Meta `frame-ancestors` y `nosniff` no sustituyen cabeceras HTTP. | Retorno a `./`; enlaces externos con `noopener`; recursos locales presentes. | Alta: cabeceras reales. |
| `alternadc.html` | Sin scripts, formularios, datos dinámicos ni sinks XSS. | `frame-ancestors` por meta y `'unsafe-inline'` innecesario. | Retorno a `./`; enlace a `tallerrojo.html`, recursos locales y enlaces externos comprobados. | Alta: cabeceras. Media: retirar inline. |
| `dcelm327.html` | Sin scripts, formularios ni XSS. | `frame-ancestors` meta y `'unsafe-inline'` innecesario. | Retorno a `./`; PDF e imágenes locales presentes; enlaces APK GitHub. | Alta: cabeceras. Baja: hashes visibles de APK. |
| `dcesp32.html` | Renderizado dinámico con `textContent` y nodos; exportación local Blob, sin envío externo. | CSP permite scripts/estilos inline; no se confirmó sink XSS. | Anclas internas; sin enlace directo a índice; recursos locales presentes. | Media: CSP. Baja: enlace al índice. |
| `dcking-live.html` | Estado local de demo actualizado con `textContent`; sin entradas externas, formularios ni XSS. | Metas no sustituyen cabeceras; JavaScript inline exige endurecimiento posterior. | Enlaces relativos de vuelta a `index.html`; recursos locales presentes. | Alta: cabeceras. Media: CSP. |
| `dcking.html` | Juego usa canvas y `textContent`; no se reportaron sinks HTML peligrosos. | Meta anti-framing inefectivo y `'unsafe-inline'` por script embebido. | Retorno a `index.html` presente; **falta `dcking-m2000-cover.png`**. | Alta: cabeceras. Media: CSP. Baja: imagen. |
| `dcm2000/index.html` | Runtime React; no se confirmó flujo de datos no confiables a sinks. Listener `postMessage` visible sin validación de origen. | Meta/cabeceras no garantizadas; `'unsafe-inline'`; **Umami externo bloqueado por CSP**. | Módulo local contiene enlace a `/`; sin `target="_blank"` en HTML. | Alta: cabeceras. Media: Umami/CSP. Baja: `postMessage`. |
| `dcsgps.html` | Sin scripts, entradas, formularios, almacenamiento ni sinks XSS. | `'unsafe-inline'` sin scripts; meta `frame-ancestors`/`nosniff` no efectiva como cabecera. | Vuelve a `./`; GitHub con `noopener`; imagen local presente. | Alta: cabeceras. Media: retirar inline. |
| `dctuner-red-edition.html` | Sin scripts, formularios, almacenamiento, `postMessage` ni sinks solicitados. | Metas de cabeceras ineficaces y `'unsafe-inline'` innecesario. | Vuelta a `./`, vínculos locales existentes y enlaces externos con `noopener`. | Alta: cabeceras. Media: retirar inline. |
| `dctuner.html` | Sin lógica dinámica, scripts, formularios ni sinks XSS. | Meta `frame-ancestors` y `'unsafe-inline'` innecesario. | Vuelta a `./`; repo con `noopener`; descargas HTTPS. | Alta: cabeceras. Media: retirar inline. |
| `dctunerpi.html` | Sin scripts, formularios, almacenamiento, `postMessage` ni sinks XSS. | Meta `frame-ancestors` y `'unsafe-inline'` innecesario. | Vuelta a `./`; enlaces internos existentes y externos con `noopener`. | Alta: cabeceras. Media: retirar inline. |
| `superrasp.html` | Sin scripts, entradas, formularios ni sinks XSS. | Meta `frame-ancestors`/`nosniff` no equivalente a cabeceras; `'unsafe-inline'` innecesario. | Retorno a `./`; imagen local presente; GitHub con `noopener`. | Alta: cabeceras. Media: retirar inline. |
| `tallerrojo.html` | Sin scripts, formularios, almacenamiento, `postMessage` ni sinks XSS. | Meta anti-framing y otras metas de cabecera no garantizan controles; `'unsafe-inline'` innecesario. | Retorno a `alternadc.html`, no directo a índice; recurso local presente; enlace externo con `noopener`. | Alta: cabeceras. Media: retirar inline. Baja: retorno al índice. |

## Matriz breve de repositorio y configuración

| Área | Resultado confirmado | Riesgo/efecto | Acción recomendada |
|---|---|---|---|
| Hosting y `_headers` | `_headers` contiene cabeceras útiles, pero `SECURITY.md` identifica GitHub Pages, que no aplica cabeceras arbitrarias. | Las cabeceras pueden no llegar al navegador. | Usar CDN/proxy/host con cabeceras HTTP verificables o documentar la limitación. |
| `SECURITY.md` | Reconoce el límite del hosting, pero requiere separar metas de cabeceras reales. | Falsa sensación de protección. | Documentar el estado efectivo por control y plataforma. |
| CSP transversal | `script-src 'unsafe-inline'` es frecuente; algunas páginas no tienen script. | Menor defensa en profundidad XSS. | Eliminar la excepción donde no haga falta; hashes/nonces o recursos locales cuando haga falta. |
| `dcm2000` / Umami | Script de `manus-analytics.com` no está permitido por `script-src`. | Analítica bloqueada. | Autorizar únicamente lo necesario tras evaluación o eliminarla. |
| Workflows | Tags no inmutables; checkout conserva credenciales y un workflow usa historial completo. | Riesgo de cadena de suministro reducible, sin compromiso confirmado. | SHA pinning, Dependabot, `persist-credentials: false`, menor profundidad cuando proceda. |
| Secretos | Detector heurístico y con exclusiones; `.gitignore` no protege secretos ya rastreados. | Cobertura incompleta, sin secreto expuesto confirmado. | Escáner mantenido, allowlists mínimas y controles de proveedor. |
| Divulgación | `SECURITY.md` y `.well-known/security.txt` dirigen a GitHub Advisories; README usa HTTPS. | Práctica positiva observada. | Mantener y verificar publicación efectiva de `security.txt`. |
| APK | Un APK local coincidió con su SHA-256; otros enlaces APK no muestran hashes junto a descarga. | Verificabilidad desigual. | Publicar hashes por release y explicaciones de validación. |

## Revisión de enlaces, navegación y dependencias externas

### Enlaces y navegación

- La navegación principal de `index.html` enlaza a secciones internas existentes.
- Se comprobó retorno al índice o a la raíz mediante `./`/`index.html` en la mayoría de páginas. **Excepciones de usabilidad:** `dcesp32.html` no enlaza directamente al índice y `tallerrojo.html` vuelve a `alternadc.html`, no directamente al índice.
- Todos los enlaces examinados con `target="_blank"` incluyen `rel="noopener"` o `rel="noopener noreferrer"`; no se reportaron excepciones.
- No se reportaron enlaces `javascript:`, formularios remotos, iframes, ni recursos locales ausentes excepto `dcking-m2000-cover.png`.
- `.well-known/security.txt` existe y `_config.yml` está configurado para incluir `.well-known`, pero la publicación efectiva no fue comprobada.

### Recursos externos inventariados

- **Google Fonts**: utilizados por varias páginas mediante `fonts.googleapis.com` y fuentes indirectas de `fonts.gstatic.com`; las CSP reportadas los permiten donde se usan.
- **GitHub, GitHub Releases, raw.githubusercontent.com y Shields.io**: aparecen como enlaces, insignias o descargas HTTPS; no se navegaron ni validaron externamente.
- **Umami (`manus-analytics.com`)**: aparece únicamente en `dcm2000/index.html`; su carga está bloqueada por la CSP declarada.
- No se reportaron scripts externos ni iframes en las demás páginas revisadas.

## Plan de arreglos recomendado

1. **Definir el modelo de alojamiento y aplicar cabeceras HTTP reales.** Si se mantiene GitHub Pages sin proxy, retirar afirmaciones que indiquen que `_headers` se aplica y aceptar/documentar la limitación. Si la protección es un requisito, situar el sitio tras un CDN/proxy/host que emita y permita comprobar CSP, `X-Frame-Options`, `X-Content-Type-Options`, HSTS, COOP, CORP y `Permissions-Policy`.
2. **Actualizar `SECURITY.md`.** Diferenciar controles de meta CSP de cabeceras HTTP, identificar los controles no efectivos en GitHub Pages y mantener instrucciones de divulgación responsable.
3. **Corregir DCM2000.** Resolver la decisión de analítica (autorizar estrictamente el origen o eliminarlo), revisar el listener `postMessage` y conservar CSP lo más restrictiva posible.
4. **Endurecer CSP de forma gradual.** Inventariar cada script/style inline, moverlos a archivos locales o calcular hashes, retirar `'unsafe-inline'` primero en páginas sin scripts y probar cada página antes de desplegar.
5. **Corregir artefactos y navegación.** Añadir/corregir `dcking-m2000-cover.png`, incluir hashes de todas las APK y ofrecer enlaces claros al índice en `dcesp32.html` y `tallerrojo.html`.
6. **Mejorar la higiene CI.** Ampliar detección de secretos, reducir exclusiones, fijar acciones a SHA y minimizar credenciales/historial de checkout según la necesidad de cada job.
7. **Validar en despliegue tras los cambios.** Inspeccionar cabeceras HTTP reales, consola CSP, funcionamiento de analítica y rutas/recursos publicados. Esta validación es necesaria porque no formó parte de la revisión estática consolidada.

## Limitaciones de la auditoría estática consolidada

- No se ejecutó JavaScript, no se interactuó con chats, juegos, exportaciones, `postMessage` ni el runtime React.
- No se visitaron enlaces, recursos remotos ni la URL publicada; por ello no se verificaron cabeceras HTTP de producción, disponibilidad de recursos externos, redirecciones, comportamiento del CDN ni configuración efectiva de GitHub Pages.
- No se realizaron pruebas de explotación, fuzzing, análisis dinámico, revisión de tráfico, autenticación, permisos de repositorio, secret scanning alojado ni escaneo de dependencias en ejecución.
- Los resultados sobre XSS se limitan a los sinks, flujos y patrones estáticos reportados. La ausencia de un hallazgo estático **no garantiza** la inexistencia de vulnerabilidades dinámicas o de servidor.
- Las severidades se han normalizado por impacto y evidencia disponible; los elementos etiquetados como endurecimiento/recomendación no se presentan como vulnerabilidades explotables confirmadas.

## Conclusión

El estado consolidado es el de un sitio estático sin una vulnerabilidad de inyección, enlace inseguro o secreto filtrado **confirmado** por la evidencia disponible. La mayor necesidad es alinear el modelo de despliegue, las cabeceras efectivas y la documentación: las metas HTML no sustituyen las protecciones que requieren cabeceras HTTP, especialmente `frame-ancestors` y los controles anti-framing. Corregir esa brecha de configuración/documentación, resolver la analítica bloqueada y eliminar progresivamente `'unsafe-inline'` aportará la mejora de seguridad más importante sin cambios funcionales innecesarios.


## Addendum — estado posterior a remasterización y validación (18 de octubre de 2026)

> La matriz y los hallazgos anteriores describen la auditoría estática previa a las correcciones. Este addendum registra lo aplicado y probado después; sus estados actualizados prevalecen cuando contradicen los hallazgos históricos. La PR [#8](https://github.com/dcg0/DC-laboratory/pull/8) se fusionó a `main` el 18 de octubre de 2026 en el commit `799c50d2da018fa69bedf719615d3112153adcd2`. GitHub Pages sigue configurado para publicar desde `fix/downloads-as-project-cards`, por lo que la portada pública aún no refleja este commit; no cambié esa configuración.

### Cambios y remediaciones incorporadas

- Se integró la portada remasterizada con las imágenes del logotipo y el ícono; se conservaron los originales y se agregaron derivados WebP y opciones responsivas para las imágenes principales y de tarjetas. El logo y la tarjeta de Studio mantienen una alternativa PNG/JPEG mediante `<picture>`.
- Se corrigieron los enlaces de retorno al índice en `dcesp32.html` y `tallerrojo.html`, se resolvió el recurso de portada faltante de DC King y se agregó un favicon local.
- Se ajustaron las etiquetas accesibles de contacto/mapa y los tamaños reservados de insignias; la tarjeta de ubicación usa su texto visible como nombre accesible.
- Se retiró `unsafe-inline` de las políticas de scripts después de externalizar los scripts locales. Se eliminó el recurso de analítica de vista previa bloqueado por CSP y el runtime de vista previa innecesario de DCM2000. El runtime React del juego se probó en Chromium y sigue iniciando.
- Se documentó con claridad en `SECURITY.md` que `_headers` no acredita cabeceras HTTP en GitHub Pages y que una página estática `admin.html` no incorpora autenticación por llamarse “admin”.
- Se añadieron el verificador `tools/check_site_links.py` y controles al workflow de seguridad. El checkout se configuró para no persistir credenciales y usar historial superficial donde corresponde. La referencia de Actions aún es por tag, no por SHA inmutable.

### Resultados de validación

| Control | Resultado final |
|---|---|
| Integridad y rutas | `tools/check_site_links.py`: **14 páginas**, CSP, enlaces, fragmentos, imágenes, metadatos, sitemap y `rel=noopener` comprobados; sin rutas locales rotas. |
| Navegador | **28 cargas Chromium** (14 rutas × escritorio y móvil): HTTP 200, sin errores de consola/JavaScript, imágenes rotas ni desbordamiento horizontal. Se probó el menú móvil y los controles de pausa/reinicio de DC King. DCM2000 montó su raíz React. |
| Lighthouse — móvil | Rendimiento **89**, accesibilidad **100**, buenas prácticas **100**, SEO **100**. FCP/LCP 3.0 s, TBT 0 ms, CLS 0.028; cero diagnósticos de texto visible omitido del nombre accesible. |
| Lighthouse — escritorio | Rendimiento **95**, accesibilidad **100**, buenas prácticas **100**, SEO **100**. FCP/LCP 0.8 s, TBT 0 ms, CLS 0.117; cero diagnósticos de texto visible omitido del nombre accesible. |
| Código y repositorio | `node --check` para scripts locales y bundle DCM2000, `compileall` Python, sintaxis YAML, escaneo heurístico de secretos y `git diff --check`: **sin errores**. El SHA-256 de `downloads/DCA-ChromeOS.apk` coincide con su archivo publicado. |
| Build estático y publicación | El repositorio no define un `Gemfile`/comando Jekyll ni un empaquetado de aplicación; se validaron y sirvieron los archivos estáticos directamente en Chromium. Tras la fusión, la API de Pages aún reportaba el build anterior y la URL pública devolvía HTTP 200 con contenido antiguo; la fuente de Pages está configurada en otra rama. |

Las puntuaciones se midieron sobre un servidor estático local con Lighthouse y pueden variar por red/dispositivo. La prueba local no confirma la compresión, la caché ni las cabeceras HTTP del hosting de producción.

### Pendientes y riesgos residuales

1. **Despliegue y cabeceras HTTP.** GitHub Pages puede seguir sin emitir las cabeceras descritas en `_headers`; CSP en meta no implementa `frame-ancestors`. Si la protección anti-framing, HSTS y demás cabeceras son requisito, se necesita CDN/proxy/hosting compatible y validar las respuestas reales después del despliegue.
2. **`admin.html` es público.** No poner allí secretos, credenciales ni datos sensibles; no ofrece autenticación ni control de acceso.
3. **Fuentes web y CLS.** Lighthouse atribuye el CLS de escritorio (0.117) a la sustitución de fuentes remotas. El CSS de Google Fonts continúa siendo render-blocking (ahorro estimado del diagnóstico local: 1,490 ms móvil y 370 ms escritorio). Una siguiente mejora es autoalojar fuentes con licencia compatible o calibrar fuentes de reserva (`size-adjust`/métricas) y volver a medir sin sacrificar el diseño.
4. **Imágenes restantes.** Lighthouse aún estima ahorros adicionales de carga adaptable de alrededor de 33 KiB en móvil y 258 KiB en escritorio, según viewport/DPR. Son oportunidades de refinamiento, no errores ni recursos rotos.
5. **Cadena de suministro.** El escaneo añadido es heurístico y las GitHub Actions siguen referenciadas por tags; fijarlas por SHA y sumar un escáner de secretos mantenido mejoraría la defensa. El checksum validado es el de DCA-ChromeOS; esto no constituye una auditoría de firma, reproducibilidad ni permisos de todas las APK.
6. **Publicación efectiva.** La fuente de Pages está configurada en `fix/downloads-as-project-cards` y la URL pública aún entrega la versión anterior. No cambié esa configuración porque cambiaría el sitio público; para publicar esta versión, se requiere cambiar la fuente a `main` y luego verificar rutas, recursos, Lighthouse y cabeceras HTTP reales.

### Referencias externas observadas durante la medición

- Hoja de estilos de fuentes usada por la página: https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800;900&family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap
- Insignia dinámica de workflow: https://github.com/dcg0/DC-laboratory/actions/workflows/security.yml/badge.svg
- Insignias Shields.io: https://img.shields.io/badge/secret%20scanning-enabled-176b46 · https://img.shields.io/badge/Dependabot-enabled-2f81f7 · https://img.shields.io/badge/SHA--256-verified-2f81f7

Las URLs se registran para identificar dependencias que afectan el renderizado y la privacidad; su disponibilidad futura depende de esos proveedores.
