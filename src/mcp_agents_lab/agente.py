import sys

import ollama

MODELO = "qwen3:4b"


def main() -> None:

    if len(sys.argv) < 2:
        print('uso: agente "sua pergunta"', file=sys.stderr)
        raise SystemExit(1)

    question = " ".join(sys.argv[1:])
    messages = [
        {
            "role": "system",
            "content": "Você é um assistente útil e objetivo.",
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    response = ollama.chat(
        model=MODELO,
        messages=messages,
    )

    if response.message.thinking:
        print("=== THINKING ===")
        print(response.message.thinking)

    print("\n=== CONTENT ===")
    print(response.message.content)


if __name__ == "__main__":
    main()
