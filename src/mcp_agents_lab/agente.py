import sys

import ollama

from pathlib import Path


MODELO = "qwen3:4b"
MAX_ITERACOES = 5


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

    for _ in range(MAX_ITERACOES):
        response = ollama.chat(
            model=MODELO,
            messages=messages,
            tools=TOOLS_SCHEMA,
        )
        messages.append(response.message)

        if not response.message.tool_calls:
            print(response.message.content)
            break

        for tc in response.message.tool_calls:
            funcao = FERRAMENTAS.get(tc.function.name)
            if funcao is None:
                resultado = f"ferramenta desconhecida: {tc.function.name}"
            else:
                try:
                    resultado = funcao(**tc.function.arguments)
                except Exception as erro:
                    resultado = f"erro em {tc.function.name}: {erro}"

            messages.append({
                "role": "tool",
                "tool_name": tc.function.name,
                "content": str(resultado),
            })
    else:
        print("limite de iterações atingido")


if __name__ == "__main__":
    main()
