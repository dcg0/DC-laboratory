# Política de seguridad

## Reportar una vulnerabilidad

No publiques credenciales, datos personales ni detalles explotables en issues públicos. Reporta vulnerabilidades mediante [GitHub Security Advisories](https://github.com/dcg0/DC-laboratory/security/advisories/new). Incluye la URL o archivo afectado, pasos mínimos para reproducir el problema, impacto y una propuesta de corrección si la tienes.

## Alcance

Este repositorio es un sitio estático publicado en GitHub Pages. No contiene un servidor de autenticación ni una base de datos propia. Los proyectos externos enlazados desde el sitio tienen sus propias políticas y deben reportarse a sus respectivos mantenedores.

`admin.html` es públicamente accesible mediante URL. Su exclusión en `robots.txt` solo solicita a rastreadores conformes que no la recorran; **no es autenticación ni control de acceso**. No se deben incluir allí datos privados, credenciales ni operaciones que requieran permisos.

## Controles y límites del hosting

GitHub Pages no permite configurar cabeceras HTTP arbitrarias para este sitio. El archivo `_headers` es una configuración de referencia para proveedores que sí reconocen esa convención; su presencia no acredita que GitHub Pages la aplique.

| Control | ¿Puede declararse con meta HTML? | Estado en GitHub Pages según este repositorio |
| --- | --- | --- |
| Content Security Policy | Sí, con limitaciones | Se incluye una CSP meta. `frame-ancestors` no funciona desde meta; no se debe asumir protección anti-iframe. |
| Referrer Policy | Sí | Se incluye `strict-origin-when-cross-origin`. |
| `X-Content-Type-Options` | No | Requiere una cabecera HTTP; no se garantiza mediante este repositorio en GitHub Pages. |
| `X-Frame-Options` | No | Requiere una cabecera HTTP; no se garantiza mediante este repositorio en GitHub Pages. |
| `Permissions-Policy` | No | Requiere una cabecera HTTP; no se garantiza mediante este repositorio en GitHub Pages. |
| HSTS, COOP y CORP | No | Requieren cabeceras HTTP; no se garantiza su configuración personalizada aquí. |

La CSP de las páginas restringe los scripts a recursos del mismo origen; las hojas de estilo siguen permitiendo estilos inline para conservar los diseños estáticos existentes. Las comprobaciones de CI verifican esa política y los enlaces locales, pero no sustituyen una prueba de las cabeceras entregadas por el servidor.

Para activar controles de respuesta que GitHub Pages no permite configurar, el sitio debe servirse mediante un proxy/CDN u otro host que aplique las cabeceras y después verificar las respuestas HTTP reales. No se ha configurado ni verificado un proxy de ese tipo.

## Descargas

Descarga aplicaciones únicamente desde los enlaces oficiales del proyecto. Un hash SHA-256 permite comprobar que un archivo coincide con el publicado, pero por sí solo no demuestra que el APK sea benigno, que su código corresponda a una fuente determinada ni quién lo firmó. Verifica la procedencia, firma y permisos antes de instalarlo y mantén actualizado el sistema operativo.

El sitio no solicita contraseñas, claves API ni datos bancarios.

## Revisión del sitio

La revisión estática del portal y sus páginas se documenta en [`docs/security-review-remastered.md`](docs/security-review-remastered.md). No equivale a una prueba de penetración, análisis dinámico de cada APK ni auditoría de los servicios externos enlazados.
