# Projeto de Estudos da Faculdadade

Projeto da faculdade explorando as Azure Functions desenvolvidas em **Python**.

## Integrantes da equipe

| Nome |
| --- |
| João Gabriel |
| Thiogo Antônio |
| Luiz Chaves |
| Arthur Luckman |
| Gabriel Fagundes |

## Functions

Todas as functions estão em [`function_app.py`](function_app.py). Cada uma é um Timer trigger que roda a cada 5 minutos (`0 */5 * * * *`), extrai uma tabela do schema `itsm` e registra os registros no log.

| Function | Gatilho | Tabela |
| --- | --- | --- |
| `extract_analista` | Timer (`0 */5 * * * *`) | `itsm.analista` |
| `extract_categoria` | Timer (`0 */5 * * * *`) | `itsm.categoria` |
| `extract_chamado` | Timer (`0 */5 * * * *`) | `itsm.chamado` |
| `extract_chamado_sla` | Timer (`0 */5 * * * *`) | `itsm.chamado_sla` |
| `extract_chamado_status_historico` | Timer (`0 */5 * * * *`) | `itsm.chamado_status_historico` |
| `extract_cliente_organizacao` | Timer (`0 */5 * * * *`) | `itsm.cliente_organizacao` |
| `extract_csat_avaliacao` | Timer (`0 */5 * * * *`) | `itsm.csat_avaliacao` |
| `extract_fila` | Timer (`0 */5 * * * *`) | `itsm.fila` |
| `extract_sla` | Timer (`0 */5 * * * *`) | `itsm.sla` |
| `extract_solicitante` | Timer (`0 */5 * * * *`) | `itsm.solicitante` |

## Variáveis de ambiente

As credenciais do banco **não** ficam no código. Elas são lidas das variáveis de ambiente abaixo:

| Variável | Descrição |
| --- | --- |
| `DB_HOST` | Servidor SQL (ex.: `<servidor>.database.windows.net`) |
| `DB_NAME` | Nome do banco |
| `DB_USER` | Usuário |
| `DB_PASSWORD` | Senha |

- **Local:** copie `local.settings.json.example` para `local.settings.json` (que está no `.gitignore`) e preencha os valores.
- **Azure:** configure em *Function App → Settings → Environment variables (App settings)*.

## Diagrama

<img width="804" height="551" alt="image" src="https://github.com/user-attachments/assets/af7a483a-02de-443d-98a0-469d4fd392d4" />
