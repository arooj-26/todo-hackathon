# Research: Todo Full-Stack Web Application

**Feature**: 001-fullstack-todo-webapp
**Date**: 2025-12-17
**Purpose**: Resolve technical unknowns and document architectural decisions

## Research Topics

### 1. Better Auth Integration with Next.js 16+ App Router

**Decision**: Use Better Auth with JWT strategy for session management

**Rationale**:
- Better Auth is designed for modern Next.js applications with first-class App Router support
- Supports server components and server actions out of the box
- Built-in JWT token generation, validation, and secure storage
- Handles password hashing securely using bcrypt
- Provides TypeScript types and excellent DX
- Actively maintained and production-ready

**Implementation Approach**:
1. Install Better Auth: `npm install better-auth`
2. Configure in `frontend/lib/auth.ts`:
   ```typescript
   import { createAuth } from 'better-auth'

   export const auth = createAuth({
     secret: process.env.BETTER_AUTH_SECRET,
     session: {
       cookieOptions: {
         httpOnly: true,
         secure: process.env.NODE_ENV === 'production',
         sameSite: 'lax'
       }
     },
     jwt: {
       expiresIn: '24h'
     }
   })
   ```
3. Create API routes in `app/api/auth/[...better-auth]/route.ts` for callbacks
4. Store JWT in httpOnly cookies for XSS protection
5. Implement client-side hooks for auth state management

**Security Considerations**:
- HttpOnly cookies prevent JavaScript access (XSS protection)
- Secure flag in production (HTTPS only)
- SameSite=lax protects against CSRF
- 24-hour token expiration balances security and UX

**Alternatives Considered**:
- **NextAuth.js**: More features but overkill for simple JWT needs; heavier bundle size; more complex configuration
- **Custom JWT implementation**: Reinventing the wheel; high risk of security vulnerabilities; requires extensive testing
- **Supabase Auth**: External service dependency; not aligned with Neon PostgreSQL choice; adds complexity

**Resources**:
- Better Auth Documentation: https://www.better-auth.com/docs
- Next.js Authentication Patterns: https://nextjs.org/docs/app/building-your-application/authentication

---

### 2. FastAPI JWT Verification Best Practices

**Decision**: Use python-jose for JWT encoding/decoding with HS256 algorithm

**Rationale**:
- python-jose is FastAPI's officially recommended JWT library
- Well-maintained with active community and security updates
- Supports multiple algorithms (HS256 suitable for our use case)
- Clean, Pythonic API for token creation and validation
- Handles expiration, claims validation, and signature verification automatically
- Integrates seamlessly with FastAPI dependency injection

**Implementation Approach**:

1. Install dependencies:
   ```bash
   pip install python-jose[cryptography] passlib[bcrypt]
   ```

2. Create JWT utilities in `backend/auth/jwt.py`:
   ```python
   from jose import JWTError, jwt
   from datetime import datetime, timedelta

   SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
   ALGORITHM = "HS256"

   def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=24)):
       to_encode = data.copy()
       expire = datetime.utcnow() + expires_delta
       to_encode.update({"exp": expire})
       return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

   def verify_token(token: str) -> dict:
       payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
       return payload
   ```

3. Create FastAPI dependency in `backend/dependencies.py`:
   ```python
   from fastapi import Depends, HTTPException, status
   from fastapi.security import HTTPBearer

   security = HTTPBearer()

   async def get_current_user(token: str = Depends(security)):
       try:
           payload = verify_token(token.credentials)
           user_id: int = payload.get("sub")
           if user_id is None:
               raise HTTPException(status_code=401)
           return user_id
       except JWTError:
           raise HTTPException(status_code=401)
   ```

4. Use dependency in route handlers to get authenticated user_id

**Security Considerations**:
- Use strong secret key (minimum 32 characters, randomly generated)
- Store secret in environment variable, never in code
- Set appropriate token expiration (24 hours balances security and UX)
- Include minimal claims in payload (user_id, expiration)
- Use HS256 algorithm (symmetric key suitable for single backend)
- Validate token signature on every request via dependency injection

