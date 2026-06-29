"""International product primitives for SUPREME V4.

Phase 15 keeps international behavior explicit and deterministic. The module
does not claim legal or clinical compliance; it only exposes locale,
jurisdiction and consent metadata that downstream reports/exports can record.
"""

from __future__ import annotations

import copy
from datetime import datetime
from typing import Any

SUPPORTED_LOCALES = ("pt-BR", "en-US", "es-ES")
DEFAULT_LOCALE = "pt-BR"
SUPPORTED_JURISDICTIONS = ("BR", "EU", "US", "GENERIC")
DEFAULT_JURISDICTION = "BR"
DEFAULT_TIMEZONE = "America/Sao_Paulo"

DISCLAIMERS = {
    "pt-BR": [
        "nao_diagnostico_clinico",
        "nao_nexo_causal_automatico",
        "nao_decisao_trabalhista_ou_disciplinar_isolada",
        "nao_admissibilidade_juridica_universal",
        "nao_substitui_avaliacao_profissional",
    ],
    "en-US": [
        "not_clinical_diagnosis",
        "not_automatic_causal_nexus",
        "not_standalone_employment_or_disciplinary_decision",
        "not_universal_legal_admissibility",
        "not_a_replacement_for_professional_assessment",
    ],
    "es-ES": [
        "not_clinical_diagnosis",
        "not_automatic_causal_nexus",
        "not_standalone_employment_or_disciplinary_decision",
        "not_universal_legal_admissibility",
        "not_a_replacement_for_professional_assessment",
    ],
}

JURISDICTION_PROFILES: dict[str, dict[str, Any]] = {
    "BR": {
        "name": "Brazil",
        "privacy_frameworks": ["LGPD"],
        "default_locale": "pt-BR",
        "requires_institutional_authorization": True,
        "disclaimer_key": "br_no_automatic_lgpd_compliance",
    },
    "EU": {
        "name": "European Union",
        "privacy_frameworks": ["GDPR"],
        "default_locale": "en-US",
        "requires_institutional_authorization": True,
        "disclaimer_key": "eu_no_automatic_gdpr_compliance",
    },
    "US": {
        "name": "United States",
        "privacy_frameworks": ["state_privacy", "hipaa_like_constraints_when_applicable"],
        "default_locale": "en-US",
        "requires_institutional_authorization": True,
        "disclaimer_key": "us_no_automatic_hipaa_or_state_compliance",
    },
    "GENERIC": {
        "name": "Generic forensic deployment",
        "privacy_frameworks": ["local_law_review_required"],
        "default_locale": "en-US",
        "requires_institutional_authorization": True,
        "disclaimer_key": "generic_local_legal_review_required",
    },
}

GLOSSARY: dict[str, dict[str, str]] = {
    "exposure": {"pt-BR": "exposição", "en-US": "exposure", "es-ES": "exposición"},
    "forensic_session": {"pt-BR": "sessão pericial", "en-US": "forensic session", "es-ES": "sesión forense"},
    "psychometric_screening": {
        "pt-BR": "triagem psicométrica",
        "en-US": "psychometric screening",
        "es-ES": "cribado psicométrico",
    },
    "custody_chain": {"pt-BR": "cadeia de custódia", "en-US": "custody chain", "es-ES": "cadena de custodia"},
    "integrity_report": {
        "pt-BR": "relatório de integridade",
        "en-US": "integrity report",
        "es-ES": "informe de integridad",
    },
    "participant": {"pt-BR": "participante", "en-US": "participant", "es-ES": "participante"},
    "case": {"pt-BR": "caso", "en-US": "case", "es-ES": "caso"},
    "study": {"pt-BR": "estudo", "en-US": "study", "es-ES": "estudio"},
    "institution": {"pt-BR": "instituição", "en-US": "institution", "es-ES": "institución"},
    "red_flag": {"pt-BR": "red flag", "en-US": "red flag", "es-ES": "red flag"},
    "data_quality": {
        "pt-BR": "qualidade de dados",
        "en-US": "data quality",
        "es-ES": "calidad de datos",
    },
}

