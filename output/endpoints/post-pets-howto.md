# How to Create Pets

## Overview

This guide walks you through creating new pet records in the Petstore API. You will learn how to construct valid requests, handle responses, work with optional fields like tags, create multiple pets efficiently, and handle errors gracefully.

**Endpoint**: `POST /pets`
**Use Case**: Adding new pet entries to the store's inventory

## Prerequisites

- API access credentials for the Petstore API
- Basic understanding of REST APIs and JSON
- `curl` installed on your system (or an equivalent HTTP client)
- The base URL for the API: `https://petstore.swagger.io/v2`

## Step-by-Step Guide

### Step 1: Prepare the Request Body

Every pet requires a `name` field. The `tag` field is optional and can be used to categorize pets.

The request body schema:

| Field  | Type   | Required | Description                     |
|--------|--------|----------|---------------------------------|
| `name` | string | Yes      | The name of the pet             |
| `tag`  | string | No       | An optional label to categorize the pet |

### Step 2: Send the Create Request

Submit a `POST` request with the pet data as a JSON body.

**Request:**

```bash
curl -X POST 'https://petstore.swagger.io/v2/pets' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "name": "Buddy"
  }'
```

**What's happening:**
- The `Content-Type: application/json` header tells the server the body is JSON
- The `Accept: application/json` header requests a JSON response
- The body contains the required `name` field

**Response (200):**

```json
{
  "id": 1,
  "name": "Buddy"
}
```

The server assigns a unique `id` (integer) to the newly created pet and returns the full pet object.

### Step 3: Capture the Pet ID

The `id` field in the response is a server-generated 64-bit integer that uniquely identifies the pet. Store this value for subsequent operations such as retrieving, updating, or deleting the pet.

```bash
PET_ID=$(curl -s -X POST 'https://petstore.swagger.io/v2/pets' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{"name": "Buddy"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "Created pet with ID: $PET_ID"
```

### Step 4: Verify the Pet Was Created

After creating a pet, confirm it exists by retrieving it with the assigned ID.

```bash
curl -X GET "https://petstore.swagger.io/v2/pets/${PET_ID}" \
  -H 'Accept: application/json'
```

**Expected Response (200):**

```json
{
  "id": 1,
  "name": "Buddy"
}
```

## Common Workflows

### Workflow 1: Minimal Pet Creation

The simplest case -- create a pet with only the required `name` field.

```bash
curl -X POST 'https://petstore.swagger.io/v2/pets' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "name": "Luna"
  }'
```

**Response:**

```json
{
  "id": 2,
  "name": "Luna"
}
```

This is useful when you need to register a pet quickly and do not have categorization information yet.

### Workflow 2: Creating a Pet with a Tag

Tags allow you to categorize pets for easier filtering and organization. Supply the optional `tag` field in the request body.

```bash
curl -X POST 'https://petstore.swagger.io/v2/pets' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "name": "Whiskers",
    "tag": "cat"
  }'
```

**Response:**

```json
{
  "id": 3,
  "name": "Whiskers",
  "tag": "cat"
}
```

Tags are returned in the response and can be used later when listing pets to filter by category.

### Workflow 3: Batch Creation of Multiple Pets

The API does not provide a dedicated batch endpoint, but you can create multiple pets sequentially using a shell loop. This is useful for seeding data or migrating records from another system.

```bash
#!/bin/bash

PETS='[
  {"name": "Buddy", "tag": "dog"},
  {"name": "Whiskers", "tag": "cat"},
  {"name": "Goldie", "tag": "fish"},
  {"name": "Tweety", "tag": "bird"},
  {"name": "Patches", "tag": "cat"}
]'

COUNT=$(echo "$PETS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")

for i in $(seq 0 $(($COUNT - 1))); do
  PET=$(echo "$PETS" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin)[$i]))")

  RESPONSE=$(curl -s -X POST 'https://petstore.swagger.io/v2/pets' \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -d "$PET")

  NAME=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('name','unknown'))")
  ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id','N/A'))")
  echo "Created pet '${NAME}' with ID: ${ID}"
done
```

**Expected Output:**

```
Created pet 'Buddy' with ID: 10
Created pet 'Whiskers' with ID: 11
Created pet 'Goldie' with ID: 12
Created pet 'Tweety' with ID: 13
Created pet 'Patches' with ID: 14
```

**Considerations for batch creation:**
- Add a brief delay between requests if the API enforces rate limiting
- Track created IDs so you can roll back on partial failure
- The API allows duplicates, so running the script twice will create duplicate entries

## Error Handling

### Common Errors and Solutions

#### Error: Missing Required Field

**Problem**: You receive an error when the `name` field is omitted from the request body.

**Cause**: The `name` field is required in the `NewPet` schema. The server rejects requests without it.

