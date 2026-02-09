# OpenAPI Documentation Generator Plan

An advanced Claude Code implementation demonstrating sophisticated multi-agent workflows for generating comprehensive API documentation from OpenAPI specifications.

## Overview

This system uses Claude Code agents and hooks to automatically generate high-quality API documentation including:
- API reference documentation with parameter tables
- Realistic request/response examples
- Tutorial-style how-to guides
- Comprehensive glossary
- Organized table of contents


## Architecture

### Multi-Agent System

```
OpenAPI Spec
     ↓
[Parser Agent] ──→ Extract endpoint data
     ↓
[Orchestrator] ──→ Coordinate parallel execution
     ↓
┌────┴────┬──────────┬──────────┐
Parameter Example   How-To    (parallel per endpoint)
Documenter Generator Guide
└────┬────┴──────────┴──────────┘
     ↓
[Glossary Agent] ──→ Build terminology index
     ↓
[TOC Agent] ──→ Create navigation
     ↓
Complete Documentation
```

### Agents

1. **OpenAPI Parser** (`Agents/openapi-parser.md`)
   - Extracts and validates endpoint data from OpenAPI specs
   - Resolves schema references (including `$ref` and `allOf`)
   - Outputs structured JSON for downstream agents

2. **Parameter Documenter** (`Agents/parameter-documenter.md`)
   - Creates API reference markdown with formatted parameter tables
   - Handles complex nested objects
   - Documents request/response schemas

3. **Example Generator** (`Agents/example-generator.md`)
   - Generates realistic request/response examples
   - Creates cURL commands
   - Provides error scenario examples

4. **How-To Guide Generator** (`Agents/howto-generator.md`)
   - Creates tutorial-style documentation
   - Demonstrates multi-step workflows
   - Includes error handling and best practices

5. **Glossary Builder** (`Agents/glossary-builder.md`)
   - Extracts technical terms from all documentation
   - Deduplicates and organizes alphabetically
   - Cross-references related endpoints

6. **TOC Generator** (`Agents/toc-generator.md`)
   - Creates nested table of contents
   - Validates all links
   - Organizes by resource hierarchy

### Hooks

1. **validate-openapi.sh** (PreToolUse)
   - Validates OpenAPI spec before processing
   - Checks YAML syntax
   - Verifies required fields (paths, info, version)

2. **validate-markdown.sh** (PostToolUse)
   - Validates markdown table formatting
   - Checks for unclosed code blocks
   - Ensures consistent header syntax

3. **lint-format.sh** (PostToolUse)
   - Formats documentation consistently
   - Removes trailing whitespace
   - Limits consecutive blank lines
   - Reports style warnings

## Usage

### Prerequisites

- Claude Code installed and configured
- Python 3.7+ (for orchestrator script)
- PyYAML library: `pip install pyyaml`

<!--
### Quick Start

1. **Place your OpenAPI spec** in the project root:
   ```bash
   cp your-api-spec.yaml <Project_path>.yaml
   ```

2. **Run the orchestrator**:
   ```bash
   cd openapi-doc-generator
   python scripts/orchestrator.py ../<API_file_name>.yaml
   ```

3. **View generated documentation**:
   ```bash
   ls output/
   # toc.md - Table of contents
   # glossary.md - API glossary
   # endpoints/ - All endpoint documentation
   ```

### Running Individual Agents

You can also run agents individually using Claude Code's Task tool:

```bash
# Parse the OpenAPI spec
claude task --agent Agents/openapi-parser.md

# Generate parameter documentation for a specific endpoint
claude task --agent Agents/parameter-documenter.md --input "<method-path>"

# Build the glossary
claude task --agent Agents/glossary-builder.md
```
-->
## Advanced Features

### Parallel Execution

The orchestrator runs Parameter Documenter, Example Generator, and How-To Guide Generator in parallel for each endpoint, significantly improving performance:

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    # Submit multiple agents simultaneously
    for endpoint in endpoints:
        executor.submit(run_agent, 'parameter-documenter', endpoint['id'])
        executor.submit(run_agent, 'example-generator', endpoint['id'])
        executor.submit(run_agent, 'howto-generator', endpoint['id'])
```

### Error Handling

The system includes comprehensive error handling:
- **Validation hooks**: Catch malformed inputs before processing
- **Agent-level errors**: Each agent reports failures gracefully
- **Orchestrator recovery**: Continues processing even if individual endpoints fail
- **Error aggregation**: Collects and reports all errors at completion

### Context Management

Agents are designed with careful context management:
- **Isolated contexts**: Each agent operates in its own context via Task tool
- **Write-only mode**: Agents write outputs directly to files
- **Tool restrictions**: Agents have minimal required tools (Read, WriteFile, Grep)
- **No state sharing**: Agents communicate through files, not shared state

### Complex Object Handling

The Parameter Documenter demonstrates sophisticated nested object handling:
- Resolves `$ref` schema references
- Flattens `allOf` composition
- Presents nested properties clearly in tables
- Uses dot notation for deeply nested fields


## Configuration

### Verify Outputs

Check that all expected files were generated:

```bash
ls output/endpoints/*-reference.md
ls output/endpoints/*-howto.md

# Should have central docs
test -f output/glossary.md
test -f output/toc.md
```

### Validate Generated Markdown

Run the validation hook manually:

```bash
Scripts/validate-markdown.sh < output/endpoints/<Reference_file_name>.md
```

## Performance Considerations

### Parallel Processing

- Default max workers: 4 concurrent agents
- Adjust in `orchestrator.py`: `max_workers = min(4, len(endpoints))`
- Higher values may hit rate limits or context window issues

### Context Window Management

Each agent operates independently with its own context window:
- Parser: Loads full OpenAPI spec (~10-50KB)
- Per-endpoint agents: Load single endpoint data (~1-5KB)
- Glossary/TOC: Load all generated docs (~50-200KB)



## License

This is example code for educational purposes demonstrating Claude Code capabilities.
