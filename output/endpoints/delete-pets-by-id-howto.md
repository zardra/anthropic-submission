# How to Delete a Pet

## Overview

This guide walks you through deleting a pet resource from the Petstore API using the `DELETE /pets/{id}` endpoint. You will learn how to safely remove a pet record by its unique identifier, verify the deletion was successful, and handle common error scenarios.

**Endpoint**: `DELETE /pets/{id}`
**Use Case**: Permanently removing a pet record from the system when it is no longer needed, such as after adoption, transfer, or data cleanup.

## Prerequisites

- API access credentials for the Petstore API
- Base URL: `https://petstore.swagger.io/v2`
- Basic understanding of REST APIs and HTTP methods
- A valid pet `id` (integer) for the pet you want to delete
- `curl` installed on your system (or an equivalent HTTP client)
- The pet must already exist in the system before it can be deleted

## Step-by-Step Guide

### Step 1: Identify the Pet to Delete

Before deleting a pet, confirm the pet exists and retrieve its details to verify you are targeting the correct record.

**Request:**

```bash
curl -X GET 'https://petstore.swagger.io/v2/pets/123' \
  -H 'Accept: application/json'
```

**What's happening:**
- The `GET /pets/{id}` endpoint retrieves the pet record matching the provided ID
- This confirmation step prevents accidental deletion of the wrong resource

**Response:**

```json
{
  "id": 123,
  "name": "Max",
  "tag": "dog"
}
```

Review the response to confirm this is the pet you intend to delete. Take note of the `name` and `tag` fields so you can verify the correct record is being removed.

### Step 2: Delete the Pet

Once you have confirmed the pet's identity, issue the delete request.

**Request:**

```bash
curl -X DELETE 'https://petstore.swagger.io/v2/pets/123' \
  -H 'Accept: application/json' \
  -v
```

**What's happening:**
- The `-X DELETE` flag specifies the HTTP DELETE method
- The `{id}` path parameter (here `123`) identifies which pet to remove
- The `-v` flag enables verbose output so you can inspect the HTTP status code in the response headers

**Response:**

A successful deletion returns an HTTP `204 No Content` status with an empty response body:

```
< HTTP/1.1 204 No Content
```

The `204` status code confirms the pet was successfully deleted. There is no response body because the resource no longer exists.

### Step 3: Verify the Deletion

After deletion, confirm the pet has been removed by attempting to retrieve it again.

**Request:**

```bash
curl -X GET 'https://petstore.swagger.io/v2/pets/123' \
  -H 'Accept: application/json' \
  -w "\nHTTP Status: %{http_code}\n"
```

**What's happening:**
- The `-w` flag appends the HTTP status code to the output for easy verification
- A `404 Not Found` or error response confirms the pet no longer exists

**Expected Response:**

```json
{
  "code": 404,
  "message": "Pet not found"
}
```

If you receive a `404` response, the deletion was successful. If the pet data is still returned, the deletion may not have been processed -- retry the `DELETE` request.

## Common Workflows

### Workflow 1: Verify-Then-Delete

This is the safest approach for production systems. It ensures you never delete a pet without first confirming its identity.

1. **Retrieve the pet to confirm its identity**

   ```bash
   curl -s -X GET 'https://petstore.swagger.io/v2/pets/456' \
     -H 'Accept: application/json' \
     -w "\nHTTP Status: %{http_code}\n"
   ```

   Inspect the response. If the status code is `200` and the pet details match your expectations, proceed.

2. **Store the pet details for your records (optional)**

   ```bash
   curl -s -X GET 'https://petstore.swagger.io/v2/pets/456' \
     -H 'Accept: application/json' > pet-456-backup.json
   ```

   Saving a local backup allows you to restore the record later if the deletion was a mistake.

3. **Delete the pet**

   ```bash
   curl -s -X DELETE 'https://petstore.swagger.io/v2/pets/456' \
     -H 'Accept: application/json' \
     -w "\nHTTP Status: %{http_code}\n"
   ```

   Confirm you receive a `204` status code.

4. **Verify the deletion**

   ```bash
   curl -s -X GET 'https://petstore.swagger.io/v2/pets/456' \
     -H 'Accept: application/json' \
     -w "\nHTTP Status: %{http_code}\n"
   ```

   A `404` response confirms the pet has been removed.

### Workflow 2: Bulk Cleanup

When you need to remove multiple pets -- for example, clearing test data or removing all pets with a specific tag -- combine the list and delete endpoints in a scripted workflow.

1. **List all pets matching a filter**

   ```bash
   curl -s -X GET 'https://petstore.swagger.io/v2/pets?tags=temporary&limit=50' \
     -H 'Accept: application/json'
   ```

