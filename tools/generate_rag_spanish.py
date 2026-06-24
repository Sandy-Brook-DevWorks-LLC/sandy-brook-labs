from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RAG = ROOT / "guides" / "rag"
ES = RAG / "es"

chapter_titles = {
    "chapter01.html": "Topología de la solución",
    "chapter02.html": "Aspire como plano de control local",
    "chapter03.html": "Configuración y contratos compartidos",
    "chapter04.html": "Metadatos con SQLite y EF Core",
    "chapter05.html": "API e interfaz de carga",
    "chapter06.html": "Almacenamiento de objetos con MinIO",
    "chapter07.html": "Pipeline de ingesta del worker",
    "chapter08.html": "Extracción y división de texto en chunks",
    "chapter09.html": "Artefactos literarios",
    "chapter10.html": "Abstracciones de proveedores de IA",
    "chapter11.html": "Almacenamiento vectorial con Qdrant",
    "chapter12.html": "Flujo de preguntas y estrategia de recuperación",
    "chapter13.html": "Prompts y citas",
    "chapter14.html": "Pruebas del pipeline",
    "chapter15.html": "Notas de desarrollo local",
}

chapter_descriptions = {
    "chapter01.html": "Cómo la solución .NET separa orquestación, API, worker, servicios core y pruebas.",
    "chapter02.html": "RAG.AppHost/AppHost.cs define el entorno local.",
    "chapter03.html": "Cómo las opciones e interfaces compartidas mantienen proveedores de modelos y detalles de almacenamiento fuera del código del workflow.",
    "chapter04.html": "Cómo SQLite y EF Core registran el ciclo de vida, el progreso y el estado de ingesta de documentos.",
    "chapter05.html": "El endpoint de carga está en RAG.Api/Program.cs:",
    "chapter06.html": "Los archivos originales se guardan en almacenamiento de objetos antes de indexarlos. La implementación local está en RAG.Core/Services/S3ObjectStorage.cs.",
    "chapter07.html": "RAG.Worker/Worker.cs es un servicio en segundo plano que consulta periódicamente. En cada intervalo configurado, pide a IDocumentIngestionService que procese documentos pendientes.",
    "chapter08.html": "La extracción de texto vive en RAG.Core/Services/TextExtractor.cs.",
    "chapter09.html": "Por qué el pipeline guarda perfiles literarios generados junto a los chunks fuente, preservando su procedencia.",
    "chapter10.html": "El proyecto soporta Ollama y Gemini mediante implementaciones de proveedores:",
    "chapter11.html": "RAG.Core/Services/QdrantVectorStore.cs controla la interacción con Qdrant.",
    "chapter12.html": "Cómo la ruta de preguntas expande consultas, reordena evidencia, expone diagnósticos y aplica límites de seguridad.",
    "chapter13.html": "Cómo los proveedores de chat reciben evidencia y devuelven respuestas con registros de citas inspeccionables.",
    "chapter14.html": "Las pruebas son intencionalmente enfocadas, no exhaustivas.",
    "chapter15.html": "Comandos y URLs locales para ejecutar el pipeline RAG con Gemini u Ollama.",
}

