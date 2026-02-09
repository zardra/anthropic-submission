#!/bin/bash
# PostToolUse Hook: Validate Markdown Table Syntax
# This hook checks markdown files for properly formatted tables

set -e

# Read the tool use result from stdin
TOOL_DATA=$(cat)

# Extract the file path from WriteFile operations
FILE_PATH=$(echo "$TOOL_DATA" | grep -oP '"path":\s*"\K[^"]+' || echo "")

# Only validate markdown files
if [[ "$FILE_PATH" == *.md ]]; then
    echo "[HOOK] Validating markdown table syntax in $FILE_PATH..." >&2
    
    if [[ ! -f "$FILE_PATH" ]]; then
        echo "[HOOK] File not found, skipping validation" >&2
        echo "{\"approved\": true}"
        exit 0
    fi
    
    # Check for common table formatting issues
    ERRORS=()
    
    # Check 1: Tables should have header separator with pipes and dashes
    # Example: |------|------|
    if grep -q "|" "$FILE_PATH"; then
        # File contains pipes (likely has tables)
        
        # Check for tables with inconsistent column counts
        # This is a simplified check - counts pipes in consecutive lines
        TABLE_LINES=$(grep "^|.*|$" "$FILE_PATH" || true)
        
        if [[ -n "$TABLE_LINES" ]]; then
            echo "[HOOK] Found table content, validating structure..." >&2
            
            # Check for header separator line (should contain only |, -, and spaces)
            if ! echo "$TABLE_LINES" | grep -q "^|[-: |]*|$"; then
                ERRORS+=("Missing or malformed table header separator (should be |---|---|)")
            fi
            
            # Check for empty table cells (|| with no content)
            if echo "$TABLE_LINES" | grep -q "||"; then
                echo "[HOOK] ⚠️  Warning: Found empty table cells (||)" >&2
            fi
        fi
    fi
    
    # Check 2: Code blocks should be properly closed
    BACKTICK_COUNT=$(grep -o '```' "$FILE_PATH" | wc -l || echo "0")
    if (( BACKTICK_COUNT % 2 != 0 )); then
        ERRORS+=("Unclosed code block (odd number of \`\`\` markers)")
    fi
    
    # Check 3: Headers should have space after #
    if grep -qE '^#+[^ ]' "$FILE_PATH"; then
        echo "[HOOK] ⚠️  Warning: Headers should have space after # symbols" >&2
    fi
    
    # Report errors if any
    if [ ${#ERRORS[@]} -gt 0 ]; then
        echo "[HOOK] ❌ Validation errors found:" >&2
        for error in "${ERRORS[@]}"; do
            echo "  - $error" >&2
        done
        echo "{\"approved\": false, \"error\": \"Markdown validation failed: ${ERRORS[0]}\"}"
        exit 1
    fi
    
    echo "[HOOK] ✓ Markdown validation passed" >&2
fi

echo "{\"approved\": true}"
exit 0