2. **Extract the IDs and delete each pet**

   ```bash
   # Parse the pet IDs from the JSON response and delete each one
   for PET_ID in $(curl -s -X GET 'https://petstore.swagger.io/v2/pets?tags=temporary&limit=50' \
     -H 'Accept: application/json' | python3 -c "
   import sys, json
   pets = json.load(sys.stdin)
   for pet in pets:
       print(pet['id'])
   "); do
     echo "Deleting pet $PET_ID..."
     HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
       -X DELETE "https://petstore.swagger.io/v2/pets/$PET_ID" \
       -H 'Accept: application/json')
     if [ "$HTTP_STATUS" -eq 204 ]; then
       echo "  Successfully deleted pet $PET_ID"
     else
       echo "  Failed to delete pet $PET_ID (HTTP $HTTP_STATUS)"
     fi
   done
   ```

3. **Verify the cleanup**

   ```bash
   curl -s -X GET 'https://petstore.swagger.io/v2/pets?tags=temporary&limit=50' \
     -H 'Accept: application/json'
   ```

   An empty array `[]` confirms all targeted pets have been removed.

## Error Handling

### Common Errors and Solutions

#### Error: Pet Not Found (404)

**Problem**: You attempt to delete a pet that does not exist.

```bash
curl -X DELETE 'https://petstore.swagger.io/v2/pets/99999' \
  -H 'Accept: application/json' \
  -v
```

**Response:**

```json
{
  "code": 404,
  "message": "Pet not found"
}
```

**Cause**: The pet ID does not correspond to any existing record. The pet may have already been deleted, or the ID may be incorrect.

**Solution:**
- Verify the pet ID by listing pets with `GET /pets` first
- If the pet was already deleted, treat this as a successful outcome (idempotent delete pattern)
- Check that you are using the correct base URL and environment

#### Error: Invalid ID Format

**Problem**: The `id` parameter is not a valid integer.

```bash
# Wrong -- id must be an integer, not a string
curl -X DELETE 'https://petstore.swagger.io/v2/pets/abc' \
  -H 'Accept: application/json'
```

**Response:**

```json
{
  "code": 400,
  "message": "Invalid ID format: id must be a 64-bit integer"
}
```

**Cause**: The `id` path parameter requires a value of type `integer` with `int64` format. Strings, floats, or negative numbers are not valid.

**Solution:**

```bash
# Correct -- use a valid integer ID
curl -X DELETE 'https://petstore.swagger.io/v2/pets/123' \
  -H 'Accept: application/json'
```

#### Error: Unexpected Server Error

**Problem**: The API returns a `500` or other unexpected error.

**Response:**

```json
{
  "code": 500,
  "message": "Internal server error"
}
```

**Cause**: A transient server-side issue prevented the deletion from being processed.

**Solution:**
- Wait a few seconds and retry the request
- Implement exponential backoff for automated workflows:

```bash
MAX_RETRIES=3
RETRY_DELAY=2

for i in $(seq 1 $MAX_RETRIES); do
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X DELETE 'https://petstore.swagger.io/v2/pets/123' \
    -H 'Accept: application/json')
  if [ "$HTTP_STATUS" -eq 204 ]; then
    echo "Pet deleted successfully."
    break
  fi
  echo "Attempt $i failed (HTTP $HTTP_STATUS). Retrying in ${RETRY_DELAY}s..."
  sleep $RETRY_DELAY
  RETRY_DELAY=$((RETRY_DELAY * 2))
done
```

## Best Practices

- **Always verify before deleting**: Use `GET /pets/{id}` to confirm the pet's identity before issuing a `DELETE` request, especially in production environments.
- **Treat deletes as idempotent**: If a `DELETE` request returns `404`, the resource is already gone. Your application logic should treat this as a success rather than a failure.
- **Back up before bulk operations**: When deleting multiple pets, save their details to a local file first so you can recreate them if needed.
- **Use proper error handling**: Always check the HTTP status code of the response. Do not assume success without verifying the `204` status.
- **Log deletions for auditing**: Maintain a log of deleted pet IDs, timestamps, and the user or process that initiated the deletion.
- **Avoid hardcoding IDs**: In automated workflows, dynamically retrieve pet IDs from the `GET /pets` endpoint rather than hardcoding them into scripts.
- **Implement retry logic**: For critical deletions in production, use exponential backoff to handle transient server failures gracefully.

## Next Steps

- **List remaining pets**: Use `GET /pets` to view the current set of pet records after deletion. See the [List Pets how-to guide](get-pets-howto.md).
- **Retrieve a specific pet**: Use `GET /pets/{id}` to look up an individual pet by its ID. See the [Find Pet by ID how-to guide](get-pets-by-id-howto.md).
- **Add a new pet**: Use `POST /pets` to create a new pet record, which may be useful if you need to replace a deleted pet. See the [Create Pet how-to guide](post-pets-howto.md).
- **API reference**: Consult the [Delete Pet reference documentation](delete-pets-by-id-reference.md) for full parameter and response schema details.
