# Oyster360 - API Documentation

## Base URL

```
Production: https://api.oyster360.com
Development: http://localhost:8000
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## Core Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/register` | User registration |

### Batches

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/batches` | List all batches |
| POST | `/api/batches` | Create new batch |
| PATCH | `/api/batches/{id}/stage` | Update batch stage |
| GET | `/api/batches/{id}` | Get batch details |

### Recipes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/recipes` | List all recipes |
| POST | `/api/recipes` | Create new recipe |
| POST | `/api/recipes/{id}/versions` | Create new version |
| GET | `/api/recipes/{id}/performance` | Get recipe analytics |

### AI Features

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/assistant/chat` | Chat with AI Cultivation Assistant |
| POST | `/api/inspections/upload` | Upload image for analysis |
| POST | `/api/inspections/{id}/analyze` | Run AI image analysis |
| POST | `/api/analytics/predict-yield` | Get yield prediction |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard` | Main dashboard statistics |
| GET | `/api/analytics/environment` | Environmental trends |
| GET | `/api/analytics/strains` | Strain performance |
| GET | `/api/analytics/recipes` | Recipe performance |

### Inventory & Purchases

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/inventory/items` | List inventory items |
| POST | `/api/inventory/transactions` | Record stock movement |
| GET | `/api/purchases/suppliers` | List suppliers |
| POST | `/api/purchases/orders` | Create purchase order |

---

## Response Format

### Success Response

```json
{
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response

```json
{
  "detail": "Error message",
  "code": "ERROR_CODE"
}
```

---

**Last Updated**: July 2026