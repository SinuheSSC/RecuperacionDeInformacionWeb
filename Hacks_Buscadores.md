# Guía Maestra: 100 Hacks para Entornos de Búsqueda
**Estudiante:** Sinuhe Sánchez Contreras  
**Profesor** Jesus Eduardo Alcaraz Chavez 
**Materia** Recuperacion Web
**Carrera:** Ingeniería en Sistemas Computacionales  

---

## 1. Google: Operadores y Precisión
1. **`"Frase exacta"`**: Fuerza la búsqueda de palabras en el orden específico.  
   *Ejemplo:* `"cloud computing architecture"`
2. **`-término`**: Excluye resultados que contengan la palabra tras el guion.  
   *Ejemplo:* `java -café`
3. **`site:URL`**: Busca contenido exclusivamente dentro de un dominio.  
   *Ejemplo:* `site:oracle.com "mysql"`
4. **`filetype:ext`**: Filtra por tipo de archivo específico.  
   *Ejemplo:* `filetype:pdf "guía docker"`
5. **`*` (Asterisco)**: Comodín que sustituye una o más palabras.  
   *Ejemplo:* `"cómo configurar * en azure"`
6. **`intitle:palabra`**: El término debe estar en el título de la página.  
   *Ejemplo:* `intitle:tutorial react`
7. **`inurl:palabra`**: Busca páginas que tengan el término en su dirección web.  
   *Ejemplo:* `inurl:login admin`
8. **`intext:palabra`**: Busca el término solo dentro del cuerpo del mensaje.  
   *Ejemplo:* `intext:vulnerabilidad log4j`
9. **`related:URL`**: Encuentra sitios con contenido similar al sitio base.  
   *Ejemplo:* `related:github.com`
10. **`cache:URL`**: Muestra la versión guardada en el historial de Google.  
    *Ejemplo:* `cache:youtube.com`
11. **`..` (Puntos)**: Busca dentro de un rango numérico o de fechas.  
    *Ejemplo:* `laptop $800..$1200`
12. **`OR`**: Combina dos búsquedas para que aparezca una u otra.  
    *Ejemplo:* `python OR javascript`
13. **`AROUND(X)`**: Encuentra términos cercanos entre sí por X palabras.  
    *Ejemplo:* `cloud AROUND(3) security`
14. **`location:país`**: Segmenta los resultados por ubicación geográfica.  
    *Ejemplo:* `empleos sistemas location:mexico`
15. **`define:término`**: Muestra la definición técnica del concepto.  
    *Ejemplo:* `define:microservicios`
16. **`weather:ciudad`**: Muestra el pronóstico del clima local.  
    *Ejemplo:* `weather:Morelia`
17. **`source:nombre`**: Filtra noticias por una agencia específica.  
    *Ejemplo:* `tecnología source:reuters`
18. **Traductor**: Traduce términos directamente en la interfaz.  
    *Ejemplo:* `traducir software al inglés`
19. **Calculadora**: Resuelve operaciones matemáticas complejas.  
    *Ejemplo:* `sqrt(256) * 10`
20. **Buscador de mapas**: Ubica una dirección o negocio rápidamente.  
    *Ejemplo:* `Tecnológico de Morelia mapas`

---

## 2. Bing: Integración Microsoft y Multimedia
1. **`contains:ext`**: Encuentra páginas que tengan enlaces a ciertos archivos.  
   *Ejemplo:* `redes contains:pdf`
2. **`ext:ext`**: Filtra por extensión de archivo (equivalente a filetype).  
   *Ejemplo:* `automatización ext:pptx`
3. **`feed:término`**: Localiza fuentes RSS sobre un tema de interés.  
   *Ejemplo:* `feed:tecnología nube`
4. **`hasfeed:URL`**: Verifica si un sitio específico ofrece feeds.  
   *Ejemplo:* `hasfeed:microsoft.com`
5. **`ip:dirección`**: Rastrea dominios alojados en una IP específica.  
   *Ejemplo:* `ip:192.168.1.1`
6. **`image:size:large`**: Filtra solo imágenes de alta resolución.  
   *Ejemplo:* `wallpapers 4k image:size:large`
7. **`image:aspect:square`**: Encuentra imágenes con proporciones cuadradas.  
   *Ejemplo:* `logo python image:aspect:square`
8. **`video:duration:long`**: Filtra videos extensos (más de 20 min).  
   *Ejemplo:* `conferencia kubernetes video:duration:long`
9. **Búsqueda Visual**: Usa una imagen para encontrar productos o códigos.  
   *Ejemplo:* [Subir foto de placa madre para identificar modelo]
10. **`mycalendar`**: Consulta tu agenda de Outlook directamente.  
    *Ejemplo:* Escribir `mycalendar` en la barra de búsqueda.
11. **`myfiles`**: Busca documentos en tu OneDrive personal.  
    *Ejemplo:* `myfiles tarea redes`
