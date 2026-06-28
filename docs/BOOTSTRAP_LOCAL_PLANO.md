# Plano de Bootstrap Local - SUPREME V4

## Objetivo

Automatizar o setup local do stack SUPREME/SENTINELA/IPED para reduzir falhas manuais de ambiente, secrets, certificados e portas ocupadas.

## Problemas observados na validação local

1. O stack depende de `.env` raiz, mas o arquivo não é gerado automaticamente.
2. O stack depende de `sentinela/.env.production`.
3. O stack depende de `supreme-backend/.env.production`.
4. O NGINX depende de `certs/fullchain.pem` e `certs/privkey.pem`.
5. Containers antigos podem ocupar as portas 80, 443 e 8081.
6. Prometheus recebe 403 ao consultar `/metrics`.
7. Certificados e secrets locais não devem ser versionados.

## Entregáveis planejados

1. `scripts/setup_env_local.ps1`
2. `scripts/gerar_cert_local.ps1`
3. Atualização de `.env.production.example`
4. Atualização de `sentinela/.env.production.example`
5. Atualização de `supreme-backend/.env.production.example`
6. Validação de `.gitignore`
7. Documentação de teste local
8. Registro da pendência Prometheus `/metrics`

## Restrições

1. Não alterar cálculo IEO.
2. Não alterar PSI.
3. Não alterar autenticação.
4. Não alterar modelos de banco.
5. Não alterar fluxo IPED.
6. Não commitar secrets reais.
7. Não commitar certificados privados.

## Status

Branch planejada para implementação: `chore/local-bootstrap-hardening`.
