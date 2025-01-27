# Oyster360 - Deployment Tutorial (Beginner Friendly)

This guide will help you deploy **Oyster360** to the internet step by step. We will use **free or low-cost** services.

---

## Overview of Deployment

We will deploy:

| Component     | Service          | Cost          | Difficulty |
|---------------|------------------|---------------|------------|
| **Frontend**  | Vercel           | Free          | Easy       |
| **Backend**   | Railway          | Free tier     | Easy       |
| **Database**  | Neon PostgreSQL  | Free tier     | Easy       |

**Total Monthly Cost**: **$0** (using free tiers)

---

## Step 1: Prepare Your Project

### 1.1 Create a `.env.production` file

In your project root, create a file called `.env.production`:

```env
# Database (we will get this from Neon later)
DATABASE_URL=postgresql://username:password@host:5432/oyster360

# JWT Secret (create a strong random string)
JWT_SECRET=your-super-long-random-secret-key-here-123456789

# AI Provider
AI_PROVIDER=rule-based
```

### 1.2 Update Frontend Environment Variables

Create a file called `.env.production.local` in the `frontend` folder:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.up.railway.app
```

> **Note**: We will replace `your-backend-url.up.railway.app` later.

---

## Step 2: Deploy the Database (Neon - Free)

### Step 2.1: Create a Neon Account

1. Go to: [https://neon.tech](https://neon.tech)
2. Click **Sign up** (use GitHub or email)
3. Verify your email

### Step 2.2: Create a New Project

1. Click **Create a Project**
2. Give it a name: `oyster360-db`
3. Choose region closest to you
4. Click **Create Project**

### Step 2.3: Get Database Connection String

1. After project is created, you will see a connection string like:
   ```
   postgresql://username:password@ep-xxx.region.aws.neon.tech/oyster360?sslmode=require
   ```
2. **Copy this connection string** — we will need it later.

### Step 2.4: Enable pgvector Extension

Run this SQL command in Neon's SQL Editor:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Step 3: Deploy the Backend (Railway - Free)

### Step 3.1: Create a Railway Account

1. Go to: [https://railway.app](https://railway.app)
2. Click **Login** → Use GitHub
3. Authorize Railway

### Step 3.2: Create a New Project

1. Click **New Project**
2. Select **Deploy from GitHub repo**
3. Choose your Oyster360 repository

### Step 3.3: Configure the Backend Service

1. Railway will detect multiple services. Select the **backend** folder.
2. Go to **Variables** tab and add these:

| Variable Name     | Value                                      |
|-------------------|--------------------------------------------|
| `DATABASE_URL`    | Paste the Neon connection string           |
| `JWT_SECRET`      | Create a long random string                |
| `AI_PROVIDER`     | `rule-based`                               |

### Step 3.4: Deploy

1. Click **Deploy**
2. Wait for the build to finish (usually 2-4 minutes)
3. Copy the generated URL (example: `https://oyster360-backend-production.up.railway.app`)

---

## Step 4: Deploy the Frontend (Vercel - Free)

### Step 4.1: Create a Vercel Account

1. Go to: [https://vercel.com](https://vercel.com)
2. Click **Sign up** with GitHub

### Step 4.2: Import Your Project

1. Click **Add New Project**
2. Select your GitHub repository
3. Vercel will detect it is a Next.js project

### Step 4.3: Configure Environment Variables

Add these in Vercel:

| Variable Name              | Value                                              |
|---------------------------|----------------------------------------------------|
| `NEXT_PUBLIC_API_URL`     | `https://your-backend-url.up.railway.app`          |

### Step 4.4: Deploy

1. Click **Deploy**
2. Wait for deployment (usually 1-2 minutes)
3. Copy your Vercel URL

---

## Step 5: Update Backend CORS (Important!)

After getting your Vercel URL, go back to Railway and add this environment variable:

| Variable Name     | Value                                      |
|-------------------|--------------------------------------------|
| `CORS_ORIGINS`    | `https://your-vercel-url.vercel.app`       |

Then **redeploy** the backend.

---

## Step 6: Run Database Migrations

After both frontend and backend are deployed:

1. Go to your Railway backend service
2. Open **Console** or **Shell**
3. Run these commands:

```bash
alembic upgrade head
python -m app.database.seed
```

---

## Step 7: Test Your Deployment

Open your Vercel URL and test:

1. Login with demo credentials
2. View the dashboard
3. Create a test batch
4. Use the AI Assistant

---

## Free Tier Limits Summary

| Service   | Free Tier Limits                          | Good For                  |
|-----------|-------------------------------------------|---------------------------|
| **Vercel**    | 100GB bandwidth/month                     | Small to medium traffic   |
| **Railway**   | $5 credit/month                           | Good for small apps       |
| **Neon**      | 0.5 GB storage, 1 project                 | Perfect for MVP           |

---

## Troubleshooting

### Frontend shows "Failed to fetch"

→ Make sure `NEXT_PUBLIC_API_URL` is set correctly in Vercel.

### Backend shows CORS error

→ Add your Vercel URL to Railway environment variables as `CORS_ORIGINS`.

### Database connection error

→ Make sure `DATABASE_URL` is correct and includes `?sslmode=require`.

### Migrations not running

→ Run `alembic upgrade head` manually in Railway shell.

---

## Alternative Free Options

| Component   | Alternative Services                     | Notes                              |
|-------------|------------------------------------------|------------------------------------|
| Frontend    | Netlify, Cloudflare Pages                | Also free                          |
| Backend     | Render, Fly.io, Google Cloud Run         | Render has generous free tier      |
| Database    | Supabase, ElephantSQL                    | Supabase also gives free storage   |

---

## Next Steps After Deployment

1. Set up a custom domain (optional)
2. Enable automatic deployments on Git push
3. Set up monitoring (optional)
4. Add real OpenAI API key for better AI responses

---

**Congratulations!** Your Oyster360 application is now live on the internet.

---

**Last Updated**: July 2026