chapter_body = {
    "chapter01.html": """<section class="chapter-body tutorial-content"><p>Cómo la solución .NET separa orquestación, API, worker, servicios core y pruebas.</p>
<pre><code data-lang="text">RAG.AppHost   Aspire orchestration
RAG.Api       ASP.NET Core API + static UI
RAG.Worker    background ingestion loop
RAG.Core      shared domain, providers, storage, vector, EF Core
RAG.Tests     focused unit tests</code></pre>
<p>Esta forma es útil porque cada proyecto tiene una responsabilidad clara:</p>
<ul>
<li><code>RAG.Api</code> acepta la entrada del usuario y devuelve resultados.</li>
<li><code>RAG.Worker</code> ejecuta el trabajo lento de ingesta fuera de la ruta de solicitudes.</li>
<li><code>RAG.Core</code> contiene lógica reutilizable y contratos.</li>
<li><code>RAG.AppHost</code> conecta la infraestructura local.</li>
</ul>
<p>El usuario sube un documento a la API, pero la API no procesa el libro de inmediato. Guarda el archivo, crea un registro de metadatos y responde rápido. Más tarde, el worker toma documentos pendientes y ejecuta extracción, enriquecimiento, división en chunks, embeddings e indexación vectorial.</p>
<p>Ese workflow asíncrono importa porque crear embeddings para un PDF grande puede tomar minutos. Bloquear la solicitud de carga hasta que todos los vectores estén creados produciría timeouts y una mala experiencia de usuario.</p></section>""",
    "chapter02.html": """<section class="chapter-body tutorial-content"><p><a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main/RAG.AppHost/AppHost.cs" target="_blank" rel="noopener noreferrer"><code>RAG.AppHost/AppHost.cs</code></a> define el entorno local.</p>
<p>Inicia:</p>
<ul>
<li>Qdrant en los puertos <code>6333</code> y <code>6334</code>.</li>
<li>MinIO en los puertos <code>9000</code> y <code>9001</code>.</li>
<li>API en <code>http://127.0.0.1:5080/</code>.</li>
<li>Worker como proceso en segundo plano.</li>
<li>Ollama solo cuando Gemini no está seleccionado.</li>
</ul>
<p>El AppHost también crea volúmenes Docker persistentes:</p>
<ul>
<li><code>rag-qdrant-data</code></li>
<li><code>rag-minio-data</code></li>
<li><code>rag-ollama-data</code></li>
</ul>
<p>Esos volúmenes permiten que los vectores indexados, los archivos cargados y los modelos descargados de Ollama sobrevivan reinicios de contenedores.</p>
<p>Nota de producción: estos servicios se exponen en puertos locales fijos y MinIO usa credenciales de ejemplo. Eso es aceptable para este proyecto de aprendizaje, que no está pensado para producción, pero un despliegue real debería usar redes privadas, secretos administrados y acceso restringido a servicios.</p>
<p>Aspire inyecta configuración en la API y en el worker mediante variables de entorno:</p>
<pre><code data-lang="csharp">.WithEnvironment("Rag__Qdrant__BaseUrl", qdrant.GetEndpoint("http"))
.WithEnvironment("Rag__Storage__ServiceUrl", minio.GetEndpoint("api"))
.WithEnvironment("Rag__DatabasePath", databasePath)</code></pre>
<p>La sintaxis de doble guion bajo mapea variables de entorno a secciones de configuración de .NET. Por ejemplo, <code>Rag__Qdrant__BaseUrl</code> se convierte en <code>Rag:Qdrant:BaseUrl</code>.</p>
<h3>Selección del proveedor de IA</h3>
<p>El AppHost elige Gemini cuando <code>GEMINI_API_KEY</code> está presente:</p>
<pre><code data-lang="text">GEMINI_API_KEY present -&gt; Gemini
otherwise              -&gt; Ollama</code></pre>
<p>Puedes sobrescribirlo con:</p>
<pre><code data-lang="bash">export RAG_AI_PROVIDER="Gemini"</code></pre>
<div class="table-wrap"><table>
<thead><tr><th>Opción</th><th>Pros</th><th>Contras</th></tr></thead>
<tbody>
<tr><td>LLM local con Ollama</td><td>Mantiene prompts y contenido de documentos en tu máquina. Funciona bien para experimentar offline después de descargar los modelos. Evita costos por solicitud de API.</td><td>Requiere recursos locales de CPU/GPU, memoria y disco. Las descargas de modelos pueden ser grandes. En hardware modesto, las respuestas suelen ser más lentas que en APIs alojadas.</td></tr>
<tr><td>LLM alojado por API con Gemini</td><td>No requiere alojar modelos localmente. Suele dar respuestas más rápidas y mejor calidad de modelo. Es más fácil de escalar más allá de una sola máquina de desarrollo.</td><td>Envía prompts y contexto recuperado del documento a un servicio externo. Requiere API key, acceso de red y facturación/cuotas del proveedor.</td></tr>
</tbody>
</table></div>
<p>Los valores predeterminados actuales de Gemini son:</p>
<ul>
<li>Modelo de embeddings: <code>gemini-embedding-2</code></li>
<li>Modelo de chat: <code>gemini-2.5-pro</code></li>
</ul>
<p>Los valores predeterminados locales de Ollama son:</p>
<ul>
<li>Modelo de embeddings: <code>nomic-embed-text</code></li>
<li>Modelo de chat: <code>llama3.2</code></li>
</ul>
<p>Nota: RAG usa dos tipos de modelos porque la recuperación y la generación de respuestas son trabajos distintos. El modelo de embeddings convierte chunks de documentos y preguntas del usuario en vectores numéricos, llamados embeddings, que capturan significado semántico. El almacén vectorial usa esos embeddings para encontrar chunks relacionados con la pregunta. Luego el modelo de chat recibe la pregunta más los chunks recuperados y escribe la respuesta final.</p></section>""",
    "chapter03.html": """<section class="chapter-body tutorial-content"><p><a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main/RAG.Core/Configuration/RagOptions.cs" target="_blank" rel="noopener noreferrer"><code>RAG.Core/Configuration/RagOptions.cs</code></a> define configuración fuertemente tipada:</p>
<ul>
<li><code>StorageOptions</code></li>
<li><code>AiOptions</code></li>
<li><code>QdrantOptions</code></li>
<li><code>IngestionOptions</code></li>
<li><code>RequestOptions</code></li>
</ul>
<p>Esto mantiene consistente el acceso a configuración. En lugar de leer strings sueltos por toda la app, los servicios reciben <code>IOptions&lt;RagOptions&gt;</code>.</p>
<p>Las interfaces clave viven en <a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main/RAG.Core/Services/Contracts.cs" target="_blank" rel="noopener noreferrer"><code>RAG.Core/Services/Contracts.cs</code></a>.</p>
<p>Contratos importantes:</p>
<ul>
<li><code>IObjectStorage</code>: subir y leer archivos originales.</li>
<li><code>ITextExtractor</code>: extraer texto de PDFs y archivos TXT.</li>
<li><code>ITextChunker</code>: dividir texto extraído en chunks.</li>
<li><code>ITokenEstimator</code>: estimar tokens para chunking dejando explícita la aproximación.</li>
<li><code>IEmbeddingProvider</code>: convertir texto en vectores.</li>
<li><code>IChatCompletionProvider</code>: producir respuestas finales a partir de evidencia.</li>
<li><code>ILiteraryAnalysisProvider</code>: generar perfiles para club de lectura.</li>
<li><code>IVectorStore</code>: upsert, búsqueda y recuperación de chunks en Qdrant.</li>
<li><code>IRetrievalReranker</code>: convertir candidatos vectoriales más contexto de la pregunta en chunks ordenados con razones.</li>
<li><code>IDocumentIngestionService</code>: procesar documentos pendientes.</li>
<li><code>IIngestionWorkSource</code>: decidir qué IDs de documentos deben ingerirse después.</li>
<li><code>IDocumentManagementService</code>: borrar documentos y poner reindexación en cola.</li>
<li><code>IChatAnswerService</code>: responder preguntas de usuarios.</li>
</ul>
<p>Estas interfaces son el punto didáctico principal del proyecto. El workflow de la aplicación depende de capacidades estables, no de un SDK específico de un proveedor.</p>
<h3>Límites de seguridad para solicitudes</h3>
<p><code>RequestOptions</code> agrega límites alrededor de la ruta de preguntas: caracteres máximos de pregunta, documentos seleccionados máximos, consultas de recuperación generadas máximas y segundos de timeout del proveedor. Esos límites están respaldados por configuración a propósito porque costo y latencia en RAG son preocupaciones operativas, no solo de código.</p>
<pre><code data-lang="csharp">public sealed class RequestOptions
{
    public int MaxQuestionCharacters { get; set; } = 2000;
    public int MaxSelectedDocuments { get; set; } = 20;
    public int MaxRetrievalQueries { get; set; } = 12;
    public int ProviderTimeoutSeconds { get; set; } = 90;
}</code></pre>
<p>Este es un cambio pequeño pero importante: el ejemplo ya no trata las preguntas de usuario como strings inofensivos. La aplicación valida la forma de la solicitud antes de crear embeddings, buscar vectores o llamar a un modelo pagado/remoto.</p></section>""",
    "chapter04.html": """<section class="chapter-body tutorial-content"><p><a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main/RAG.Core/Data/DocumentRecord.cs" target="_blank" rel="noopener noreferrer"><code>RAG.Core/Data/DocumentRecord.cs</code></a> guarda metadatos del documento:</p>
<ul>
<li>ID del documento;</li>
<li>nombre de archivo y tipo de contenido;</li>
<li>clave de almacenamiento de objetos;</li>
<li>estado de ingesta;</li>
<li>mensaje de error;</li>
<li>conteo final de chunks;</li>
<li>etapa y porcentaje de progreso;</li>
<li>chunks procesados y totales;</li>
<li>timestamps.</li>
</ul>
<p>Los estados son:</p>
<pre><code data-lang="csharp">Pending
Processing
Indexed
Failed</code></pre>
<p><a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main/RAG.Core/Data/RagDbContext.cs" target="_blank" rel="noopener noreferrer"><code>RAG.Core/Data/RagDbContext.cs</code></a> mapea esta entidad con EF Core. Esto es intencionalmente simple. SQLite es suficiente para un proyecto local de aprendizaje y da a la API y al worker un estado durable compartido.</p>
<p>El inicializador de base de datos vive en <code>ServiceCollectionExtensions.EnsureRagDatabaseAsync</code>. Usa <code>EnsureCreatedAsync</code> y también hace verificaciones ligeras e idempotentes de columnas para los campos de progreso. Esto evita obligar a un desarrollador a borrar datos locales después de cambios en el modelo durante el tutorial.</p>
<p>En un sistema de producción, normalmente reemplazarías esto con migraciones formales de EF Core.</p></section>""",
    "chapter05.html": """<section class="chapter-body tutorial-content"><p>El endpoint de carga está en <a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main/RAG.Api/Program.cs" target="_blank" rel="noopener noreferrer"><code>RAG.Api/Program.cs</code></a>:</p>
<pre><code data-lang="text">POST /api/documents</code></pre>
<p>El endpoint:</p>
<ol>
<li>verifica que la solicitud sea multipart form data;</li>
<li>requiere un archivo PDF o TXT;</li>
<li>aplica el límite de carga configurado;</li>
<li>escribe el archivo original en almacenamiento de objetos;</li>
<li>crea un <code>DocumentRecord</code> con estado <code>Pending</code>;</li>
<li>devuelve <code>202 Accepted</code>.</li>
</ol>
<p>La API evita deliberadamente hacer extracción y embeddings dentro de la solicitud. Encola trabajo creando una fila pendiente en la base de datos.</p>
<p>Nota de producción: el límite de carga protege el cuerpo de la solicitud, pero este ejemplo todavía confía lo suficiente en el archivo cargado como para guardarlo y procesarlo después. Un sistema de producción normalmente agregaría validación de contenido más fuerte, escaneo de malware, cuotas por usuario más estrictas y respuestas de error genéricas en vez de devolver detalles internos de excepciones. Este proyecto mantiene el comportamiento simple porque es un proyecto de aprendizaje, no software de producción.</p>
<p>La UI en <code>RAG.Api/wwwroot</code> es intencionalmente sencilla:</p>
<ul>
<li><code>index.html</code>: estructura para carga y chat.</li>
<li><code>styles.css</code>: layout y estilos de progreso.</li>
<li><code>app.js</code>: llama a la API, consulta estado de documentos y renderiza respuestas y citas.</li>
</ul>
<p>La UI consulta <code>GET /api/documents</code> cada pocos segundos. Para libros grandes, la ingesta puede tardar, así que el worker actualiza:</p>
<ul>
<li><code>progressStage</code></li>
<li><code>progressPercent</code></li>
<li><code>processedChunks</code></li>
<li><code>totalChunks</code></li>
</ul>
<p>Nota de producción: polling es simple y funciona bien para este ejemplo local, pero una UI de producción normalmente se suscribiría a actualizaciones de estado. Por ejemplo, la API podría publicar eventos de progreso del documento mediante SignalR, WebSockets, Server-Sent Events o un servicio de notificaciones respaldado por un message broker, y el navegador podría recibir actualizaciones cuando ocurren en lugar de pedir repetidamente la lista completa de documentos.</p>
<p>Esto permite que la UI muestre progreso útil en lugar de dejar un libro atrapado en un estado vago de <code>Processing</code>.</p>
<h3>Controles de borrar y reindexar</h3>
<p>La API ahora expone controles del ciclo de vida del documento además de carga y consulta de estado:</p>
<pre><code data-lang="text">DELETE /api/documents/{id}
POST   /api/documents/{id}/reindex</code></pre>
<p><code>DocumentManagementService</code> controla esas operaciones. La eliminación borra la fila de metadatos, elimina el objeto original y remueve los puntos vectoriales del documento. La reindexación restablece estado y progreso a <code>Pending</code> para que el worker pueda reconstruir chunks y vectores desde el archivo original.</p>
<p>Esto importa porque los sistemas RAG necesitan workflows de mantenimiento. Cuando cambian el chunking, la extracción, los prompts, los embeddings o los artefactos generados, los usuarios necesitan una forma de reconstruir el índice derivado sin subir otra vez el mismo documento.</p></section>""",
    "chapter06.html": """<section class="chapter-body tutorial-content"><p>Los archivos originales se guardan en almacenamiento de objetos antes de indexarlos. La implementación local está en <a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main/RAG.Core/Services/S3ObjectStorage.cs" target="_blank" rel="noopener noreferrer"><code>RAG.Core/Services/S3ObjectStorage.cs</code></a>.</p>
<p>MinIO se usa porque es compatible con S3 y fácil de ejecutar localmente en Docker. La misma abstracción podría soportar después:</p>
<ul>
<li>AWS S3;</li>
<li>Azure Blob Storage;</li>
<li>Google Cloud Storage;</li>
<li>almacenamiento local en filesystem.</li>
</ul>
<p>La clave del objeto usa el ID del documento:</p>
<pre><code data-lang="text">{documentId}/{originalFileName}</code></pre>
<p>Esto evita colisiones de nombres de archivo y facilita rastrear un objeto guardado hasta su fila de metadatos.</p>
<p>Conservar archivos originales importa porque los chunks vectoriales son datos derivados. Si más tarde cambian el chunking, la extracción, los embeddings o el análisis, el worker puede reprocesar el documento original.</p>
<p>La abstracción de almacenamiento ahora incluye <code>DeleteAsync</code> además de operaciones de carga y lectura. Eso permite que la eliminación de documentos limpie el objeto original junto con metadatos y puntos vectoriales, que es el soporte mínimo de ciclo de vida que necesita un sistema RAG real de documentos.</p></section>""",
    "chapter07.html": """<section class="chapter-body tutorial-content"><p><a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main/RAG.Worker/Worker.cs" target="_blank" rel="noopener noreferrer"><code>RAG.Worker/Worker.cs</code></a> es un servicio en segundo plano que consulta periódicamente. En cada intervalo configurado, pide a <code>IDocumentIngestionService</code> que procese documentos pendientes.</p>
<p>El worker soporta recuperación de procesamiento vencido. Si un documento está marcado como <code>Processing</code> pero no se ha actualizado recientemente, puede tomarse de nuevo. Esto es útil durante desarrollo cuando la app se detiene a mitad de la ingesta.</p>
<p>La consulta de polling está detrás de <code>IIngestionWorkSource</code>. <code>DatabaseIngestionWorkSource</code> es la implementación predeterminada y lee filas pendientes o vencidas desde SQLite, ordenadas por fecha de creación y limitadas a un lote pequeño. Una versión de producción podría reemplazar ese punto con una fuente basada en cola sin cambiar el pipeline de ingesta.</p>
<p><a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main/RAG.Core/Services/DocumentIngestionService.cs" target="_blank" rel="noopener noreferrer"><code>RAG.Core/Services/DocumentIngestionService.cs</code></a> es el pipeline:</p>
<ol>
<li>marcar el documento como <code>Processing</code>;</li>
<li>verificar que almacenamiento y Qdrant estén disponibles;</li>
<li>abrir el archivo original desde MinIO;</li>
<li>extraer texto;</li>
<li>dividir texto fuente en chunks;</li>
<li>generar artefactos literarios;</li>
<li>combinar chunks de artefactos y chunks fuente;</li>
<li>borrar vectores anteriores del documento;</li>
<li>generar embeddings;</li>
<li>hacer upsert de chunks con embeddings en Qdrant;</li>
<li>marcar el documento como <code>Indexed</code>;</li>
<li>guardar progreso final.</li>
</ol>
<p>El progreso se actualiza entre etapas principales:</p>
<pre><code data-lang="text">Preparing storage
Extracting text
Chunking text
Building book club profile
Resetting existing index
Generating embeddings
Writing vector index
Ready</code></pre>
<p>Si ocurre cualquier excepción, el documento se marca como <code>Failed</code> y el mensaje de error se muestra en la UI.</p>
<p>Nota de producción: la reindexación actualmente borra los vectores existentes antes de que el índice de reemplazo haya terminado con éxito, y los errores de ingesta se muestran directamente en la UI para visibilidad del desarrollador. En producción, un enfoque más seguro construiría primero el índice de reemplazo, haría el cambio solo después del éxito y mantendría el texto detallado de excepciones en logs en lugar de respuestas visibles para usuarios. Este ejemplo favorece la legibilidad porque es un proyecto de aprendizaje.</p>
<p>El servicio de ingesta también registra hitos estructurados: tamaño del lote de work source, inicio y fin de ingesta, conteo de páginas extraídas, conteo de chunks fuente, conteo de artefactos generados, conteo de embeddings, conteo de upserts vectoriales y fallas. Los logs evitan texto completo de documentos y prompts; se enfocan en IDs, conteos, etapas y tiempos que ayudan a operar el pipeline.</p></section>""",
    "chapter08.html": """<section class="chapter-body tutorial-content"><p>La extracción de texto vive en <a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main/RAG.Core/Services/TextExtractor.cs" target="_blank" rel="noopener noreferrer"><code>RAG.Core/Services/TextExtractor.cs</code></a>.</p>
<p>Para archivos TXT, la extracción es una lectura UTF-8 directa. Para PDFs, el proyecto usa PdfPig para extraer texto por página. La extracción de texto en PDF es imperfecta porque los PDFs son documentos de layout, no documentos de texto semántico. Por eso las citas incluyen números de página cuando están disponibles, pero el texto extraído puede contener espacios raros o artefactos.</p>
<p>Nota de producción: extracción y chunking son intencionalmente directos y materializan archivos completos, texto extraído, listas de tokens, chunks y embeddings en memoria. Eso puede volverse costoso o inestable con archivos grandes incluso cuando la carga está debajo del límite configurado de bytes. Un pipeline de producción haría streaming cuando sea posible, aplicaría límites de texto extraído y tokens, y escribiría embeddings/vectores por lotes. Este repositorio conserva la implementación simple porque el objetivo es aprender el flujo, no preparar producción.</p>
<p>El chunking vive en <a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main/RAG.Core/Services/TextChunker.cs" target="_blank" rel="noopener noreferrer"><code>RAG.Core/Services/TextChunker.cs</code></a>.</p>
<p>La configuración predeterminada de ingesta es:</p>
<pre><code data-lang="json">{
  "ChunkTokenCount": 800,
  "ChunkOverlapTokens": 100
}</code></pre>
<p>El tokenizador es aproximado, pero el objetivo de diseño es claro: producir chunks lo bastante grandes para contener contexto útil y lo bastante pequeños para que muchos chunks quepan en un prompt de LLM.</p>
<p>El código ahora hace explícita esa aproximación mediante <code>ITokenEstimator</code>. El <code>ApproximateTokenEstimator</code> predeterminado divide por espacios en blanco; no es el tokenizador usado por Gemini, Ollama ni ningún proveedor de embeddings. Ese nombre importa porque <code>ChunkTokenCount</code> es un control de ingeniería, no una garantía de que el proveedor verá exactamente 800 tokens de modelo.</p>
<pre><code data-lang="csharp">public interface ITokenEstimator
{
    IReadOnlyList&lt;string&gt; EstimateTokens(string text);
}</code></pre>
<p>El overlap ayuda a conservar continuidad. Si una oración importante queda cerca de un límite, el overlap da a los chunks vecinos una oportunidad de conservar suficiente contexto alrededor.</p>
<p>Nota: <code>800</code> y <code>100</code> son valores iniciales, no números mágicos. Un <code>ChunkTokenCount</code> de <code>800</code> da a cada chunk embebido suficiente espacio para contexto de párrafo, lo cual ayuda en preguntas literarias que dependen de evidencia cercana. Un valor menor como <code>400</code> puede mejorar la recuperación puntual para pasajes factuales cortos, pero crea más chunks, más llamadas de embeddings, más filas vectoriales y más oportunidades de separar ideas relacionadas. <code>ChunkOverlapTokens</code> es <code>100</code>, o 12.5% del tamaño del chunk, así que los chunks adyacentes comparten suficiente contexto sin duplicar demasiado texto. En la práctica, el overlap suele ajustarse como proporción, comúnmente alrededor de 10-20%, y luego se adapta al tipo de documento y a la calidad observada de respuestas.</p>
<p>Los factores limitantes principales son el límite de entrada del modelo de embeddings, la ventana de contexto del modelo de chat, la cantidad de recuperación, latencia, almacenamiento y costo. Chunks más grandes reducen el volumen de indexación pero pueden hacer menos precisos los resultados de búsqueda. Chunks más pequeños mejoran precisión pero exigen recuperar más chunks para responder preguntas amplias. Más overlap conserva continuidad pero aumenta embeddings duplicados y almacenamiento vectorial. Los valores correctos deben medirse contra las preguntas que el sistema necesita responder.</p>
<p>Un tokenizador específico del proveedor sería una mejora futura, pero el punto de extensión actual ya es útil: las pruebas pueden fijar el comportamiento de chunking, y un tokenizador posterior puede reemplazar el estimador sin reescribir la ingesta.</p></section>""",
    "chapter09.html": """<section class="chapter-body tutorial-content"><p>Simplemente crear embeddings del texto fuente muchas veces no alcanza. Las preguntas amplias pueden requerir material de apoyo generado que se indexa para recuperación sin tratarse como evidencia primaria.</p>
<p>Este capítulo es donde el pipeline RAG empieza a convertirse en producto en lugar de una demo genérica de búsqueda de documentos. El sistema de recuperación crudo puede encontrar pasajes, pero los artefactos literarios moldean el sistema alrededor de las expectativas de un usuario de club de lectura. Le dan a la aplicación su comportamiento de dominio: eso la convierte en un chat de club de lectura y no en un chat de información de viajes, documentos legales o PDFs genéricos.</p>
<p>La pregunta de diseño importante no es solo \"¿qué texto indexamos?\" También es \"¿qué preguntarán usuarios reales y qué conocimiento de apoyo debería existir para que el sistema responda bien?\" Para un asistente de club de lectura, los usuarios suelen preguntar por personajes, temas, escenario, motivaciones, simbolismo y prompts de discusión. Esas preguntas pueden requerir síntesis de todo el libro, no solo de un párrafo cercano.</p>
<p>Para mejorar esto, el worker genera chunks derivados adicionales:</p>
<ul>
<li>un perfil de club de lectura;</li>
<li>un perfil de nombres/entidades.</li>
</ul>
<p>Se crean mediante <a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main/RAG.Core/Services/LiteraryArtifactGenerator.cs" target="_blank" rel="noopener noreferrer"><code>RAG.Core/Services/LiteraryArtifactGenerator.cs</code></a> y el <code>ILiteraryAnalysisProvider</code> configurado.</p>
<p>El generador de artefactos lee chunks fuente representativos y pide al proveedor de IA seleccionado que cree resúmenes estructurados y buscables para el dominio. Estos resúmenes no reemplazan los chunks fuente. Son objetivos de recuperación adicionales que facilitan responder preguntas amplias centradas en el usuario.</p>
<p>Los artefactos generados se embeben y guardan en Qdrant como chunks normales, pero su <code>chunkType</code> los identifica:</p>
<pre><code data-lang="text">literary_book_club_profile
literary_name_profile</code></pre>
<p>Esta es una lección importante de RAG: la base vectorial puede almacenar tanto material fuente como material de apoyo generado. El material de apoyo debe diseñarse alrededor de las preguntas esperadas de los usuarios.</p>
<p>En un proyecto real, aquí importa el análisis de producto. Un sistema RAG útil empieza con el workflow del usuario, no solo con el esquema de base de datos o la elección del modelo. Si el producto fuera un chat de información de viajes, los artefactos generados podrían enfocarse en destinos, horarios, opciones de transporte, clima, accesibilidad y restricciones de itinerario. Si fuera un asistente legal, podrían enfocarse en partes, obligaciones, fechas, cláusulas, riesgos y definiciones. La capa de recuperación debe reflejar el trabajo que el usuario intenta hacer.</p>
<p>Para este MVP, el dominio esperado es discusión de club de lectura, así que el perfil generado se enfoca en:</p>
<ul>
<li>protagonistas probables;</li>
<li>personajes principales;</li>
<li>escenario;</li>
<li>resumen de trama;</li>
<li>arcos de personajes;</li>
<li>temas;</li>
<li>motivos;</li>
<li>preguntas de discusión;</li>
<li>notas de evidencia.</li>
</ul>
<h3>Procedencia de artefactos generados</h3>
<p>El código mantiene honestos los artefactos generados con <code>ChunkProvenance</code>. Los chunks fuente no se marcan como generados. El perfil determinista de nombres registra <code>Provider = \"RAGPipeline\"</code>, <code>Model = \"deterministic-name-extractor\"</code> y <code>PromptVersion = \"deterministic-name-profile-v1\"</code>. El perfil de club de lectura del LLM registra el proveedor de IA configurado, modelo de chat, versión de prompt, timestamp de generación y los índices de chunks y páginas fuente usados para construir el perfil.</p>
<pre><code data-lang="csharp">public sealed record ChunkProvenance(
    bool IsGenerated,
    string? ArtifactKind,
    string? Provider,
    string? Model,
    string? PromptVersion,
    DateTimeOffset? GeneratedAtUtc,
    IReadOnlyList&lt;int&gt;? SourceChunkIndexes,
    IReadOnlyList&lt;int&gt;? SourcePageNumbers);</code></pre>
<p>Esa procedencia es la diferencia entre usar resúmenes generados responsablemente y fingir que son evidencia primaria. Los artefactos generados mejoran la recuperación, pero las citas y etiquetas de UI todavía deben decir al lector cuándo un chunk vino de material de apoyo generado.</p></section>""",
    "chapter10.html": """<section class="chapter-body tutorial-content"><p>El proyecto soporta Ollama y Gemini mediante implementaciones de proveedores:</p>
<ul>
<li><code>OllamaEmbeddingProvider</code></li>
<li><code>OllamaChatCompletionProvider</code></li>
<li><code>OllamaLiteraryAnalysisProvider</code></li>
<li><code>GeminiEmbeddingProvider</code></li>
<li><code>GeminiChatCompletionProvider</code></li>
<li><code>GeminiLiteraryAnalysisProvider</code></li>
</ul>
<p>La selección de proveedor ocurre en <code>ServiceCollectionExtensions.AddAiProviders</code>.</p>
<p>El resto del código depende solo de:</p>
<pre><code data-lang="csharp">IEmbeddingProvider
IChatCompletionProvider
ILiteraryAnalysisProvider</code></pre>
<p>Eso significa que agregar otro proveedor debería ser un cambio enfocado:</p>
<ol>
<li>implementar las interfaces del proveedor;</li>
<li>agregar una rama de configuración en <code>AddAiProviders</code>;</li>
<li>definir la URL base, nombres de modelos y fuente de API key específicas del proveedor.</li>
</ol>
<p>Un proveedor futuro para Azure OpenAI, AWS Bedrock, Vertex AI u OpenAI no debería requerir cambios en el servicio de ingesta, endpoints de API ni orquestación del worker.</p></section>""",
    "chapter11.html": """<section class="chapter-body tutorial-content"><p><a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main/RAG.Core/Services/QdrantVectorStore.cs" target="_blank" rel="noopener noreferrer"><code>RAG.Core/Services/QdrantVectorStore.cs</code></a> controla la interacción con Qdrant.</p>
<p>Cada punto guarda:</p>
<ul>
<li>vector;</li>
<li><code>documentId</code>;</li>
<li><code>fileName</code>;</li>
<li><code>chunkIndex</code>;</li>
<li><code>pageNumber</code>;</li>
<li><code>sourceObjectKey</code>;</li>
<li><code>text</code>;</li>
<li><code>chunkType</code>;</li>
<li><code>title</code>;</li>
<li>campos de procedencia de artefactos generados como <code>isGeneratedArtifact</code>, <code>artifactKind</code>, proveedor, modelo, versión de prompt, hora de generación e índices de chunk/página fuente.</li>
</ul>
<p>El endpoint de búsqueda vectorial devuelve chunks y payloads coincidentes. Los payloads se convierten en citas, diagnósticos y contexto para el LLM. Preservar la procedencia en Qdrant permite que un perfil generado de club de lectura sobreviva el recorrido de ingesta a recuperación y renderizado de citas sin confundirse con texto fuente.</p>
<p>El store también soporta dos helpers de recuperación no vectorial:</p>
<ul>
<li><code>GetDocumentProfileChunksAsync</code></li>
<li><code>GetChunksContainingTextAsync</code></li>
</ul>
<p>Existen porque la búsqueda vectorial no siempre alcanza. Si un usuario hace una pregunta comparativa con personajes nombrados, una búsqueda exacta por nombre puede asegurar que cada sujeto nombrado aporte evidencia.</p>
<p>Así es como el proyecto maneja preguntas como:</p>
<pre><code data-lang="text">Can you find any similarities between Calpurnia and Hermione?</code></pre>
<p>La recuperación semántica top-k pura puede enfocarse demasiado en un solo libro. La ruta mejorada de recuperación combina búsqueda semántica, chunks de perfiles y chunks con nombres exactos.</p>
<p>El almacén vectorial también tiene una operación de borrado por documento. Reindexación y eliminación llaman a <code>DeleteDocumentAsync</code> para que puntos vectoriales antiguos no permanezcan después de cambios en datos derivados o cuando un usuario elimina un documento.</p></section>""",
    "chapter12.html": """<section class="chapter-body tutorial-content"><p>Cómo la ruta de preguntas expande consultas, reordena evidencia, expone diagnósticos y aplica límites de seguridad.</p>
<pre><code data-lang="text">POST /api/ask</code></pre>
<p>Acepta:</p>
<pre><code data-lang="json">{
  "question": "Can you compare Calpurnia and Hermione?",
  "documentIds": null,
  "includeDiagnostics": false
}</code></pre>
<p><a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main/RAG.Core/Services/ChatAnswerService.cs" target="_blank" rel="noopener noreferrer"><code>RAG.Core/Services/ChatAnswerService.cs</code></a> maneja el workflow:</p>
<ol>
<li>validar la pregunta;</li>
<li>construir múltiples consultas de recuperación;</li>
<li>crear embeddings para cada consulta;</li>
<li>buscar en Qdrant;</li>
<li>detectar preguntas de tipo comparación;</li>
<li>extraer sujetos nombrados;</li>
<li>agregar perfiles literarios coincidentes;</li>
<li>agregar chunks con nombres exactos;</li>
<li>ordenar y filtrar candidatos;</li>
<li>enviar chunks seleccionados al proveedor de chat;</li>
<li>devolver respuesta y citas.</li>
</ol>
<p>La ruta de preguntas ahora aplica límites configurados antes de que empiece la recuperación: la pregunta debe existir, su longitud debe caber en <code>MaxQuestionCharacters</code>, los IDs de documentos seleccionados deben caber en <code>MaxSelectedDocuments</code>, las consultas de recuperación generadas están limitadas por <code>MaxRetrievalQueries</code> y las llamadas a proveedores corren con un timeout enlazado desde <code>ProviderTimeoutSeconds</code>.</p>
<p>Nota de producción: estos límites no reemplazan autenticación, autorización, rate limiting ni controles de facturación. Son controles locales que evitan que una app de tutorial acepte trabajo sin límites antes de crear embeddings o llamar a un proveedor de modelos.</p>
<p>Las preguntas literarias amplias generan consultas expandidas:</p>
<pre><code data-lang="text">literary book club profile protagonists major characters themes...
main characters protagonists central people important names...
who are the key people and what roles do they have...</code></pre>
<h3>La recuperación es un problema de ranking</h3>
<p>El servicio de preguntas ahora separa tres ideas que suelen mezclarse en demos simples de RAG: generación de candidatos, reranking y selección de contexto. La búsqueda semántica crea candidatos, <code>IRetrievalReranker</code> asigna ranks finales con razones, y la selección de contexto deduplica y recorta la evidencia final enviada al modelo de chat.</p>
<p>El <code>HeuristicRetrievalReranker</code> predeterminado empieza con el score vectorial y luego suma boosts explícitos para perfiles generados, coincidencias de consultas con sujetos nombrados y coincidencias de sujetos nombrados en comparaciones. Devuelve registros <code>RankedChunk</code> con razones de ranking, que luego aparecen en diagnósticos.</p>
<p>Las preguntas comparativas reciben manejo adicional:</p>
<ul>
<li>términos como <code>similarities</code>, <code>compare</code>, <code>between</code>, <code>both</code>, <code>contrast</code> y <code>differences</code> activan el modo comparación;</li>
<li>nombres con mayúscula se tratan como sujetos nombrados;</li>
<li>documentos no relacionados de bajo ranking se filtran;</li>
<li>se devuelven citas para todo el contexto enviado al LLM.</li>
</ul>
<p>Este diseño sigue siendo genérico. No está hardcodeado a Calpurnia, Hermione, Harry Potter ni Eisenhorn. Usa la forma de la pregunta y los nombres para recuperar mejor evidencia.</p>
<h3>Diagnósticos de recuperación</h3>
<p>Para depuración local, quien llama puede activar <code>includeDiagnostics</code> en <code>POST /api/ask</code> o llamar al endpoint dedicado de debug:</p>
<pre><code data-lang="text">POST /api/ask/debug</code></pre>
<p>Los diagnósticos incluyen texto de consultas expandidas, extracción de sujetos nombrados, detección de modo comparación, scores vectoriales crudos, ranks finales, razones de ranking, contexto seleccionado y si los candidatos fueron filtrados por umbral de comparación, deduplicación o límites de contexto.</p>
<p>Esta es una de las adiciones profesionales más importantes. Cuando una respuesta es mala, un ingeniero puede inspeccionar si la recuperación encontró chunks incorrectos, si el ranking prefirió evidencia equivocada, si el presupuesto de contexto descartó material útil o si el modelo ignoró buena evidencia.</p></section>""",
    "chapter13.html": """<section class="chapter-body tutorial-content"><p>La forma del prompt de chat es compartida por los proveedores Gemini y Ollama. <code>GeminiChatCompletionProvider</code> y <code>OllamaChatCompletionProvider</code> envían un mensaje de sistema más un mensaje de usuario que contiene extractos de evidencia numerados.</p>
<p>El prompt de sistema indica al modelo que:</p>
<ul>
<li>responda directamente;</li>
<li>use solo los extractos proporcionados;</li>
<li>prefiera artefactos literarios para preguntas literarias amplias;</li>
<li>evite volcar pasajes largos;</li>
<li>distinga evidencia de interpretación;</li>
<li>cite extractos inline con números entre corchetes;</li>
<li>diga qué falta cuando la evidencia es insuficiente.</li>
</ul>
<p>El prompt de usuario lista extractos numerados:</p>
<pre><code data-lang="text">[1] File name, page, chunk
chunk text...

[2] File name, page, chunk
chunk text...</code></pre>
<p>La API devuelve registros <code>CitationDto</code> con:</p>
<ul>
<li>ID de documento;</li>
<li>nombre de archivo;</li>
<li>índice de chunk;</li>
<li>número de página;</li>
<li>score;</li>
<li>snippet;</li>
<li>tipo de chunk;</li>
<li>título;</li>
<li>si la cita es un artefacto generado;</li>
<li>tipo de artefacto cuando aplica.</li>
</ul>
<p>La UI muestra estas citas debajo de la respuesta para que el usuario pueda inspeccionar de dónde vino la respuesta.</p>
<p>La UI etiqueta las citas como <code>Source text</code>, <code>Generated book-club profile</code>, <code>Generated name profile</code> o una ayuda genérica de recuperación generada.</p>
<h3>Las citas no son prueba</h3>
<p>Una cita en esta app significa: \"este chunk fue seleccionado y enviado como contexto\". No prueba que el modelo haya usado el chunk correctamente, y no prueba que un artefacto generado sea evidencia directa de la fuente. Esa distinción es la razón por la que los DTOs de citas exponen <code>ChunkType</code>, <code>Title</code>, <code>IsGeneratedArtifact</code> y <code>ArtifactKind</code>.</p>
<p>En un sistema de producción más estricto, la fidelidad de citas se evaluaría por separado: si cada afirmación de la respuesta tiene soporte en texto fuente citado, si el modelo citó el extracto correcto y si evitó tratar resúmenes generados como verdad de base.</p></section>""",
    "chapter14.html": """<section class="chapter-body tutorial-content"><p>Las pruebas son intencionalmente enfocadas, no exhaustivas.</p>
<p><code>TextChunkerTests</code> verifica tamaño de chunks y comportamiento de overlap.</p>
<p><code>AiProviderRegistrationTests</code> verifica la selección de proveedor mediante configuración.</p>
<p><code>ChatAnswerServiceTests</code> verifica:</p>
<ul>
<li>los chunks recuperados se convierten en citas;</li>
<li>preguntas amplias sobre personajes expanden la recuperación;</li>
<li>preguntas sobre protagonistas pueden usar perfiles de documento;</li>
<li>preguntas comparativas recuperan evidencia para cada sujeto nombrado;</li>
<li>documentos no relacionados se filtran del contexto de comparación;</li>
<li>la procedencia de citas se devuelve para artefactos generados;</li>
<li>los diagnósticos se incluyen cuando se piden;</li>
<li>los límites de longitud de pregunta, documentos seleccionados, consultas de recuperación y timeout se comportan correctamente.</li>
</ul>
<h3>Evaluación con preguntas doradas</h3>
<p><code>RAG.Tests/Evaluation/RagEvaluationTests.cs</code> es un pequeño harness de evaluación RAG. Usa embeddings, búsqueda vectorial y chat completion falsos y deterministas para correr en pruebas unitarias normales sin Docker, Qdrant, Ollama, Gemini ni acceso de red.</p>
<p>Los casos dorados revisan recuperación factual directa, recuperación literaria amplia, comparación entre documentos, restricciones de documentos seleccionados, manejo sin evidencia y etiquetado de citas de artefactos generados. Las aserciones se enfocan en contexto seleccionado y tipos de cita porque esas son las partes que una prueba determinista puede juzgar de forma confiable.</p>
<pre><code data-lang="csharp">public sealed record RagEvaluationCase(
    string Name,
    string Question,
    IReadOnlyList&lt;Guid&gt;? DocumentIds,
    IReadOnlyList&lt;string&gt; ExpectedFileNames,
    IReadOnlyList&lt;string&gt; ExpectedTermsInSelectedContext,
    bool RequiresSourceCitation,
    bool AllowsGeneratedArtifactCitation);</code></pre>
<p>Esto no reemplaza revisión humana de calidad de respuesta, pero da al proyecto una suite de regresión para comportamiento de recuperación. Es un paso grande más allá de probar manualmente \"hazle unas preguntas\".</p>
<h3>Pruebas adicionales de puntos de extensión para producción</h3>
<p><code>DatabaseIngestionWorkSourceTests</code>, <code>DocumentManagementServiceTests</code>, <code>HeuristicRetrievalRerankerTests</code> y <code>QdrantVectorStoreTests</code> cubren los nuevos puntos de extensión para reemplazo de polling, transiciones de estado de borrar/reindexar, reranking heurístico y procedencia de payload vectorial.</p>
<p>Ejecuta pruebas con:</p>
<pre><code data-lang="bash">dotnet test RAGPipeline.sln</code></pre>
<p>El proyecto también se beneficia de pruebas manuales porque el comportamiento RAG depende de documentos reales, salida del modelo y calidad de búsqueda vectorial.</p>
<p>Revisiones manuales recomendadas:</p>
<ol>
<li>Sube un archivo TXT corto.</li>
<li>Sube un libro en PDF.</li>
<li>Confirma que el progreso avanza por las etapas de ingesta.</li>
<li>Haz una pregunta directa sobre un documento.</li>
<li>Haz una pregunta amplia sobre personajes.</li>
<li>Haz una pregunta comparativa entre documentos.</li>
<li>Confirma que las citas referencian los documentos esperados.</li>
</ol></section>""",
    "chapter15.html": """<section class="chapter-body tutorial-content"><p>Comandos y URLs locales para ejecutar el pipeline RAG con Gemini u Ollama.</p>
<pre><code data-lang="bash">dotnet build RAGPipeline.sln
dotnet test RAGPipeline.sln
dotnet run --project RAG.AppHost/RAG.AppHost.csproj</code></pre>
<p>Con Gemini:</p>
<pre><code data-lang="bash">export GEMINI_API_KEY="your-key"
export RAG_AI_PROVIDER="Gemini"
dotnet run --project RAG.AppHost/RAG.AppHost.csproj</code></pre>
<p>Con Ollama local:</p>
<pre><code data-lang="bash">unset GEMINI_API_KEY
unset RAG_AI_PROVIDER
dotnet run --project RAG.AppHost/RAG.AppHost.csproj</code></pre>
<p>URLs locales:</p>
<ul>
<li>UI/API: <code>http://127.0.0.1:5080/</code></li>
<li>Dashboard: <code>https://localhost:17071</code></li>
<li>Qdrant: <code>http://localhost:6333</code></li>
<li>MinIO API: <code>http://localhost:9000</code></li>
<li>Consola MinIO: <code>http://localhost:9001</code></li>
</ul>
<p>El dashboard de Aspire puede mostrar advertencias del certificado local de desarrollo HTTPS. Son separadas de la API, que se sirve por HTTP en este ejemplo.</p>
<h3>A dónde ir después</h3>
<p>En este punto, el siguiente paso útil no es otra página de resumen; es ejecutar el sistema e inspeccionar su comportamiento. Ejecuta las pruebas, prueba <code>/api/ask/debug</code>, inspecciona <code>RAG.Tests/Evaluation/RagEvaluationTests.cs</code> y experimenta con tamaño de chunks, expansión de consultas de recuperación y reranking para ver cómo cambia la calidad de respuesta.</p></section>""",
}

