# Oyster360 API Documentation

## Authentication

All API requests require a JWT token:

```
Authorization: Bearer <token>
```

## Core Endpoints

### Authentication
- `POST /api/auth/login`
- `POST /api/auth/register`
- `POST /api/auth/logout`
- `POST /api/auth/forgot-password`
- `POST /api/auth/reset-password`

### Organizations
- `POST /api/organizations`
- `GET /api/organizations/my-organizations`
- `POST /api/organizations/switch/{id}`

### Billing
- `POST /api/billing/create-checkout-session`
- `GET /api/billing/subscription`
- `POST /api/billing/cancel-subscription`

### Notifications
- `GET /api/notifications`
- `POST /api/notifications/{id}/read`

---

**Last Updated**: July 2026