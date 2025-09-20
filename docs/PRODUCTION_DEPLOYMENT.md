# Oyster360 - Production Deployment Guide (AWS / GCP)

This guide covers **professional production deployment** of Oyster360 using major cloud providers, plus how to purchase a domain in Sri Lanka and connect it.

---

## Overview

We will deploy:

| Component     | Recommended Service       | Alternative          |
|---------------|---------------------------|----------------------|
| **Frontend**  | AWS Amplify / Vercel      | GCP Cloud Run        |
| **Backend**   | AWS ECS / Elastic Beanstalk | GCP Cloud Run      |
| **Database**  | Amazon RDS / Cloud SQL    | Neon / Supabase      |
| **Domain**    | .lk domain (LK Domain)    | Namecheap            |

---

## Part 1: Production Deployment Options

### Option A: AWS (Recommended for Sri Lanka)

#### 1.1 Deploy Backend using AWS Elastic Beanstalk

**Step 1: Install AWS CLI**

```bash
# macOS
brew install awscli

# Windows
choco install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**Step 2: Configure AWS Credentials**

```bash
aws configure
```

Enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `ap-southeast-1` (Singapore - closest to Sri Lanka)
- Output format: `json`

**Step 3: Initialize Elastic Beanstalk**

```bash
cd backend
eb init -p python-3.12 oyster360-backend --region ap-southeast-1
```

**Step 4: Create Environment**

```bash
eb create oyster360-production
```

**Step 5: Set Environment Variables**

```bash
eb setenv DATABASE_URL="your-production-db-url" \
          JWT_SECRET="your-secret-key" \
          AI_PROVIDER="rule-based"
```

**Step 6: Deploy**

```bash
eb deploy
```

Your backend will be available at:
```
http://oyster360-production.ap-southeast-1.elasticbeanstalk.com
```

---

#### 1.2 Deploy Frontend using AWS Amplify

**Step 1: Install Amplify CLI**

```bash
npm install -g @aws-amplify/cli
```

**Step 2: Initialize Amplify**

```bash
cd frontend
amplify init
```

**Step 3: Add Hosting**

```bash
amplify add hosting
```

Choose:
- Hosting with Amplify Console
- Continuous deployment (GitHub)

**Step 4: Deploy**

```bash
amplify publish
```

---

#### 1.3 Database using Amazon RDS

**Step 1: Create PostgreSQL Instance**

1. Go to AWS RDS Console
2. Click **Create database**
3. Choose **PostgreSQL**
4. Template: **Free tier**
5. DB instance identifier: `oyster360-db`
6. Master username: `oyster360`
7. Master password: Create strong password
8. Region: `ap-southeast-1`

**Step 2: Enable pgvector**

Connect to your RDS instance and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**Step 3: Get Connection String**

Format:
```
postgresql://oyster360:password@your-rds-endpoint.ap-southeast-1.rds.amazonaws.com:5432/oyster360
```

---

### Option B: Google Cloud Platform (GCP)

#### 2.1 Deploy Backend using Cloud Run

**Step 1: Install gcloud CLI**

```bash
# macOS
brew install google-cloud-sdk

# Follow official installation for your OS
```

**Step 2: Initialize GCP Project**

```bash
gcloud init
gcloud auth login
```

**Step 3: Deploy to Cloud Run**

```bash
cd backend
gcloud run deploy oyster360-backend \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated
```

**Step 4: Set Environment Variables**

```bash
gcloud run services update oyster360-backend \
  --update-env-vars DATABASE_URL="...",JWT_SECRET="..."