source_summaries = {
    "chapter01.html": "El mapa del proyecto del tutorial",
    "chapter02.html": "AppHost conecta dependencias locales con API y worker",
    "chapter03.html": "Los contratos mantienen proveedores de modelos fuera del workflow",
    "chapter04.html": "Los estados del ciclo de vida del documento",
    "chapter05.html": "El endpoint de carga encola trabajo en vez de hacerlo",
    "chapter06.html": "Las claves de objetos empiezan con el ID del documento",
    "chapter07.html": "El servicio de ingesta controla el pipeline de larga duración",
    "chapter08.html": "La configuración predeterminada de chunks",
    "chapter09.html": "Los chunks de artefactos tienen sus propios tipos",
    "chapter10.html": "La superficie neutral al proveedor",
    "chapter11.html": "Cada vector lleva payload de cita",
    "chapter12.html": "El endpoint de preguntas delega recuperación y generación de respuesta",
    "chapter13.html": "La API devuelve respuesta más registros de citas",
    "chapter14.html": "Ejecuta la suite de pruebas desde la raíz del repo",
    "chapter15.html": "Comandos locales comunes",
}

index_body = """<main class="rag-main rag-index"><section class="rag-hero"><div class="rag-hero__copy"><span class="rag-kicker">Introducción a RAG</span><h1>Construye respuestas desde evidencia, no desde memoria.</h1><p class="subtitle">Un recorrido práctico por un pipeline RAG de club de lectura en .NET con Aspire, Qdrant, MinIO, Gemini u Ollama, y respuestas respaldadas por citas.</p><div class="rag-hero__actions"><a href="chapter01.html">Empezar la guía</a><a href="https://github.com/jaime-reyes-rrtx/rag-intro-tutorial/blob/main" target="_blank" rel="noopener noreferrer">Abrir el repo</a></div></div><figure class="rag-hero__image"><img src="../images/rag-guide-og.svg" alt="Ilustración de un pipeline de generación aumentada por recuperación, desde documentos hasta citas." loading="eager"></figure></section><section class="translation-note"><strong>Nota de traducción:</strong> Esta versión en español fue traducida con ayuda de un LLM y revisada para conservar los términos técnicos, el código y los nombres de archivos en inglés cuando corresponde.</section><section class="rag-explainer" aria-labelledby="what-is-rag"><div><span class="rag-kicker">¿Qué es RAG?</span><h2 id="what-is-rag">La generación aumentada por recuperación conecta un modelo de lenguaje con tu propia evidencia.</h2></div><div><p>Los modelos grandes de lenguaje son excelentes con el lenguaje, pero no conocen automáticamente tus documentos privados, tus datos operativos más recientes ni los pasajes exactos que un usuario necesita para confiar en una respuesta. RAG agrega un paso de recuperación antes de la generación: guardar material fuente, buscar chunks relevantes, pasar esos chunks al modelo y devolver una respuesta con citas.</p><p>Eso vuelve necesario RAG cuando la respuesta debe estar basada en un corpus privado o cambiante: políticas, tickets, libros, registros de clientes, manuales, notas de investigación o bases internas de conocimiento. El modelo escribe la respuesta, pero la capa de recuperación decide qué evidencia puede usar.</p><p>En la práctica, las partes difíciles no son solo la selección del modelo. Un sistema RAG profesional debe hacer la recuperación inspeccionable, distinguir evidencia primaria de material de apoyo generado, evaluar el comportamiento de respuestas contra preguntas conocidas y poner límites alrededor de costo, latencia y entrada de usuario.</p><div class="rag-flow" aria-label="Flujo RAG"><span>Cargar</span><span>Extraer</span><span>Chunk</span><span>Embedding</span><span>Recuperar</span><span>Responder</span><span>Evaluar</span></div></div></section><section class="rag-source-note"><h2>Resumen de la serie</h2><p>Esta guía explica el proyecto de ejemplo actual como una serie respaldada por código fuente. Está escrita para ingenieros que ya conocen C# básico y ASP.NET Core, pero todavía están aprendiendo cómo se ensamblan y evalúan los sistemas RAG modernos.</p><p>El objetivo no es presentar una arquitectura perfecta de producción. El objetivo es mostrar cómo se conectan las piezas, dónde están los límites y por qué esos límites importan al construir un sistema de ingesta de documentos y preguntas-respuestas en .NET.</p><h3>Workflow del proyecto</h3><p>El proyecto implementa este workflow:</p><pre><code data-lang="text">1. Upload PDF/TXT
2. Store original file in object storage
3. Track metadata in SQLite
4. Worker extracts text
5. Generate book-club literary artifacts
6. Chunk source text and artifacts
7. Generate embeddings
8. Store vectors and citation payloads in Qdrant
9. Retrieve relevant chunks for a question
10. Send chunks to an LLM
11. Return answer + citations</code></pre><p>En alto nivel, el sistema tiene seis responsabilidades:</p><ul><li><strong>Orquestación:</strong> Aspire inicia la API, worker, Qdrant, MinIO y opcionalmente Ollama.</li><li><strong>Interacción de usuario:</strong> La API hospeda la UI de carga y chat.</li><li><strong>Estado durable:</strong> SQLite registra estado de documentos; MinIO guarda originales; Qdrant guarda vectores.</li><li><strong>Ingesta:</strong> El worker convierte archivos en chunks buscables.</li><li><strong>Respuesta:</strong> El servicio de preguntas recupera evidencia y pide a un LLM que responda desde esa evidencia.</li><li><strong>Evaluación y operaciones:</strong> Pruebas, diagnósticos, procedencia, límites de solicitud, logging y controles de borrar/reindexar hacen que el ejemplo sea inspeccionable en vez de opaco.</li></ul><p>La decisión de diseño más importante es que la API y el worker no conocen formatos de solicitud específicos de modelos. Dependen de interfaces como <code>IEmbeddingProvider</code>, <code>IChatCompletionProvider</code> e <code>IVectorStore</code>. La misma idea ahora aplica dentro de la recuperación: estimación de tokens, reranking, descubrimiento de trabajo de ingesta, gestión documental, diagnósticos y evaluación tienen puntos explícitos para que el ejemplo enseñe las decisiones de ingeniería detrás de RAG, no solo el flujo feliz.</p><p>Esta guía se mantiene como la fuente narrativa de verdad para el proyecto de aprendizaje RAGPipeline. Sigue el código fuente actual directamente, incluyendo diagnósticos de recuperación, procedencia de artefactos generados, etiquetado de citas, límites de solicitud, pruebas de evaluación y puntos operativos.</p></section><section class="rag-editorial" aria-labelledby="what-this-guide-teaches"><div><span class="rag-kicker">Qué enseña esta guía</span><h2 id="what-this-guide-teaches">Los hábitos de ingeniería detrás de sistemas RAG creíbles.</h2><p>Los capítulos técnicos recorren la implementación, pero el proyecto también busca mostrar cómo piensan ingenieros con experiencia sobre RAG: preservar material fuente, hacer explícitos los artefactos derivados, inspeccionar recuperación, evaluar comportamiento y mantener visibles los límites operativos.</p></div><div class="rag-editorial__grid"><ul><li>Guardar documentos originales separados de vectores.</li><li>Registrar la ingesta como estado durable.</li><li>Mantener la ingesta larga fuera de rutas request/response.</li><li>Usar abstracciones neutrales al proveedor para servicios de IA.</li><li>Crear embeddings de metadatos generados, no solo texto fuente crudo, y preservar su procedencia.</li><li>Ajustar la recuperación según los tipos de preguntas esperados.</li></ul><ul><li>Combinar búsqueda vectorial con recuperación estructurada y fallback simple por nombre exacto.</li><li>Hacer la recuperación inspeccionable con diagnósticos y razones de ranking.</li><li>Devolver citas que distinguen chunks fuente de ayudas de recuperación generadas.</li><li>Mostrar fallas y progreso de ingesta en la UI.</li><li>Usar límites para tamaño de pregunta, documentos seleccionados, expansión de recuperación y timeouts de proveedores.</li><li>Probar comportamiento RAG con evaluaciones deterministas de preguntas doradas.</li></ul></div></section><section class="rag-editorial rag-editorial--compact" aria-labelledby="production-hardening"><div><span class="rag-kicker">Preparación para producción</span><h2 id="production-hardening">Qué todavía necesita más rigor antes de un despliegue real.</h2><p>Este ejemplo es un proyecto didáctico con puntos de extensión con forma de producción. Es útil para aprender arquitectura, comportamiento de recuperación y hábitos de evaluación, pero por sí solo no es una plantilla segura ni escalable de despliegue.</p></div><div class="rag-editorial__grid"><ul><li>Reemplazar actualizaciones ad hoc de esquema SQLite con migraciones.</li><li>Agregar autenticación, autorización, auditoría y política de retención.</li><li>Soportar almacenamiento de objetos en la nube directamente.</li><li>Agregar implementaciones de proveedores para Azure OpenAI, Bedrock, Vertex AI u OpenAI.</li></ul><ul><li>Agregar observabilidad más profunda sobre uso de tokens, latencia, errores de proveedor, calidad de recuperación y drift de evaluación.</li><li>Mejorar calidad de extracción de PDF.</li><li>Reemplazar la fuente de trabajo basada en base de datos por infraestructura de colas para despliegues multi-worker.</li><li>Agregar tokenización compatible con proveedor, reranking opcional basado en modelo y verificaciones de fidelidad de citas.</li></ul></div></section><section class="rag-grid" aria-label="Capítulos"></section></main>"""

