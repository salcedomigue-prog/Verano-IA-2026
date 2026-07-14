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