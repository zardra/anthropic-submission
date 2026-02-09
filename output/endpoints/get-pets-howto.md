# How-To Guide: Listing and Finding Pets

## Overview

The `GET /pets` endpoint returns all pets from the system that the user has access to. It supports filtering by tags and limiting the number of results, making it the primary way to browse, search, and retrieve pet records from the Petstore API.

This guide walks you through common usage patterns -- from retrieving a simple list of all pets to building filtered queries that return exactly the data you need.

## Prerequisites

Before you begin, make sure you have:

- **API access**: A working connection to the Petstore API at `https://petstore.swagger.io/v2`
- **curl**: Installed on your system (or an equivalent HTTP client)
- **At least one pet record**: The database should contain pet entries. If it is empty, use the `POST /pets` endpoint to create a few records first

## Step-by-Step Guide

### Step 1: Retrieve a Basic List of All Pets

The simplest call requires no parameters at all. It returns every pet the user has access to.

```bash
curl -X GET "https://petstore.swagger.io/v2/pets" \
  -H "Accept: application/json"
```

**Expected response** (HTTP 200):

```json
[
  {
    "id": 1,
    "name": "Luna",
    "tag": "dog"
  },
  {
    "id": 2,
    "name": "Whiskers",
    "tag": "cat"
  },
  {
    "id": 3,
    "name": "Goldie",
    "tag": "fish"
  }
]
```

Each pet object in the response contains:

| Field  | Type    | Description                          |
|--------|---------|--------------------------------------|
| `id`   | integer | Unique identifier for the pet        |
| `name` | string  | Name of the pet                      |
| `tag`  | string  | Optional category or label           |

### Step 2: Filter Pets by Tags

Use the `tags` query parameter to retrieve only pets matching one or more tags. This is useful when your database contains many records and you want a specific subset.

**Filter by a single tag:**

```bash
curl -X GET "https://petstore.swagger.io/v2/pets?tags=dog" \
  -H "Accept: application/json"
```

**Expected response** (HTTP 200):

```json
[
  {
    "id": 1,
    "name": "Luna",
    "tag": "dog"
  },
  {
    "id": 7,
    "name": "Barkley",
    "tag": "dog"
  }
]
```

**Filter by multiple tags:**

Pass the `tags` parameter multiple times to match pets with any of the specified tags:

```bash
curl -X GET "https://petstore.swagger.io/v2/pets?tags=dog&tags=cat" \
  -H "Accept: application/json"
```

**Expected response** (HTTP 200):

```json
[
  {
    "id": 1,
    "name": "Luna",
    "tag": "dog"
  },
  {
    "id": 2,
    "name": "Whiskers",
    "tag": "cat"
  },
  {
    "id": 7,
    "name": "Barkley",
    "tag": "dog"
  }
]
```

### Step 3: Limit the Number of Results

Use the `limit` query parameter to control how many pets are returned. This is essential for pagination and for keeping response payloads small.

```bash
curl -X GET "https://petstore.swagger.io/v2/pets?limit=2" \
  -H "Accept: application/json"
```

**Expected response** (HTTP 200):

```json
[
  {
    "id": 1,
    "name": "Luna",
    "tag": "dog"
  },
  {
    "id": 2,
    "name": "Whiskers",
    "tag": "cat"
  }
]
```

### Step 4: Combine Filters and Limits

You can combine `tags` and `limit` in a single request to get a constrained, filtered result set:

```bash
curl -X GET "https://petstore.swagger.io/v2/pets?tags=cat&limit=5" \
  -H "Accept: application/json"
```

**Expected response** (HTTP 200):

```json
[
  {
    "id": 2,
    "name": "Whiskers",
    "tag": "cat"
  },
  {
    "id": 9,
    "name": "Mittens",
    "tag": "cat"
  }
]
```

## Common Workflows

### Workflow 1: Building a Pet Directory Page

When building a UI that displays pets in pages, use `limit` to fetch a fixed batch size:

```bash
# Fetch first page (5 pets)
curl -X GET "https://petstore.swagger.io/v2/pets?limit=5" \
  -H "Accept: application/json"

# Fetch second page (next 5 pets, adjusting offset as needed)
curl -X GET "https://petstore.swagger.io/v2/pets?limit=5" \
  -H "Accept: application/json"
```