card_text = {
    "chapter01.html": "Layout del proyecto y por qué la ingesta corre fuera de la ruta de solicitudes.",
    "chapter02.html": "RAG.AppHost/AppHost.cs define el entorno local.",
    "chapter03.html": "Configuración e interfaces que mantienen el código del workflow neutral al proveedor.",
    "chapter04.html": "Metadatos SQLite para estado, progreso y ciclo de vida de documentos.",
    "chapter05.html": "El endpoint de carga está en RAG.Api/Program.cs:",
    "chapter06.html": "Los archivos originales se guardan en almacenamiento de objetos antes de indexarlos. La implementación local está en RAG.Core/Services/S3ObjectStorage.cs.",
    "chapter07.html": "RAG.Worker/Worker.cs es un servicio en segundo plano que consulta periódicamente y pide a IDocumentIngestionService que procese documentos pendientes.",
    "chapter08.html": "La extracción de texto vive en RAG.Core/Services/TextExtractor.cs.",
    "chapter09.html": "Los perfiles literarios generados mejoran la recuperación amplia para club de lectura sin fingir que son evidencia fuente.",
    "chapter10.html": "El proyecto soporta Ollama y Gemini mediante implementaciones de proveedores:",
    "chapter11.html": "RAG.Core/Services/QdrantVectorStore.cs controla la interacción con Qdrant.",
    "chapter12.html": "Expansión de consultas, reranking, diagnósticos y límites de solicitud en la ruta de preguntas.",
    "chapter13.html": "Los prompts de proveedor convierten evidencia seleccionada en respuestas con citas inspeccionables.",
    "chapter14.html": "Las pruebas son intencionalmente enfocadas, no exhaustivas.",
    "chapter15.html": "Comandos y URLs locales para Gemini, Ollama, Aspire, Qdrant y MinIO.",
}

