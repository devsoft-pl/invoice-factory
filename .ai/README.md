# .ai/ — Instrukcje dla agentow AI

Struktura kompatybilna z Claude Code (CLAUDE.md) i Gemini (AGENTS.md).

## Struktura

```
.ai/
├── README.md           # Ten plik
├── rules/              # Zasady obowiazujace przy KAZDYM tasku
│   ├── django.md       # Stack, architektura, konwencje Django
│   ├── style.md        # Formatowanie, nazewnictwo, commity
│   └── testing.md      # Jak pisac i uruchamiac testy
└── tasks/              # Pojedyncze taski do wykonania przez AI
    ├── 01-atomic-transactions.md
    ├── 02-delete-requires-post.md
    ├── 03-deduplicate-invoice-views.md
    ├── 04-item-save-n-plus-1.md
    ├── 05-fix-thousand-separator.md
    ├── 06-fix-nip-validator.md
    ├── 07-replace-generic-exceptions.md
    ├── 08-api-rate-limiting.md
    ├── 09-fix-ci-pytest.md
    ├── 10-unique-constraint-migration.md
    ├── 11-add-db-indexes.md
    ├── 12-remove-dead-code.md
    ├── 13-sentry-sample-rate.md
    └── 14-add-timestamps.md
```

## Jak uzywac

### Claude Code
Powiedz: `przeczytaj .ai/rules/ i wykonaj task z .ai/tasks/01-atomic-transactions.md`

### Gemini
Gemini automatycznie czyta AGENTS.md z roota. Taski wskazuj recznie.

## Konwencja plikow task

Kazdy plik task ma:
- **Priority**: CRITICAL / HIGH / MEDIUM / LOW
- **Status**: todo / in-progress / done
- **Files to modify**: lista plikow do zmiany
- **Steps**: krok po kroku co zrobic
- **Constraints**: czego NIE robic
- **Acceptance criteria**: kiedy task jest ukonczony
