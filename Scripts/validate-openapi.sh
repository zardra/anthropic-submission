#!/bin/bash
# PreToolUse Hook: Validate OpenAPI Specification
# This hook validates the OpenAPI spec before any processing begins

set -e

# Read the tool use data from stdin
TOOL_DATA=$(cat)

# Extract the file being read (if it's a Read tool for the OpenAPI spec)
FILE_PATH=$(echo "$TOOL_DATA" | grep -oP '"path":\s*"\K[^"]+' || echo "")

# Check if this is reading the OpenAPI spec
if [[ "$FILE_PATH" == *"petstore-expanded.yaml"* ]] || [[ "$FILE_PATH" == *".yaml"* ]] || [[ "$FILE_PATH" == *".yml"* ]]; then
    echo "[HOOK] Validating OpenAPI specification..." >&2
    
    # Check if the file exists
    if [[ ! -f "$FILE_PATH" ]]; then
        echo "{\"approved\": false, \"error\": \"OpenAPI spec file not found: $FILE_PATH\"}"
        exit 1
    fi
    
    # Basic YAML validation - check if it can be parsed
    if ! python3 -c "import yaml; yaml.safe_load(open('$FILE_PATH'))" 2>/dev/null; then
        echo "{\"approved\": false, \"error\": \"Invalid YAML format in OpenAPI spec\"}"
        exit 1
    fi
    
    # Validate that it's an OpenAPI 3.0 spec
    OPENAPI_VERSION=$(python3 -c "import yaml; print(yaml.safe_load(open('$FILE_PATH')).get('openapi', ''))" 2>/dev/null)
    
    if [[ ! "$OPENAPI_VERSION" =~ ^3\. ]]; then
        echo "{\"approved\": false, \"error\": \"Not a valid OpenAPI 3.x specification. Found version: $OPENAPI_VERSION\"}"
        exit 1
    fi
    
    # Check for required fields
    HAS_PATHS=$(python3 -c "import yaml; spec=yaml.safe_load(open('$FILE_PATH')); print('paths' in spec)" 2>/dev/null)
    HAS_INFO=$(python3 -c "import yaml; spec=yaml.safe_load(open('$FILE_PATH')); print('info' in spec)" 2>/dev/null)
    
    if [[ "$HAS_PATHS" != "True" ]] || [[ "$HAS_INFO" != "True" ]]; then
        echo "{\"approved\": false, \"error\": \"OpenAPI spec missing required fields (paths or info)\"}"
        exit 1
    fi
    
    echo "[HOOK] ✓ OpenAPI specification is valid" >&2
fi

# Approve the tool use
echo "{\"approved\": true}"
exit 0