def page_urls(filename):
    english = "https://sandybrook.io/guides/rag/" if filename == "index.html" else f"https://sandybrook.io/guides/rag/{filename}"
    spanish = "https://sandybrook.io/guides/rag/es/" if filename == "index.html" else f"https://sandybrook.io/guides/rag/es/{filename}"
    return english, spanish

def replace_meta(html, selector, value):
    if selector.startswith("name:"):
        key = selector[5:]
        return re.sub(rf'(<meta name="{re.escape(key)}" content=")[^"]*(">)', rf'\1{value}\2', html)
    key = selector[9:]
    return re.sub(rf'(<meta property="{re.escape(key)}" content=")[^"]*(">)', rf'\1{value}\2', html)

def add_alternates(html, english, spanish):
    html = re.sub(r'\n?<link rel="alternate" hreflang="[^"]+" href="[^"]+">', "", html)
    alt = f'\n<link rel="alternate" hreflang="en" href="{english}">\n<link rel="alternate" hreflang="es-419" href="{spanish}">'
    return re.sub(r'(<link rel="canonical" href="[^"]+">)', r'\1' + alt, html, count=1)

def switch_html(current, other):
    if current == "en":
        return f'<div class="language-switch" aria-label="Language selector"><span class="is-active" aria-current="page">EN</span><a href="{other}" hreflang="es-419" lang="es">ES</a></div>'
    return f'<div class="language-switch" aria-label="Selector de idioma"><a href="{other}" hreflang="en" lang="en">EN</a><span class="is-active" aria-current="page">ES</span></div>'

