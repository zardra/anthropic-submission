# How to Fetch a Pet by ID

## Overview

This guide walks you through retrieving a single pet resource from the Petstore API using its unique identifier. You will learn how to construct the request, interpret the response, handle common error scenarios, and integrate this endpoint into broader application workflows.

**Endpoint**: `GET /pets/{id}`
**Base URL**: `https://petstore.swagger.io/v2`
**Use Case**: Retrieve the full details of a specific pet when you already know its numeric ID.

## Prerequisites

- API access to the Petstore service at `https://petstore.swagger.io/v2`
- A command-line tool such as `curl` (or an HTTP client library in your language of choice)
- Basic understanding of REST APIs and HTTP methods
- A valid pet ID (integer) -- you can obtain one by listing pets via `GET /pets`

## Step-by-Step Guide

### Step 1: Identify the Pet ID

Before fetching a pet, you need its numeric ID. If you do not already have one, retrieve the list of available pets first.

```bash
curl -s -X GET 'https://petstore.swagger.io/v2/pets?limit=5' \
  -H 'Accept: application/json'
```

From the response, note the `id` field of the pet you want to look up. For this guide, we will use pet ID `42`.

### Step 2: Send the GET Request

Construct a `GET` request with the pet ID substituted into the URL path.

**Request:**

```bash
curl -s -X GET 'https://petstore.swagger.io/v2/pets/42' \
  -H 'Accept: application/json'
```

**What's happening:**

- The `{id}` path parameter is replaced with the integer value `42`.
- The `Accept` header tells the server you expect a JSON response.
- No request body is needed because this is a `GET` request.

### Step 3: Interpret the Response

A successful request returns HTTP status `200` with a JSON object representing the pet.

**Response:**

```json
{
  "id": 42,
  "name": "Fido",
  "tag": "dog"
}
```

**Response fields:**

| Field  | Type    | Required | Description                          |
|--------|---------|----------|--------------------------------------|
| `id`   | integer | Yes      | The unique identifier of the pet     |
| `name` | string  | Yes      | The name of the pet                  |
| `tag`  | string  | No       | An optional classification tag       |

### Step 4: Use the Data in Your Application

Once you have the response, parse the JSON and use it as needed. For example, in a shell script:

```bash
RESPONSE=$(curl -s -X GET 'https://petstore.swagger.io/v2/pets/42' \
  -H 'Accept: application/json')

PET_NAME=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['name'])")
echo "Pet name: $PET_NAME"
```

## Common Workflows

### Workflow 1: Verify a Newly Created Pet

After creating a pet with `POST /pets`, confirm it was saved correctly by fetching it back.

1. **Create the pet**

   ```bash
   curl -s -X POST 'https://petstore.swagger.io/v2/pets' \
     -H 'Content-Type: application/json' \
     -d '{"name": "Bella", "tag": "cat"}'
   ```

   Note the `id` returned in the response (e.g., `107`).

2. **Fetch the pet by its ID to verify**

   ```bash
   curl -s -X GET 'https://petstore.swagger.io/v2/pets/107' \
     -H 'Accept: application/json'
   ```

3. **Compare the returned data against what you submitted**

   - Confirm `name` is `"Bella"` and `tag` is `"cat"`.
   - If the values do not match, investigate potential data transformation or encoding issues.

### Workflow 2: Display Pet Details in a User Interface

When building a pet detail page, fetch the pet on page load and handle the loading/error states.

1. **Request the pet data when the page loads**

   ```bash
   curl -s -o response.json -w "%{http_code}" \
     -X GET 'https://petstore.swagger.io/v2/pets/42' \
     -H 'Accept: application/json'
   ```

2. **Check the HTTP status code**

   ```bash
   HTTP_STATUS=$(curl -s -o response.json -w "%{http_code}" \
     -X GET 'https://petstore.swagger.io/v2/pets/42' \
     -H 'Accept: application/json')

   if [ "$HTTP_STATUS" -eq 200 ]; then
     echo "Pet found:"
     cat response.json
   elif [ "$HTTP_STATUS" -eq 404 ]; then
     echo "Pet not found. Show a friendly 'not found' message to the user."
   else
     echo "Unexpected error (HTTP $HTTP_STATUS)."
   fi
   ```

3. **Render the pet details or an appropriate error state in your UI**

### Workflow 3: Pre-Delete Confirmation

Before deleting a pet, fetch its details so you can show a confirmation dialog with the pet's name.

1. **Fetch the pet details**

   ```bash
   curl -s -X GET 'https://petstore.swagger.io/v2/pets/42' \
     -H 'Accept: application/json'
   ```

2. **Display the details and ask the user to confirm**

   ```
   Are you sure you want to delete "Fido" (ID: 42)? [y/N]
   ```

