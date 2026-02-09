# POST /pets

## Overview

**Operation ID**: `addPet`

**Base URL**: `https://petstore.swagger.io/v2`

**Full URL**: `https://petstore.swagger.io/v2/pets`

Creates a new pet in the store. Duplicates are allowed.

## Request

### Path Parameters

None

### Query Parameters

None

### Request Body

**Content-Type**: `application/json`

**Required**: Yes

**Description**: Pet to add to the store

**Schema**: `NewPet`

```json
{
  "name": "string",
  "tag": "string"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | The name of the pet |
| tag | string | No | An optional tag for categorizing the pet |

## Responses

### 200 OK

pet response

Returns the created Pet object with a server-assigned identifier.

**Content-Type**: `application/json`

**Schema**: `Pet` (extends `NewPet` via `allOf`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer (int64) | Yes | Unique identifier assigned by the server |
| name | string | Yes | The name of the pet |
| tag | string | No | An optional tag for categorizing the pet |

**Example Response**:

```json
{
  "id": 12345,
  "name": "Fido",
  "tag": "dog"
}
```

### Default (Error)

unexpected error

Returned when an unexpected error occurs during pet creation.

**Content-Type**: `application/json`

**Schema**: `Error`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| code | integer (int32) | Yes | Machine-readable error code |
| message | string | Yes | Human-readable error message |

**Example Response**:

```json
{
  "code": 500,
  "message": "Internal server error"
}
```

## Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Pet successfully created and returned |
| default | Unexpected error occurred |

## Referenced Schemas

- `NewPet` -- Request body schema (name, tag)
- `Pet` -- Response schema, extends NewPet with an id field (allOf composition)
- `Error` -- Error response schema (code, message)
