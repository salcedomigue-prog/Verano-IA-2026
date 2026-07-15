# Notas · Semana 2

## Lunes 13 · Qué es un agente

- Un agente es un programa que usa un LLM como "cerebro" para razonar,
  decidir y actuar por sí solo hasta cumplir un objetivo.
- La diferencia con un chatbot: el chatbot solo responde; el agente
  planifica pasos y usa herramientas (buscar, calcular, leer archivos).
- El LLM no "hace" nada por sí mismo: solo genera texto. Es el código del
  agente el que lee ese texto y ejecuta las acciones.
- Una conversación es una lista de mensajes con roles: system (instrucciones
  de comportamiento), user (lo que pido) y assistant (lo que responde).
- Lo comprobé en hola_llm.py: añadí un system prompt ("eres un pirata") y
  cambió toda la personalidad sin tocar la pregunta.
- Idea para el proyecto de agosto: el system prompt será donde le diga al
  asistente docente que actúa como profesor de secundaria en España (LOMLOE).

## Martes 14 · El bucle Pensar → Actuar → Observar

Objetivo del agente: preparar un examen de recuperación de Programación
para 4º de ESO sobre bucles y condicionales.

### Vuelta 1
- PENSAR: "Necesito saber qué contenidos entran. Debo consultar la
  programación didáctica antes de redactar nada."
- ACTUAR: usa la herramienta leer_documento("programacion_4ESO.pdf")
- OBSERVAR: "El documento dice: bucles for/while, condicionales, listas.
  Ya sé qué debe cubrir el examen."

### Vuelta 2
- PENSAR: "Con los contenidos claros, redacto 5 preguntas de dificultad
  creciente y una rúbrica."
- ACTUAR: usa la herramienta generar_texto(instrucciones)
- OBSERVAR: "Tengo el borrador. ¿Cumple todo? Falta la rúbrica → otra vuelta."

### Vuelta 3
- PENSAR: "Falta la rúbrica. La genero y ya puedo terminar."
- ACTUAR: genera la rúbrica → respuesta final al usuario.

Clave: el agente NO lo hace todo de golpe. Da vueltas al bucle y en cada
una decide el siguiente paso según lo que OBSERVÓ en la anterior.
Es exactamente lo que haré en agosto con mi asistente docente.