FORM_I18N: dict[str, dict[str, dict[str, Any]]] = {
    "pt-BR": {
        "SRQ20": {
            "notice": "Uso ocupacional e científico pseudonimizado. Este instrumento não produz diagnóstico clínico nem nexo causal automático.",
            "session_secure": "Sessão segura",
            "session_unavailable": "Sessão indisponível",
            "back": "Voltar",
            "next": "Próxima",
            "submit": "Concluir",
            "item_label": "Item",
            "of_label": "de",
            "missing_prefix": "Faltam",
            "missing_suffix": "item(ns).",
            "complete_before_submit": "Complete este item antes de transmitir.",
            "submitting": "Transmitindo...",
            "retry": "Tentar novamente",
            "submitted": "Respostas transmitidas. Esta aba será fechada.",
            "fineprint": "As respostas são transmitidas apenas ao backend SUPREME usando a sessão segura deste formulário.",
        },
        "DASS21": {},
        "OLBI": {},
        "PANAS_SHORT": {},
    },
    "en-US": {
        "SRQ20": {
            "title": "Self-Reporting Questionnaire",
            "subtitle": "Symptoms in the last four weeks",
            "instruction": "Answer yes or no considering the last four weeks.",
            "scaleHint": "No = 0 - Yes = 1",
            "scale": [{"value": 0, "label": "No"}, {"value": 1, "label": "Yes"}],
            "questions": [
                "Do you often have headaches?",
                "Is your appetite poor?",
                "Do you sleep badly?",
                "Are you easily frightened?",
                "Do your hands shake?",
                "Do you feel nervous, tense, or worried?",
                "Is your digestion poor?",
                "Do you have trouble thinking clearly?",
                "Have you felt unhappy recently?",
                "Have you been crying more than usual?",
                "Do you find it difficult to enjoy your daily activities?",
                "Do you find it difficult to make decisions?",
                "Is your work difficult, stressful, or causing suffering?",
                "Are you unable to play a useful part in your life?",
                "Have you lost interest in things?",
                "Do you feel that you are a worthless person?",
                "Have you had thoughts of ending your life?",
                "Do you feel tired all the time?",
                "Do you have uncomfortable feelings in your stomach?",
                "Do you get tired easily?",
            ],
            "notice": "Pseudonymized occupational and scientific use. This screening is not a clinical diagnosis and does not establish automatic causal nexus.",
            "session_secure": "Secure session",
            "session_unavailable": "Session unavailable",
            "back": "Back",
            "next": "Next",
            "submit": "Submit",
            "item_label": "Item",
            "of_label": "of",
            "missing_prefix": "Missing",
            "missing_suffix": "item(s).",
            "complete_before_submit": "Complete this item before submitting.",
            "submitting": "Submitting...",
            "retry": "Try again",
            "submitted": "Answers submitted. This tab will close.",
            "fineprint": "Answers are transmitted only to the SUPREME backend using this form's secure session.",
        },
        "DASS21": {
            "notice": "Pseudonymized occupational and scientific use. This screening is not a clinical diagnosis and does not establish automatic causal nexus.",
            "session_secure": "Secure session",
            "session_unavailable": "Session unavailable",
            "complete_before_submit": "Complete this item before submitting.",
            "submitting": "Submitting...",
            "retry": "Try again",
            "submitted": "Answers submitted. This tab will close.",
            "fineprint": "Answers are transmitted only to the SUPREME backend using this form's secure session.",
        },
        "OLBI": {},
        "PANAS_SHORT": {},
    },
    "es-ES": {
        "SRQ20": {
            "title": "Cuestionario de Autoinforme",
            "subtitle": "Síntomas en las últimas cuatro semanas",
            "instruction": "Responda sí o no considerando las últimas cuatro semanas.",
            "scaleHint": "No = 0 - Sí = 1",
            "scale": [{"value": 0, "label": "No"}, {"value": 1, "label": "Sí"}],
            "questions": [
                "¿Tiene dolores de cabeza frecuentes?",
                "¿Tiene poco apetito?",
                "¿Duerme mal?",
                "¿Se asusta con facilidad?",
                "¿Le tiemblan las manos?",
                "¿Se siente nervioso(a), tenso(a) o preocupado(a)?",
                "¿Tiene mala digestión?",
                "¿Tiene dificultad para pensar con claridad?",
                "¿Se ha sentido triste últimamente?",
                "¿Ha llorado más de lo habitual?",
                "¿Le cuesta disfrutar de sus actividades diarias?",
                "¿Tiene dificultad para tomar decisiones?",
                "¿Su trabajo es difícil, estresante o le causa sufrimiento?",
                "¿Se siente incapaz de desempeñar un papel útil en su vida?",
                "¿Ha perdido interés por las cosas?",
                "¿Se siente una persona inútil o sin valor?",
                "¿Ha tenido ideas de acabar con su vida?",
                "¿Se siente cansado(a) todo el tiempo?",
                "¿Tiene sensaciones desagradables en el estómago?",
                "¿Se cansa con facilidad?",
            ],
            "notice": "Estructura preparada para traducción completa en español. No es diagnóstico clínico ni nexo causal automático.",
            "session_secure": "Sesión segura",
            "session_unavailable": "Sesión no disponible",
            "back": "Volver",
            "next": "Siguiente",
            "submit": "Enviar",
            "item_label": "Item",
            "of_label": "de",
            "missing_prefix": "Faltan",
            "missing_suffix": "item(s).",
            "complete_before_submit": "Complete este item antes de enviar.",
            "submitting": "Enviando...",
            "retry": "Intentar de nuevo",
            "submitted": "Respuestas enviadas. Esta pestaña se cerrará.",
            "fineprint": "Las respuestas se transmiten solo al backend SUPREME mediante la sesión segura de este formulario.",
        },
        "DASS21": {},
        "OLBI": {},
        "PANAS_SHORT": {},
    },
}

