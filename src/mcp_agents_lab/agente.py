import sys

import ollama

from pathlib import Path


MODELO = "qwen3:4b"


def listar_arquivos(pasta: str ) -> str:
    """Lista os arquivos de uma pasta.
    
    Args:
        pasta (str): Caminho da pasta a ser listada.
    """
    p = Path(pasta)

    arquivos = [
        arquivo.name
        for arquivo in p.iterdir()
        if arquivo.is_file()
    ]

    return str(arquivos)



TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "listar_arquivos",
            "description": "Lista os arquivos de uma pasta.",
            "parameters": {
                "type": "object",
                "required": ["pasta"],
                "properties": {
                    "pasta": { "type": "string",
                    "description": "caminho da pasta a listar"}
                }
            }
        }
    }
]


FERRAMENTAS = {
    "listar_arquivos": listar_arquivos,
}

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
        tools=TOOLS_SCHEMA,
    )

    if response.message.thinking:
        print("=== THINKING ===")
        print(response.message.thinking)

    print(response.message.tool_calls)
    tc = response.message.tool_calls[0]

    resultado = FERRAMENTAS[tc.function.name](**tc.function.arguments)

    messages.append(response.message)

    messages.append({"role": "tool", "tool_name": tc.function.name, "content": resultado})

    resposta_final = ollama.chat(
        model=MODELO,
        messages=messages,
        tools=TOOLS_SCHEMA,
    )

    print("\n=== CONTENT ===")
    print(resposta_final.message.content)


if __name__ == "__main__":
    main()
