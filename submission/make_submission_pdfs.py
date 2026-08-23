"""Generate Oyster360 submission PDFs (pitch deck + one-page brochure) with ReportLab."""
from pathlib import Path

from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from pdf_theme import (
    AMBER, BODY, BULLET, CREAM, GREY, H, INK, KPI_LBL, KPI_NUM, LINE, SMALL,
    TEAL, TEAL_DARK, W, WHITE, bullets, content_slide, footer, kpi_row, style,
)

OUTPUT_DIR = Path(__file__).resolve().parent

TOTAL = 12

def deck():
    c = canvas.Canvas(str(OUTPUT_DIR / "Oyster360_Pitch_Deck.pdf"), pagesize=landscape(letter))
    c.setTitle("Oyster360 — Pitch Deck")

    # 1 — Cover
    c.setFillColor(INK); c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(TEAL); c.rect(0, H - 0.18 * inch, W, 0.18 * inch, stroke=0, fill=1)
    c.setFillColor(AMBER); c.setFont("Helvetica-Bold", 12)
    c.drawString(0.9 * inch, H - 1.5 * inch, "AI-POWERED SAAS FOR SPECIALTY AGRICULTURE")
    c.setFillColor(white); c.setFont("Helvetica-Bold", 54)
    c.drawString(0.9 * inch, H - 2.35 * inch, "Oyster360")
    c.setFont("Helvetica", 20); c.setFillColor(HexColor("#B7C9CE"))
    c.drawString(0.9 * inch, H - 2.78 * inch, "From experience to intelligence.")
    c.setFillColor(HexColor("#8FA3AD")); c.setFont("Helvetica", 13)
    c.drawString(0.9 * inch, H - 3.3 * inch, "Multi-tenant farm management & intelligence for commercial oyster mushroom cultivation.")
    c.setStrokeColor(TEAL); c.setLineWidth(2)
    c.line(0.9 * inch, 1.05 * inch, W - 0.9 * inch, 1.05 * inch)
    c.setFillColor(HexColor("#8FA3AD")); c.setFont("Helvetica", 11)
    c.drawString(0.9 * inch, 0.72 * inch, "github.com/Inkithai/Oyster360   |   August 2026")
    c.showPage()

    # 2 — Problem
    content_slide(c, "Mushroom farms run on paper, memory and luck", kicker="The Problem")
    items = [
        "<b>Fragmented records.</b> Batches, environment readings and harvests live in notebooks and Excel — no history, no analysis.",
        "<b>Late problem detection.</b> Contamination (Trichoderma, cobweb) is often found only after it spreads — 15–25% of batches lost.",
        "<b>Inconsistent yields.</b> 600–900 g per bag with high variation; nobody knows which strain, recipe or climate drove success.",
        "<b>Knowledge trapped in people.</b> Success depends on a few experienced growers; scaling stalls and training takes months.",
    ]
    bullets(c, 1.02 * inch, H - 1.75 * inch, items)
    c.setFillColor(TEAL_DARK); c.setFont("Helvetica-Bold", 13)
    c.drawString(1.02 * inch, 0.95 * inch, "Result: thin margins, wasted substrate, and farms that cannot scale past ~5,000 bags per manager.")
    footer(c, 2, TOTAL); c.showPage()

    # 3 — Solution
    content_slide(c, "One platform for the whole farm, with AI on top", kicker="The Solution")
    c.setFillColor(white); c.roundRect(1.02 * inch, H - 4.55 * inch, 8.9 * inch, 2.9 * inch, 10, stroke=0, fill=1)
    c.setStrokeColor(LINE); c.roundRect(1.02 * inch, H - 4.55 * inch, 8.9 * inch, 2.9 * inch, 10, stroke=1, fill=0)
    p = Paragraph(
        "Oyster360 is a multi-tenant SaaS that digitizes the entire oyster mushroom operation — batch lifecycle "
        "(preparation → inoculation → colonization → fruiting → harvest), rooms and grow spaces, strain catalogue, versioned "
        "substrate recipes, environment records (temperature / humidity / CO₂), inventory & purchasing, harvest grading and revenue — "
        "then layers AI decision support on each farm's own data.", BODY)
    w, h = p.wrap(8.5 * inch, 1000); p.drawOn(c, 1.22 * inch, H - 1.75 * inch - h)
    kpi_row(c, 1.02 * inch, H - 4.85 * inch, [
        ("24", "API modules"),
        ("28", "service modules"),
        ("28", "app pages"),
        ("4", "roles / RBAC"),
    ])
    footer(c, 3, TOTAL); c.showPage()

    # 4 — AI capabilities
    content_slide(c, "Four AI engines, grounded in farm data", kicker="AI Technology")
    boxes = [
        ("Cultivation Assistant (NLP + GenAI)",
         "Natural-language Q&A grounded in live batch, environment and growth data. Multi-provider LLM layer (OpenAI / Gemini / local) with a deterministic rule-based fallback so the assistant always works."),
        ("Knowledge RAG",
         "Farms upload SOPs and notes; documents are chunked, stored and retrieved per-user to augment every answer — farm knowledge becomes searchable and reusable."),
        ("Image Inspection (Computer Vision)",
         "Photos of bags/substrate are analyzed for health score, contamination probability and growth stage, with findings and concrete corrective actions."),
        ("Yield Prediction (ML)",
         "Feature-based model predicts kg per batch, confidence score and expected harvest date from strain, recipe and environment history."),
    ]
    bw = 4.32 * inch; bh = 1.42 * inch
    for i, (t, d) in enumerate(boxes):
        x = 1.02 * inch + (i % 2) * (bw + 0.24 * inch)
        y = H - 1.62 * inch - (i // 2) * (bh + 0.22 * inch)
        c.setFillColor(white); c.roundRect(x, y - bh, bw, bh, 8, stroke=0, fill=1)
        c.setStrokeColor(LINE); c.roundRect(x, y - bh, bw, bh, 8, stroke=1, fill=0)
        c.setFillColor(TEAL_DARK); c.setFont("Helvetica-Bold", 12.5)
        c.drawString(x + 12, y - 20, t)
        q = Paragraph(d, style("bd", fontSize=10.5, leading=14.5, textColor=INK))
        w2, h2 = q.wrap(bw - 24, 1000); q.drawOn(c, x + 12, y - 34 - h2)
    footer(c, 4, TOTAL); c.showPage()

    # 5 — Why unique
    content_slide(c, "What makes Oyster360 unique", kicker="Differentiation")
    items = [
        "<b>Domain-specific, not generic agri-software.</b> Built around oyster mushroom biology: substrate recipes, colonization stages, flush cycles, harvest grading.",
        "<b>AI-native from day one.</b> Not dashboards-only — assistant, RAG, vision inspection and yield prediction are core workflows, running as tenant-scoped background jobs.",
        "<b>Works with or without an AI key.</b> Deterministic rule-based engines guarantee reliable advice offline; LLM providers upgrade it when available.",
        "<b>Production-grade SaaS.</b> Tenant isolation, RBAC, MFA/TOTP, Stripe billing with signed webhooks, GDPR export/delete, Docker + CI/CD.",
    ]
    bullets(c, 1.02 * inch, H - 1.72 * inch, items)
    footer(c, 5, TOTAL); c.showPage()

    # 6 — Impact / ROI
    content_slide(c, "Measured impact targets", kicker="Impact")
    kpi_row(c, 1.02 * inch, H - 1.85 * inch, [
        ("+15–25%", "yield per bag (650–750 → 780–850 g)"),
        ("−50–60%", "contamination losses (15–25% → 6–10%)"),
        ("3×", "bags per manager (5k → 15k+)"),
    ])
    kpi_row(c, 1.02 * inch, H - 3.45 * inch, [
        ("80%", "faster problem resolution"),
        ("60%", "faster staff onboarding (3–6 mo → 2–4 wks)"),
        ("100%", "of decisions backed by farm data"),
    ])
    footer(c, 6, TOTAL); c.showPage()

    # 7 — Product tour
    content_slide(c, "What farm teams use every day", kicker="Product")
    col1 = ["Batch lifecycle & stage tracking", "Rooms, strains & recipe versions", "Environment logging (T / RH / CO₂)", "AI assistant chat, grounded in live data", "Photo inspection & contamination findings"]
    col2 = ["Yield forecasts & harvest planning", "Harvest grading & quality scores", "Inventory, suppliers & purchase orders", "Farm dashboards & KPIs", "Subscription billing & admin analytics"]
    c.setFillColor(TEAL_DARK); c.setFont("Helvetica-Bold", 12)
    c.drawString(1.02 * inch, H - 1.72 * inch, "Cultivation & quality")
    bullets(c, 1.02 * inch, H - 2.0 * inch, col1, width=4.2 * inch)
    c.drawString(5.6 * inch, H - 1.72 * inch, "Operations & business")
    bullets(c, 5.6 * inch, H - 2.0 * inch, col2, width=4.2 * inch)
    footer(c, 7, TOTAL); c.showPage()

    # 8 — Market
    content_slide(c, "Who we serve", kicker="Market")
    items = [
        "<b>Medium to large oyster mushroom farms</b> (1,000+ bags per cycle) seeking consistent yield and lower contamination.",
        "<b>Multi-site mushroom companies</b> that need standardized processes and cross-site visibility.",
        "<b>Agricultural consultants & researchers</b> who need structured cultivation data and traceable outcomes.",
        "Oyster mushrooms are one of the fastest-growing specialty food segments — low entry capital, high spoilage risk, and almost no dedicated software today.",
    ]
    bullets(c, 1.02 * inch, H - 1.75 * inch, items)
    footer(c, 8, TOTAL); c.showPage()

    # 9 — Business model
    content_slide(c, "Business model", kicker="Commercial")
    items = [
        "<b>SaaS subscriptions</b> billed through Stripe — server-controlled pricing, verified webhooks, idempotent subscription sync, cancellation at period end.",
        "<b>Multi-tenant isolation:</b> every farm is an organization with enforced data boundaries — one deployment serves many customers.",
        "<b>Expansion paths:</b> per-seat and per-bag tiers, sensor integrations, consultancy analytics, and white-label deployments.",
    ]
    bullets(c, 1.02 * inch, H - 1.75 * inch, items)
    c.setFillColor(TEAL_DARK); c.setFont("Helvetica-Bold", 13)
    c.drawString(1.02 * inch, 1.05 * inch, "Billing infrastructure is implemented end-to-end; the platform is commercially deployable today.")
    footer(c, 9, TOTAL); c.showPage()

    # 10 — Architecture
    content_slide(c, "Built for production", kicker="Technology")
    left = [
        "<b>Frontend:</b> Next.js 16, React 19 + TypeScript, Tailwind 4, TanStack Query, Chart.js",
        "<b>Backend:</b> FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, PostgreSQL 16 + pgvector",
        "<b>Async:</b> Celery workers + Beat on Redis for AI jobs, emails, reports, cleanup",
    ]
    right = [
        "<b>Security:</b> JWT + rotating refresh tokens, Argon2, TOTP MFA, RBAC, rate limits, audit logs",
        "<b>Compliance:</b> GDPR export & deletion, data retention services",
        "<b>Ops:</b> Docker multi-stage images, Compose topology, GitHub Actions CI, Trivy scans, tests",
    ]
    bullets(c, 1.02 * inch, H - 1.72 * inch, left, width=4.35 * inch)
    bullets(c, 5.55 * inch, H - 1.72 * inch, right, width=4.35 * inch)
    footer(c, 10, TOTAL); c.showPage()

    # 11 — Status & roadmap
    content_slide(c, "Status & roadmap", kicker="Where we are")
    done = ["Multi-tenant isolation & security suite", "Full cultivation + inventory + purchasing workflows",
            "AI assistant, RAG, vision inspection, yield prediction", "Stripe billing & SaaS analytics", "Docker deployment & CI/CD"]
    next_ = ["Real-time sensor ingestion (IoT)", "Embedding-based RAG over pgvector", "Fine-tuned contamination vision model",
             "Mobile field app & offline mode"]
    c.setFillColor(TEAL_DARK); c.setFont("Helvetica-Bold", 12)
    c.drawString(1.02 * inch, H - 1.7 * inch, "Shipped")
    bullets(c, 1.02 * inch, H - 1.98 * inch, done, width=4.3 * inch)
    c.drawString(5.6 * inch, H - 1.7 * inch, "Next")
    bullets(c, 5.6 * inch, H - 1.98 * inch, next_, width=4.3 * inch)
    footer(c, 11, TOTAL); c.showPage()

    # 12 — Closing
    c.setFillColor(INK); c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(TEAL); c.rect(0, 0, W, 0.18 * inch, stroke=0, fill=1)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 40)
    c.drawString(0.9 * inch, H - 2.2 * inch, "From experience to intelligence.")
    c.setFont("Helvetica", 16); c.setFillColor(HexColor("#B7C9CE"))
    c.drawString(0.9 * inch, H - 2.75 * inch, "Oyster360 gives every oyster mushroom farm the operating system — and the AI — to grow more with less.")
    c.setFont("Helvetica-Bold", 13); c.setFillColor(AMBER)
    c.drawString(0.9 * inch, H - 3.5 * inch, "Try the demo  ·  github.com/Inkithai/Oyster360")
    c.setFillColor(HexColor("#8FA3AD")); c.setFont("Helvetica", 11)
    c.drawString(0.9 * inch, 0.72 * inch, "Oyster360 — AI-powered, multi-tenant farm management for commercial oyster mushroom cultivation.")
    c.showPage()

    c.save()