FORM_COMMON_I18N: dict[str, dict[str, Any]] = {
    "pt-BR": {
        "session_secure": "Sessão segura",
        "session_unavailable": "Sessão indisponível",
        "back": "Voltar",
        "next": "Próxima",
        "submit": "Concluir",
        "item_label": "Item",
        "of_label": "de",
        "missing_prefix": "Faltam",
        "missing_suffix": "item(ns).",
        "complete_before_submit": "Complete este item antes de transmitir.",
        "submitting": "Transmitindo...",
        "retry": "Tentar novamente",
        "submitted": "Respostas transmitidas. Esta aba será fechada.",
        "error_prefix": "Erro:",
        "fineprint": "As respostas são transmitidas apenas ao backend SUPREME usando a sessão segura deste formulário.",
        "notice": "Uso ocupacional e científico pseudonimizado. Este instrumento não produz diagnóstico clínico nem nexo causal automático.",
    },
    "en-US": {
        "session_secure": "Secure session",
        "session_unavailable": "Session unavailable",
        "back": "Back",
        "next": "Next",
        "submit": "Submit",
        "item_label": "Item",
        "of_label": "of",
        "missing_prefix": "Missing",
        "missing_suffix": "item(s).",
        "complete_before_submit": "Complete this item before submitting.",
        "submitting": "Submitting...",
        "retry": "Try again",
        "submitted": "Answers submitted. This tab will close.",
        "error_prefix": "Error:",
        "fineprint": "Answers are transmitted only to the SUPREME backend using this form's secure session.",
        "notice": "Pseudonymized occupational and scientific use. This screening is not a clinical diagnosis and does not establish automatic causal nexus.",
    },
    "es-ES": {
        "session_secure": "Sesión segura",
        "session_unavailable": "Sesión no disponible",
        "back": "Volver",
        "next": "Siguiente",
        "submit": "Enviar",
        "item_label": "Item",
        "of_label": "de",
        "missing_prefix": "Faltan",
        "missing_suffix": "item(s).",
        "complete_before_submit": "Complete este item antes de enviar.",
        "submitting": "Enviando...",
        "retry": "Intentar de nuevo",
        "submitted": "Respuestas enviadas. Esta pestaña se cerrará.",
        "error_prefix": "Error:",
        "fineprint": "Las respuestas se transmiten solo al backend SUPREME mediante la sesión segura de este formulario.",
        "notice": "Uso ocupacional y científico seudonimizado. Este instrumento no produce diagnóstico clínico ni nexo causal automático.",
    },
}

