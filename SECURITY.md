# Política de seguridad

## Reportar una vulnerabilidad

No publiques credenciales, datos personales ni detalles explotables en issues públicos. Reporta vulnerabilidades mediante [GitHub Security Advisories](https://github.com/dcg0/DC-laboratory/security/advisories/new). Incluye la URL o archivo afectado, pasos mínimos para reproducir el problema, impacto y una propuesta de corrección si la tienes.

## Alcance

Este repositorio es un sitio estático publicado en GitHub Pages. No contiene un servidor de autenticación ni una base de datos propia. Los proyectos externos enlazados desde el sitio tienen sus propias políticas y deben reportarse a sus respectivos mantenedores.

## Recomendaciones para las descargas

Antes de instalar un APK o archivo comprimido, descárgalo únicamente desde los enlaces oficiales, verifica el hash SHA-256 publicado cuando exista y mantén actualizado el sistema operativo. El sitio no solicita contraseñas, claves API ni datos bancarios.

## Límites de esta protección

Las cabeceras del archivo `_headers` se aplican en proveedores que lo soportan. GitHub Pages no permite configurar cabeceras HTTP arbitrarias; por eso las páginas incluyen también políticas equivalentes mediante metadatos HTML. Para una protección de transporte estricta en producción, usa HTTPS y un proxy/CDN que permita aplicar las cabeceras del archivo `_headers`.
