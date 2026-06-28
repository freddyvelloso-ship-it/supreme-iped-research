# Perfil Longitudinal do Perito

O Perfil Longitudinal do Perito e uma classificacao operacional calculada pelo
backend SUPREME a partir de outputs ja auditaveis: baseline congelada, IEO, PSI,
red flags, cronicidade, dissonancia, reatividade, qualidade de dado e historico
longitudinal.

Ele nao e diagnostico clinico, avaliacao psicologica, nexo causal automatico ou
decisao autonoma. O SENTINELA apenas visualiza o output recebido do SUPREME.

## Classes controladas

- `medio` - Medio
- `resiliente` - Resiliente
- `vulneravel` - Vulneravel
- `junior` - Junior
- `senior` - Senior

Quando a baseline ou o historico ainda nao sustentam uma leitura longitudinal, o
SUPREME retorna `medio` com `profile_evidence.provisional=true` e baixa
confianca. Isso mantem o contrato fechado nas cinco classes originais do
simulador, sem criar uma sexta categoria operacional.

## Evidencia obrigatoria no output

Cada perfil persistido em `longitudinal_profiles` carrega:

- `id_hash`
- `profile_class`
- `profile_label`
- `profile_confidence`
- `profile_evidence`
- `baseline_version`
- `algorithm_version`
- `algorithm_parameters`
- `classified_at`

O algoritmo deve ser deterministico: o mesmo input longitudinal gera o mesmo
perfil, a mesma evidencia e a mesma versao de parametros.