FORM_FULL_I18N: dict[str, dict[str, dict[str, Any]]] = {
    "pt-BR": {
        "SRQ20": {
            "title": "Questionário de Autorrelato",
            "subtitle": "Sintomas nas últimas quatro semanas",
            "instruction": "Responda sim ou não considerando as últimas quatro semanas.",
            "scaleHint": "Não = 0 - Sim = 1",
            "scale": [{"value": 0, "label": "Não"}, {"value": 1, "label": "Sim"}],
            "questions": [
                "Tem dores de cabeça frequentes?",
                "Tem falta de apetite?",
                "Dorme mal?",
                "Assusta-se com facilidade?",
                "Tem tremores nas mãos?",
                "Sente-se nervoso(a), tenso(a) ou preocupado(a)?",
                "Tem má digestão?",
                "Tem dificuldade de pensar com clareza?",
                "Tem se sentido triste ultimamente?",
                "Tem chorado mais do que de costume?",
                "Encontra dificuldade para realizar com satisfação suas atividades diárias?",
                "Tem dificuldade para tomar decisões?",
                "Tem dificuldade no serviço, ou seu trabalho é penoso e causa sofrimento?",
                "É incapaz de desempenhar um papel útil em sua vida?",
                "Tem perdido o interesse pelas coisas?",
                "Você se sente uma pessoa inútil, sem préstimo?",
                "Tem tido ideia de acabar com a sua vida?",
                "Sente-se cansado(a) o tempo todo?",
                "Tem sensações desagradáveis no estômago?",
                "Você se cansa com facilidade?",
            ],
        },
        "DASS21": {
            "title": "Depressão, ansiedade e estresse",
            "subtitle": "Frequência na última semana",
            "instruction": "Para cada frase, selecione o quanto ela se aplicou a você na última semana.",
            "scaleHint": "0 = não se aplicou - 3 = aplicou-se muito",
            "scale": [
                {"value": 0, "label": "Não se aplicou"},
                {"value": 1, "label": "Algumas vezes"},
                {"value": 2, "label": "Boa parte"},
                {"value": 3, "label": "Maior parte"},
            ],
            "questions": [
                "Achei difícil me acalmar",
                "Percebi minha boca seca",
                "Não consegui sentir nenhum sentimento positivo",
                "Tive dificuldade em respirar",
                "Achei difícil ter iniciativa para fazer as coisas",
                "Reagi exageradamente a certas situações",
                "Senti tremores nas mãos",
                "Senti que estava sempre nervoso(a)",
                "Preocupei-me com situações de pânico",
                "Senti que não tinha nada a esperar do futuro",
                "Senti-me agitado(a)",
                "Achei difícil descontrair",
                "Senti-me para baixo / deprimido(a)",
                "Fui intolerante com o que me impedia de concluir o que fazia",
                "Senti que estava próximo(a) do pânico",
                "Não consegui entusiasmar-me com nada",
                "Senti que não tinha muito valor como pessoa",
                "Senti que estava muito irritado(a)",
                "O meu coração acelerou sem ter feito exercício físico",
                "Senti medo sem razão aparente",
                "Senti que a vida não tinha sentido",
            ],
        },
        "OLBI": {
            "title": "Inventario de Burnout de Oldenburg",
            "subtitle": "Percepção sobre o trabalho atual",
            "instruction": "Indique seu grau de concordância com cada afirmação sobre o seu trabalho atual.",
            "scaleHint": "1 = discordo muito - 4 = concordo muito",
            "scale": [
                {"value": 1, "label": "Discordo muito"},
                {"value": 2, "label": "Discordo"},
                {"value": 3, "label": "Concordo"},
                {"value": 4, "label": "Concordo muito"},
            ],
            "questions": [
                "Posso tolerar muito bem a pressão do meu trabalho",
                "Depois do trabalho, tenho tendencia a precisar de mais tempo para relaxar do que antes",
                "Ha dias em que ja me sinto cansado(a) antes mesmo de chegar ao trabalho",
                "Consigo suportar muito bem as demandas do meu trabalho",
                "Ultimamente tenho pensado cada vez mais em desistir do meu trabalho",
                "Acho o meu trabalho um desafio positivo",
                "Durante o meu trabalho, tenho muita dificuldade em me concentrar",
                "No meu trabalho, encontro muitas coisas que me interessam fazer",
                "Apos o trabalho, costumo sentir-me exausto(a)",
                "Depois de trabalhar, tenho energia suficiente para minhas atividades de lazer",
                "As vezes sinto-me farto(a) do meu trabalho",
                "E raro que eu me entusiasme com o meu trabalho",
                "Apos o trabalho costumo sentir-me bem",
                "Geralmente não me identifico com o meu trabalho",
                "Quando trabalho, costumo sentir-me energizado(a)",
                "Sinto que o meu trabalho tem significado pessoal para mim",
            ],
        },
        "PANAS_SHORT": {
            "title": "Afeto positivo e negativo",
            "subtitle": "Como voce se sente agora, neste momento",
            "instruction": "Indique em que medida cada palavra descreve o que voce sente agora.",
            "scaleHint": "1 = nada - 5 = extremamente",
            "scale": [
                {"value": 1, "label": "Nada"},
                {"value": 2, "label": "Um pouco"},
                {"value": 3, "label": "Moderadamente"},
                {"value": 4, "label": "Bastante"},
                {"value": 5, "label": "Extremamente"},
            ],
            "questions": [
                "Interessado(a)",
                "Angustiado(a) / perturbado(a)",
                "Animado(a) / excitado(a)",
                "Contrariado(a)",
                "Forte / vigoroso(a)",
                "Culpado(a)",
                "Assustado(a)",
                "Hostil / com raiva",
                "Entusiasmado(a)",
                "Orgulhoso(a)",
            ],
        },
    },
    "en-US": {
        "SRQ20": {
            "title": "Self-Reporting Questionnaire",
            "subtitle": "Symptoms in the last four weeks",
            "instruction": "Answer yes or no considering the last four weeks.",
            "scaleHint": "No = 0 - Yes = 1",
            "scale": [{"value": 0, "label": "No"}, {"value": 1, "label": "Yes"}],
            "questions": [
                "Do you often have headaches?",
                "Is your appetite poor?",
                "Do you sleep badly?",
                "Are you easily frightened?",
                "Do your hands shake?",
                "Do you feel nervous, tense, or worried?",
                "Is your digestion poor?",
                "Do you have trouble thinking clearly?",
                "Have you felt sad recently?",
                "Have you been crying more than usual?",
                "Do you find it difficult to enjoy your daily activities?",
                "Do you find it difficult to make decisions?",
                "Is your work difficult, stressful, or causing suffering?",
                "Are you unable to play a useful role in your life?",
                "Have you lost interest in things?",
                "Do you feel that you are a worthless person?",
                "Have you had thoughts of ending your life?",
                "Do you feel tired all the time?",
                "Do you have uncomfortable feelings in your stomach?",
                "Do you get tired easily?",
            ],
        },
        "DASS21": {
            "title": "Depression, anxiety and stress",
            "subtitle": "Frequency during the last week",
            "instruction": "For each statement, select how much it applied to you during the last week.",
            "scaleHint": "0 = did not apply - 3 = applied very much",
            "scale": [
                {"value": 0, "label": "Did not apply"},
                {"value": 1, "label": "Sometimes"},
                {"value": 2, "label": "Often"},
                {"value": 3, "label": "Most of the time"},
            ],
            "questions": [
                "I found it difficult to calm down",
                "I noticed my mouth was dry",
                "I could not experience positive feelings",
                "I had difficulty breathing",
                "I found it hard to get started on tasks",
                "I overreacted to some situations",
                "I felt trembling in my hands",
                "I felt constantly nervous",
                "I worried about panic situations",
                "I felt I had nothing to look forward to",
                "I felt agitated",
                "I found it difficult to relax",
                "I felt down or depressed",
                "I was intolerant of things that kept me from finishing what I was doing",
                "I felt close to panic",
                "I could not feel enthusiastic about anything",
                "I felt I was not worth much as a person",
                "I felt very irritable",
                "My heart raced without physical exercise",
                "I felt afraid without an apparent reason",
                "I felt that life had no meaning",
            ],
        },
        "OLBI": {
            "title": "Oldenburg Burnout Inventory",
            "subtitle": "Perception of current work",
            "instruction": "Indicate your level of agreement with each statement about your current work.",
            "scaleHint": "1 = strongly disagree - 4 = strongly agree",
            "scale": [
                {"value": 1, "label": "Strongly disagree"},
                {"value": 2, "label": "Disagree"},
                {"value": 3, "label": "Agree"},
                {"value": 4, "label": "Strongly agree"},
            ],
            "questions": [
                "I can tolerate the pressure of my work very well",
                "After work, I tend to need more time to relax than before",
                "There are days when I already feel tired before arriving at work",
                "I can cope very well with the demands of my work",
                "Lately I have increasingly thought about leaving my job",
                "I see my work as a positive challenge",
                "During work, I have great difficulty concentrating",
                "In my work, I find many things that interest me",
                "After work, I often feel exhausted",
                "After working, I have enough energy for leisure activities",
                "Sometimes I feel fed up with my work",
                "It is rare for me to feel enthusiastic about my work",
                "After work, I usually feel well",
                "I generally do not identify with my work",
                "When I work, I usually feel energized",
                "I feel that my work has personal meaning for me",
            ],
        },
        "PANAS_SHORT": {
            "title": "Positive and negative affect",
            "subtitle": "How you feel right now",
            "instruction": "Indicate how much each word describes what you feel right now.",
            "scaleHint": "1 = not at all - 5 = extremely",
            "scale": [
                {"value": 1, "label": "Not at all"},
                {"value": 2, "label": "A little"},
                {"value": 3, "label": "Moderately"},
                {"value": 4, "label": "Quite a bit"},
                {"value": 5, "label": "Extremely"},
            ],
            "questions": [
                "Interested",
                "Distressed / upset",
                "Excited",
                "Upset",
                "Strong / vigorous",
                "Guilty",
                "Scared",
                "Hostile / angry",
                "Enthusiastic",
                "Proud",
            ],
        },
    },
    "es-ES": {
        "SRQ20": {
            "title": "Cuestionario de Autoinforme",
            "subtitle": "Síntomas en las últimas cuatro semanas",
            "instruction": "Responda sí o no considerando las últimas cuatro semanas.",
            "scaleHint": "No = 0 - Sí = 1",
            "scale": [{"value": 0, "label": "No"}, {"value": 1, "label": "Sí"}],
            "questions": [
                "¿Tiene dolores de cabeza frecuentes?",
                "¿Tiene poco apetito?",
                "¿Duerme mal?",
                "¿Se asusta con facilidad?",
                "¿Le tiemblan las manos?",
                "¿Se siente nervioso(a), tenso(a) o preocupado(a)?",
                "¿Tiene mala digestión?",
                "¿Tiene dificultad para pensar con claridad?",
                "¿Se ha sentido triste últimamente?",
                "¿Ha llorado más de lo habitual?",
                "¿Le cuesta disfrutar de sus actividades diarias?",
                "¿Tiene dificultad para tomar decisiones?",
                "¿Su trabajo es difícil, estresante o le causa sufrimiento?",
                "¿Se siente incapaz de desempeñar un papel útil en su vida?",
                "¿Ha perdido interés por las cosas?",
                "¿Se siente una persona inútil o sin valor?",
                "¿Ha tenido ideas de acabar con su vida?",
                "¿Se siente cansado(a) todo el tiempo?",
                "¿Tiene sensaciones desagradables en el estómago?",
                "¿Se cansa con facilidad?",
            ],
        },
        "DASS21": {
            "title": "Depresion, ansiedad y estres",
            "subtitle": "Frecuencia durante la ultima semana",
            "instruction": "Para cada frase, seleccione cuanto se aplico a usted durante la ultima semana.",
            "scaleHint": "0 = no se aplico - 3 = se aplico mucho",
            "scale": [
                {"value": 0, "label": "No se aplico"},
                {"value": 1, "label": "A veces"},
                {"value": 2, "label": "A menudo"},
                {"value": 3, "label": "La mayor parte"},
            ],
            "questions": [
                "Me resultó difícil calmarme",
                "Note que tenia la boca seca",
                "No pude sentir emociones positivas",
                "Tuve dificultad para respirar",
                "Me resultó difícil iniciar actividades",
                "Reaccione de forma exagerada ante algunas situaciones",
                "Senti temblores en las manos",
                "Senti que estaba siempre nervioso(a)",
                "Me preocupé por situaciones de pánico",
                "Senti que no tenia nada que esperar del futuro",
                "Me senti agitado(a)",
                "Me resultó difícil relajarme",
                "Me senti decaido(a) o deprimido(a)",
                "Fui intolerante con lo que me impedia terminar lo que hacia",
                "Sentí que estaba cerca del pánico",
                "No pude entusiasmarme con nada",
                "Senti que no valia mucho como persona",
                "Senti que estaba muy irritable",
                "Mi corazon se acelero sin ejercicio fisico",
                "Senti miedo sin razon aparente",
                "Senti que la vida no tenia sentido",
            ],
        },
        "OLBI": {
            "title": "Inventario de Burnout de Oldenburg",
            "subtitle": "Percepcion sobre el trabajo actual",
            "instruction": "Indique su grado de acuerdo con cada afirmacion sobre su trabajo actual.",
            "scaleHint": "1 = muy en desacuerdo - 4 = muy de acuerdo",
            "scale": [
                {"value": 1, "label": "Muy en desacuerdo"},
                {"value": 2, "label": "En desacuerdo"},
                {"value": 3, "label": "De acuerdo"},
                {"value": 4, "label": "Muy de acuerdo"},
            ],
            "questions": [
                "Puedo tolerar muy bien la presion de mi trabajo",
                "Después del trabajo, suelo necesitar más tiempo para relajarme que antes",
                "Hay dias en los que ya me siento cansado(a) antes de llegar al trabajo",
                "Puedo soportar muy bien las demandas de mi trabajo",
                "Últimamente he pensado cada vez más en dejar mi trabajo",
                "Considero mi trabajo un desafio positivo",
                "Durante mi trabajo, tengo mucha dificultad para concentrarme",
                "En mi trabajo encuentro muchas cosas que me interesan",
                "Después del trabajo, suelo sentirme exhausto(a)",
                "Después de trabajar, tengo energía suficiente para actividades de ocio",
                "A veces me siento harto(a) de mi trabajo",
                "Es raro que me entusiasme con mi trabajo",
                "Después del trabajo suelo sentirme bien",
                "Generalmente no me identifico con mi trabajo",
                "Cuando trabajo, suelo sentirme energizado(a)",
                "Siento que mi trabajo tiene significado personal para mí",
            ],
        },
        "PANAS_SHORT": {
            "title": "Afecto positivo y negativo",
            "subtitle": "Como se siente ahora, en este momento",
            "instruction": "Indique en que medida cada palabra describe lo que siente ahora.",
            "scaleHint": "1 = nada - 5 = extremadamente",
            "scale": [
                {"value": 1, "label": "Nada"},
                {"value": 2, "label": "Un poco"},
                {"value": 3, "label": "Moderadamente"},
                {"value": 4, "label": "Bastante"},
                {"value": 5, "label": "Extremadamente"},
            ],
            "questions": [
                "Interesado(a)",
                "Angustiado(a) / perturbado(a)",
                "Animado(a) / excitado(a)",
                "Contrariado(a)",
                "Fuerte / vigoroso(a)",
                "Culpable",
                "Asustado(a)",
                "Hostil / con rabia",
                "Entusiasmado(a)",
                "Orgulloso(a)",
            ],
        },
    },
}