3. **If confirmed, delete the pet**

   ```bash
   curl -s -X DELETE 'https://petstore.swagger.io/v2/pets/42'
   ```

## Error Handling

### Error: Pet Not Found (404)

**Problem**: You receive a `404` status or an error response when the pet ID does not exist in the system.

**Cause**: The pet with the specified ID has never been created, or it was previously deleted.

**Example error response:**

```json
{
  "code": 404,
  "message": "Pet not found"
}
```

**Solution:**

```bash
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -X GET 'https://petstore.swagger.io/v2/pets/99999' \
  -H 'Accept: application/json')

if [ "$HTTP_STATUS" -eq 404 ]; then
  echo "Pet with ID 99999 does not exist."
  echo "Verify the ID by listing available pets:"
  curl -s -X GET 'https://petstore.swagger.io/v2/pets?limit=10' \
    -H 'Accept: application/json'
fi
```

**Prevention**: Always validate that the pet ID exists (e.g., from a previous list response) before attempting to fetch it.

### Error: Invalid ID Format (400)

**Problem**: You receive a `400` status when the ID is not a valid integer.

**Cause**: The `id` path parameter must be an integer (`int64`). Passing a string, negative number, floating-point value, or extremely large number will be rejected.

**Examples:**

```bash
# Wrong -- passing a string instead of an integer
curl -s -X GET 'https://petstore.swagger.io/v2/pets/fido' \
  -H 'Accept: application/json'

# Wrong -- passing a floating-point value
curl -s -X GET 'https://petstore.swagger.io/v2/pets/42.5' \
  -H 'Accept: application/json'

# Correct -- passing a valid integer
curl -s -X GET 'https://petstore.swagger.io/v2/pets/42' \
  -H 'Accept: application/json'
```

**Solution**: Validate the ID on the client side before making the request.

```bash
PET_ID="fido"

if [[ "$PET_ID" =~ ^[0-9]+$ ]]; then
  curl -s -X GET "https://petstore.swagger.io/v2/pets/$PET_ID" \
    -H 'Accept: application/json'
else
  echo "Error: Pet ID must be a positive integer. Got: '$PET_ID'"
fi
```

### Error: Unexpected Server Error (5xx)

**Problem**: The server returns a `500` or other `5xx` status code.

**Cause**: An internal server issue unrelated to your request.

**Example error response:**

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

for i in $(seq 1 $MAX_RETRIES); do
  HTTP_STATUS=$(curl -s -o response.json -w "%{http_code}" \
    -X GET 'https://petstore.swagger.io/v2/pets/42' \
    -H 'Accept: application/json')

  if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "Success:"
    cat response.json
    break
  elif [ "$HTTP_STATUS" -ge 500 ]; then
    echo "Server error (attempt $i/$MAX_RETRIES). Retrying in ${RETRY_DELAY}s..."
    sleep $RETRY_DELAY
    RETRY_DELAY=$((RETRY_DELAY * 2))
  else
    echo "Client error (HTTP $HTTP_STATUS). Not retrying."
    cat response.json
    break
  fi
done
```

## Best Practices

- **Validate IDs client-side**: Always confirm the ID is a positive integer before sending the request. This avoids unnecessary network round-trips for obviously invalid inputs.
- **Handle all response codes**: Do not assume every request will succeed. Check for `200`, `404`, `400`, and `5xx` responses and handle each case appropriately in your application logic.
- **Cache responses when appropriate**: If pet data does not change frequently, cache the response for a short period (e.g., 30-60 seconds) to reduce API calls and improve performance. Use the pet ID as the cache key.
- **Use timeouts**: Set a connection and response timeout on your HTTP client to avoid hanging indefinitely if the server is slow or unresponsive.

  ```bash
  curl -s --connect-timeout 5 --max-time 10 \
    -X GET 'https://petstore.swagger.io/v2/pets/42' \
    -H 'Accept: application/json'
  ```

- **Log errors with context**: When logging a failed request, include the pet ID, HTTP status, and response body so you can diagnose issues quickly.
- **Do not expose raw error responses to end users**: Translate API error messages into user-friendly language in your application's UI layer.

## Next Steps

- **List all pets**: Use `GET /pets` to browse available pets and discover valid IDs. See [get-pets-reference.md](get-pets-reference.md).
- **Create a new pet**: Use `POST /pets` to add a pet to the store. See [post-pets-howto.md](post-pets-howto.md).
- **Delete a pet**: Use `DELETE /pets/{id}` to remove a pet once it is no longer needed. See [delete-pets-by-id-howto.md](delete-pets-by-id-howto.md).
- **Build a full CRUD workflow**: Combine create, read, and delete operations to build a complete pet management feature in your application.