def add_switch(html, current, other):
    html = re.sub(r'<div class="language-switch"[^>]*>.*?</div>', "", html)
    marker = '<a href="../" class="hidden md:inline-flex text-sm font-medium hover:text-brand transition-colors">Guides</a>'
    replacement = marker + switch_html(current, other)
    if marker in html:
        return html.replace(marker, replacement, 1)
    marker_es = '<a href="../" class="hidden md:inline-flex text-sm font-medium hover:text-brand transition-colors">Guías</a>'
    if marker_es in html:
        return html.replace(marker_es, marker_es + switch_html(current, other), 1)
    marker_es_deep = '<a href="../../" class="hidden md:inline-flex text-sm font-medium hover:text-brand transition-colors">Guías</a>'
    return html.replace(marker_es_deep, marker_es_deep + switch_html(current, other), 1)

def rewrite_paths_for_es(html):
    html = html.replace('href="../../', 'href="__ROOT__/')
    html = html.replace('src="../../', 'src="__ROOT__/')
    html = html.replace('href="../', 'href="../../')
    html = html.replace('src="../', 'src="../../')
    html = html.replace('href="__ROOT__/', 'href="../../../')
    html = html.replace('src="__ROOT__/', 'src="../../../')
    html = html.replace('href="styles.css"', 'href="../styles.css"')
    html = html.replace('src="scripts/', 'src="../scripts/')
    html = html.replace('src="images/', 'src="../images/')
    return html