CONSENT_TEMPLATES: dict[str, dict[str, dict[str, dict[str, str]]]] = {
    "BR": {
        "pt-BR": {
            "operational": {
                "version": "BR-pt-BR-operational-v1",
                "text": "Autorizo o uso operacional pseudonimizado para suporte ao fluxo pericial.",
            },
            "research": {
                "version": "BR-pt-BR-research-v1",
                "text": "Autorizo uso de dados pseudonimizados em pesquisa aprovada pela instituicao.",
            },
            "institutional_authorization": {
                "version": "BR-pt-BR-institutional-v1",
                "text": "A instituicao declara base legal e autorizacao para operar o SUPREME.",
            },
        }
    },
    "EU": {
        "en-US": {
            "operational": {
                "version": "EU-en-US-operational-v1",
                "text": "Operational pseudonymized processing requires institution-approved lawful basis.",
            },
            "research": {
                "version": "EU-en-US-research-v1",
                "text": "Research use requires approved protocol and jurisdiction-specific safeguards.",
            },
            "institutional_authorization": {
                "version": "EU-en-US-institutional-v1",
                "text": "The institution records lawful basis and controller/processor responsibilities.",
            },
        }
    },
    "US": {
        "en-US": {
            "operational": {
                "version": "US-en-US-operational-v1",
                "text": "Operational use requires institutional authorization and applicable state/federal review.",
            },
            "research": {
                "version": "US-en-US-research-v1",
                "text": "Research use requires approved protocol and privacy review.",
            },
            "institutional_authorization": {
                "version": "US-en-US-institutional-v1",
                "text": "The institution records authorization and applicable privacy constraints.",
            },
        }
    },
    "GENERIC": {
        "en-US": {
            "operational": {
                "version": "GENERIC-en-US-operational-v1",
                "text": "Operational processing requires local legal and institutional review.",
            },
            "research": {
                "version": "GENERIC-en-US-research-v1",
                "text": "Research use requires local ethics, privacy and institutional approval.",
            },
            "institutional_authorization": {
                "version": "GENERIC-en-US-institutional-v1",
                "text": "The institution must document local authorization before deployment.",
            },
        }
    },
}