**Solution:**

```bash
# Wrong -- missing the required "name" field
curl -X POST 'https://petstore.swagger.io/v2/pets' \
  -H 'Content-Type: application/json' \
  -d '{
    "tag": "dog"
  }'

# Correct -- include the "name" field
curl -X POST 'https://petstore.swagger.io/v2/pets' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Buddy",
    "tag": "dog"
  }'
```

**Error Response:**

```json
{
  "code": 400,
  "message": "Missing required field: name"
}
```

#### Error: Invalid Content-Type

**Problem**: The server does not recognize the request body format.

**Cause**: The `Content-Type` header is missing or set to something other than `application/json`.

**Solution:**

```bash
# Wrong -- no Content-Type header
curl -X POST 'https://petstore.swagger.io/v2/pets' \
  -d '{"name": "Buddy"}'

# Correct -- explicitly set Content-Type to application/json
curl -X POST 'https://petstore.swagger.io/v2/pets' \
  -H 'Content-Type: application/json' \
  -d '{"name": "Buddy"}'
```

#### Error: Malformed JSON

**Problem**: The server returns an error because the request body is not valid JSON.

**Cause**: Syntax issues in the JSON payload such as trailing commas, unquoted keys, or single quotes instead of double quotes.

**Solution:**

```bash
# Wrong -- single quotes are not valid JSON
curl -X POST 'https://petstore.swagger.io/v2/pets' \
  -H 'Content-Type: application/json' \
  -d "{'name': 'Buddy'}"

# Wrong -- trailing comma after the last field
curl -X POST 'https://petstore.swagger.io/v2/pets' \
  -H 'Content-Type: application/json' \
  -d '{"name": "Buddy",}'

# Correct -- valid JSON with double quotes and no trailing comma
curl -X POST 'https://petstore.swagger.io/v2/pets' \
  -H 'Content-Type: application/json' \
  -d '{"name": "Buddy"}'
```

#### Error: Unexpected Server Error

**Problem**: The API returns an unexpected error with a non-200 status code.

**Error Response:**

```json
{
  "code": 500,
  "message": "Internal server error"
}
```

**Solution**: Implement retry logic with exponential backoff.

```bash
MAX_RETRIES=3
RETRY_DELAY=1

for ATTEMPT in $(seq 1 $MAX_RETRIES); do
  HTTP_CODE=$(curl -s -o /tmp/pet_response.json -w "%{http_code}" \
    -X POST 'https://petstore.swagger.io/v2/pets' \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -d '{"name": "Buddy"}')

  if [ "$HTTP_CODE" -eq 200 ]; then
    echo "Pet created successfully:"
    cat /tmp/pet_response.json
    break
  else
    echo "Attempt ${ATTEMPT} failed with HTTP ${HTTP_CODE}. Retrying in ${RETRY_DELAY}s..."
    sleep $RETRY_DELAY
    RETRY_DELAY=$((RETRY_DELAY * 2))
  fi

  if [ "$ATTEMPT" -eq "$MAX_RETRIES" ]; then
    echo "All retries exhausted. Last response:"
    cat /tmp/pet_response.json
    exit 1
  fi
done
```

## Best Practices

- **Always validate input before sending**: Confirm the `name` field is a non-empty string before making the request. This avoids unnecessary round trips to the server.
- **Set both Content-Type and Accept headers**: Explicitly specify `Content-Type: application/json` for the request body and `Accept: application/json` for the response format. Do not rely on server defaults.
- **Store the returned ID**: The `id` in the response is the only way to reference the pet in future API calls. Persist it immediately after creation.
- **Handle duplicates intentionally**: The API allows duplicate pet names. If uniqueness matters in your application, check for existing pets with `GET /pets` before creating a new one.
- **Use tags consistently**: Establish a tagging convention (e.g., lowercase species names like `dog`, `cat`, `fish`) and apply it uniformly across all pet records to make filtering reliable.
- **Implement error handling**: Always check the HTTP status code in the response. A `200` indicates success; any other code indicates an error with a `code` and `message` in the response body.
- **Add timeouts to requests**: Use `curl --max-time 10` to prevent requests from hanging indefinitely in production scripts.

## Next Steps

- **List all pets**: Use `GET /pets` to retrieve all pet records and verify your newly created entries appear in the list.
- **Retrieve a specific pet**: Use `GET /pets/{id}` with the ID returned from creation to fetch a single pet's details.
- **Delete a pet**: Use `DELETE /pets/{id}` to remove a pet record when it is no longer needed.
- **Build a management workflow**: Combine create, list, and delete operations into a complete pet lifecycle management script.
- **Add filtering by tag**: When listing pets, use query parameters to filter by tag values to find pets in specific categories.
