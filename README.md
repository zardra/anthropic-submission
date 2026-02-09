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

1. **OpenAPI Parser** (`.claude/agents/openapi-parser.md`)
   - Extracts and validates endpoint data from OpenAPI specs
   - Resolves schema references (including `$ref` and `allOf`)
   - Outputs structured JSON for downstream agents

2. **Parameter Documenter** (`.claude/agents/parameter-documenter.md`)
   - Creates API reference markdown with formatted parameter tables
   - Handles complex nested objects
   - Documents request/response schemas

3. **Example Generator** (`.claude/agents/example-generator.md`)
   - Generates realistic request/response examples
   - Creates cURL commands
   - Provides error scenario examples

4. **How-To Guide Generator** (`.claude/agents/howto-generator.md`)
   - Creates tutorial-style documentation
   - Demonstrates multi-step workflows
   - Includes error handling and best practices

5. **Glossary Builder** (`.claude/agents/glossary-builder.md`)
   - Extracts technical terms from all documentation
   - Deduplicates and organizes alphabetically
   - Cross-references related endpoints

6. **TOC Generator** (`.claude/agents/toc-generator.md`)
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
claude task --agent .claude/agents/openapi-parser.md

# Generate parameter documentation for a specific endpoint
claude task --agent .claude/agents/parameter-documenter.md --input "<method-path>"

# Build the glossary
claude task --agent .claude/agents/glossary-builder.md
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

## Project Structure

```
openapi-doc-generator/
├── .claude/
│   ├── agents/
│   │   ├── openapi-parser.md
│   │   ├── parameter-documenter.md
│   │   ├── example-generator.md
│   │   ├── howto-generator.md
│   │   ├── glossary-builder.md
│   │   └── toc-generator.md
│   ├── hooks/
│   │   ├── validate-openapi.sh
│   │   ├── validate-markdown.sh
│   │   └── lint-format.sh
│   └── hooks.yaml
├── scripts/
│   └── orchestrator.py
├── output/
│   ├── parsed/          # Intermediate JSON data
│   ├── endpoints/       # Generated endpoint docs
│   ├── glossary.md
│   └── toc.md
└── README.md
```

## Configuration
<!--
### Hooks Configuration

Edit `.claude/hooks.yaml` to customize hook behavior:

```yaml
hooks:
  - event: PreToolUse
    type: command
    command: .claude/hooks/validate-openapi.sh
    description: Validate OpenAPI specification before processing
```

### Agent Customization

Each agent's behavior can be customized by editing its `.md` file:
- Modify system prompts
- Add/remove tool permissions
- Change output formats
- Adjust validation rules

## Testing

### Test with Sample Spec

The included `petstore-expanded.yaml` is a complete OpenAPI 3.0 spec perfect for testing:

```bash
python scripts/orchestrator.py ../petstore-expanded.yaml
```
-->
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
.claude/hooks/validate-markdown.sh < output/endpoints/<Reference_file_name>.md
```
<!--
## Common Issues and Solutions

### Issue: "OpenAPI spec file not found"

**Solution**: Ensure the spec path is correct and the file exists:
```bash
ls -la your-spec.yaml
```

### Issue: "Invalid YAML format"

**Solution**: Validate your YAML syntax:
```bash
python3 -c "import yaml; yaml.safe_load(open('your-spec.yaml'))"
```

### Issue: Agents not generating output

**Solution**: Check that agents have write permissions:
```bash
ls -la .claude/agents/
# All .md files should be readable
```

### Issue: Hooks not executing

**Solution**: Ensure hooks are executable:
```bash
chmod +x .claude/hooks/*.sh
```
-->
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
<!--
### Optimization Tips

1. **Batch similar endpoints**: Group related endpoints in spec
2. **Limit endpoint count**: For large APIs, process in chunks
3. **Cache intermediate results**: Parsed JSON can be reused
4. **Adjust parallelism**: Reduce workers if hitting rate limits
-->
## Extension Ideas

### Add More Agent Types

- **Code Sample Generator**: Generate SDK code examples in multiple languages
- **Postman Collection Generator**: Create Postman collections from spec
- **API Client Generator**: Generate client libraries
- **Test Suite Generator**: Create automated API tests

### Enhance Existing Agents

- **Parameter Documenter**: Add JSON Schema diagrams
- **Example Generator**: Include language-specific code samples
- **How-To Guide**: Add video tutorial scripts
- **Glossary**: Add links to external resources

### Additional Hooks

- **Pre-commit hook**: Validate spec before committing
- **Post-generation hook**: Deploy to documentation site
- **Notification hook**: Send Slack message on completion

## Best Practices

### Agent Design

1. **Single Responsibility**: Each agent has one clear purpose
2. **Minimal Tools**: Grant only necessary tool permissions
3. **Clear Contracts**: Define input/output formats explicitly
4. **Error Reporting**: Provide actionable error messages

### Orchestration

1. **Fail Fast**: Validate inputs before heavy processing
2. **Parallel Where Possible**: Run independent tasks concurrently
3. **Aggregate Errors**: Collect all errors, don't stop at first failure
4. **Progress Reporting**: Print clear status updates

### Hook Implementation

1. **Non-Blocking**: Hooks should be fast (<1s)
2. **Clear Output**: Use stderr for logging, stdout for results
3. **Graceful Degradation**: Warn but don't fail on minor issues
4. **Idempotent**: Safe to run multiple times

## Architecture Decisions

### Why Separate Agents for Reference and How-To?

**Decision**: Use separate Parameter Documenter and How-To Guide Generator agents

**Rationale**:
- Different audiences (reference users vs learners)
- Different writing styles (technical vs tutorial)
- Easier to parallelize
- Allows specialized prompting for each type

### Why JSON Intermediate Format?

**Decision**: Parser outputs JSON files instead of passing data directly

**Rationale**:
- Debugging visibility
- Allows re-running downstream agents without re-parsing
- Enables manual intervention if needed
- Better error isolation

### Why Parallel Execution?

**Decision**: Run per-endpoint agents in parallel using ThreadPoolExecutor

**Rationale**:
- Significant speed improvement (3-4x for 4 endpoints)
- Endpoints are independent (no shared state)
- Claude Code supports concurrent subagents
- Limits can be adjusted based on rate limits

## License

This is example code for educational purposes demonstrating Claude Code capabilities.
<!--
## Support

For issues or questions:
1. Check this README's troubleshooting section
2. Review agent system prompts in `.claude/agents/`
3. Examine hook implementations in `.claude/hooks/`
4. Check orchestrator logs for specific error messages
-->
