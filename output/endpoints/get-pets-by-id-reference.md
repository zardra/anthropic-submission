# GET /pets/{id}

## Overview

**Find pet by id** -- Returns a user based on a single ID, if the user does not have access to the pet.

| Property | Value |
|----------|-------|
| **HTTP Method** | `GET` |
| **Endpoint** | `/pets/{id}` |
| **Full URL** | `https://petstore.swagger.io/v2/pets/{id}` |

## Path Parameters

| Name | Type | Format | Required | Description |
|------|------|--------|----------|-------------|
| `id` | integer | int64 | Yes | ID of pet to fetch |

## Responses

### 200 -- Pet Response

Returns a `Pet` object representing the requested pet.

**Schema:**

| Field | Type | Format | Required | Description |
|-------|------|--------|----------|-------------|
| `id` | integer | int64 | Yes | The unique identifier for the pet |
| `name` | string | -- | Yes | The name of the pet |
| `tag` | string | -- | No | An optional tag for the pet |

**Example response:**

```json
{
  "id": 1,
  "name": "Fido",
  "tag": "dog"
}
```

### Default -- Unexpected Error

Returned when an unexpected error occurs on the server.

**Schema (`Error`):**

| Field | Type | Format | Required | Description |
|-------|------|--------|----------|-------------|
| `code` | integer | int32 | Yes | The error code |
| `message` | string | -- | Yes | A human-readable error message |

**Example response:**

```json
{
  "code": 404,
  "message": "Pet not found"
}
```

## Example Request

```bash
curl -X GET "https://petstore.swagger.io/v2/pets/1" \
  -H "Accept: application/json"
```

## Referenced Schemas

- `Pet`
- `NewPet`
- `Error`