def localize_common_es(html, filename):
    replacements = {
        '<html lang="en">': '<html lang="es-419">',
        '>Intro to RAG<': '>Introducción a RAG<',
        '>Home<': '>Inicio<',
        '>Guide Home<': '>Inicio de la guía<',
        '>All Guides<': '>Todas las guías<',
        '>Guides<': '>Guías<',
        'aria-label="Open Menu"': 'aria-label="Abrir menú"',
        'aria-label="Toggle Theme"': 'aria-label="Cambiar tema"',
        'aria-label="Sandy Brook Projects Lab Home"': 'aria-label="Inicio de Sandy Brook Projects Lab"',
        'alt="Sandy Brook DevWorks Logo"': 'alt="Logo de Sandy Brook DevWorks"',
        '>Services<': '>Servicios<',
        '>About<': '>Acerca de<',
        '>Contact<': '>Contacto<',
        '<span>Guide navigation</span><strong>Index and chapters</strong>': '<span>Navegación de la guía</span><strong>Índice y capítulos</strong>',
        'aria-label="Introduction to RAG chapters"': 'aria-label="Capítulos de Introducción a RAG"',
        '>Guide index<': '>Índice de la guía<',
        '<span class="label">Previous</span>': '<span class="label">Anterior</span>',
        '<span class="label">Next</span>': '<span class="label">Siguiente</span>',
        '<span class="label">Guide home</span>': '<span class="label">Inicio de la guía</span>',
        'aria-label="Source files for this chapter"': 'aria-label="Archivos fuente de este capítulo"',
        '>Source trail<': '>Archivos fuente<',
        '>Open the complete code in the RAG tutorial repo.<': '>Abre el código completo en el repositorio del tutorial de RAG.<',
        '>Full source: ': '>Código fuente completo: ',
    }
    for old, new in replacements.items():
        html = html.replace(old, new)
    mobile_titles = {
        "1. Solution Topology": "1. Topología de la solución",
        "2. Aspire as": "2. Aspire como plano de control local",
        "3. Shared Configuration": "3. Configuración y contratos compartidos",
        "4. Metadata with": "4. Metadatos con SQLite y EF Core",
        "5. Upload API": "5. API e interfaz de carga",
        "6. Object Storage": "6. Almacenamiento de objetos con MinIO",
        "7. Worker Ingestion": "7. Pipeline de ingesta del worker",
        "8. Extracting and": "8. Extracción y división de texto",
        "9. Literary Artifacts": "9. Artefactos literarios",
        "10. AI Provider": "10. Abstracciones de proveedores de IA",
        "11. Qdrant Vector": "11. Almacenamiento vectorial con Qdrant",
        "12. Ask Flow": "12. Flujo de preguntas y recuperación",
        "13. Prompting and": "13. Prompts y citas",
        "14. Testing the": "14. Pruebas del pipeline",
        "15. Local Development": "15. Notas de desarrollo local",
    }
    for old, new in mobile_titles.items():
        html = html.replace(f">{old}<", f">{new}<")
    english_to_spanish = {
        "Solution Topology": chapter_titles["chapter01.html"],
        "Aspire as the Local Control Plane": chapter_titles["chapter02.html"],
        "Shared Configuration and Contracts": chapter_titles["chapter03.html"],
        "Metadata with SQLite and EF Core": chapter_titles["chapter04.html"],
        "Upload API and UI": chapter_titles["chapter05.html"],
        "Object Storage with MinIO": chapter_titles["chapter06.html"],
        "Worker Ingestion Pipeline": chapter_titles["chapter07.html"],
        "Extracting and Chunking Text": chapter_titles["chapter08.html"],
        "Literary Artifacts": chapter_titles["chapter09.html"],
        "AI Provider Abstractions": chapter_titles["chapter10.html"],
        "Qdrant Vector Storage": chapter_titles["chapter11.html"],
        "Ask Flow and Retrieval Strategy": chapter_titles["chapter12.html"],
        "Prompting and Citations": chapter_titles["chapter13.html"],
        "Testing the Pipeline": chapter_titles["chapter14.html"],
        "Local Development Notes": chapter_titles["chapter15.html"],
        "Introduction to RAG": "Introducción a RAG",
    }
    for old, new in english_to_spanish.items():
        html = re.sub(rf'(<span class="title">){re.escape(old)}(</span>)', rf'\1{new}\2', html)
        html = re.sub(rf'(<a href="chapter\d\d\.html"(?: aria-current="page" class="is-current"| class="is-current")?><span>\d+</span>){re.escape(old)}(</a>)', rf'\1{new}\2', html)
    if filename in source_summaries:
        html = re.sub(r'(<details class="source-panel"><summary>).*?(</summary>)', rf'\1{source_summaries[filename]}\2', html, count=1)
    return html