**Token Payload Structure**:
```json
{
  "sub": 123,           // user_id (subject)
  "exp": 1735300800     // expiration timestamp
}
```

**Alternatives Considered**:
- **PyJWT**: Less FastAPI-specific documentation; python-jose is FastAPI's official recommendation
- **Authlib**: More comprehensive but overkill for JWT-only needs
- **Custom JWT**: High security risk; complex to implement correctly

**Resources**:
- python-jose Documentation: https://python-jose.readthedocs.io/
- FastAPI Security Tutorial: https://fastapi.tiangolo.com/tutorial/security/
- JWT Best Practices: https://tools.ietf.org/html/rfc8725

---

### 3. SQLModel Schema Design for Multi-Tenancy

**Decision**: User and Task models with foreign key relationship, indexes, and timestamps

**Rationale**:
- SQLModel combines SQLAlchemy (ORM power) with Pydantic (validation and FastAPI integration)
- Type-safe model definitions work seamlessly with FastAPI request/response schemas
- Foreign key constraints enforce referential integrity at database level
- Indexes on user_id and email enable fast queries
- Timestamps (created_at, updated_at) provide audit trail
- Aligns with FastAPI ecosystem and Python type hints

**Database Schema**:

```python
# backend/models.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    description: str = Field(nullable=False)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: Optional[User] = Relationship(back_populates="tasks")
```

**Index Strategy**:
- `users.email`: Unique index for fast login lookups (email is username)
- `tasks.user_id`: Index for fast filtering by user (most common query)
- Primary keys automatically indexed

**Data Constraints**:
- Email must be unique (enforced at database level)
- Password hash required (no plaintext passwords)
- User_id foreign key with cascade delete (removing user removes their tasks)
- Description required (no empty tasks)
- Completed defaults to False

**Migration Strategy**:
1. Use Alembic for schema migrations (SQLModel/SQLAlchemy compatible)
2. Initial migration creates both tables with all constraints
3. Add indexes in same migration for immediate performance
4. Future migrations for schema evolution

