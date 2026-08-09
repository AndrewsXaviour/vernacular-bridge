# Vernacular Bridge — Free-Tier Deployment Guide

This guide covers deploying the Vernacular Bridge system to **completely free tiers** of popular cloud platforms. The goal is a live public demo without spending any money.

## Architecture Overview for Deployment

```
┌──────────────────────────────────────────────────┐
│                  VERCEL (Free)                    │
│  Next.js Frontend (vernacular-bridge-ui/)        │
│  URL: https://vernacular-bridge.vercel.app       │
│  Rewrites proxy /api/* → Railway backend         │
└────────────────────┬─────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────┐
│              RAILWAY / RENDER (Free)              │
│  FastAPI Backend (orchestrator.py)               │
│  URL: https://vernacular-bridge-backend.railway.app│
│  Environment: GOOGLE_API_KEY + config             │
└──────────────────────────────────────────────────┘
```

---

## Option A: Vercel (Frontend) + Railway (Backend) — RECOMMENDED

### Prerequisites

1. **GitHub account** (for repository hosting)
2. **Vercel account** (sign up at vercel.com with GitHub)
3. **Railway account** (sign up at railway.app with GitHub — $5 free credit, no card required)
4. **Google API key** for Gemini (get one at https://aistudio.google.com/apikey — free tier available)

### Step 1: Push Code to GitHub

```bash
# From the project root
git init
git add .
git commit -m "Initial commit"
# Create a repo on GitHub first, then:
git remote add origin https://github.com/yourusername/vernacular-bridge.git
git push -u origin main
```

### Step 2: Deploy Backend to Railway

1. **Go to Railway dashboard** → `New Project` → `Deploy from GitHub repo`
2. **Select your repository**
3. **Set start command:**
   ```
   python orchestrator.py
   ```
4. **Add environment variables:**

   | Key | Value |
   |---|---|
   | `GOOGLE_API_KEY` | `your-gemini-api-key` |
   | `ALLOWED_ORIGINS` | `https://vernacular-bridge.vercel.app` |
   | `API_KEYS` | `demo-key-change-in-production` |
   | `PYTHON_VERSION` | `3.11` |

5. **Add a `Procfile`** at the project root (Railway reads this):
   ```
   web: python orchestrator.py
   ```

6. **Wait for build** → Railway gives you a URL like:
   ```
   https://vernacular-bridge-backend.up.railway.app
   ```
   Test it: `curl https://vernacular-bridge-backend.up.railway.app/health`

### Step 3: Deploy Frontend to Vercel

1. **Go to Vercel dashboard** → `Add New` → `Project`
2. **Import your GitHub repository**
3. **Set Root Directory:** `vernacular-bridge-ui`
4. **Set Framework Preset:** `Next.js`
5. **Set Build Command:** `npm run build`
6. **Set Output Directory:** `.next`
7. **Add environment variables:**

   | Key | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | `https://vernacular-bridge-backend.up.railway.app` |

8. **Update `next.config.ts`** to use the production backend URL:

   ```typescript
   import type { NextConfig } from "next";

   const nextConfig: NextConfig = {
     async rewrites() {
       return [
         {
           source: "/full-flow",
           destination: `${process.env.NEXT_PUBLIC_API_URL}/full-flow`,
         },
         {
           source: "/coach",
           destination: `${process.env.NEXT_PUBLIC_API_URL}/coach`,
         },
         {
           source: "/navigator",
           destination: `${process.env.NEXT_PUBLIC_API_URL}/navigator`,
         },
         {
           source: "/learn",
           destination: `${process.env.NEXT_PUBLIC_API_URL}/learn`,
         },
         {
           source: "/generate",
           destination: `${process.env.NEXT_PUBLIC_API_URL}/generate`,
         },
         {
           source: "/health",
           destination: `${process.env.NEXT_PUBLIC_API_URL}/health`,
         },
       ];
     },
   };

   export default nextConfig;
   ```

9. **Deploy** → Vercel gives you a URL like:
   ```
   https://vernacular-bridge.vercel.app
   ```

### Step 4: Update CORS Configuration

Back in Railway, update `ALLOWED_ORIGINS` to include your Vercel domain:

```
ALLOWED_ORIGINS=https://vernacular-bridge.vercel.app
```

### Step 5: Verify the Demo

1. Open `https://vernacular-bridge.vercel.app`
2. Enter a query (e.g., "Photosynthesis" or "ஒளிச்சேர்க்கை")
3. Verify the response shows Tamil explanation + English academic version + steps + MCQs
4. Test `/health` endpoint: `https://vernacular-bridge-backend.up.railway.app/health`

---

## Option B: Vercel (Frontend) + Render (Backend)

### Backend on Render Free Tier

Render's free tier has some limitations:
- **Cold start delay** (15+ seconds on first request after inactivity)
- **512 MB RAM**
- **Sleeps after 15 minutes of inactivity**

### Step 1: Deploy Backend to Render

1. **Go to Render dashboard** → `New` → `Web Service`
2. **Connect your GitHub repository**
3. **Settings:**

   | Field | Value |
   |---|---|
   | Name | `vernacular-bridge-backend` |
   | Runtime | `Python 3` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `python orchestrator.py` |
   | Plan | **Free** |

4. **Add environment variables** (same as Railway above)
5. **Create a `requirements.txt`** at project root if not exists:
   ```
   fastapi==0.115.0
   uvicorn==0.30.0
   google-genai==0.3.0
   pydantic==2.9.0
   pydantic-settings==2.4.0
   python-dotenv==1.0.0
   httpx==0.27.0
   ```

6. **Deploy** → Render gives you a URL like:
   ```
   https://vernacular-bridge-backend.onrender.com
   ```

### Step 2: Prevent Sleeping (Optional)

Render free tier sleeps after 15 minutes. To keep it alive:
- Set up a free cron job at https://cron-job.org to hit `/health` every 10 minutes
- Or use Kaffeine (https://kaffeine.herokuapp.com) — but this is for Heroku, not Render

### Step 3: Deploy Frontend to Vercel

Same as **Option A, Step 3** above, with:
```
NEXT_PUBLIC_API_URL=https://vernacular-bridge-backend.onrender.com
```

---

## Option C: Vercel (Frontend) + Google Cloud Run (Backend)

### Backend on Google Cloud Run Free Tier

Google Cloud Run offers:
- **2 million requests/month free**
- **360,000 vCPU-seconds/month free**
- **Always-on** (no cold starts if you set min-instances=0)
- **Custom domains supported**

### Step 1: Create a Dockerfile

Create `Dockerfile` at project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY orchestrator.py .
COPY models/ models/
COPY utils/ utils/
COPY validators/ validators/
COPY data/ data/

# Run the application
CMD ["uvicorn", "orchestrator:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Step 2: Add `requirements.txt`

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
google-genai==0.3.0
pydantic==2.9.0
pydantic-settings==2.4.0
python-dotenv==1.0.0
```

### Step 3: Deploy to Google Cloud Run

```bash
# Install Google Cloud SDK first, then:
gcloud auth login
gcloud config set project your-project-id

# Build and deploy
gcloud builds submit --tag gcr.io/your-project-id/vernacular-bridge
gcloud run deploy vernacular-bridge-backend \
  --image gcr.io/your-project-id/vernacular-bridge \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_API_KEY=your-key,ALLOWED_ORIGINS=https://vernacular-bridge.vercel.app"
```

### Step 4: Deploy Frontend to Vercel

Same as **Option A, Step 3** with:
```
NEXT_PUBLIC_API_URL=https://vernacular-bridge-backend-xxxxx-uc.a.run.app
```

---

## Option D: Fully Self-Hosted with Docker Compose (FREE)

For maximum control with zero cloud costs (runs on your own machine or a free VM):

### Step 1: Create `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - ALLOWED_ORIGINS=http://localhost:3000
      - API_KEYS=demo-key
    volumes:
      - ./data:/app/data

  frontend:
    build:
      context: ./vernacular-bridge-ui
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
```

### Step 2: Create Frontend Dockerfile

Create `vernacular-bridge-ui/Dockerfile`:

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --production
EXPOSE 3000
CMD ["npm", "start"]
```

### Step 3: Run

```bash
# Set your API key
export GOOGLE_API_KEY=your-key-here

# Start everything
docker-compose up --build

# Open http://localhost:3000
```

### Free VM Options:
- **Oracle Cloud Free Tier** — Always-free ARM VM (4 cores, 24GB RAM)
- **Google Cloud Free Tier** — f1-micro VM (1 core, 614MB RAM)
- **Azure Free Tier** — B1s VM (1 core, 1GB RAM)
- **Fly.io** — Free tier with 3 shared VMs (256MB each)

---

## Environment Variable Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `GOOGLE_API_KEY` | **Yes** | — | Gemini API key for LLM calls |
| `ALLOWED_ORIGINS` | No | `http://localhost:3000,http://localhost:7860` | Comma-separated CORS origins |
| `API_KEYS` | No | (empty = no auth) | Comma-separated API keys for auth |
| `PRIMARY_MODEL` | No | `gemini-2.5-flash` | Primary Gemini model |
| `SECONDARY_MODEL` | No | `gemini-2.5-pro` | Fallback Gemini model |
| `LLM_TIMEOUT` | No | `30` | LLM call timeout (seconds) |
| `RATE_LIMIT_RPM` | No | `20` | Max requests per minute per IP |
| `CACHE_TTL` | No | `600` | Cache TTL (seconds) |
| `CACHE_MAX_SIZE` | No | `100` | Max cached responses |
| `CB_THRESHOLD` | No | `3` | Circuit breaker failure threshold |
| `CB_COOLDOWN` | No | `60` | Circuit breaker cooldown (seconds) |

---

## Health Check Endpoint

After deployment, verify the backend is running:

```bash
curl https://your-backend-url/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": 1718000000.0,
  "version": "1.0.0",
  "cache_size": 0,
  "active_ips": 0
}
```

---

## Troubleshooting

### "Connection failed with intelligence bridge" on frontend

**Cause:** Frontend cannot reach backend API.

**Fix:**
1. Verify backend is running: visit `/health` directly
2. Check CORS settings: `ALLOWED_ORIGINS` must include your frontend domain
3. Check rewrites in `next.config.ts` — domain must match exactly
4. If using Railway/Render free tier, the backend may be sleeping. Hit `/health` to wake it up, then retry the frontend.

### "429 Too Many Requests"

**Cause:** Rate limiter triggered.

**Fix:** Wait 60 seconds and retry. For demo purposes, you can increase `RATE_LIMIT_RPM` or set it to a high value (e.g., `1000`).

### "JSON extraction failed" errors

**Cause:** LLM returned malformed JSON.

**Fix:** Check `GOOGLE_API_KEY` is valid and has access to Gemini 2.5 Flash. The free tier has quota limits.

### Backend crashes on startup

**Cause:** Missing dependencies or Python version mismatch.

**Fix:**
1. Verify `requirements.txt` is complete
2. Set `PYTHON_VERSION=3.11` in environment
3. Check Railway/Render logs for detailed error messages

---

## Cost Summary

| Platform | Frontend | Backend | Total Monthly Cost |
|---|---|---|---|
| Vercel + Railway | Free ($0) | Free ($5 credit, renews) | **$0** |
| Vercel + Render | Free ($0) | Free (512MB, sleeps) | **$0** |
| Vercel + Google Cloud Run | Free ($0) | Free (2M reqs/mo) | **$0** |
| Docker Compose + Oracle VM | Free VM | Free VM | **$0** |

All options are **completely free** for demo/development use. Google Cloud Run and Oracle VM are the best options for always-on availability without cold starts.

---

## Recommended Setup for Hackathon Demo

Use **Option A (Vercel + Railway)** for the best balance of:

- ✅ **No cold starts** (Railway keeps warm for free tier)
- ✅ **Custom domains** (both platforms support them)
- ✅ **Easy deployment** (GitHub-connected, auto-deploys on push)
- ✅ **No credit card required** for Railway
- ✅ **HTTPS by default** on both platforms

Total setup time: **~30 minutes**