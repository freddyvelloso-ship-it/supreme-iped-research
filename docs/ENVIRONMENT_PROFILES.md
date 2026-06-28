# SUPREME V4 - Environment profiles

Fase 0 separates four execution profiles:

| Profile | Purpose | Data policy |
|---|---|---|
| local | Developer workstation | No real case data |
| demo | Sales/demo | Synthetic data only |
| homologation | Client validation | Synthetic or authorized pseudonymized data |
| production | Real operation | Contracted real data with LGPD and security controls |

Profile files live in `env/` and are examples only. The production stack still
uses `.env.production.example`, `supreme-backend/.env.production.example` and
`sentinela/.env.production.example` as the complete variable references.

Do not ship `.env`, `.env.production`, certificates, local tokens, local
databases, audit logs or real IPED evidence files in any release package.
