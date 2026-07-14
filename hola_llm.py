import anthropic

client = anthropic.Anthropic()  # lee ANTHROPIC_API_KEY del entorno

respuesta = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=300,
    system="Eres un pirata del siglo XVIII y respondes siempre como tal.",
    messages=[{
        "role": "user",
        "content": "Explica en 3 frases qué es un agente de IA "
                   "a un profesor de secundaria.",
    }],
)
print(respuesta.content[0].text)
