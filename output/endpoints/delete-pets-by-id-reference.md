# DELETE /pets/{id}

Delete a single pet by ID.

## Overview

The `DELETE /pets/{id}` endpoint deletes a single pet based on the ID supplied. On success the server returns a `204 No Content` response with no body. If the pet does not exist or an unexpected server-side problem occurs, the response follows the standard error schema.

**Method:** `DELETE`
**URL:** `https://petstore.swagger.io/v2/pets/{id}`

---

## Path Parameters

| Name | Type | Format | Required | Description |
|------|------|--------|----------|-------------|
| `id` | integer | int64 | Yes | ID of pet to delete |

---

## Request Body

This endpoint does not accept a request body.

---

## Responses

### 204 No Content

Returned when the pet has been successfully deleted. The response contains no body.

**Example**

```
HTTP/1.1 204 No Content
```

### Default Error

Returned when an unexpected error occurs.

**Schema**

| Field | Type | Format | Required | Description |
|-------|------|--------|----------|-------------|
| `code` | integer | int32 | Yes | Machine-readable error code |
| `message` | string | -- | Yes | Human-readable error message |

**Example Response Body**

```json
{
  "code": 404,
  "message": "Pet not found"
}
```

---

## Example Request

```bash
curl -X DELETE "https://petstore.swagger.io/v2/pets/123"
```

**Successful Response**

```
HTTP/1.1 204 No Content
```

**Error Response**

```bash
curl -X DELETE "https://petstore.swagger.io/v2/pets/999"
```

```json
{
  "code": 404,
  "message": "Pet not found"
}
```

---

## Referenced Schemas

- **Error** -- Standard error object containing a required `code` (integer) and `message` (string).
