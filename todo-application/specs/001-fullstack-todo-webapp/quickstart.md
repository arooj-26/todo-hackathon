# Quickstart Guide: Todo Full-Stack Web Application

**Feature**: 001-fullstack-todo-webapp
**Last Updated**: 2025-12-17

## Overview

This guide helps you set up and run the Todo Full-Stack Web Application locally for development. The application consists of a Next.js frontend and FastAPI backend with PostgreSQL database.

## Prerequisites

### Required Software

- **Node.js**: 18.x or higher ([Download](https://nodejs.org/))
- **Python**: 3.11 or higher ([Download](https://www.python.org/downloads/))
- **npm**: 9.x or higher (comes with Node.js)
- **pip**: Latest version (comes with Python)
- **Git**: Latest version ([Download](https://git-scm.com/))

### External Services

- **Neon PostgreSQL Database**: Free serverless PostgreSQL instance ([Sign up](https://neon.tech/))

### Verify Installations

```bash
# Check Node.js version
node --version  # Should be v18.x or higher

# Check Python version
python --version  # Should be 3.11 or higher

# Check npm version
npm --version  # Should be 9.x or higher

# Check pip version
pip --version  # Should show latest version

# Check Git version
git --version  # Should show latest version
```

## Project Setup

### 1. Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd todo-application

# Checkout the feature branch
git checkout 001-fullstack-todo-webapp
```

### 2. Set Up Neon Database

1. Sign up at [neon.tech](https://neon.tech/)
2. Create a new project
3. Copy the connection string (looks like: `postgresql://user:password@host/database?sslmode=require`)
4. Save for environment configuration

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create `.env` file in `backend/` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# Security
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long-change-in-production

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Environment
ENVIRONMENT=development
```

**Important**:
- Replace `DATABASE_URL` with your Neon connection string
- Generate a strong random secret for `BETTER_AUTH_SECRET`:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

### 5. Initialize Database

```bash
# Run database migrations
alembic upgrade head

# Verify database connection
python -c "from database import engine; print('Database connected!')"
```

### 6. Start Backend Server

```bash
# Start FastAPI development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend should now be running at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs (Interactive API documentation)

## Frontend Setup

Open a new terminal window/tab for frontend.

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
# Install Node.js dependencies
npm install
```

### 3. Configure Environment Variables

Create `.env.local` file in `frontend/` directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_SECRET=same-secret-as-backend
BETTER_AUTH_URL=http://localhost:3000

# Environment
NODE_ENV=development
```

**Important**:
- Use the same `BETTER_AUTH_SECRET` as backend
- `NEXT_PUBLIC_API_URL` points to backend server

### 4. Start Frontend Server

```bash
# Start Next.js development server
npm run dev
```

Frontend should now be running at:
- Application: http://localhost:3000

## Verify Installation

### 1. Access Application

Open your browser and navigate to http://localhost:3000

### 2. Test Signup Flow

1. Click "Sign Up" button
2. Enter email: `test@example.com`
3. Enter password: `TestPass123!`
4. Click "Create Account"
5. Should redirect to dashboard

### 3. Test Task Creation

1. After signing in, enter a task description
2. Click "Add Task"
3. Task should appear in the list

### 4. Check API Documentation

Navigate to http://localhost:8000/docs to view interactive API documentation

## Development Workflow

### Running Tests

**Backend Tests**:
```bash
cd backend
pytest
```

**Frontend Tests**:
```bash
cd frontend
npm test
```

### Database Migrations

**Create New Migration**:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

**Apply Migrations**:
```bash
alembic upgrade head
```

**Rollback Migration**:
```bash
alembic downgrade -1
```

### Code Formatting

**Backend**:
```bash
cd backend
black .
isort .
```

**Frontend**:
```bash
cd frontend
npm run format
npm run lint
```

## Docker Setup (Optional)

For simplified local development with Docker:

### 1. Create docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - CORS_ORIGINS=http://localhost:3000
    volumes:
      - ./backend:/app
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev
```

### 2. Run with Docker

```bash
# Start all services
docker-compose up

# Stop all services
docker-compose down
```

## Troubleshooting

### Backend Issues

**Port 8000 already in use**:
```bash
# Find and kill process using port 8000
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

**Database connection error**:
- Verify DATABASE_URL is correct
- Check Neon database is running
- Ensure SSL mode is set (`?sslmode=require`)

**Module not found errors**:
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Port 3000 already in use**:
```bash
# Change port in package.json or use:
npm run dev -- -p 3001
```

**CORS errors in browser console**:
- Verify backend CORS_ORIGINS includes frontend URL
- Restart backend server after changing CORS_ORIGINS

**Environment variables not loading**:
- Ensure `.env.local` exists in frontend directory
- Restart frontend server after changes
- Variables starting with `NEXT_PUBLIC_` are accessible in browser

**Module not found errors**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Database Issues

**Alembic migration errors**:
```bash
# Reset migrations (WARNING: drops all data)
alembic downgrade base
alembic upgrade head
```

**Connection pool exhausted**:
- Reduce concurrent requests
- Increase pool_size in database.py
- Check for connection leaks

## Environment Variables Reference

### Backend (.env)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| DATABASE_URL | Yes | Neon PostgreSQL connection string | postgresql://user:pass@host/db?sslmode=require |
| BETTER_AUTH_SECRET | Yes | Secret key for JWT signing (32+ chars) | your-secret-key-here |
| CORS_ORIGINS | Yes | Allowed frontend origins (comma-separated) | http://localhost:3000 |
| ENVIRONMENT | No | Environment name | development |

### Frontend (.env.local)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Yes | Backend API base URL | http://localhost:8000 |
| BETTER_AUTH_SECRET | Yes | Same as backend secret | your-secret-key-here |
| BETTER_AUTH_URL | Yes | Frontend base URL | http://localhost:3000 |
| NODE_ENV | No | Node environment | development |

## Useful Commands

### Backend

```bash
# Start development server
uvicorn main:app --reload

# Run tests with coverage
pytest --cov=.

# Format code
black . && isort .

# Type checking
mypy .

# Create database backup
pg_dump $DATABASE_URL > backup.sql
```

### Frontend

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test

# Run linter
npm run lint

# Format code
npm run format
```

## Next Steps

1. Read [API Documentation](./contracts/) for endpoint details
2. Review [Data Model](./data-model.md) for database schema
3. Check [Feature Specification](./spec.md) for requirements
4. See [Implementation Plan](./plan.md) for architecture

## Support

For issues or questions:
1. Check this quickstart guide
2. Review troubleshooting section
3. Check API documentation at http://localhost:8000/docs
4. Consult feature specification and implementation plan
