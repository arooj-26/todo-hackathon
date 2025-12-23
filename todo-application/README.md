# Todo Full-Stack Web Application

A modern, full-stack todo application built with Next.js, FastAPI, and PostgreSQL. Features user authentication, real-time task management, and a responsive UI.

## Features

- ✅ **User Authentication**: Secure signup/signin with JWT tokens
- ✅ **Task Management**: Create, read, update, delete, and toggle tasks
- ✅ **Multi-User Support**: Each user has their own isolated task list
- ✅ **Real-time Updates**: Immediate UI feedback for all operations
- ✅ **Responsive Design**: Works seamlessly on desktop and mobile devices
- ✅ **Form Validation**: Client and server-side validation for data integrity
- ✅ **Error Handling**: Comprehensive error boundaries and user-friendly messages
- ✅ **Loading States**: Skeleton loaders for better UX

## Tech Stack

### Frontend
- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **HTTP Client**: Axios
- **Authentication**: JWT tokens

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: JWT with python-jose
- **Password Hashing**: passlib with bcrypt

### Testing
- **Frontend**: Jest + React Testing Library
- **Backend**: pytest + httpx

## Project Structure

```
todo-application/
├── frontend/              # Next.js frontend application
│   ├── app/              # Next.js App Router pages
│   ├── components/       # React components
│   ├── lib/              # API clients and utilities
│   ├── types/            # TypeScript type definitions
│   └── hooks/            # Custom React hooks
├── backend/              # FastAPI backend application
│   ├── app/              # Application code
│   │   ├── routers/      # API endpoints
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── auth/         # Authentication logic
│   ├── alembic/          # Database migrations
│   └── tests/            # Backend tests
├── specs/                # Feature specifications
├── .agents/              # Multi-agent orchestration system
└── docker-compose.yml    # Docker composition for local development
```

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11 or 3.12 (Recommended for Windows users)
- **PostgreSQL** database (optional - SQLite works for development)
- **Docker** and Docker Compose (optional, for containerized development)

## 🪟 Windows Users - Quick Start (No PostgreSQL Required!)

**Good news!** The project is pre-configured to use SQLite on Windows, so you don't need PostgreSQL installed.

### Backend Setup (Windows)

1. **Install Python packages** (should work without errors now):
   ```powershell
   cd backend
   pip install -r requirements.txt
   ```

2. **The `.env` file is already configured** with SQLite:
   ```env
   DATABASE_URL=sqlite:///./todo_dev.db
   ```
   No changes needed! ✅

3. **Run migrations**:
   ```powershell
   alembic upgrade head
   ```

4. **Start the server**:
   ```powershell
   uvicorn app.main:app --reload
   ```

5. **Access the API**:
   - API Docs: http://localhost:8000/api/docs
   - Health: http://localhost:8000/health

### Troubleshooting Windows Installation

**If you still get errors installing packages:**

1. **Upgrade pip first**:
   ```powershell
   python -m pip install --upgrade pip setuptools wheel
   ```

2. **Install individually** (if batch install fails):
   ```powershell
   pip install fastapi uvicorn sqlmodel pg8000 alembic
   pip install python-jose passlib python-multipart
   pip install pydantic-settings pytest httpx python-dotenv
   ```

3. **Check Python version** (3.11 or 3.12 recommended):
   ```powershell
   python --version
   ```

**The `pg8000` driver is pure Python** (no compilation required) and works perfectly on Windows!

### Switching to PostgreSQL Later

When ready for production, just update `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql+pg8000://user:pass@host:5432/db
```

---

## Getting Started (All Platforms)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd todo-application
```

### 2. Backend Setup

#### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# Security
SECRET_KEY=your-secret-key-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# CORS
ALLOWED_ORIGINS=["http://localhost:3000"]

# Application
PROJECT_NAME=Todo API
VERSION=1.0.0
API_PREFIX=/api
ENVIRONMENT=development
```

#### Run Database Migrations

```bash
alembic upgrade head
```

#### Start the Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/api/docs`
- Alternative Docs: `http://localhost:8000/api/redoc`

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Configure Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
NEXT_PUBLIC_ENVIRONMENT=development
```

#### Start the Frontend Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### 4. Using Docker Compose (Alternative)

For a containerized setup:

```bash
docker-compose up -d
```

This will start:
- Frontend on `http://localhost:3000`
- Backend on `http://localhost:8000`
- PostgreSQL database on `localhost:5432`

## API Endpoints

### Authentication

- `POST /auth/signup` - Create a new user account
- `POST /auth/signin` - Sign in and receive JWT token
- `POST /auth/signout` - Sign out (client-side token removal)
- `GET /auth/me` - Get current user information

### Tasks

- `GET /api/{user_id}/tasks` - Get all tasks for a user
- `POST /api/{user_id}/tasks` - Create a new task
- `GET /api/{user_id}/tasks/{task_id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{task_id}` - Update a task
- `PATCH /api/{user_id}/tasks/{task_id}/toggle` - Toggle task completion
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete a task

All task endpoints require authentication via JWT token in the `Authorization` header.

## Testing

### Backend Tests

```bash
cd backend
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
```

Run with coverage:

```bash
npm test -- --coverage
```

## Development Workflow

1. **Feature Development**: Create a specification in `specs/<feature>/spec.md`
2. **Planning**: Document architecture in `specs/<feature>/plan.md`
3. **Task Breakdown**: Define tasks in `specs/<feature>/tasks.md`
4. **Implementation**: Build features following the task list
5. **Testing**: Write and run tests for each task
6. **Review**: Ensure code follows constitutional principles in `.specify/memory/constitution.md`

## Environment Variables

### Backend

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `SECRET_KEY` | JWT secret key | Yes | - |
| `ALGORITHM` | JWT algorithm | No | HS256 |
| `ACCESS_TOKEN_EXPIRE_HOURS` | Token expiration time | No | 24 |
| `ALLOWED_ORIGINS` | CORS allowed origins (JSON array) | Yes | - |
| `ENVIRONMENT` | Environment (development/production) | No | development |

### Frontend

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes | - |
| `NEXT_PUBLIC_APP_URL` | Frontend app URL | Yes | - |
| `BETTER_AUTH_SECRET` | Auth secret key | Yes | - |
| `NEXT_PUBLIC_ENVIRONMENT` | Environment | No | development |

## Deployment

### Backend Deployment

1. Set environment variables in your hosting platform
2. Run database migrations: `alembic upgrade head`
3. Start the server: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

Recommended platforms:
- Railway
- Render
- Fly.io
- AWS (EC2/ECS)
- DigitalOcean App Platform

### Frontend Deployment

1. Set environment variables
2. Build the application: `npm run build`
3. Start the server: `npm start`

Recommended platforms:
- Vercel (optimized for Next.js)
- Netlify
- Railway
- Render

### Database

Recommended PostgreSQL providers:
- **Neon** (Serverless PostgreSQL)
- Supabase
- Railway
- Render
- AWS RDS

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security

- Never commit `.env` files
- Always use HTTPS in production
- Regularly update dependencies
- Review the security guide in `backend/CLAUDE.md` and `frontend/CLAUDE.md`

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the documentation in `/specs`
- Review CLAUDE.md files for development guidance
- Open an issue on GitHub

## Roadmap

- [ ] Add task categories/tags
- [ ] Implement task priorities
- [ ] Add due dates and reminders
- [ ] Enable task sharing between users
- [ ] Add real-time collaboration
- [ ] Implement dark mode
- [ ] Add mobile applications (React Native)
- [ ] Enable offline support with service workers

---

**Built with** ❤️ **using Claude Code and Spec-Driven Development**
