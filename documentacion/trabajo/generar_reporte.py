from pathlib import Path
import json, re, hashlib
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image as RLImage, Preformatted
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib import colors
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'documentacion'; EV=OUT/'evidencias'
for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf')]: pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
fonts={s:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',s) for s in [24,28,32,36]}
# Diagramas originales UML: representan el código, no son capturas de ejecución.
def diagrams():
 im=Image.new('RGB',(1500,850),'white'); d=ImageDraw.Draw(im)
 d.rectangle((340,25,1470,825),outline='black',width=3);d.text((650,45),'Simulador Efecto Dominó',font=fonts[32],fill='black')
 d.ellipse((80,330,140,390),outline='black',width=3);d.line((110,390,110,510),fill='black',width=3);d.line((40,425,180,425),fill='black',width=3);d.line((110,510,45,590),fill='black',width=3);d.line((110,510,175,590),fill='black',width=3);d.text((55,610),'Usuario',font=fonts[28],fill='black')
 labels=['Colocar fichas','Quitar fichas','Seleccionar inicio','Seleccionar objetivo','Cargar escenario','Iniciar simulación','Controlar reproducción','Consultar resultados','Comparar BFS y DFS']
 for i,label in enumerate(labels):
  x=650;y=105+i*77
  d.line((180,460,x,y+32),fill='black',width=2)
 for i,label in enumerate(labels):
  x=650;y=105+i*77
  d.ellipse((x,y,x+760,y+64),fill='white',outline='black',width=3);d.text((x+380,y+32),label,font=fonts[28],fill='black',anchor='mm')
 im.save(EV/'casos_uso.png')
 im=Image.new('RGB',(1500,760),'white');d=ImageDraw.Draw(im)
 def box(rect,lines):
  d.rectangle(rect,outline='black',width=3);x,y,x2,y2=rect
  for i,line in enumerate(lines):d.text(((x+x2)/2,y+28+i*42),line,font=fonts[28],fill='black',anchor='mm')
 box((30,40,400,170),['«componente»','main.py','Punto de entrada'])
 box((520,40,1470,240),['«componente» ui.py','DominoApp / matriz y selecciones','Canvas / controles / estadísticas','after() / reproducción de grupos'])
 box((520,390,1470,590),['«componente» algorithms.py','Result / search / bfs / dfs','reconstruct_path / compare','scenario / SCENARIOS'])
 box((30,390,400,550),['«componente»','tests.py','unittest'])
 box((30,630,1470,735),['«artefacto» README.md','Guía de ejecución y fundamentos; sin dependencia en ejecución'])
 for xy in [(400,100,520,100),(980,240,980,390),(400,460,520,460),(210,390,520,220)]:
  x,y,x2,y2=xy;
  import math
  length=math.hypot(x2-x,y2-y);ux,uy=(x2-x)/length,(y2-y)/length
  for distance in range(0,int(length),18):
   end=min(distance+10,length);d.line((x+ux*distance,y+uy*distance,x+ux*end,y+uy*end),fill='black',width=3)
  d.line((x2-ux*18-uy*9,y2-uy*18+ux*9,x2,y2,x2-ux*18+uy*9,y2-uy*18-ux*9),fill='black',width=3)
 d.text((1000,305),'utiliza',font=fonts[24],fill='black');d.text((270,300),'prueba',font=fonts[24],fill='black')
 im.save(EV/'componentes.png')
diagrams()
pages=[]
def page(): pages.append([])
def add(kind,text,**kw):pages[-1].append((kind,text,kw))
def h(t):add('h',t)
def sub(t):add('sub',t)
def p(t):add('p',t)
def table(rows,widths=None):add('table',rows,widths=widths)
def img(file,caption,width=468):add('image',file,caption=caption,width=width)
def code(file,start,end):
 lines=(ROOT/file).read_text(encoding='utf-8').splitlines(); fragment='\n'.join(lines[start-1:end]);add('code',fragment);add('caption',f'Fuente: {file}, líneas {start}–{end}.')
page()
add('cover','UNIVERSIDAD POLITÉCNICA DE SINALOA')
add('center','Ingeniería en Tecnologías de la Información e Innovación Digital')
add('space',25)
add('cover','REPORTE TÉCNICO')
add('cover','EFECTO DOMINÓ')
add('center','Simulación de Estrategias de Búsqueda BFS y DFS')
add('space',15)
add('center','Unidad 2: Algoritmos de Estrategias de Búsqueda')
add('center','Actividad: EVD2.5-EVP2.5-EVC2.5')
add('center','Materia: Inteligencia Artificial')
add('center','Docente: Iliana Amabely Silva Hernandez')
add('space',15)
add('center','Integrantes del equipo: [Nombres pendientes]')
add('center','Fecha: 9 de noviembre de 2026')
page(); h('ÍNDICE GENERAL');add('toc','')
page();h('1. RESUMEN');sub('1.1. Síntesis del Proyecto')
p('El proyecto Efecto Dominó aborda el problema de determinar qué fichas serán alcanzadas desde un punto inicial y en qué tiempo discreto se propagará una reacción. La mesa se representa mediante una matriz de ocho filas y doce columnas, donde únicamente las fichas vecinas ortogonales pueden transmitir la caída. El objetivo es ofrecer un caso de estudio de búsqueda no informada mediante un agente basado en metas que interpreta el tablero, calcula resultados y los representa visualmente. La implementación utiliza Python, Tkinter y estructuras de la biblioteca estándar. BFS emplea una cola FIFO para obtener distancias mínimas y agrupar las fichas por niveles; DFS utiliza una pila LIFO para contrastar el orden de exploración y las rutas encontradas. La animación permite observar niveles, pausar y revisar pasos. La verificación confirmó 16 pruebas automatizadas, incluida la comparación exhaustiva de distancias en las 511 configuraciones no vacías de una matriz de 3 × 3. En el laberinto, BFS procesó 31 nodos y obtuvo una ruta de 9 conexiones; DFS procesó 26 y obtuvo 19 conexiones. Los resultados muestran la utilidad de BFS para propagación mínima, sin atribuirle una ventaja universal de tiempo de procesamiento.')
h('2. INTRODUCCIÓN');sub('2.1. Contexto Teórico')
p('La inteligencia artificial estudia agentes que perciben un entorno y actúan para cumplir objetivos. En un agente basado en metas, la búsqueda permite examinar estados y transiciones antes de producir una solución (Russell y Norvig, 2021). El agente conoce el tablero completo y no aprende de datos históricos.')
p('El tablero se interpreta como un grafo. BFS explora primero los vecinos más próximos mediante una cola FIFO: el primero que entra es el primero que sale. DFS profundiza mediante una pila LIFO: el último que entra sale primero. Ambas estrategias son no informadas porque no emplean una heurística. Los niveles BFS representan tiempos discretos con costos uniformes.')
page();sub('2.2. Planteamiento del Problema')
p('Dada una matriz M de 8 × 12, con 1 para una ficha y 0 para una celda vacía, se requiere identificar el componente alcanzable desde una ficha inicial s. Si se selecciona una meta t, también se solicita una ruta. Para BFS, su longitud debe ser mínima. Una transición válida conecta fichas existentes arriba, abajo, a la izquierda o a la derecha; las diagonales y los huecos no transmiten la reacción.')
p('La interfaz exige un inicio válido antes de ejecutar. Eliminar una ficha seleccionada elimina también su designación como inicio o meta. Durante la reproducción o pausa, la edición se bloquea; reiniciar o cargar un escenario cancela el temporizador. La meta opcional no detiene la animación completa: solo la comparación utiliza terminación al extraerla. El modelo es discreto, sin cálculo de fuerzas, gravedad ni colisiones.')
sub('2.3. Diagrama de caso de uso del caso de estudio')
img('casos_uso.png','Figura 1. Casos de uso correspondientes a las operaciones de DominoApp.',468)
p('Controlar reproducción comprende pausar, reanudar, avanzar, retroceder, reiniciar y ajustar la velocidad. Consultar resultados incluye el registro de exploración, las estadísticas y la ruta. Las asociaciones representan acceso del usuario a cada función; no implican una secuencia obligatoria.')
page();h('3. DESARROLLO');sub('3.1. Arquitectura del Agente Inteligente')
p('La ejecución comienza en main.py, que crea DominoApp y entra en mainloop(). La clase de interfaz conserva la matriz, las selecciones y el estado de reproducción. algorithms.py recibe la matriz y el inicio, realiza la búsqueda y devuelve un objeto Result con orden, niveles, predecesores y duración. La lógica de búsqueda no importa Tkinter.')
p('El flujo es lectura del escenario, validación, búsqueda, agrupación y presentación. prepare() calcula todo el componente antes de animarlo. tick() actualiza el grupo actual en doce fotogramas y programa el siguiente con after(). cancel_timer() evita que una ejecución anterior continúe después de reiniciar. Los botones de revisión reconstruyen estados desde los grupos precalculados, sin ejecutar nuevamente la búsqueda.')
sub('3.1.1. Identificación y Clasificación del Tipo de Agente')
p('Se clasifica como agente basado en metas porque utiliza un modelo explícito de estados para determinar alcanzabilidad y, mediante BFS, un camino mínimo hacia una meta seleccionada. Los sensores y actuadores son abstracciones de software: lectura de entradas y actualización de la pantalla. No es un agente de aprendizaje, ni controla fichas físicas. La ejecución es deliberativa sobre una configuración fija.')
sub('3.1.2. Matriz de Diagnóstico del Modelo PEAS/RASA')
table([['Elemento','Aplicación al caso'],['Rendimiento','Exactitud de niveles, cobertura alcanzable, ruta mínima BFS y eficiencia de cálculo.'],['Entorno / ambiente','Mesa discreta de fichas y conexiones ortogonales.'],['Actuadores','Actualizar estados, dibujar fichas, rutas, conexiones y resultados.'],['Sensores','Leer matriz, inicio y meta; derivar conexiones por vecindad.']],[135,333])
page();sub('3.2. Propiedades del Entorno de Búsqueda')
table([['Propiedad','Justificación'],['Totalmente observable','La matriz y las selecciones están disponibles al iniciar. No hay fichas ocultas.'],['Determinista','Una misma configuración y orden fijo de vecinos producen el mismo recorrido y ruta.'],['Estático durante la ejecución','El cálculo es síncrono; la edición se bloquea durante la reproducción. Reiniciar abre una nueva ejecución.'],['Discreto','Hay 96 celdas posibles, estados de ocupación binarios y costos enteros por conexión.']],[145,323])
p('El tiempo de CPU puede variar entre ejecuciones sin alterar estas propiedades. La orientación de la pieza dibujada y los puntos son recursos visuales: no modifican las aristas. La atenuación de fichas inaccesibles proviene del resultado de búsqueda, no de una medición física.')
sub('3.4. Diagrama de componentes del caso a desarrollar')
img('componentes.png','Figura 2. Componentes reales y dependencias. Las flechas de dependencia señalan el componente utilizado.',468)
p('El modelo de mesa y la animación forman parte de ui.py; no existen módulos independientes para ellos. tests.py comprueba tanto las funciones de búsqueda como la reproducción y los datos de la tabla. README.md documenta el uso del proyecto.')
page();sub('3.5. Abstracción del Espacio de Estados')
p('Sea G = (V, E) un grafo no ponderado. Cada posición ocupada es un vértice: V = {(r, c) | M[r][c] = 1}, con 0 ≤ r < 8 y 0 ≤ c < 12. Existe una arista entre u y v cuando ambas posiciones están ocupadas y |u.r − v.r| + |u.c − v.c| = 1. Las aristas son simétricas y no incluyen diagonales.')
p('El estado inicial es s en V. Una acción selecciona un vecino válido; la transición cambia el nodo actual. La meta opcional es t en V. Para la simulación se busca el conjunto R de vértices alcanzables y la función de distancias d(s, v). El tiempo total de propagación es max{d(s, v) | v en R}; el nivel inicial vale cero.')
table([['Estructura','Contenido y función'],['frontier','Tuplas (nodo, padre, profundidad). deque en BFS; lista usada como pila en DFS.'],['visited','Conjunto de nodos procesados; evita explorar un nodo más de una vez.'],['queued','Conjunto de descubiertos. BFS impide insertar duplicados; DFS no aplica ese filtro.'],['levels / parents','Distancia BFS o profundidad DFS y predecesor del nodo procesado.'],['order / Result','Orden real de procesamiento y datos retornados a la interfaz.']],[135,333])
p('Ejemplo: una cruz de cinco fichas con inicio en el centro. El centro tiene nivel 0 y sus cuatro vecinos nivel 1. Los cuatro comienzan su animación en el mismo grupo. El número de niveles es 2, pero el tiempo final discreto es 1. Una ficha separada por un hueco no pertenece a R y permanece sin caer.')
p('El estado gráfico se conserva por separado en states. Cada ficha tiene un progreso de 0 a 1; la rotación representa hasta 90 grados. En BFS, groups reúne posiciones con igual distancia. En DFS, cada grupo contiene un único nodo y expresa exploración, no propagación mínima.')
page();h('4. ALGORITMO DE BÚSQUEDA UTILIZADO');sub('4.1. Descripción de la Estrategia Seleccionada')
p('BFS inicia la cola con (s, None, 0). Extrae por la izquierda, omite nodos visitados y registra padre, distancia y orden. Después examina vecinos en orden arriba, abajo, izquierda y derecha. Los vecinos válidos no descubiertos se insertan al final con profundidad incrementada. collections.deque ofrece append() y popleft() para estas operaciones (Python Software Foundation, s. f.-a).')
add('code','Validar matriz e inicio\nCola ← [(inicio, sin padre, 0)]; descubiertos ← {inicio}\nMientras la cola no esté vacía:\n    Extraer (nodo, padre, nivel) por la izquierda\n    Si ya fue visitado: continuar\n    Registrar visitado, padre, nivel y orden\n    Si se compara y nodo es meta: terminar\n    Para cada vecino ortogonal válido no descubierto:\n        Marcar descubierto\n        Insertar (vecino, nodo, nivel + 1) al final')
p('El pseudocódigo resume la rama BFS real. En DFS, frontier es una lista y se extrae con pop(). Los vecinos se insertan en orden inverso para priorizar la misma secuencia direccional. El padre se fija al procesar el nodo; las entradas duplicadas pendientes se descartan al extraerse si el nodo ya fue visitado. Por ello se conserva una exploración en profundidad sin bucles infinitos.')
p('compare() ejecuta ambos métodos sobre la misma matriz y activa stop_at_target. Ambos terminan cuando extraen y procesan la meta, incluida en el conteo; si no hay meta o no es alcanzable, agotan la frontera. reconstruct_path() sigue los predecesores desde la meta y revierte la lista; devuelve una lista vacía si no hay ruta.')
p('El costo temporal del recorrido es O(V + E). BFS utiliza memoria O(V); esta implementación DFS puede mantener entradas repetidas en la pila, por lo que su cota general es O(V + E). Como cada ficha tiene a lo sumo cuatro vecinos, E = O(V) en esta mesa y ambas usan espacio lineal. La animación y el dibujo se analizan aparte del cálculo.')
page();sub('4.2. Formulación de Costos')
p('Se define g(inicio) = 0 y g(n) = g(padre) + 1. Cada arista vale una unidad de tiempo discreto. No se utiliza h(n), porque BFS es una estrategia no informada. El control de velocidad modifica la reproducción en milisegundos por grupo, pero no cambia g(n), las distancias ni las rutas.')
p('La cola procesa los niveles en orden no decreciente. Cuando BFS descubre por primera vez un vecino, todos los caminos con menos conexiones ya tuvieron oportunidad de alcanzarlo. Con costos unitarios, esa primera distancia es mínima. DFS no mantiene este orden por capas, de modo que la ruta que encuentra puede ser más larga.')
h('5. CÓDIGO FUENTE');sub('5.1. Implementación de Clases y Funciones')
p('Los siguientes fragmentos se extraen directamente de los archivos del proyecto. Result es el contenedor de resultados y DominoApp es la clase de interfaz. La ocupación de la mesa se inicializa mediante una lista de ocho filas independientes:')
code('ui.py',18,18)
p('La selección de estructura, la extracción FIFO/LIFO y el registro de visitados se concentran en search():')
code('algorithms.py',28,39)
p('La parada por meta ocurre después de registrar el nodo. Esta ubicación explica por qué el conteo incluye a la propia meta. La validación previa rechaza matrices vacías o irregulares e inicios o metas sobre celdas sin ficha.')
page();sub('5.1. Implementación de Clases y Funciones (continuación)')
p('La inserción incrementa el costo en una unidad y controla el descubrimiento de BFS. La duración registrada excluye validación inicial y animación:')
code('algorithms.py',42,51)
p('La reconstrucción sigue únicamente predecesores obtenidos en la búsqueda:')
code('algorithms.py',62,69)
p('La comparación reutiliza search(); no contiene métricas predeterminadas:')
code('algorithms.py',72,74)
p('La interfaz agrupa por distancia antes de reproducir. En tick(), todas las posiciones del grupo reciben el mismo avance en un solo callback y luego se dibujan:')
code('ui.py',258,259)
code('ui.py',263,266)

page();h('6. CAPTURA DE PANTALLA DE EJECUCIÓN');sub('6.1. Evidencia del Sistema en Funcionamiento')
p('Las capturas corresponden a la aplicación ejecutada en Windows. La configuración de bifurcación contiene 15 fichas; el inicio está en la rama izquierda y la meta en el extremo superior.')
img('bifurcacion.png','Figura 3. Interfaz principal con el escenario Bifurcación cargado.',468)
p('Las herramientas del panel lateral permiten editar, elegir el algoritmo y controlar la reproducción. Las tarjetas inferiores separan el cálculo de la situación de las fichas durante la animación. Los bordes identifican inicio y meta.')
page();sub('6.1. Evidencia del Sistema en Funcionamiento (continuación)')
img('progreso.png','Figura 4. Simulación en curso: inicio ámbar y niveles calculados visibles.',468)
p('La ficha inicial aparece inclinada y ámbar. Las demás conservan su posición de pie y muestran el nivel que recibirán al propagarse la reacción. Las estadísticas de alcanzables y explorados ya están calculadas, aunque la reproducción todavía no termina.')
p('Los controles de pausa y revisión permiten detener la presentación sin recalcular las distancias. La simultaneidad por niveles se comprobó además en las pruebas fotograma a fotograma; una captura estática, por sí sola, no demuestra esa propiedad temporal.')
page();sub('6.1. Evidencia del Sistema en Funcionamiento (continuación)')
img('completada.png','Figura 5. Bifurcación completada: 15 alcanzables, 0 sin caer y tiempo final 9.',390)
p('El cálculo completo obtiene 10 niveles, del 0 al 9. La meta está a 6 conexiones. Estos valores no dependen de la velocidad de animación. ')
img('comparacion.png','Figura 6. Comparación real de la bifurcación con terminación en la meta.',420)
p('En esta captura BFS procesa 9 nodos y DFS 7; ambas rutas tienen 6 conexiones. No contradice las 15 fichas del recorrido completo: la comparación se detiene en la meta. Los tiempos que aparecen en pantalla son mediciones de esa ejecución particular.')
page();sub('6.2. Comparativa de Eficiencia entre Estrategias')
m=json.loads((EV/'mediciones.json').read_text()); results=m['results']
p('Se ejecutó compare() con el escenario Laberinto de dominós, sin modificar sus posiciones. El inicio interno es (3, 1) y la meta (3, 10), con índices desde cero. Se utilizó Python '+m['python']+' en Windows. Los siguientes datos proceden de una ejecución registrada en evidencias/mediciones.json, independiente de la captura de bifurcación.')
table([['Algoritmo','Nodos','Ruta','Cálculo (ms)','Ruta mínima']]+[[r['algorithm'],str(r['nodes']),str(r['route']),f"{r['ms']:.4f}",'Sí' if r['algorithm']=='BFS' else 'No garantiza'] for r in results],[85,60,60,110,153])
p('BFS obtuvo 9 conexiones frente a 19 de DFS: diez conexiones menos. DFS procesó 26 nodos frente a 31 de BFS: cinco nodos menos antes de llegar a la meta. Por tanto, procesar menos nodos en este ejemplo no produjo una ruta mejor. La elección depende de la propiedad buscada; para niveles de propagación mínima corresponde utilizar BFS.')
p('Los tiempos se obtienen con perf_counter() (Python Software Foundation, s. f.-b): son intervalos transcurridos dentro de search(), no tiempo exclusivo de CPU ni duración de la animación. Una muestra tan breve no constituye un estudio de rendimiento estadístico; cambia por carga del sistema, resolución del contador y calentamiento del intérprete. No se concluye que BFS siempre sea más rápido.')
p('La ejecución de unittest confirmó 16 pruebas aprobadas. La prueba exhaustiva evalúa las 511 ocupaciones no vacías de una matriz 3 × 3 y cada ficha como inicio: 2 304 búsquedas. Contrasta las distancias con relajación independiente de aristas. Esta cobertura prueba todos esos casos pequeños, sin sustituir una demostración general de corrección.')
p('Otra prueba inspecciona los doce fotogramas de cada nivel de la bifurcación: verifica idéntico progreso en todo el grupo, niveles anteriores completos y niveles posteriores sin iniciar. La prueba de la tabla envuelve compare() sin sustituir sus cálculos y verifica que los valores visibles coincidan con nodos, rutas y tiempos reales en dos escenarios.')
page();h('7. CONCLUSIONES');sub('7.1. Análisis y Cierre')
p('La implementación resuelve el caso de estudio de propagación sobre una mesa discreta. BFS permite conocer el componente alcanzable, las distancias mínimas y una ruta mínima hacia una meta opcional. La separación entre cálculo y animación facilita explicar que el nivel es una propiedad del grafo, mientras que la velocidad de reproducción es una decisión de presentación.')
p('Las verificaciones confirman una cola FIFO real, control de visitados y sincronización de las fichas del mismo nivel. La diferencia observada en el laberinto muestra que DFS puede llegar a la meta después de procesar menos nodos y, aun así, entregar un camino más largo. Esta comparación es válida porque ambas búsquedas usan la misma matriz y la misma condición de terminación.')
p('El agente basado en metas representa una abstracción didáctica: percibe entradas del editor y actúa sobre la visualización. No aprende, no controla objetos reales y no modela interacciones mecánicas. Los resultados son reproducibles en orden y distancias; las duraciones de cálculo pueden variar. La batería de pruebas y las evidencias respaldan el funcionamiento documentado, dentro de esas limitaciones.')
sub('7.2. Propuestas de Mejora')
p('Como trabajo futuro, podría incorporarse orientación direccional para que cada ficha solo transmita la caída hacia determinadas vecinas. Un modelo físico más preciso requeriría dimensiones, separación, fuerzas y colisiones, además de una validación distinta. Estas capacidades no forman parte de la versión actual.')
p('También se propone exportar escenarios y resultados, admitir mesas mayores y comparar con otras estrategias. Si se introducen costos diferentes por conexión, se deberá sustituir la garantía de BFS por un algoritmo apropiado para grafos ponderados. Las mediciones futuras deberían incluir repeticiones, escenarios de tamaños controlados y resúmenes estadísticos, manteniendo separadas búsqueda y animación.')
page();h('8.0. REFERENCIAS BIBLIOGRÁFICAS')
refs=[
'Python Software Foundation. (s. f.-a). collections — Container datatypes. En Python 3.13 documentation. https://docs.python.org/3.13/library/collections.html',
'Python Software Foundation. (s. f.-b). time — Time access and conversions. En Python 3.13 documentation. https://docs.python.org/3.13/library/time.html',
'Python Software Foundation. (s. f.-c). tkinter — Python interface to Tcl/Tk. En Python 3.13 documentation. https://docs.python.org/3.13/library/tkinter.html',
'Russell, S. J., & Norvig, P. (2021). Artificial intelligence: A modern approach (4.ª ed.). Pearson. https://aima.eecs.berkeley.edu/newchap00.pdf']
for ref in refs:add('ref',ref)
p('La referencia de Russell y Norvig corresponde a la cuarta edición estadounidense, cuya portada legal identifica Pearson y el año 2021. La documentación oficial de Python respalda las estructuras empleadas, la medición temporal y el uso de Tkinter como interfaz de Tcl/Tk (Python Software Foundation, s. f.-c).')
h('9.0. APÉNDICES / ANEXOS');sub('A. Estructura y ejecución')
table([['Archivo','Responsabilidad'],['main.py','Entrada: crea DominoApp y ejecuta mainloop().'],['algorithms.py','BFS, DFS, rutas, comparación y cinco escenarios.'],['ui.py','Matriz, editor, dibujo, reproducción y estadísticas.'],['tests.py','16 pruebas de algoritmos y comportamiento de interfaz.'],['README.md','Instalación, controles y fundamentos del proyecto.']],[135,333])
p('Requisitos: Python 3.11 o posterior con Tcl/Tk y sesión de escritorio en Windows. Abrir la carpeta Domino en VS Code, seleccionar el intérprete y ejecutar python main.py. Para comprobar Tkinter: python -m tkinter. Para las pruebas: python -m unittest tests -v. La aplicación no necesita paquetes externos, base de datos ni servidor.')
page();sub('B. Casos de prueba y evidencia de unittest')
table([['Grupo','Casos verificados','Resultado'],['SearchTests (7)','Cadena, bifurcación, aisladas, ciclos y niveles, desvío por obstáculo, comparación y rutas, inicio inválido.','7 aprobadas'],['PlaybackTests (3)','Pausa/reanudación y reinicio, pasos y cambio de algoritmo, fotogramas y finalización.','3 aprobadas'],['ScenarioTests (3)','Cinco escenarios y laberinto, meta ausente o inaccesible, meta igual al inicio.','3 aprobadas'],['DeliveryChecks (3)','Distancias exhaustivas, simultaneidad por fotograma, datos reales de tabla.','3 aprobadas']],[110,260,98])
p('La siguiente transcripción procede del archivo de salida conservado en evidencias/unittest.txt; es evidencia textual del comando ejecutado, no una captura reconstruida de una terminal:')
log=(EV/'unittest.txt').read_text(encoding='utf-8-sig');summary='\n'.join(log.strip().splitlines()[-4:]);add('code',summary)
p('El conjunto exhaustivo contiene 511 máscaras de ocupación y considera todos sus inicios ocupados. El total de casos internos es 9 × 2⁸ = 2 304. Los obstáculos, desconexiones y ciclos aparecen entre esas configuraciones. La prueba usa relajación de aristas como referencia independiente de la cola FIFO.')
sub('C. Trazabilidad y límites de la evidencia')
p('Las imágenes bifurcacion.png, progreso.png, completada.png y comparacion.png son capturas de ventanas reales. casos_uso.png y componentes.png son diagramas explicativos elaborados a partir del código. mediciones.json conserva el intérprete y la muestra del laberinto; unittest.txt conserva la salida de pruebas. Los scripts de documentación están separados de los módulos de la aplicación.')
p('Los archivos de la aplicación se conservaron sin modificaciones durante la elaboración del reporte. Las evidencias no incluyen un estudio físico ni una evaluación de rendimiento a gran escala. Los nombres del equipo deben completarse en la portada editable antes de la entrega académica.')
# Construcción simultánea: mismo contenido y saltos explícitos en ambos formatos.
DOC=Document(); sec=DOC.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=sec.bottom_margin=sec.left_margin=sec.right_margin=Cm(2.5)
for style in DOC.styles:
 if hasattr(style,'font'):
  style.font.name='Arial';style.font.color.rgb=RGBColor(0,0,0)
normal=DOC.styles['Normal'];normal.font.size=Pt(12);normal.paragraph_format.line_spacing=1.5;normal.paragraph_format.space_after=Pt(6);normal.paragraph_format.first_line_indent=Cm(.6);normal.paragraph_format.widow_control=True
for nm,size in [('Title',14),('Heading 1',14),('Heading 2',12)]:
 st=DOC.styles[nm];st.font.size=Pt(size);st.font.bold=True;st.paragraph_format.first_line_indent=Cm(0);st.paragraph_format.keep_with_next=True;st.paragraph_format.space_before=Pt(6);st.paragraph_format.space_after=Pt(6);st.paragraph_format.line_spacing=1.5
header=sec.header.paragraphs[0];header.text='Efecto Dominó | Inteligencia Artificial';header.alignment=WD_ALIGN_PARAGRAPH.RIGHT;header.paragraph_format.first_line_indent=Cm(0)
for run in header.runs:run.font.size=Pt(9)
f=sec.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.CENTER;f.paragraph_format.first_line_indent=Cm(0)
r=f.add_run();field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');r._r.addnext(field)
styles={}
for kind,size,lead,align,bold in [('p',12,18,TA_JUSTIFY,False),('h',14,19,TA_LEFT,True),('sub',12,18,TA_LEFT,True),('caption',10,13,TA_CENTER,False),('center',12,18,TA_CENTER,False),('cover',14,21,TA_CENTER,True),('ref',12,18,TA_LEFT,False),('cell',10,13,TA_LEFT,False)]:
 styles[kind]=ParagraphStyle(kind,fontName='Arial-Bold' if bold else 'Arial',fontSize=size,leading=lead,textColor=colors.black,alignment=align,spaceAfter=6,firstLineIndent=17 if kind=='p' else 0,spaceBefore=6 if kind in ('h','sub') else 0)
headings=[(text,i+1,kind) for i,blocks in enumerate(pages) for kind,text,kw in blocks if kind in ('h','sub') and text!='ÍNDICE GENERAL' and '(continuación)' not in text and not re.match('[ABC]\\.',text)]
flow=[]
for idx,blocks in enumerate(pages):
 if idx:flow.append(PageBreak())
 new_doc_page = idx > 0
 for kind,text,kw in blocks:
  if kind=='space':flow.append(Spacer(1,text));continue
  if kind=='toc':
   for title,num,k in headings:
    flow.append(Paragraph(escape(title)+f' <b>{num}</b>',ParagraphStyle('toc',parent=styles['cell'],fontSize=10.5,leading=15,spaceAfter=3,leftIndent=0 if k=='h' else 10)))
    pp=DOC.add_paragraph();pp.paragraph_format.first_line_indent=Cm(0);pp.paragraph_format.line_spacing=1;pp.paragraph_format.space_after=Pt(3);rr=pp.add_run(title+'  '+str(num));rr.font.size=Pt(10.5)
   continue
  if kind=='image':
   path=EV/text;im=Image.open(path);w=kw['width'];height=w*im.height/im.width
   flow.extend([RLImage(str(path),width=w,height=height),Paragraph(escape(kw['caption']),styles['caption'])])
   pp=DOC.add_paragraph();pp.paragraph_format.first_line_indent=Cm(0);pp.paragraph_format.line_spacing=1;pp.paragraph_format.keep_with_next=True;pp.alignment=WD_ALIGN_PARAGRAPH.CENTER;pp.add_run().add_picture(str(path),width=Pt(w))
   pp=DOC.add_paragraph(kw['caption']);pp.alignment=WD_ALIGN_PARAGRAPH.CENTER;pp.paragraph_format.first_line_indent=Cm(0);pp.paragraph_format.line_spacing=1
   for rr in pp.runs:rr.font.size=Pt(10)
   continue
  if kind=='table':
   rows=[[Paragraph(escape(v),styles['cell']) for v in row] for row in text]
   t=Table(rows,colWidths=kw['widths'],hAlign='CENTER');t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.5,colors.grey),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));flow.extend([t,Spacer(1,8)])
   tab=DOC.add_table(rows=0,cols=len(text[0]));tab.style='Table Grid';tab.autofit=False
   for i,width in enumerate(kw['widths']):tab.columns[i].width=Pt(width)
   for ri,row in enumerate(text):
    cells=tab.add_row().cells
    for ci,value in enumerate(row):
     cells[ci].width=Pt(kw['widths'][ci]);pp=cells[ci].paragraphs[0];pp.paragraph_format.first_line_indent=Cm(0);pp.paragraph_format.line_spacing=1.1;pp.paragraph_format.space_after=Pt(5);rr=pp.add_run(value);rr.font.size=Pt(10);rr.bold=(ri==0)
    trpr=tab.rows[-1]._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
   continue
  if kind=='code':
   # Líneas originales, con ajuste visual solo si exceden el ancho imprimible.
   flow.append(Preformatted(text,ParagraphStyle('code',fontName='Arial',fontSize=9,leading=11,spaceAfter=3),maxLineLength=110))
   pp=DOC.add_paragraph();pp.paragraph_format.first_line_indent=Cm(0);pp.paragraph_format.line_spacing=1;rr=pp.add_run(text);rr.font.size=Pt(9)
   continue
  flow.append(Paragraph(escape(text),styles[kind]))
  pp=DOC.add_paragraph(style='Title' if kind=='cover' else 'Heading 1' if kind=='h' else 'Heading 2' if kind=='sub' else 'Normal');rr=pp.add_run(text)
  if new_doc_page:
   pp.paragraph_format.page_break_before=True
   new_doc_page=False
  pp.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY if kind=='p' else WD_ALIGN_PARAGRAPH.CENTER if kind in ('center','cover','caption') else WD_ALIGN_PARAGRAPH.LEFT
  if kind!='p':pp.paragraph_format.first_line_indent=Cm(0)
  if kind=='caption':rr.font.size=Pt(10);pp.paragraph_format.line_spacing=1
