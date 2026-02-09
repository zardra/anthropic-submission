# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenAPI Documentation Generator — a multi-agent system that generates comprehensive API documentation (reference docs, examples, how-to guides, glossary, table of contents) from OpenAPI 3.0 specifications. This is a demonstration/educational project showcasing Claude Code's multi-agent orchestration capabilities.

## Commands

### Run the orchestrator
```bash
pip install pyyaml  # prerequisite
python Scripts/orchestrator.py <openapi-spec.yaml>
python Scripts/orchestrator.py petstore-expanded.yaml  # with included sample
```

### Validate outputs
```bash
ls output/endpoints/*-reference.md output/endpoints/*-howto.md
test -f output/glossary.md && test -f output/toc.md
```

### Run hook scripts manually
```bash
chmod +x Scripts/*.sh
Scripts/validate-openapi.sh < petstore-expanded.yaml
Scripts/validate-markdown.sh < output/endpoints/<file>.md
```

## Architecture

### Workflow Phases

The orchestrator (`Scripts/orchestrator.py`) coordinates 6 agents through 4 sequential phases:

1. **Parse** (sequential): OpenAPI Parser extracts endpoint data → `output/parsed/[endpoint-id].json`
2. **Document** (parallel, up to 4 workers via `ThreadPoolExecutor`): Per endpoint, three agents run concurrently:
   - Parameter Documenter → `output/endpoints/[endpoint-id]-reference.md`
   - Example Generator → `output/parsed/[endpoint-id]-examples.json`
   - How-To Guide Generator → `output/endpoints/[endpoint-id]-howto.md`
3. **Glossary** (sequential): Glossary Builder scans all docs → `output/glossary.md`
4. **TOC** (sequential): TOC Generator creates navigation → `output/toc.md`

### Agent Definitions (`Agents/`)

Each agent is a markdown file defining a Claude Code subagent with frontmatter specifying `mode: write-only` and permitted tools. Agents communicate exclusively through files (no shared state). All agents use only Read and WriteFile tools; the glossary builder additionally uses Grep.

- `openapi-parser.md` — Resolves `$ref` and `allOf` schemas, outputs structured JSON per endpoint
- `parameter-documenter.md` — Creates API reference markdown with formatted parameter/response tables
- `example-generator.md` — Generates realistic cURL commands and error scenario examples
- `howto-generator.md` — Creates tutorial-style docs with multi-step workflows
- `glossary-builder.md` — Extracts/deduplicates terms across all generated docs
- `toc-generator.md` — Creates hierarchical navigation with link validation

### Hooks (`hooks.yaml` → `Scripts/`)

Configured in `hooks.yaml`, scripts live in `Scripts/`:

- **PreToolUse** `validate-openapi.sh` — Validates YAML syntax, OpenAPI 3.x version, and required fields (paths, info) before spec processing
- **PostToolUse** `validate-markdown.sh` — Checks table formatting, unclosed code blocks, header syntax on generated `.md` files
- **PostToolUse** `lint-format.sh` — Removes trailing whitespace, limits consecutive blank lines, warns on lines >120 chars; only processes files under `output/`

### Key Design Decisions

- **JSON intermediate format**: Parser outputs JSON files rather than passing data directly between agents, enabling debugging, re-running downstream agents independently, and manual intervention
- **Endpoint IDs**: Generated as `{method}-{path}` with braces converted to `by-` prefix (e.g., `/pets/{id}` → `get-pets-by-id`)
- **Error handling**: Orchestrator continues processing on per-endpoint failures and aggregates all errors for a final summary report

## Current State

The orchestrator currently simulates agent execution (prints commands, creates marker files) rather than invoking Claude Code's Task tool. The sample spec is `petstore-expanded.yaml` (Swagger Petstore with 4 endpoints using `allOf` composition and `$ref` references).
