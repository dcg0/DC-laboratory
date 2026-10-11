# DC Laboratory Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rediseñar la portada de DC Laboratory con una interfaz profesional, moderna e innovadora, preservando todos los proyectos, enlaces, servicios, contacto, mapa, redes sociales y reproductor de música existentes.

**Architecture:** Mantener el sitio como una página estática GitHub Pages en `index.html`, usando los assets existentes del repositorio y CSS embebido para no introducir dependencias ni cambiar el mecanismo de publicación. Reorganizar la información en una navegación clara, hero de marca, tarjeta destacada de DCtuneRstudio, grid de proyectos, bloque de servicios, contacto/mapa y footer; conservar la lógica inline del audio y del icono arrastrable.

**Tech Stack:** HTML5 semántico, CSS3 responsive con custom properties, JavaScript vanilla existente, GitHub Pages.

**Spec:** Solicitud del usuario del 2026-09-21: rediseñar `https://github.com/dcg0/DC-laboratory` manteniendo las mismas funciones y haciendo la interfaz profesional, llamativa, moderna e innovadora.

## Global Constraints

- Mantener todos los proyectos actuales y sus URLs sin cambiar destinos.
- Mantener los servicios actuales: creación de páginas web, aplicaciones y software personalizado.
- Mantener teléfono `8114895750`, WhatsApp, correo, GitHub y mapa de Monterrey.
- Mantener el reproductor de `musica.mp3` y el icono flotante arrastrable.
- Mantener la tarjeta destacada de DCtuneRstudio y su enlace oficial.
- No eliminar ni reemplazar los assets existentes.
- Publicar el resultado en la rama `main` del repositorio `dcg0/DC-laboratory`.
- Mantener compatibilidad estática con GitHub Pages, sin backend ni build obligatorio.
- Mantener la licencia y la información de contacto existente.

## Design Read

- **Artifact:** Landing / portfolio público de proyectos y servicios.
- **Audience:** Clientes, colaboradores y usuarios de herramientas automotrices y de software de DC Laboratory.
- **Visual language:** Laboratorio digital automotriz: dashboard oscuro, señalética técnica, paneles de telemetría, gradientes neón controlados y composición editorial.
- **Mode:** Redesign · Preserve; cambio visual amplio con contratos funcionales protegidos.
- **Visual variance:** 8/10.
- **Motion intensity:** 5/10, con reveals suaves, hover states y microinteracciones no esenciales respetando reduced motion.
- **Information density:** 7/10, porque debe mostrar varios proyectos sin parecer un listado plano.
- **Asset dependence:** 9/10; se usarán las imágenes reales del repositorio.
- **Brand fidelity:** 9/10; se conserva el lenguaje DC azul/cian, rojo y fondo negro.

## Design Decisions

- **Color palette:** fondo `#050508` y `#0b0e16`; panel `#101522`; azul principal `#00ccff`; azul profundo `#0099ff`; rojo acento `#ff2244` / `#ff4466`; verde de estado `#00ff99`; texto `#e8e8f0`; líneas `#20283a`.
- **Typography:** `Barlow Condensed` para titulares y etiquetas grandes; `Manrope` para lectura; `DM Mono` para metadatos, tags y detalles técnicos, cargadas desde Google Fonts con fallback local.
- **Spacing:** sistema base de 8 px: 8, 16, 24, 32, 48, 64, 96.
- **Border-radius:** 2–4 px en controles técnicos; 12–18 px en tarjetas e imágenes para suavizar la interfaz sin volverla genérica.
- **Shadow hierarchy:** glow cian tenue para elementos interactivos; glow rojo solo para destacados; sombras negras profundas para separar paneles.
- **Motion:** `cubic-bezier(.22,1,.36,1)`, transiciones de 160–280 ms, reveal por IntersectionObserver y `prefers-reduced-motion`.
- **Layout:** header sticky con navegación por anclas; hero asimétrico; tarjeta DCtuneRstudio como featured; proyectos en grid; servicios en una franja de tres bloques; contacto/mapa en dos columnas; footer compacto.