def brochure():
    c = canvas.Canvas(str(OUTPUT_DIR / "Oyster360_Brochure.pdf"), pagesize=letter)  # portrait
    w, h = letter
    # Header band
    c.setFillColor(INK); c.rect(0, h - 1.7 * inch, w, 1.7 * inch, stroke=0, fill=1)
    c.setFillColor(TEAL); c.rect(0, h - 1.78 * inch, w, 0.08 * inch, stroke=0, fill=1)
    c.setFillColor(AMBER); c.setFont("Helvetica-Bold", 10)
    c.drawString(0.7 * inch, h - 0.62 * inch, "AI-POWERED FARM MANAGEMENT")
    c.setFillColor(white); c.setFont("Helvetica-Bold", 30)
    c.drawString(0.7 * inch, h - 1.05 * inch, "Oyster360")
    c.setFont("Helvetica", 12); c.setFillColor(HexColor("#B7C9CE"))
    c.drawString(0.7 * inch, h - 1.32 * inch, "From experience to intelligence — for commercial oyster mushroom farms.")

    y = h - 2.15 * inch
    p = Paragraph(
        "Oyster360 is a multi-tenant SaaS platform that digitizes the entire oyster mushroom operation — batches, rooms, strains, "
        "substrate recipes, environment records, inventory, purchasing, harvest grading and revenue — and layers AI decision support "
        "on each farm's own data. Farms move from notebooks and guesswork to consistent, data-driven production.", BODY)
    wq, hq = p.wrap(w - 1.4 * inch, 1000); p.drawOn(c, 0.7 * inch, y - hq); y -= hq + 22

    c.setFillColor(TEAL_DARK); c.setFont("Helvetica-Bold", 14)
    c.drawString(0.7 * inch, y, "Why farms choose Oyster360"); y -= 20
    items = [
        "<b>+15–25% yield per bag</b> — data-driven strain, recipe and climate decisions lift output from 650–750 g to 780–850 g.",
        "<b>50–60% fewer contamination losses</b> — AI image inspection catches problems early, cutting losses from 15–25% to 6–10%.",
        "<b>Instant answers</b> — the AI cultivation assistant is grounded in live farm data and the farm's own documents (RAG).",
        "<b>3× operational scale</b> — one manager oversees 15,000+ bags instead of 5,000.",
        "<b>Faster onboarding</b> — standardized workflows and AI guidance make new staff productive in 2–4 weeks.",
    ]
    for it in items:
        q = Paragraph("<bullet>&bull;</bullet> " + it, BULLET)
        wq, hq = q.wrap(w - 1.5 * inch, 1000); q.drawOn(c, 0.78 * inch, y - hq); y -= hq + 7
    y -= 10

    c.setFillColor(TEAL_DARK); c.setFont("Helvetica-Bold", 14)
    c.drawString(0.7 * inch, y, "Built-in intelligence"); y -= 20
    feats = [
        ("Cultivation Assistant", "Natural-language advice grounded in batch, environment and growth data; multi-LLM with a reliable rule-based fallback."),
        ("Knowledge RAG", "Upload SOPs and notes; retrieval-augmented answers restricted to your farm's documents."),
        ("Image Inspection", "Photos analyzed for health score, contamination risk and growth stage, with actionable findings."),
        ("Yield Prediction", "Per-batch kg forecasts, confidence scores and expected harvest dates."),
    ]
    for t, d in feats:
        q = Paragraph(f"<b>{t}.</b> {d}", style("fb", fontSize=11.5, leading=16, textColor=INK))
        wq, hq = q.wrap(w - 1.5 * inch, 1000); q.drawOn(c, 0.78 * inch, y - hq); y -= hq + 6
    y -= 10

    c.setFillColor(TEAL_DARK); c.setFont("Helvetica-Bold", 14)
    c.drawString(0.7 * inch, y, "Enterprise-grade platform"); y -= 20
    q = Paragraph(
        "Tenant-isolated organizations, role-based access (Admin / Farm Manager / Worker / Viewer), MFA, Stripe subscription billing, "
        "GDPR export &amp; deletion, background jobs, dashboards and SaaS analytics — deployed with Docker and CI/CD.",
        style("fb2", fontSize=11.5, leading=16, textColor=INK))
    wq, hq = q.wrap(w - 1.5 * inch, 1000); q.drawOn(c, 0.78 * inch, y - hq)

    # Footer band
    c.setFillColor(INK); c.rect(0, 0, w, 0.62 * inch, stroke=0, fill=1)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 10.5)
    c.drawString(0.7 * inch, 0.34 * inch, "Oyster360 — github.com/Inkithai/Oyster360")
    c.setFont("Helvetica", 9.5); c.setFillColor(HexColor("#B7C9CE"))
    c.drawRightString(w - 0.7 * inch, 0.34 * inch, "Multi-tenant · AI-native · Production-ready")
    c.save()

if __name__ == "__main__":
    deck()
    brochure()
    print(f"PDFs generated in {OUTPUT_DIR}")
