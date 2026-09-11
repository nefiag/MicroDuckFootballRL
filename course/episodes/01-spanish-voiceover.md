# Episodio 1: Enseñar al pato a jugar al fútbol

> Idioma: español  
> Duración: 10:00  
> Estilo: educativo, cercano, divertido y con intriga

---

## 00:00–00:30｜¿Puede este pato aprender a jugar?

Imagina que ponemos un pequeño pato robot en un campo de fútbol, le damos un balón y no le explicamos absolutamente nada. ¿Qué ocurrirá? ¿Aprenderá a marcar por sí solo? Es posible. Pero antes seguramente veremos un festival de torpeza artificial: correrá de espaldas al balón, dará vueltas a su alrededor o adoptará una pose de campeón para fallar el golpe por completo. No te vayas. Al final verás cómo ese mismo principiante consigue llevar el balón hasta la portería.

## 00:30–01:20｜Comienza el proyecto

Hola a todos. Bienvenidos al curso de fútbol con aprendizaje por refuerzo de MicroDuck. Vamos a construir un proyecto completo de inteligencia artificial: crearemos un campo virtual, enseñaremos al pato a localizar el balón, acercarse y disparar. Después haremos que la simulación sea deliberadamente imperfecta y trasladaremos la estrategia al robot real. Seremos entrenadores, preparadores físicos, tácticos y también agentes de un fichaje desde el mundo virtual hasta el mundo real. Usaremos Gymnasium para crear el entorno, PPO de Stable-Baselines3 para aprender la estrategia y aleatorización de dominio para reducir la distancia entre simulación y realidad. Hoy no necesitamos fórmulas. Solo responderemos qué es el aprendizaje por refuerzo y cómo planeamos convertir este pato en futbolista.

## 01:20–02:20｜Por qué no escribir reglas manuales

La primera idea es programar reglas. Si el balón está a la izquierda, gira a la izquierda; si está a la derecha, gira a la derecha; si está delante, avanza; y si está junto al pie, golpea. Parece resuelto, ¿verdad? La realidad protesta enseguida. ¿Qué pasa si el balón está detrás, si el robot llega con un ángulo distinto, si el césped frena pero el suelo de madera resbala, o si la cámara muestra dónde estaba el balón hace una décima de segundo? Añadimos condiciones, parámetros y parches. El código crece, mientras el robot necesita veinte requisitos antes de mover una pierna. Las reglas sirven, pero en un partido que cambia continuamente queremos que aprenda de la experiencia, no encerrar todas las situaciones posibles dentro de una montaña de instrucciones «si».

## 02:20–03:20｜Qué es el aprendizaje por refuerzo

Aquí entra el aprendizaje por refuerzo. Puedes imaginarlo como entrenar a una mascota: premiamos lo correcto, penalizamos un poco los errores y, después de muchos intentos, elegirá con mayor frecuencia las acciones que producen una buena recompensa a largo plazo. Pero no consiste en probar cosas sin rumbo. Debemos definir qué información puede observar, qué acciones puede realizar, qué resultados son buenos y cuándo termina cada episodio. Si esas definiciones son malas, un millón de intentos solo harán que se equivoque con más experiencia. Cuando la inteligencia artificial aprende algo extraño, no la culpes demasiado rápido. Muchas veces ha leído nuestra puntuación con enorme atención y ha encontrado un atajo. No se está rebelando; simplemente comprendió las reglas mejor que nosotros.

## 03:20–05:20｜Cinco conceptos dentro del campo

Hay cinco conceptos esenciales. El primero es el agente: quien toma decisiones. Aquí es MicroDuck. El balón no decide hacia dónde rodar y la portería todavía no puede escapar. En un partido entre dos patos habrá varios agentes.

El segundo es el entorno: el campo, el balón, la portería, los límites, las colisiones y la fricción. Cada vez que el agente actúa, el entorno avanza un paso.

El tercero es la observación. ¿Está el balón a la izquierda o a la derecha? ¿A qué distancia? ¿Dónde está la portería y hacia dónde mira el robot? La estrategia no comprende mágicamente una fotografía: recibe números que forman un vector de estado.

El cuarto concepto es la acción. Nuestra primera versión solo ofrece cuatro: avanzar, girar a la izquierda, girar a la derecha y chutar. No controlamos todavía cada articulación y cada motor, porque unas acciones sencillas permiten entender por qué funciona la estrategia y descubrir dónde falla.

