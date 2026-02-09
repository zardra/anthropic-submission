# GET /pets

## Overview

| Property    | Value                                                        |
|-------------|--------------------------------------------------------------|
| **Method**  | `GET`                                                        |
| **Path**    | `/pets`                                                      |
| **URL**     | `https://petstore.swagger.io/v2/pets`                        |
| **Summary** | findPets                                                     |

Returns all pets from the system that the user has access to.

---

## Query Parameters

| Name   | Type            | Required | Description                        |
|--------|-----------------|----------|------------------------------------|
| `tags` | array\<string\> | No       | Tags to filter by                  |
| `limit`| integer (int32) | No       | Maximum number of results to return|

### Parameter Details

#### `tags`

An array of string values used to filter the returned pets. When multiple tags are provided, pets matching any of the supplied tags are included in the response. Pass multiple values by repeating the query parameter:

```
GET /pets?tags=indoor&tags=friendly
```

#### `limit`

A 32-bit integer that caps the number of pet records returned. When omitted, the server returns all matching results.

```
GET /pets?limit=10
```

---

## Response Schemas

### 200 -- Pet Response

Returns an array of Pet objects.

**Schema:** `array<Pet>`

Each element in the array is a **Pet** object with the following properties:

| Name   | Type            | Required | Description                        |
|--------|-----------------|----------|------------------------------------|
| `id`   | integer (int64) | Yes      | Unique identifier for the pet      |
| `name` | string          | Yes      | Name of the pet                    |
| `tag`  | string          | No       | Optional tag associated with the pet|

**Example Response:**

```json
[
  {
    "id": 1,
    "name": "Luna",
    "tag": "cat"
  },
  {
    "id": 2,
    "name": "Buddy",
    "tag": "dog"
  },
  {
    "id": 3,
    "name": "Goldie"
  }
]
```

### Default -- Error

Returned for any unexpected error. The response body contains an **Error** object.

**Schema:** `Error`

| Name      | Type            | Required | Description                          |
|-----------|-----------------|----------|--------------------------------------|
| `code`    | integer (int32) | Yes      | Machine-readable error code          |
| `message` | string          | Yes      | Human-readable error description     |

**Example Response:**

```json
{
  "code": 500,
  "message": "An unexpected error occurred while retrieving pets."
}
```

---

## Status Code Reference

| Status Code | Meaning          | Description                                                                 |
|-------------|------------------|-----------------------------------------------------------------------------|
| `200`       | OK               | The request succeeded. The response body contains an array of Pet objects.  |
| `default`   | Unexpected Error | Any non-200 response indicates an error. The body contains an Error object. |

---

## Referenced Schemas

This endpoint references the following schemas defined in the OpenAPI specification:

- **Pet** -- A pet record composed of `id`, `name`, and an optional `tag`.
- **NewPet** -- The schema used when creating a new pet (referenced as a base schema via `allOf` composition).
- **Error** -- A standard error response containing a `code` and `message`.