def normalize_locale(locale: str | None) -> str:
    value = (locale or DEFAULT_LOCALE).strip()
    return value if value in SUPPORTED_LOCALES else DEFAULT_LOCALE


def normalize_jurisdiction(profile: str | None) -> str:
    value = (profile or DEFAULT_JURISDICTION).strip().upper()
    if value not in SUPPORTED_JURISDICTIONS:
        raise ValueError(f"invalid jurisdiction_profile: {profile}")
    return value


def normalize_timezone(value: str | None) -> str:
    return (value or DEFAULT_TIMEZONE).strip() or DEFAULT_TIMEZONE


def jurisdiction_profile(profile: str | None) -> dict[str, Any]:
    key = normalize_jurisdiction(profile)
    return {"code": key, **copy.deepcopy(JURISDICTION_PROFILES[key])}


def international_metadata(
    *,
    locale: str | None = None,
    jurisdiction: str | None = None,
    timezone_name: str | None = None,
    consent_version: str | None = None,
) -> dict[str, Any]:
    loc = normalize_locale(locale)
    jur = normalize_jurisdiction(jurisdiction)
    return {
        "locale": loc,
        "jurisdiction_profile": jur,
        "timezone": normalize_timezone(timezone_name),
        "jurisdiction": jurisdiction_profile(jur),
        "disclaimers": DISCLAIMERS.get(loc, DISCLAIMERS[DEFAULT_LOCALE]),
        "consent_version": consent_version or "not_recorded",
    }