## Protected Contracts

- `index.html` continúa siendo el entry point.
- Todos los `href` actuales deben permanecer presentes y funcionales.
- Todos los `src` de imágenes y el audio `musica.mp3` deben seguir disponibles.
- Los controles de teléfono, WhatsApp, correo, GitHub y mapa deben permanecer accesibles.
- El icono flotante debe seguir arrastrándose con mouse y touch y alternando play/pause.

## Review Focus

1. **Enlaces de proyectos:** cada tarjeta debe conservar el destino actual; validar con una lista de URLs antes y después.
2. **Funciones flotantes:** el icono musical debe continuar alternando audio y permitir arrastre en desktop y touch.
3. **Responsive:** en viewport móvil no debe haber overflow horizontal ni tarjetas ilegibles.
4. **Accesibilidad:** la navegación, botones, imágenes y controles deben tener nombres accesibles, foco visible y contraste suficiente.
5. **Preservación visual:** usar los assets existentes y no generar sustitutos que desplacen la identidad reconocible de DC Laboratory.

---

### Task 1: Rediseño estructural y navegación

**Files:**
- Modify: `index.html` (estructura HTML, estilos embebidos y metadata)
- Preserve: assets root, `musica.mp3`, enlaces y script de audio/drag

- [ ] Reemplazar el header actual por navegación sticky con marca, estado “DC Laboratory / Digital workshop” y anclas `#proyectos`, `#servicios`, `#contacto`.
- [ ] Crear un hero con titular de laboratorio digital, métricas compactas y CTA a proyectos/contacto.
- [ ] Mantener la tarjeta DCtuneRstudio en primera posición con estilo featured.
- [ ] Reorganizar los proyectos restantes en tarjetas con tags de categoría y CTA existentes.
- [ ] Añadir landmarks semánticos `header`, `main`, `section`, `footer` y un enlace de salto al contenido.

### Task 2: Sistema visual responsive y motion

**Files:**
- Modify: `index.html` (bloque CSS embebido)

- [ ] Definir custom properties de color, tipografía, espaciado, bordes y sombras.
- [ ] Aplicar composición responsive para 1200 px, 760 px y móvil.
- [ ] Añadir fondos de grid/circuito sutiles, glow controlado y hover states.
- [ ] Añadir reveal con `IntersectionObserver` para tarjetas sin bloquear contenido.
- [ ] Añadir `@media (prefers-reduced-motion: reduce)` que desactive animaciones no esenciales.
- [ ] Garantizar `:focus-visible`, alt text, contraste y nombres accesibles para controles.

### Task 3: Servicios, contacto y preservación funcional

**Files:**
- Modify: `index.html`

- [ ] Mantener los tres servicios actuales con CTAs telefónicos.
- [ ] Crear sección de contacto con WhatsApp, correo, GitHub, teléfono y mapa embebido.
- [ ] Mantener el widget flotante de redes.
- [ ] Mantener `musica.mp3`, el icono flotante y su comportamiento mouse/touch.
- [ ] Validar que todos los enlaces del inventario anterior siguen presentes.

### Task 4: Verificación y publicación

**Files:**
- Modify: `index.html`
- Create: `docs/superpowers/plans/2026-09-21-dc-laboratory-redesign.md`

- [ ] Ejecutar `git diff --check`.
- [ ] Validar HTML con parser disponible o comprobación estructural.
- [ ] Verificar todas las imágenes, audio y enlaces locales.
- [ ] Verificar que el HTML público responde con HTTP 200 después del push.
- [ ] Crear commit descriptivo y subirlo a `main`.

## Acceptance Checklist

- La portada mantiene todos los proyectos y destinos.
- DCtuneRstudio aparece como tarjeta destacada al inicio.
- Servicios, teléfono, WhatsApp, correo, GitHub, mapa y reproductor siguen operativos.
- La interfaz se ve profesional en escritorio y móvil.
- No se agregan dependencias ni backend.
- GitHub Pages sirve la versión actualizada desde `main`.