```

---

#### 2.2 Deploy Frontend using Cloud Run

```bash
cd frontend
gcloud run deploy oyster360-frontend \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated
```

---

### Option C: Hybrid Approach (Recommended)

| Component     | Service                    | Reason                              |
|---------------|----------------------------|-------------------------------------|
| **Frontend**  | Vercel                     | Best Next.js experience + free      |
| **Backend**   | Railway / Render           | Easy deployment + free tier         |
| **Database**  | Neon / Supabase            | Better free tier + pgvector support |
| **Domain**    | LK Domain Registry         | Local .lk domain                    |

This combination offers the best developer experience while keeping costs low.

---

## Part 2: Purchasing a Domain in Sri Lanka

### Option 1: LK Domain Registry (Official .lk Domains)

**Website**: [https://www.domains.lk](https://www.domains.lk)

#### Steps to Buy a .lk Domain

1. Go to [https://www.domains.lk](https://www.domains.lk)
2. Click **Register a Domain**
3. Search for your desired domain (example: `oyster360.lk`)
4. If available, click **Register**
5. Fill in your details:
   - Full Name
   - Address in Sri Lanka
   - NIC Number
   - Contact Number
   - Email Address
6. Choose domain type:
   - `.lk` → Rs. 2,000/year
   - `.com.lk` → Rs. 3,500/year
7. Make payment via:
   - Bank transfer
   - Online payment
8. Domain will be active within 24-48 hours

#### Requirements for .lk Domain

- Must provide valid Sri Lankan address
- NIC number required for individuals
- Business registration for companies

---

### Option 2: International Registrars (Easier)

These support .lk domains and are easier for beginners:

| Registrar       | Website                    | Price (approx)     | Notes                          |
|-----------------|----------------------------|--------------------|--------------------------------|
| **Namecheap**   | namecheap.com              | $10-15/year        | Easy interface, good support   |
| **GoDaddy**     | godaddy.com                | $12-18/year        | Popular, many payment options  |
| **Cloudflare**  | cloudflare.com             | At cost (~$8-12)   | Cheapest + excellent DNS       |

#### Recommended: Cloudflare Registrar

**Advantages**:
- Sells domains at cost (no markup)
- Best DNS performance
- Free SSL certificates
- Excellent security features

**Steps**:
1. Go to [https://www.cloudflare.com/products/registrar](https://www.cloudflare.com/products/registrar)
2. Search for your domain
3. Purchase
4. Update nameservers (if needed)

---

## Part 3: Connecting Domain to Deployment

### Method 1: Connecting to Vercel (Frontend)

1. Go to your Vercel project
2. Go to **Settings** → **Domains**
3. Add your domain: `oyster360.lk`
4. Vercel will give you nameservers or a verification record
5. Go to your domain registrar and update nameservers or add the record
6. Wait for DNS propagation (usually 30 minutes to 48 hours)

### Method 2: Connecting to Railway (Backend)

1. Go to your Railway project
2. Go to **Settings** → **Domains**
3. Add custom domain
4. Railway will provide a CNAME record
5. Add the CNAME record at your domain registrar

**Example CNAME Record**:
```
Type: CNAME
Name: api
Value: oyster360-backend-production.up.railway.app
```

---

## Part 4: Recommended Production Architecture

### Best Free/Low-Cost Production Setup

| Component     | Service              | Monthly Cost | Reason |
|---------------|----------------------|--------------|--------|
| **Frontend**  | Vercel               | $0           | Best Next.js support |
| **Backend**   | Railway              | $0-$5        | Easy deployment |
| **Database**  | Neon                 | $0           | Free tier + pgvector |
| **Domain**    | Cloudflare Registrar | ~$10/year    | Cheap + excellent DNS |
| **SSL**       | Cloudflare (Free)    | $0           | Automatic |

**Total Monthly Cost**: **~$0.83** (only domain cost)

---

## Part 5: SSL Certificates

### Free Options

1. **Cloudflare** — Free SSL with every domain
2. **Let's Encrypt** — Free SSL (auto-configured on Vercel/Railway)
3. **AWS Certificate Manager** — Free for AWS services

**Recommendation**: Use Cloudflare + Vercel/Railway (SSL is automatic)

---

## Part 6: Monitoring & Maintenance

### Recommended Free Tools

| Purpose           | Tool                    | Cost   |
|-------------------|-------------------------|--------|
| Uptime Monitoring | UptimeRobot             | Free   |
| Error Tracking    | Sentry                  | Free   |
| Log Management    | Railway / Vercel logs   | Free   |
| Analytics         | Plausible / Umami       | Free   |

---

## Summary: Deployment Checklist

- [ ] Purchase domain (.lk or international)
- [ ] Create Neon database
- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Vercel
- [ ] Configure environment variables
- [ ] Run database migrations
- [ ] Connect custom domain
- [ ] Set up SSL (automatic)
- [ ] Configure monitoring
- [ ] Test all features

---

## Cost Summary

| Setup Type           | Monthly Cost | Best For                    |
|----------------------|--------------|-----------------------------|
| **Free Tier**        | $0           | MVP / Testing               |
| **Low Cost**         | $1-5         | Small production deployment |
| **Professional**     | $20-50       | Growing business            |
| **Enterprise**       | $100+        | Large scale operations      |

---

**Last Updated**: July 2026