def update_english_page(path):
    filename = path.name
    html = path.read_text()
    english, spanish = page_urls(filename)
    html = add_alternates(html, english, spanish)
    other = "es/" if filename == "index.html" else f"es/{filename}"
    html = add_switch(html, "en", other)
    path.write_text(html, encoding="utf-8")

def make_spanish_page(path):
    filename = path.name
    html = rewrite_paths_for_es(path.read_text())
    html = localize_common_es(html, filename)
    english, spanish = page_urls(filename)
    html = add_alternates(html, english, spanish)
    html = re.sub(r'<link rel="canonical" href="[^"]+">', f'<link rel="canonical" href="{spanish}">', html, count=1)
    html = replace_meta(html, "property:og:url", spanish)
    if filename == "index.html":
        desc = "Una introducción práctica a generación aumentada por recuperación usando el ejemplo Sandy Brook Book Club RAG Pipeline."
        html = re.sub(r'<title>.*?</title>', '<title>Introducción a RAG | Sandy Brook Projects Lab</title>', html, count=1)
        html = replace_meta(html, "name:description", desc)
        html = replace_meta(html, "property:og:title", "Introducción a RAG | Sandy Brook Projects Lab")
        html = replace_meta(html, "property:og:description", desc)
        html = replace_meta(html, "name:twitter:title", "Introducción a RAG | Sandy Brook Projects Lab")
        html = replace_meta(html, "name:twitter:description", desc)
        cards = []
        for idx, (file, title) in enumerate(chapter_titles.items(), 1):
            cards.append(f'<a href="{file}" class="rag-card"><img src="../images/chapter{idx:02}.svg" alt="Imagen decorativa del capítulo sobre {title}" loading="lazy"><span>Capítulo {idx}</span><h3>{title}</h3><p>{card_text[file]}</p></a>')
        body = index_body.replace('<section class="rag-grid" aria-label="Capítulos"></section>', '<section class="rag-grid" aria-label="Capítulos">' + "\n".join(cards) + '</section>')
        html = re.sub(r'<main class="rag-main rag-index">.*?</main>', body, html, count=1, flags=re.S)
    else:
        title = chapter_titles[filename]
        desc = chapter_descriptions[filename]
        number = int(filename[7:9])
        html = re.sub(r'<title>.*?</title>', f'<title>Capítulo {number}: {title} | Introducción a RAG</title>', html, count=1)
        html = replace_meta(html, "name:description", desc)
        html = replace_meta(html, "property:og:title", f"Capítulo {number}: {title} | Introducción a RAG")
        html = replace_meta(html, "property:og:description", desc)
        html = replace_meta(html, "name:twitter:title", f"Capítulo {number}: {title} | Introducción a RAG")
        html = replace_meta(html, "name:twitter:description", desc)
        html = re.sub(r'(<header class="chapter-head"><span class="rag-kicker">).*?(</span><h1>).*?(</h1><p class="subtitle">).*?(</p></header>)', rf'\1Capítulo {number}\2{title}\3{desc}\4', html, count=1)
        html = re.sub(r'<figure class="chapter-image"><img src="../images/(chapter\d\d\.svg)" alt="[^"]+" loading="eager"></figure>', rf'<figure class="chapter-image"><img src="../images/\1" alt="Imagen decorativa del capítulo sobre {title}" loading="eager"></figure>', html, count=1)
        note = '<section class="translation-note"><strong>Nota de traducción:</strong> Esta versión en español fue traducida con ayuda de un LLM y revisada para conservar los términos técnicos, el código y los nombres de archivos en inglés cuando corresponde.</section>'
        html = html.replace('</header><figure class="chapter-image">', f'</header>{note}<figure class="chapter-image">', 1)
        html = re.sub(r'<section class="chapter-body tutorial-content">.*?</section>', chapter_body[filename], html, count=1, flags=re.S)
    other = "../" if filename == "index.html" else f"../{filename}"
    html = add_switch(html, "es", other)
    (ES / filename).write_text(html, encoding="utf-8")

def main():
    ES.mkdir(exist_ok=True)
    for path in sorted(RAG.glob("*.html")):
        update_english_page(path)
        make_spanish_page(path)

if __name__ == "__main__":
    main()