Store the `id` of the last pet returned and use it to track your position across pages.

### Workflow 2: Searching for Pets by Category

If your application allows users to browse pets by type, map your UI categories to tags:

```bash
# User selects "Dogs" in the sidebar
curl -X GET "https://petstore.swagger.io/v2/pets?tags=dog&limit=10" \
  -H "Accept: application/json"

# User selects "Small Animals"
curl -X GET "https://petstore.swagger.io/v2/pets?tags=hamster&tags=rabbit&tags=guinea-pig&limit=10" \
  -H "Accept: application/json"
```

### Workflow 3: Fetching a Pet and Then Its Details

First list pets to find one, then fetch its full record by ID:

```bash
# Step 1: List available pets
curl -X GET "https://petstore.swagger.io/v2/pets?tags=dog&limit=3" \
  -H "Accept: application/json"

# Step 2: Use the id from the response to get full details
curl -X GET "https://petstore.swagger.io/v2/pets/1" \
  -H "Accept: application/json"
```

## Error Handling

### Error 1: Unexpected Server Error (HTTP 500)

**Cause**: The server encountered an internal problem while processing your request.

**Example response**:

```json
{
  "code": 500,
  "message": "Internal server error: unable to query pet database"
}
```

**Solution**:

1. Wait a few seconds and retry the request
2. If the error persists, check the API status page or contact the API provider
3. Implement exponential backoff in your client code:

```bash
# Simple retry after a delay
sleep 2
curl -X GET "https://petstore.swagger.io/v2/pets" \
  -H "Accept: application/json"
```

### Error 2: Invalid Query Parameter Value (HTTP 400)

**Cause**: The `limit` parameter was given a non-integer value, a negative number, or an excessively large value.

**Example request that triggers the error**:

```bash
curl -X GET "https://petstore.swagger.io/v2/pets?limit=abc" \
  -H "Accept: application/json"
```

**Example response**:

```json
{
  "code": 400,
  "message": "Invalid value for parameter 'limit': expected a positive integer"
}
```

**Solution**:

1. Verify that `limit` is a positive 32-bit integer (1 to 2,147,483,647)
2. Remove the parameter entirely if you do not need to restrict the count
3. Double-check that URL encoding has not corrupted your query string

### Error 3: Request Timeout or Network Failure

**Cause**: The server did not respond within the expected time, often due to network issues or an overloaded server.

**Example symptom**:

```bash
curl: (28) Operation timed out after 30000 milliseconds
```

**Solution**:

1. Verify your network connectivity
2. Set an explicit timeout and retry:

```bash
curl -X GET "https://petstore.swagger.io/v2/pets?limit=10" \
  -H "Accept: application/json" \
  --connect-timeout 10 \
  --max-time 30
```

3. Reduce the `limit` to request fewer records and decrease server processing time
4. If querying with many tags, try reducing the number of tags per request

## Best Practices

- **Always set a `limit`**: Avoid unbounded queries in production. Even if you want all records, set a reasonable upper bound (e.g., `limit=100`) and paginate through the results to prevent large payloads from degrading performance.

- **Use tags for targeted queries**: Rather than fetching all pets and filtering client-side, use the `tags` parameter to let the server do the filtering. This reduces bandwidth and speeds up response times.

- **Handle empty results gracefully**: A `200` response with an empty array (`[]`) is valid. Your application should treat this as "no matching pets found" rather than an error condition.

- **Cache responses when appropriate**: If the pet data does not change frequently, cache `GET /pets` responses on the client side for a short duration (e.g., 30-60 seconds) to reduce API calls.

- **Validate parameters before sending**: Ensure `limit` is a positive integer and tags are non-empty strings before making the request. This avoids unnecessary round trips that will fail with a `400` error.

## Next Steps

Now that you know how to list and find pets, consider exploring these related operations:

- **Get a single pet**: Use `GET /pets/{id}` to retrieve the full details of a specific pet by its ID
- **Add a new pet**: Use `POST /pets` to create new pet records in the system
- **Delete a pet**: Use `DELETE /pets/{id}` to remove a pet from the database
- **Build automated workflows**: Combine listing with creation and deletion to build batch management scripts for your pet inventory
