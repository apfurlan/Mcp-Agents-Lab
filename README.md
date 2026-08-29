# **MCP Agents Laboratory**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-0.12-DE5FE9?logo=uv&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-0.33-000000?logo=ollama&logoColor=white)
![Qwen3](https://img.shields.io/badge/modelo-Qwen3--4B-615CED)
![FastMCP](https://img.shields.io/badge/FastMCP-3.4-009485)
![MCP](https://img.shields.io/badge/MCP_SDK-1.29-FF6B35)
![pytest](https://img.shields.io/badge/pytest-9.1-0A9EDC?logo=pytest&logoColor=white)
![local](https://img.shields.io/badge/execução-100%25_local-2EA043)

> Laboratório para aprender, do zero, como funcionam **agentes** e o **Model Context
> Protocol** em Python — escrevendo o loop à mão, sem framework, com modelo aberto
> rodando na própria máquina.

---

## O que queremos fazer

Construir um assistente de trabalho técnico composto por **um agente CLI** e
**três servidores MCP próprios**, cada um em seu processo:

| servidor | o que faz | transporte | efeito |
|---|---|---|---|
| `mcp-notas` | anotações em SQLite — tools, resources e prompt | stdio | **escreve** |
| `mcp-repo` | `git status` / `log` / `diff` | streamable-http | lê |
| `mcp-web` | busca e extrai texto de páginas | — | lê |

A assimetria é proposital: só um servidor muda o estado do mundo, e é o único que
precisa de porteiro. Reconhecer isso cedo é metade do aprendizado.

### Princípios do laboratório

- **Sem framework de agente.** O loop é escrito à mão. Um agente é ~40 linhas; todo
  framework é embalagem em volta disso, e a embalagem esconde exatamente o que
  queremos ver.
- **100% local, 100% open source.** Modelo aberto via Ollama, sem API paga, sem
  chave, sem custo por token.
- **O MCP é o assunto, não o acessório.** O protocolo é independente de framework —
  este repo existe para provar isso na prática.
- **Aprender pela costura.** Cada etapa abre uma junta no código; a junta aberta
  para testar é a mesma onde o MCP encaixa depois.

---

## Onde estamos

**Etapa 1 — o loop do agente, ainda sem MCP.** Em andamento.

| | etapa | estado |
|---|---|---|
| 0 | ambiente: `uv`, Python 3.12, Ollama, `qwen3:4b` na GPU | ✅ |
| 1.1 | agente fala com o modelo local | ✅ |
| 1.2 | ferramenta local + schema escrito à mão | ✅ |
| 1.3 | ver o modelo *pedir* a ferramenta (`tool_calls`) | ✅ |
| 1.4 | ciclo pedido → execução → resposta, desenrolado | ✅ |
| 1.5 | laço com `MAX_ITERACOES` e erro virando mensagem | ✅ |
| 1.6 | segunda ferramenta (`escrever_nota`) + flag `--debug` | ⬜ |

O que já funciona, em [`src/mcp_agents_lab/agente.py`](src/mcp_agents_lab/agente.py):

- uma ferramenta local (`listar_arquivos`) declarada em dois lugares ligados pelo
  nome — o **schema** que vai para o modelo e o **dict** que despacha a chamada
- o laço completo: chama o modelo, acumula mensagens, executa todas as ferramentas
  pedidas, devolve os resultados com papel `tool`, repete até ele parar de pedir
- ferramenta desconhecida e exceção viram **texto de erro devolvido ao modelo**, que
  lê e se corrige — em vez de traceback

```console
$ uv run agente quais arquivos tem nesta pasta
Nesta pasta existem os seguintes arquivos:
- README.md
- pyproject.toml
- uv.lock
...

$ uv run agente liste os arquivos de /nao/existe
A pasta '/nao/existe' não existe. Verifique o caminho.
```

O segundo caso é o interessante: a exceção do `Path.iterdir()` foi capturada,
devolvida ao modelo como mensagem `tool`, e ele transformou o erro em explicação.

---

## O que falta fazer

- [ ] **1.6** — `escrever_nota(texto)` e a flag `--debug` que imprime `messages` em
      JSON a cada volta (é onde se vê a lista crescer de 2 para 6+ mensagens)
- [ ] **1.7** — extrair o laço de `main()` para `rodar_agente(..., chat=ollama.chat)`;
      com a chamada ao modelo injetada, dá para testar com um dublê determinístico,
      sem GPU. Testes: ferramentas com `tmp_path`, laço com dublê
- [ ] **Etapa 2** — primeiro servidor FastMCP (`mcp-notas`, SQLite) com testes
      in-memory, cobrindo *tools*, *resources* e *prompts*
- [ ] **Etapa 3** — ligar agente ↔ MCP: o schema deixa de ser escrito à mão e passa
      a chegar pela rede; o laço **não muda uma linha**
- [ ] **Etapa 4** — segundo servidor (`mcp-repo`) em outro transporte
      (streamable-http), para sentir a diferença entre stdio e HTTP
- [ ] **Etapa 5** — freios: *elicitation* (pedir confirmação antes de escrever) e
      saída estruturada
- [ ] **Etapa 6** — multi-agente **e medir se valeu a pena** (avaliação, `evals/`)
- [ ] **Etapa 7** — publicar os servidores como executáveis (`uvx mcp-notas`) e
      plugá-los no Claude Code
- [ ] escolher e adicionar uma `LICENSE`

---

## Stack

| camada | escolha | por quê |
|---|---|---|
| modelo | `qwen3:4b` (Apache-2.0) via Ollama | cabe em 6 GB de VRAM com folga e suporta *tool calling* |
| loop do agente | escrito à mão | é o que se quer aprender |
| servidores MCP | `fastmcp` 3.x (Apache-2.0) | o SDK de alto nível do protocolo |
| cliente MCP | `fastmcp.Client` | mesma lib, do outro lado do fio |
| ambiente | `uv` + Python 3.12 | 3.14 ainda não tem wheel para parte do ecossistema |
| testes | `pytest` | ferramentas puras + laço com modelo dublê |

## Rodando

Requisitos: [`uv`](https://docs.astral.sh/uv/) e [Ollama](https://ollama.com).

```bash
uv sync
ollama pull qwen3:4b
uv run agente quais arquivos tem nesta pasta
```

Para confirmar que o modelo está na GPU e não na CPU:

```bash
ollama ps        # a coluna PROCESSOR deve dizer 100% GPU
```
