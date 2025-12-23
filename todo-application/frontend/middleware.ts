/**
 * Next.js middleware for route protection
 *
 * DISABLED: Auth is handled client-side with localStorage tokens
 * Server-side middleware cannot access localStorage, so we use
 * client-side auth guards in the dashboard page instead.
 */
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Middleware disabled - using client-side auth guards
  return NextResponse.next()
}

export const config = {
  matcher: ['/', '/dashboard/:path*', '/auth/:path*'],
}
