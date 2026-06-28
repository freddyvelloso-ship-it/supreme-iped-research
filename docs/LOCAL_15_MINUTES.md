# SUPREME V4 - Local em 15 minutos

Este roteiro sobe SUPREME, SENTINELA, Postgres, Redis, NGINX e observabilidade local com dados controlados.

## Pre-requisitos

- Windows PowerShell
- Docker Desktop rodando
- Python 3 no PATH, `py -3`, ou variavel `PYTHON_EXE`
- Portas livres: `80`, `443`, `18000`, `18001`, `15433`, `15434`, `16379`, `8181`, `9190`, `9193`, `3300`, `3111`

## Caminho recomendado

No diretorio raiz do projeto:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\local.ps1 -Action all -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
```

Se `python` ou `py -3` estiver no PATH, o parametro `-PythonExe` pode ser omitido.

O comando faz, em ordem:

1. Gera secrets locais em `.env`, `supreme-backend\.env.production` e `sentinela\.env.production`.
2. Gera certificado TLS local para o NGINX se ele ainda nao existir.
3. Valida `docker-compose.production.yml + docker-compose.local.yml`.
4. Reseta volumes locais.
5. Sobe todos os containers.
6. Valida healthchecks de SUPREME, SENTINELA, Redis, Postgres e NGINX.
7. Aplica seed limpo.
8. Executa E2E: evento IPED simulado -> SUPREME -> Redis/RQ -> Postgres -> SENTINELA.

## Comandos por etapa

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\local.ps1 -Action setup
powershell -ExecutionPolicy Bypass -File .\scripts\local.ps1 -Action up
powershell -ExecutionPolicy Bypass -File .\scripts\local.ps1 -Action health -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
powershell -ExecutionPolicy Bypass -File .\scripts\local.ps1 -Action test -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
```

Para resetar do zero:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\local.ps1 -Action reset
```

Para inserir dados visuais de demonstracao:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\local.ps1 -Action seed-demo
```

Para remover dados demo/e2e:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\local.ps1 -Action seed-clean
```

## Acessos locais

- SENTINELA: `https://localhost/sentinela/`
- SENTINELA direto: `http://localhost:18001/`
- SUPREME API: `http://localhost:18000/docs`
- SUPREME via NGINX: `https://localhost/health`
- Prometheus: `http://localhost:9190/`
- Alertmanager: `http://localhost:9193/`
- Grafana: `https://localhost/grafana/` ou `http://localhost:3300/`
- Loki: `http://localhost:3111/ready`
- IPED proxy local: `http://localhost:8181/`

Login local SENTINELA:

- Email: `local.master@supreme.local`
- Senha: `supreme-local-admin`

## Criterio de aceite da Fase 1

A Fase 1 passa quando:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\local.ps1 -Action all
```

termina com JSON `status: ok` do E2E e sem erro nos healthchecks.

Em ambientes onde o Docker Desktop bloqueia `docker exec` para processos sem
permissao, execute o PowerShell com permissao adequada para acessar o Docker.

## Observacoes

- Os arquivos `.env` e certificados locais sao ignorados no release.
- O E2E cria dados com prefixo `phase1-e2e`.
- O seed demo cria dados com prefixo `phase1-demo`.
- `seed-clean` remove apenas dados com prefixo `phase1-`.
