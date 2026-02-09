#!/bin/bash
# PostToolUse Hook: Lint and Format Documentation
# This hook runs after documentation generation to ensure consistent formatting

set -e

TOOL_DATA=$(cat)
FILE_PATH=$(echo "$TOOL_DATA" | grep -oP '"path":\s*"\K[^"]+' || echo "")

# Only process markdown files in the output directory
if [[ "$FILE_PATH" == */output/*.md ]]; then
    echo "[HOOK] Formatting and linting $FILE_PATH..." >&2
    
    if [[ ! -f "$FILE_PATH" ]]; then
        echo "{\"approved\": true}"
        exit 0
    fi
    
    # Create a temporary file for formatting
    TEMP_FILE="${FILE_PATH}.tmp"
    
    # Format the file
    # 1. Ensure consistent line endings
    # 2. Remove trailing whitespace
    # 3. Ensure file ends with newline
    # 4. Fix multiple consecutive blank lines (max 2)
    
    sed -e 's/[[:space:]]*$//' "$FILE_PATH" | \
    awk 'BEGIN{bl=0} /^$/{bl++; if(bl<=2) print; next} {bl=0; print}' > "$TEMP_FILE"
    
    # Ensure file ends with newline
    if [ -n "$(tail -c1 "$TEMP_FILE")" ]; then
        echo >> "$TEMP_FILE"
    fi
    
    # Replace original with formatted version
    mv "$TEMP_FILE" "$FILE_PATH"
    
    # Lint checks (non-blocking, just warnings)
    WARNINGS=()
    
    # Check for very long lines (>120 chars, excluding code blocks and tables)
    LONG_LINES=$(awk '!/^```/ && !/^\|/ && length > 120 {count++} END {print count+0}' "$FILE_PATH")
    if [ "$LONG_LINES" -gt 0 ]; then
        WARNINGS+=("$LONG_LINES lines exceed 120 characters")
    fi
    
    # Check for TODO or FIXME comments
    if grep -qi "TODO\|FIXME" "$FILE_PATH"; then
        WARNINGS+=("Contains TODO or FIXME markers")
    fi
    
    # Report warnings
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo "[HOOK] ⚠️  Lint warnings:" >&2
        for warning in "${WARNINGS[@]}"; do
            echo "  - $warning" >&2
        done
    else
        echo "[HOOK] ✓ Formatting complete, no lint warnings" >&2
    fi
fi

echo "{\"approved\": true}"
exit 0