**Alembic Setup**:
```bash
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

**Alternatives Considered**:
- **Django ORM**: Requires Django framework; overkill for API-only backend
- **Tortoise ORM**: Less mature; smaller ecosystem; async-first can be overkill
- **Raw SQL**: No type safety; more boilerplate; higher maintenance; SQL injection risks

**Resources**:
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- Alembic Documentation: https://alembic.sqlalchemy.org/
- PostgreSQL Indexes Guide: https://www.postgresql.org/docs/current/indexes.html

---

### 4. Next.js App Router Patterns for Protected Routes

**Decision**: Use middleware for route protection with cookie-based auth checks

**Rationale**:
- Next.js middleware runs on Edge Runtime before page rendering
- Centralized auth logic eliminates per-page boilerplate
- Can read cookies and redirect before expensive page renders
- Works with both server and client components
- Minimal performance impact (runs on Edge)

**Implementation Approach**:

1. Create `middleware.ts` at app root:
   ```typescript
   import { NextResponse } from 'next/server'
   import type { NextRequest } from 'next/server'

   export function middleware(request: NextRequest) {
     const token = request.cookies.get('better-auth.session')
     const { pathname } = request.nextUrl

     // Public routes
     const publicRoutes = ['/signin', '/signup']
     if (publicRoutes.includes(pathname)) {
       // Redirect to dashboard if already authenticated
       if (token) {
         return NextResponse.redirect(new URL('/', request.url))
       }
       return NextResponse.next()
     }

     // Protected routes
     if (!token) {
       return NextResponse.redirect(new URL('/signin', request.url))
     }

     return NextResponse.next()
   }

   export const config = {
     matcher: ['/', '/tasks/:path*', '/signin', '/signup']
   }
   ```

2. Protected routes (require authentication):
   - `/` (task dashboard)
   - `/tasks/*` (task details and actions)

3. Public routes (accessible without auth):
   - `/signin` (login page)
   - `/signup` (registration page)

4. Smart redirects:
   - Unauthenticated users accessing protected routes → `/signin`
   - Authenticated users accessing auth pages → `/` (dashboard)

**User Experience Flow**:
1. User visits `/` without token → Redirect to `/signin`
2. User signs in → Token stored in cookie → Redirect to `/`
3. User can now access all protected routes
4. User signs out → Token cleared → Redirect to `/signin`

**Alternatives Considered**:
- **Per-page auth checks**: Repetitive code; easy to forget; inconsistent experience
- **Higher-order components**: Client-side only; flashing of unauthorized content
- **Server component checks**: Still requires duplication across pages

**Resources**:
- Next.js Middleware: https://nextjs.org/docs/app/building-your-application/routing/middleware
- Edge Runtime: https://nextjs.org/docs/app/api-reference/edge

---

### 5. API Client Pattern with Token Management

**Decision**: Axios-based API client with interceptors for automatic token injection and error handling

**Rationale**:
- Axios interceptors provide clean way to inject auth headers globally
- Centralized error handling for 401/403 responses
- Support for request/response transformations
- Works seamlessly with TypeScript
- Battle-tested in production applications

**Implementation Approach**:

1. Create API client in `frontend/lib/api.ts`:
   ```typescript
   import axios from 'axios'
   import { getCookie } from 'cookies-next'

   const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

   export const apiClient = axios.create({
     baseURL: API_BASE_URL,
     withCredentials: true
   })

   // Request interceptor: Add JWT token
   apiClient.interceptors.request.use(
     (config) => {
       const token = getCookie('better-auth.session')
       if (token) {
         config.headers.Authorization = `Bearer ${token}`
       }
       return config
     },
     (error) => Promise.reject(error)
   )

   // Response interceptor: Handle errors
   apiClient.interceptors.response.use(
     (response) => response,
     (error) => {
       if (error.response?.status === 401) {
         // Token invalid or expired - redirect to signin
         window.location.href = '/signin'
       }
       return Promise.reject(error)
     }
   )
   ```

2. Create typed API functions:
   ```typescript
   export const tasksApi = {
     list: (userId: number) =>
       apiClient.get(`/api/${userId}/tasks`),

     create: (userId: number, description: string) =>
       apiClient.post(`/api/${userId}/tasks`, { description }),

     get: (userId: number, taskId: number) =>
       apiClient.get(`/api/${userId}/tasks/${taskId}`),

     update: (userId: number, taskId: number, description: string) =>
       apiClient.put(`/api/${userId}/tasks/${taskId}`, { description }),

     toggleComplete: (userId: number, taskId: number) =>
       apiClient.patch(`/api/${userId}/tasks/${taskId}/complete`),

     delete: (userId: number, taskId: number) =>
       apiClient.delete(`/api/${userId}/tasks/${taskId}`)
   }
   ```

**Error Handling Strategy**:
- **401 Unauthorized**: Clear token, redirect to `/signin` (token invalid/expired)
- **403 Forbidden**: Show "Permission denied" message (user accessing wrong resource)
- **500 Server Error**: Show "Something went wrong, please try again" message
- **Network errors**: Show "Cannot connect to server" message

**Type Safety**:
- Define TypeScript interfaces for all request/response types
- Use generics in axios calls for type-safe responses
- Export typed functions instead of raw axios calls

**Alternatives Considered**:
- **fetch API**: No interceptors; more boilerplate; manual error handling; less features
- **tRPC**: Requires backend changes; overkill for REST API; additional learning curve
- **React Query**: Data fetching library, not HTTP client (can be used with Axios)

**Resources**:
- Axios Documentation: https://axios-http.com/docs/intro
- Axios Interceptors Guide: https://axios-http.com/docs/interceptors

---

### 6. CORS Configuration for Local Development

**Decision**: FastAPI CORS middleware with specific origin allowlist

**Rationale**:
- Frontend (localhost:3000) and backend (localhost:8000) are different origins
- CORS headers required for browser to allow requests
- Must allow credentials (cookies with JWT)
- Specific origin list more secure than wildcard
- Production will use environment-based configuration

**Configuration**:

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

**Environment Variables**:
- **Development**: `CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000`
- **Production**: `CORS_ORIGINS=https://yourdomain.com` (actual domain)

**Security Considerations**:
- Never use `allow_origins=["*"]` with `allow_credentials=True` (security risk)
- Specific origin list prevents unauthorized domains
- Only allow necessary HTTP methods
- Production origins set via environment variable

**Preflight Requests**:
- Browser sends OPTIONS request before actual request
- CORS middleware handles preflight automatically
- Response includes Access-Control-Allow-* headers

**Alternatives Considered**:
- **Proxy in Next.js**: Adds latency; doesn't work with static export; complex configuration
- **Same-origin deployment**: Not suitable for local development; limits deployment options

**Resources**:
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/
- CORS Explained: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

---

### 7. Neon Serverless PostgreSQL Connection Management

**Decision**: Use SQLModel engine with connection pooling via asyncpg driver

**Rationale**:
- Neon provides PostgreSQL-compatible serverless database
- Connection pooling reduces overhead and improves performance
- Asyncpg is fastest PostgreSQL driver for Python
- SQLModel provides sync interface over async driver
- Automatic connection management via dependency injection

**Implementation Approach**:

1. Database configuration in `backend/database.py`:
   ```python
   from sqlmodel import create_engine, SQLModel, Session
   import os

   DATABASE_URL = os.getenv("DATABASE_URL")

   # Connection pool configuration
   engine = create_engine(
       DATABASE_URL,
       echo=False,  # Set True for SQL logging in development
       pool_size=10,  # Number of connections to maintain
       max_overflow=20,  # Additional connections allowed under load
       pool_recycle=3600,  # Recycle connections after 1 hour
       pool_pre_ping=True,  # Verify connection health before using
   )

   def init_db():
       SQLModel.metadata.create_all(engine)

   def get_session():
       with Session(engine) as session:
           yield session
   ```

2. Use dependency injection in routes:
   ```python
   from fastapi import Depends
   from sqlmodel import Session

   @app.get("/api/{user_id}/tasks")
   async def list_tasks(
       user_id: int,
       session: Session = Depends(get_session),
       current_user_id: int = Depends(get_current_user)
   ):
       # Use session to query database
       pass
   ```

**Connection Pool Parameters**:
- `pool_size=10`: 10 persistent connections (suitable for moderate load)
- `max_overflow=20`: Up to 30 total connections under peak load
- `pool_recycle=3600`: Recycle after 1 hour (Neon timeout is longer, but good practice)
- `pool_pre_ping=True`: Verify connection before use (prevents stale connections)

**Connection String Format**:
```
postgresql://[user]:[password]@[host]/[database]?sslmode=require
```

**Session Management**:
1. Session created per request via dependency injection
2. Automatic commit on successful response
3. Automatic rollback on exception
4. Connection returned to pool after request

**Neon-Specific Considerations**:
- Neon supports PostgreSQL 14+ features
- Automatic scaling handles load spikes
- Connectionpooling works seamlessly with Neon's architecture
- SSL required (`sslmode=require` in connection string)

**Environment Variables**:
```bash
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Alternatives Considered**:
- **Direct asyncpg**: More complex; FastAPI sync functions easier; SQLModel simplifies
- **psycopg2**: Slower than asyncpg; synchronous only; older
- **No connection pooling**: Poor performance; connection overhead; resource waste

**Resources**:
- Neon Documentation: https://neon.tech/docs
- SQLModel Database Sessions: https://sqlmodel.tiangelo.com/tutorial/fastapi/session/
- Connection Pooling Best Practices: https://www.postgresql.org/docs/current/runtime-config-connection.html

---

## Summary

All research complete. Key technical decisions documented with rationale and implementation details. No blockers identified. Architecture aligns with constitutional principles and feature requirements.

**Next Steps**: Proceed to Phase 1 (Data Model and Contracts)
