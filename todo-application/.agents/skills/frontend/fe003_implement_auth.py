"""
Skill FE-003: Implement Better Auth

Sets up Better Auth with JWT strategy in Next.js application.
"""

from pathlib import Path
from typing import List
from ...lib.skill_base import (
    Skill,
    SkillMetadata,
    SkillInput,
    SkillOutput,
    SkillStatus,
    register_skill
)


@register_skill
class ImplementBetterAuthSkill(Skill):
    """Implement Better Auth in Next.js."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="FE-003",
            name="Implement Better Auth",
            description="Set up Better Auth with JWT strategy in Next.js application",
            category="frontend",
            version="1.0.0",
            dependencies=["FE-001"],
            inputs_schema={
                "type": "object",
                "properties": {
                    "backend_url": {
                        "type": "string",
                        "default": "http://localhost:8000"
                    }
                },
                "required": []
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "auth_config_path": {"type": "string"},
                    "middleware_path": {"type": "string"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        frontend_path = Path("frontend")
        if not frontend_path.exists():
            return False, "Frontend directory does not exist. Run FE-001 first."

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        backend_url = params.get("backend_url", "http://localhost:8000")

        try:
            frontend_path = Path("frontend")
            lib_path = frontend_path / "lib"
            lib_path.mkdir(parents=True, exist_ok=True)

            # Create auth configuration
            auth_config_path = lib_path / "auth.ts"
            auth_config_code = f"""import {{ createAuth }} from 'better-auth'

export const auth = createAuth({{
  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  session: {{
    cookieOptions: {{
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 86400 // 24 hours
    }}
  }},
  jwt: {{
    expiresIn: '24h'
  }},
  // Custom backend integration
  trustedOrigins: ['{backend_url}'],
}})

export type Session = typeof auth.$Infer.Session
"""

            auth_config_path.write_text(auth_config_code, encoding="utf-8")
            self.logger.info(f"Created auth config: {{auth_config_path}}")

            # Create auth client
            auth_client_path = lib_path / "auth-client.ts"
            auth_client_code = """import { createAuthClient } from 'better-auth/client'

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
})

export const { signIn, signUp, signOut, useSession } = authClient
"""

            auth_client_path.write_text(auth_client_code, encoding="utf-8")
            self.logger.info(f"Created auth client: {auth_client_path}")

            # Create middleware for route protection
            middleware_path = frontend_path / "middleware.ts"
            middleware_code = """import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Public routes that don't require authentication
const publicRoutes = ['/signin', '/signup', '/']

export function middleware(request: NextRequest) {
  const token = request.cookies.get('better-auth.session_token')?.value
  const { pathname } = request.nextUrl

  // Check if route is public
  const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route))

  // Redirect to signin if not authenticated and trying to access protected route
  if (!token && !isPublicRoute) {
    const signinUrl = new URL('/signin', request.url)
    signinUrl.searchParams.set('from', pathname)
    return NextResponse.redirect(signinUrl)
  }

  // Redirect to dashboard if authenticated and trying to access signin/signup
  if (token && (pathname === '/signin' || pathname === '/signup')) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public).*)',
  ],
}
"""

            middleware_path.write_text(middleware_code, encoding="utf-8")
            self.logger.info(f"Created middleware: {middleware_path}")

            # Create environment template
            env_template_path = frontend_path / ".env.example"
            env_template = f"""# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key-here-change-in-production
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Backend API URL
NEXT_PUBLIC_API_URL={backend_url}
"""

            env_template_path.write_text(env_template, encoding="utf-8")
            self.logger.info(f"Created .env.example: {env_template_path}")

            artifacts = [
                str(auth_config_path),
                str(auth_client_path),
                str(middleware_path),
                str(env_template_path)
            ]

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "auth_config_path": str(auth_config_path),
                    "middleware_path": str(middleware_path)
                },
                artifacts=artifacts,
                logs=[f"Created {len(artifacts)} auth files"]
            )

        except Exception as e:
            self.logger.exception("Failed to implement Better Auth")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Auth config created in lib/auth.ts",
            "Auth client created in lib/auth-client.ts",
            "Middleware created for route protection",
            "Environment template created (.env.example)",
            "JWT session configured with 24h expiry",
            "Public and protected routes defined"
        ]
