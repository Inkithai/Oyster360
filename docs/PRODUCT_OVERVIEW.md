# Oyster360 — Product Overview (Sri Lanka Grower Edition)

## Product Positioning

**Oyster360 helps Sri Lankan mushroom growers track grow bags, record harvests, understand their costs, and know how much profit their farm actually makes.**

## Target Customers

- Small and medium commercial mushroom growers in Sri Lanka (500 to 25,000+ grow bags)
- Women-led and family mushroom enterprises
- Farmer societies, cooperative groups, and outgrower networks
- Export-oriented or supermarket-supplying mushroom farms
- Agriculture trainers, extension officers, and agribusiness consultants

## Phase 1 Core Farm MVP Features

### 1. Simple Cultivation & Grow-Bag Tracking
- Track **bags prepared**, **bags inoculated**, **bags contaminated**, **bags harvested**, and **active healthy bags** per batch (`PATCH /api/batches/{id}/bags`).
- Automatic calculation of `expected_harvest_date` from strain colonization + fruiting days.
- Daily cultivation tasks and automatic alerts when batch contamination reaches or exceeds 10% (`GET /api/batches/daily-tasks`).
- Multi-flush harvest tracking (Flush 1, Flush 2, Flush 3+) with option to keep a batch open across flushes or complete it on the final flush (`POST /api/batches/{id}/harvest`, `GET /api/batches/{id}/harvests`).
- Sri Lanka Department of Agriculture (DOA) varieties (`GET /api/strains/doa-varieties`) and stage-by-stage cultivation checklists (`GET /api/strains/cultivation-guide`):
  - **American Oyster (Bhutani)** (*Pleurotus ostreatus*)
  - **Abalone Mushroom** (*Pleurotus cystidiosus*)
  - **Pink Oyster** (*Pleurotus djamor*)
  - **Milky Mushroom** (*Calocybe indica*)

### 2. Real Profit & Cost Calculator in LKR (`/finance`)
- Record farm expenses in **Sri Lankan Rupees (LKR / Rs.)** across local cost categories: `SUBSTRATE` (sawdust, rice bran, lime, MgSO4), `SPAWN`, `BAGS`, `PACKAGING`, `ELECTRICITY`, `WATER`, `LABOUR`, `TRANSPORT`, and `OTHER` (`POST /api/finance/expenses`, `GET /api/finance/expenses`).
- Automatic profitability calculation (`GET /api/finance/profitability`):
  - Cost per grow bag (LKR) and cost per kg (LKR)
  - Revenue per harvest/sale, gross profit, and estimated net profit (LKR)
  - Actual vs. expected yield (kg) and yield efficiency (%)
  - Per-batch profitability breakdown with CSV export and printable monthly report

### 3. Harvest Sales & Buyer Management (`/sales`)
- Manage local buyers (`RETAILER`, `RESTAURANT`, `WHOLESALER`, `DIRECT_CUSTOMER`, `HOTEL`, `INTERMEDIARY`) with phone, town/location, repeat order counts, and outstanding credit balances (`POST /api/sales/buyers`, `GET /api/sales/buyers`).
- Record harvest sales in LKR with automatic calculation of `total_amount_lkr`, `balance_due_lkr`, and `payment_status` (`PAID`, `PARTIAL`, `UNPAID`) (`POST /api/sales/orders`, `PATCH /api/sales/orders/{id}/payment`).
- Track daily sellable harvest stock (`available_for_sale_kg`) vs. sold (`total_sold_kg`), unsold (`total_unsold_kg`), and spoiled/discarded (`total_spoiled_kg`) mushrooms (`GET /api/sales/stock-summary`).

### 4. Mobile-First UX & Sinhala / Tamil / English Support
- **60-Second Harvest Entry** (`/harvests/new`): large tap buttons for Flush 1–4, one-tap weight presets, unit toggle between kilograms (`kg`) and grams (`g`), and Sri Lankan market price presets (`Rs. 500–800/kg`).
- Trilingual navigation switcher supporting **English (`EN`)**, **සිංහල (`සිං`)**, and **தமிழ் (`தமிழ்`)**.
- Consolidated farm dashboard (`/dashboard`) combining cultivation KPIs with LKR revenue, expenses, estimated profit, and outstanding buyer payments.

## Phased Roadmap

- **Phase 1 (Implemented MVP)**: Grow-bag & flush tracking, LKR cost & profit calculator, buyer & sales management, stock & low-stock alerts, DOA cultivation guide, and mobile-first trilingual UI.
- **Phase 2 (Growth)**: SMS/WhatsApp reminders, richer buyer/order workflows, multi-shed comparison, and local payment collection (bank transfer / LankaQR).
- **Phase 3 (Advanced / Enterprise)**: IoT environmental sensors, AI disease image detection, predictive yield models, and multi-farm cooperative analytics.