El quinto concepto, y el que más trampas permite, es la recompensa. Acercarse al balón suma un poco; tocarlo por primera vez suma más; moverlo hacia la portería vuelve a sumar; y marcar recibe la recompensa máxima. Alejarse o tardar demasiado puede restar puntos. Si diseñamos mal esta función, el pato encontrará una solución inesperada. Quizá descubra que tocar el balón da puntos y se quede rozándolo sin disparar. Felicidades: hemos entrenado a un artista del malabarismo, pero olvidamos decirle que esto era un partido.

## 05:20–06:30｜El ciclo de aprendizaje en código

Mira ahora el código junto a la animación. Primero, `env.reset()` reinicia el campo y devuelve la primera observación. La estrategia lee `observation` y elige una `action`: avanzar, girar o chutar. Después llamamos a `env.step(action)`. El entorno ejecuta la orden, actualiza las posiciones y devuelve una nueva observación, la recompensa, `terminated`, `truncated` e información adicional. `terminated` indica un final natural, como un gol o un balón fuera del campo. `truncated` indica que se alcanzó un límite, por ejemplo cuatrocientos pasos sin completar la misión. PPO reúne los datos y actualiza las redes de política y de valor. La nueva política vuelve al entorno. El ciclo completo es: observar, actuar, recibir recompensa, aprender y observar otra vez.

## 06:30–07:30｜Por qué marcar directamente es tan difícil

Si el objetivo es marcar, ¿por qué no dar cien puntos únicamente cuando hay gol? En teoría funciona. En la práctica, la puntuación puede quedarse siempre en cero. El pato está a un lado, el balón en el centro y la portería al otro extremo. Una política aleatoria tendría que girar correctamente, llegar al balón, ajustar el ángulo y chutar justo a tiempo. Un solo error elimina cualquier señal. Esto se llama recompensa escasa. Es como un profesor que solo dice si lograste la nota máxima del examen, pero nunca corrige tus ejercicios. Por eso añadimos señales intermedias moderadas: disminuir la distancia, tocar el balón por primera vez y moverlo hacia la portería. Moderadas es la palabra importante, porque demasiados premios también pueden hacer olvidar la meta final.

## 07:30–08:30｜Seis niveles como en un videojuego

Dividiremos el proyecto en seis niveles. Primero, aprender a moverse sin confundir girar con avanzar. Segundo, encontrar el balón. Tercero, acercarse y detenerse a la distancia correcta. Cuarto, tocar y conducir el balón. Quinto, utilizar la dirección de la portería para disparar. Sexto, Sim2Real: transferir la estrategia al MicroDuck físico. Este avance desde tareas fáciles hasta difíciles se llama aprendizaje curricular. Un buen videojuego no coloca al jefe final en la aldea inicial. Algunos juegos sí lo hacen, claro, pero eso no es un tutorial: es una manera elegante de pedirte que desinstales el juego.

## 08:30–09:20｜La ruta técnica completa

La ruta técnica sigue esos niveles. Primero definiremos en Gymnasium los espacios de estados y acciones, `reset` y `step`. Después entrenaremos PPO con Stable-Baselines3. Registraremos la curva de recompensa, pero también mediremos la tasa real de goles en un entorno fijo. Luego activaremos la aleatorización de dominio. En cada reinicio cambiarán al azar la fricción, la masa, la potencia del motor, el retraso y el ruido de observación. ¿Por qué desordenar el mundo virtual? Porque si el robot juega bien en diez mil mundos ligeramente diferentes, el mundo real deja de ser un examen desconocido y se convierte en otra variación que ya conoce. Finalmente exportaremos el modelo, aplicaremos límites físicos y comenzaremos las pruebas reales despacio y con soporte de seguridad.

## 09:20–10:00｜Pregunta final y próximo episodio

Quédate con una idea: el aprendizaje por refuerzo no es probar a ciegas, sino aprender sistemáticamente una estrategia mediante estados, acciones y recompensas. Una última pregunta. Supón que MicroDuck aprende a girar sin parar y su recompensa sigue aumentando. ¿El robot es perezoso o nuestra función de recompensa tiene un agujero? ¿Qué modificarías? Escribe tu respuesta en los comentarios. En el próximo episodio abriremos el código y construiremos el campo en Gymnasium, con MicroDuck, el balón, la portería y cuatro acciones. Esperemos que al terminar nuestro pato sepa distinguir la portería de la salida del estadio. Nos vemos.

---

## Notas de grabación

- Leer el inicio con algo más de energía.
- Reducir la velocidad en los cinco conceptos principales.
- Dejar una pausa corta después de cada broma.
- Bajar la voz antes de la pregunta final.