12. **`filetype:docx site:microsoft.com`**: Encuentra plantillas oficiales.  
    *Ejemplo:* `curriculum filetype:docx site:microsoft.com`
13. **Buscador Hex**: Convierte colores de hexadecimal a RGB.  
    *Ejemplo:* `#FF5733`
14. **`compare vs`**: Genera tablas comparativas de activos.  
    *Ejemplo:* `compare BTC vs ETH`
15. **Traductor de sitios**: Traduce una URL completa al instante.  
    *Ejemplo:* `traducir https://docs.aws.amazon.com al español`
16. **Math Solver**: Resuelve ecuaciones mostrando el procedimiento.  
    *Ejemplo:* `2x + 5 = 15`
17. **`flight [n°]`**: Rastreo visual de vuelos en tiempo real.  
    *Ejemplo:* `flight AMX123`
18. **Modo Lectura**: Elimina distracciones visuales de un artículo.  
    *Ejemplo:* [Click en icono de libro en barra de direcciones]
19. **Microsoft Rewards**: Acumula puntos canjeables por buscar.  
    *Ejemplo:* [Realizar búsquedas diarias con sesión iniciada]
20. **Región Estricta**: Cambia el mercado de búsqueda fácilmente.  
    *Ejemplo:* [Ajustar a "Estados Unidos" en configuración lateral]

---

## 3. DuckDuckGo: Privacidad y !Bangs
1. **`!g`**: Busca en Google desde DuckDuckGo de forma privada.  
   *Ejemplo:* `!g lenguajes de programación 2026`
2. **`!w`**: Salta directamente a un artículo de Wikipedia.  
   *Ejemplo:* `!w inteligencia artificial`
3. **`!amazon`**: Busca productos sin que Amazon te rastree antes.  
   *Ejemplo:* `!amazon ssd 1tb`
4. **`!yt`**: Realiza una búsqueda directa en YouTube.  
   *Ejemplo:* `!yt tutorial haskell`
5. **`!so`**: Busca soluciones de código en Stack Overflow.  
   *Ejemplo:* `!so null pointer exception java`
6. **`!github`**: Localiza repositorios de código fuente.  
   *Ejemplo:* `!github terraform examples`
7. **`base64`**: Codifica o decodifica cadenas de texto.  
   *Ejemplo:* `base64 hola mundo`
8. **`url encode`**: Convierte texto a formato de URL segura.  
   *Ejemplo:* `url encode busqueda avanzada`
9. **`hex to rgb`**: Muestra la equivalencia de un color.  
   *Ejemplo:* `hex to rgb #443411`
10. **`json format`**: Ordena y valida un objeto JSON.  
    *Ejemplo:* `json format {"id":1,"nombre":"Sinuhe"}`
11. **`password [n]`**: Genera una clave segura de n caracteres.  
    *Ejemplo:* `password 16`
12. **`lorem ipsum`**: Genera texto falso para diseño web.  
    *Ejemplo:* `lorem ipsum 3 paragraphs`
13. **`site:URL`**: Filtra resultados por sitio web.  
    *Ejemplo:* `site:stackoverflow.com android`
14. **`intitle:`**: Busca términos en el título de la página.  
    *Ejemplo:* `intitle:manual php`
15. **`expand [URL]`**: Revela el link real detrás de un link corto.  
    *Ejemplo:* `expand https://bit.ly/3xyz`
16. **`stopwatch`**: Inicia un cronómetro en el navegador.  
    *Ejemplo:* `stopwatch`
17. **`timer`**: Inicia una cuenta regresiva.  
    *Ejemplo:* `timer 10 minutes`
18. **`qr`**: Genera un código QR para un texto o link.  
    *Ejemplo:* `qr www.google.com`
19. **`cheat sheet`**: Muestra una tabla de comandos rápidos.  
    *Ejemplo:* `cheat sheet git`
20. **`/safeon`**: Activa el filtro de búsqueda segura.  
    *Ejemplo:* `/safeon` en la barra de búsqueda.

---

## 4. Brave Search: Goggles e Independencia
1. **`goggles:news_sources`**: Filtra para mostrar solo fuentes de noticias.  
   *Ejemplo:* `elecciones goggles:news_sources`
2. **`goggles:tech_blogs`**: Prioriza blogs técnicos especializados.  
   *Ejemplo:* `novedades aws goggles:tech_blogs`
3. **`goggles:no_pinterest`**: Limpia los resultados de spam de Pinterest.  
   *Ejemplo:* `decoración oficinas goggles:no_pinterest`
4. **Summarize**: Resumen con IA de los mejores resultados.  
   *Ejemplo:* [Click en el botón 'Summarize' tras buscar un tema]
5. **Preguntas Leo**: Consultas directas al asistente sobre la web.  
   *Ejemplo:* "¿Cuál es el resumen de esta página?"
