# Pending Tasks — Oyster360 Sri Lanka Grower MVP

**Last updated:** 2026-10-29
**Branch:** `arena/47079d1f-oyster360`
**Current status:** Phase 1 Sri Lankan Mushroom-Farm MVP is implemented and all ten CI quality gates pass
(`flake8`, `mypy`, `pytest` 414 tests at 94.08% coverage, `eslint`, `tsc --noEmit`, `vitest` 64 tests at 93.54% coverage).

This document is the single source of truth for what is **not** finished yet. Items are grouped by
when they should be picked up: Phase 1 polish (ready now), Phase 2 growth work, Phase 3 advanced work, and
deliberately deferred enterprise scope.

---

## 1. Phase 1 Polish — Ready to Start Now

### 1.1 Interactive Inventory & Recipe Actions
- **Current state:** `/inventory` and `/recipes` render read-only `DataTable` views over
  `GET /api/inventory/items` and `GET /api/recipes`.
- **Pending work:**
  - Add a one-tap **“+ Add Raw Material”** form (sawdust, rice bran, lime, MgSO₄, spawn, bags, packaging)
    with LKR unit cost and reorder level.
  - Add **“Record Stock Used / Purchased”** actions so bag-preparation consumption decrements stock
    instead of being entered by hand in Finance.
  - Add a **“+ DOA Standard Substrate Formula”** action that pre-fills the standard Department of
    Agriculture sawdust + rice bran recipe.
- **Acceptance:** stock never goes negative; every write is farm-scoped and audit logged.

### 1.2 Full In-Page Trilingual Translation
- **Current state:** `frontend/src/lib/i18n.tsx` exposes an `en` / `si` / `ta` provider, and the language
  switcher (`EN | සිං | தமிழ்`) translates the sidebar, mobile navigation, and DOA variety cards.
- **Pending work:** move the remaining hard-coded English strings in `/dashboard`, `/harvests/new`,
  `/finance`, `/sales`, `/batches`, and `/strains` into the translation dictionary — form labels, button
  captions, KPI titles, table headers, toast messages, and validation errors.
- **Acceptance:** switching language leaves no untranslated farmer-facing copy on the recording and
  profit pages; a test asserts a Sinhala and a Tamil label are rendered after switching.

### 1.3 Playwright End-to-End Coverage for the New Workflows
- **Current state:** `frontend/tests/e2e/` only contains `login.spec.ts` and `dashboard.spec.ts`.
- **Pending work:** add specs for the three flagship flows:
  - **60-Second Harvest Entry** (`/harvests/new`): select flush, tap a weight preset, save, see the flush
    appear on `/harvests`.
  - **LKR Profit & Cost Calculator** (`/finance`): add an expense, confirm cost per bag and estimated
    profit update.
  - **Buyer Sale & Payment Settlement** (`/sales`): create a buyer, record a partially paid sale, then
    mark the balance paid and see outstanding drop to zero.
- **Acceptance:** the three specs pass in the CI E2E job against the Docker Compose stack.

### 1.4 Documentation Sync
- **Pending work:**
  - `docs/API.md`: document `/api/finance/expenses`, `/api/finance/profitability`,
    `/api/sales/buyers`, `/api/sales/orders`, `/api/sales/orders/{id}/payment`,
    `/api/sales/stock-summary`, `/api/batches/{id}/bags`, `/api/batches/daily-tasks`,
    `/api/batches/{id}/harvests`, `/api/harvests`, `/api/strains/doa-varieties`, and
    `/api/strains/cultivation-guide`.
  - `docs/ROADMAP_STATUS.md`: replace the pre-MVP “~65% complete” snapshot with the Sri Lankan MVP
    delivery status and current coverage figures.
  - `docs/USER_GUIDE.md`: add a “first harvest in five minutes” walkthrough for a new grower.
- **Acceptance:** every router registered in `backend/app/api/__init__.py` appears in `docs/API.md`.

### 1.5 Release Hygiene
- Commit the MVP work on `arena/47079d1f-oyster360`, open a pull request, and merge to `main` once the
  full `./scripts/ci-local.sh` pipeline is green.

---

## 2. Phase 2 — Growth (Next After Phase 1 Ships)

