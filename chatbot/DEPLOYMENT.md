# Deployment Guide: AI-Powered Todo Chatbot

This guide covers deploying the Todo AI Chatbot to production.

## Prerequisites

1. **Neon PostgreSQL Database**
   - Sign up at [neon.tech](https://neon.tech)
   - Create a new database
   - Note the connection string

2. **OpenAI API Key**
   - Get API key from [platform.openai.com](https://platform.openai.com)
   - Ensure GPT-4o access

3. **Deployment Platforms**
   - Backend: Render, Railway, or similar
   - Frontend: Vercel, Netlify, or similar

## Backend Deployment

### Option 1: Railway

1. **Create Railway Account** at [railway.app](https://railway.app)

2. **Create New Project**
   ```bash
   railway init
   ```

3. **Set Environment Variables**
   ```bash
   railway variables set DATABASE_URL="postgresql://..."
   railway variables set OPENAI_API_KEY="sk-..."
   railway variables set FRONTEND_URL="https://your-frontend.vercel.app"
   ```

4. **Deploy**
   ```bash
   railway up
   ```

### Option 2: Render

1. **Create New Web Service** at [render.com](https://render.com)

2. **Configure Service**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   - `DATABASE_URL`: Your Neon connection string
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `FRONTEND_URL`: Your frontend URL

### Database Migration

Run the initial schema migration:

```bash
# Connect to your Neon database
psql $DATABASE_URL

# Run the migration script
\i backend/migrations/001_initial_schema.sql
```

Or use the migration file directly with:

```bash
cd backend
python -c "
from sqlmodel import SQLModel, create_engine
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message
import os

engine = create_engine(os.getenv('DATABASE_URL'))
SQLModel.metadata.create_all(engine)
print('Database schema created successfully!')
"
```

## Frontend Deployment

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Configure Environment Variables**
   Create `.env.local` in frontend directory:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```

3. **Deploy**
   ```bash
   cd frontend
   vercel --prod
   ```

4. **Set Environment Variable in Vercel Dashboard**
   - Go to project settings
   - Add `NEXT_PUBLIC_API_URL` with your backend URL

### Netlify Deployment

1. **Create `netlify.toml`** in frontend directory:
   ```toml
   [build]
     command = "npm run build"
     publish = ".next"

   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   ```

2. **Deploy via Netlify CLI or GitHub integration**

## Environment Variables Summary

### Backend
- `DATABASE_URL`: PostgreSQL connection string from Neon
- `OPENAI_API_KEY`: Your OpenAI API key
- `FRONTEND_URL`: URL of deployed frontend (for CORS)

### Frontend
- `NEXT_PUBLIC_API_URL`: URL of deployed backend

## Health Checks

Your backend provides health check endpoints:

- **Health Check**: `GET /health`
- **API Documentation**: `GET /docs`

Configure your hosting platform to use `/health` for health checks.

## Monitoring

### Logging

The application logs all requests and errors. Configure your platform to collect logs:

- **Railway**: View logs in dashboard
- **Render**: View logs in dashboard
- **Vercel**: View logs in deployment logs

### Performance Monitoring

Monitor these metrics:
- Response time (target: <3s for simple operations)
- Error rate (target: <1%)
- Database connection pool usage

## Scaling

### Backend Scaling

The stateless architecture allows horizontal scaling:
- Increase instance count in your platform dashboard
- All state is in the database (Neon handles connection pooling)

### Database Scaling

Neon automatically scales:
- Connection pooling included
- Autoscaling storage
- Branch for development/staging

### Rate Limiting

Built-in rate limiting:
- 60 requests/minute per user
- Configurable in `src/api/middleware.py`

For production, consider Redis-based rate limiting.

## Security Checklist

- [ ] Use HTTPS (enforced by Vercel/Railway/Render)
- [ ] Secure API keys in environment variables (never in code)
- [ ] Enable CORS only for your frontend domain
- [ ] Use Neon connection pooling
- [ ] Enable database SSL (Neon default)
- [ ] Monitor for unusual activity
- [ ] Set up alerts for errors

## Troubleshooting

### Backend Issues

**Database Connection Errors**
- Verify `DATABASE_URL` is correct
- Check Neon database status
- Ensure IP allowlist includes your host

**OpenAI API Errors**
- Verify API key is valid
- Check OpenAI usage limits
- Ensure GPT-4o access

**CORS Errors**
- Update `FRONTEND_URL` environment variable
- Check frontend URL matches exactly (no trailing slash)

### Frontend Issues

**API Connection Errors**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend is running and healthy
- Inspect browser console for CORS errors

## Cost Estimates

### Development/MVP
- **Neon**: Free tier (1GB storage, 100 hours compute/month)
- **Railway**: $5-10/month
- **Vercel**: Free tier
- **OpenAI**: ~$10-20/month (depends on usage)

**Total**: ~$15-30/month

### Production (100-1000 users)
- **Neon**: ~$20/month
- **Railway**: ~$20-50/month
- **Vercel**: Free or Pro ($20/month)
- **OpenAI**: ~$50-200/month

**Total**: ~$90-290/month

## Backup & Disaster Recovery

### Database Backups
- Neon provides automatic backups
- Enable point-in-time recovery
- Test restore process monthly

### Code Backups
- Use Git for version control
- Keep production branch protected
- Tag releases

## Next Steps

After deployment:
1. Test all features in production
2. Set up error monitoring (Sentry, etc.)
3. Configure analytics (optional)
4. Create backup strategy
5. Document runbooks for common issues
6. Set up staging environment

## Support

For issues:
- Backend API: Check `/docs` endpoint
- Health status: Check `/health` endpoint
- Logs: View in platform dashboard
- Database: Check Neon dashboard