6. **Discussions**: Bloque que resalta hilos de Reddit y foros.  
   *Ejemplo:* `error conexión cisco discussions`
7. **Brave News**: Feed de noticias basado en tus intereses privados.  
   *Ejemplo:* [Scroll hacia abajo en la página de inicio de Brave]
8. **Filtro de Tiempo**: Ajuste de resultados por horas o días.  
   *Ejemplo:* [Seleccionar 'Past 24 hours' en el menú de filtros]
9. **Image Privacy**: Búsqueda visual que no comparte datos.  
   *Ejemplo:* [Buscar cualquier imagen en la pestaña de imágenes]
10. **`:cl`**: Acceso rápido para limpiar el historial de la barra.  
    *Ejemplo:* Escribir `:cl` en la URL.
11. **`@tabs`**: Busca una palabra entre tus pestañas abiertas.  
    *Ejemplo:* `@tabs documentación`
12. **Script Block**: Bloqueo de rastreadores antes de entrar a un sitio.  
    *Ejemplo:* [Ver el icono de escudo en el resultado de búsqueda]
13. **Code Index**: Prioriza repositorios en consultas de programación.  
    *Ejemplo:* `algoritmo dijkstra python`
14. **Goggles personal**: Crea tu propio filtro de búsqueda.  
    *Ejemplo:* [Usar la herramienta de creación de Goggles en Brave]
15. **Independent Index**: Resultados que no dependen de Google/Bing.  
    *Ejemplo:* [Verificar la métrica de independencia en la búsqueda]
16. **`Alt + D`**: Atajo para ir directo a la búsqueda.  
    *Ejemplo:* Presionar `Alt + D` mientras navegas.
17. **Private IA**: Uso de IA sin entrenamiento con tus datos.  
    *Ejemplo:* [Hacer preguntas técnicas a Leo AI]
18. **Ad-Free**: Resultados limpios de publicidad pagada.  
    *Ejemplo:* [Cualquier búsqueda de producto en Brave Search]
19. **Unbiased**: Algoritmo que evita la burbuja informativa.  
    *Ejemplo:* `noticias política internacional`
20. **Playlist**: Añade videos encontrados a una lista offline.  
    *Ejemplo:* [Click derecho en video -> Add to Brave Playlist]

---

## 5. Yahoo: Finanzas y Especialización
1. **`hostname:`**: Filtra por el nombre del servidor exacto.  
   *Ejemplo:* `hostname:support.microsoft.com`
2. **`originurlext:`**: Busca archivos por su origen de extensión.  
   *Ejemplo:* `manual originurlext:pdf`
3. **`linkfromdomain:`**: Muestra sitios con links hacia un dominio.  
   *Ejemplo:* `linkfromdomain:google.com`
4. **`prefer:`**: Da prioridad a resultados con un término específico.  
   *Ejemplo:* `nube prefer:seguridad`
5. **`TICKER`**: Muestra datos de bolsa en tiempo real.  
   *Ejemplo:* `AMZN`
6. **`Compare TICKERS`**: Comparativa de rendimiento bursátil.  
   *Ejemplo:* `GOOG vs MSFT`
7. **Cripto Converter**: Conversión inmediata de criptoactivos.  
   *Ejemplo:* `1 BTC to MXN`
8. **Sectores**: Información sobre industrias económicas.  
   *Ejemplo:* `sector tecnológico yahoo finance`
9. **Source Filter**: Filtrado de noticias por agencia.  
   *Ejemplo:* `tecnología source:ap`
10. **User Sentiment**: Análisis de comentarios en artículos.  
    *Ejemplo:* [Revisar sección de comentarios en Yahoo News]
11. **`weather [CP]`**: Clima exacto por código postal.  
    *Ejemplo:* `weather 58000`
12. **Flight Tracker**: Estado de vuelos integrado.  
    *Ejemplo:* `flight Volaris 123`
13. **Yahoo Dictionary**: Definiciones directas.  
    *Ejemplo:* `diccionario algoritmo`
14. **Recipes**: Filtro de cocina por ingredientes.  
    *Ejemplo:* `receta pollo con brócoli`
15. **Search Scan**: Aviso de seguridad en sitios maliciosos.  
    *Ejemplo:* [Icono de escudo junto a la URL del resultado]
16. **Mail Search**: Buscar correos desde la barra central.  
    *Ejemplo:* `boletos avión` (con sesión iniciada)
17. **Region Switch**: Cambio de país con un botón lateral.  
    *Ejemplo:* [Seleccionar 'España' en el menú de Yahoo]
18. **SafeSearch**: Control de contenido explícito accesible.  
    *Ejemplo:* [Ajustar en menú de configuración de búsqueda]
19. **Sports Scores**: Resultados deportivos en vivo.  
    *Ejemplo:* `NFL scores`
20. **Yahoo Life**: Tendencias y estilo de vida.  
    *Ejemplo:* `tendencias moda 2026`