### 2.1 SMS / WhatsApp Farm Reminders
- Daily reminders for bag opening, misting, flush harvest readiness, high contamination alerts
  (≥ 10% of a batch), and overdue buyer payments.
- **Why deferred:** needs a paid local SMS/WhatsApp Business provider account and per-message billing.

### 2.2 Recurring Buyer Orders & Printable Delivery Notes
- Standing weekly orders for supermarkets, restaurants, and hotels, plus printable LKR delivery
  notes/invoices that match how Sri Lankan buyers actually settle accounts.
- **Why deferred:** Phase 1 already covers one-off sales, balances, and CSV export.

### 2.3 Multi-Shed / Grow-House Comparison
- Compare yield per bag, contamination rate, and cost per kg across separate mushroom sheds.
- **Depends on:** shed-level grouping of batches, which the current `Room` model only partially supports.

### 2.4 Local Payment Collection
- Record bank-transfer references and support LankaQR or PayHere collection for buyer balances.
- **Why deferred:** replaces Stripe, which does not serve Sri Lankan smallholder collections well.

### 2.5 Low-Stock Push Alerts
- Notify the grower when substrate, spawn, or bags drop below reorder level, instead of only shading the
  row orange in `/inventory`.

---

## 3. Phase 3 — Advanced (Only With Real Demand)

### 3.1 IoT Environmental Sensor Ingestion
- Automated temperature, humidity, and CO₂ ingestion for climate-controlled sheds.
- **Why deferred:** most target growers record conditions on paper; manual `EnvironmentLog` entry is enough
  for Phase 1. The existing environmental-factor yield heuristic already reads these logs when present.

### 3.2 Computer Vision Contamination Detection
- Camera-based green mould (*Trichoderma*), black mould, and cobweb disease classification trained on real
  Sri Lankan grow-bag photographs.
- **Why deferred:** no labelled local dataset exists yet; the contamination bag counter covers the need.

### 3.3 Cooperative / Outgrower Network Management
- Multi-farm aggregation for farmer societies, export collectors, and extension officers managing
  20–100+ smallholder growers.
- **Why deferred:** requires organisation-hierarchy UX that Phase 1 deliberately simplified away.

---

## 4. Deliberately Deferred Enterprise Scope

These existing modules stay in the repository behind feature flags and are **not** part of the grower
MVP path. They should not be removed without a migration plan, and they should not receive new
investment until a paying customer asks:

| Deferred capability | Existing code | Rationale |
|---|---|---|
| MFA (TOTP) enrolment UI and login challenge | `backend/app/services/mfa_service.py` | Growers sign in from one shared phone; password + rate limiting is proportionate |
| Multi-organisation switching | Organisation model, tenant middleware | Phase 1 assumes one farm per account; isolation stays enforced |
| RAG chat assistant | `backend/app/services/ai_service.py` | No local-language corpus; rule-based DOA guidance is more trustworthy |
| Dual yield-prediction engines | `backend/app/services/analytics_service.py` | Replaced by actual-vs-expected yield tracking per batch |
| Stripe billing, checkout, webhooks | `backend/app/services/stripe_service.py` | No subscription revenue model in Phase 1 |
| SaaS MRR / retention analytics | SaaS analytics router | No SaaS metrics to report until a subscription model exists |
| Admin portal, audit-log UI, feature flags | Admin router and service | Backend endpoints retained; no farmer-facing need |
| GDPR self-service export/deletion UI | Compliance endpoints | Endpoints retained; UI deferred |
| Sentry, Prometheus, log aggregation | Monitoring middleware | Structured logging + request IDs are sufficient at current scale |

---

## 5. Definition of Done for Phase 1

Phase 1 is considered shipped when:

1. All ten `./scripts/ci-local.sh` gates pass on `main`.
2. A grower can record a harvest in under 60 seconds on a phone in Sinhala, Tamil, or English.
3. Every LKR expense and sale is attributable to a batch, and profit reconciles with revenue minus expenses.
4. Bag counts can never go negative, and sales can never exceed sellable harvest stock.
5. Alembic migration `005_add_sri_lanka_mvp_tables` applies cleanly on a fresh database and on an
   existing Phase 0 database.