def form_messages(locale: str | None, instrument: str) -> dict[str, Any]:
    loc = normalize_locale(locale)
    fallback = {
        **FORM_COMMON_I18N[DEFAULT_LOCALE],
        **FORM_I18N[DEFAULT_LOCALE].get(instrument, {}),
        **FORM_FULL_I18N[DEFAULT_LOCALE].get(instrument, {}),
    }
    selected = {
        **FORM_COMMON_I18N.get(loc, FORM_COMMON_I18N[DEFAULT_LOCALE]),
        **FORM_I18N.get(loc, {}).get(instrument, {}),
        **FORM_FULL_I18N.get(loc, {}).get(instrument, {}),
    }
    return {**fallback, **selected, "locale": loc}


def consent_template(jurisdiction: str | None, locale: str | None, consent_type: str) -> dict[str, str]:
    jur = normalize_jurisdiction(jurisdiction)
    loc = normalize_locale(locale)
    templates_by_locale = CONSENT_TEMPLATES.get(jur, {})
    selected_locale = loc if loc in templates_by_locale else JURISDICTION_PROFILES[jur]["default_locale"]
    templates = templates_by_locale.get(selected_locale) or CONSENT_TEMPLATES["GENERIC"]["en-US"]
    if consent_type not in templates:
        raise ValueError(f"invalid consent_type: {consent_type}")
    return {"jurisdiction_profile": jur, "locale": selected_locale, "consent_type": consent_type, **templates[consent_type]}


def report_timestamp(now: datetime, locale: str | None) -> str:
    loc = normalize_locale(locale)
    if loc == "pt-BR":
        return now.strftime("%d/%m/%Y %H:%M:%S UTC")
    return now.strftime("%Y-%m-%d %H:%M:%S UTC")