DOC.core_properties.title='Efecto Dominó: Simulación de Estrategias de Búsqueda BFS y DFS';DOC.core_properties.author='Integrantes del equipo: [Nombres pendientes]'
DOC.save(OUT/'Reporte_Tecnico_Efecto_Domino.docx')
def footer(canvas,doc):
 canvas.setFillColor(colors.black);canvas.setFont('Arial',9);canvas.drawCentredString(306,40,str(doc.page))
 if doc.page>1:canvas.drawRightString(541,755,'Efecto Dominó | Inteligencia Artificial')
pdf=SimpleDocTemplate(str(OUT/'Reporte_Tecnico_Efecto_Domino.pdf'),pagesize=(612,792),leftMargin=70.866,rightMargin=70.866,topMargin=70.866,bottomMargin=70.866,title=DOC.core_properties.title,author='Integrantes pendientes')
pdf.build(flow,onFirstPage=footer,onLaterPages=footer)
(OUT/'trabajo'/'indice_esperado.json').write_text(json.dumps(headings,ensure_ascii=False,indent=2),encoding='utf-8')
(EV/'integridad.json').write_text(json.dumps({f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['main.py','algorithms.py','ui.py','tests.py','README.md']},indent=2),encoding='utf-8')
print('Generados',len(pages),'bloques de página')
