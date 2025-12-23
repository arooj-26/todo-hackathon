/**
 * Custom Better Auth API route handler
 * Intercepts auth requests and delegates to FastAPI backend
 *
 * This replaces Better Auth's default handlers with custom ones
 * that call the FastAPI backend for all authentication operations
 */
import { NextRequest, NextResponse } from "next/server"
import { customSignIn, customSignUp, customSignOut, syncSession } from "@/lib/auth/handlers"

/**
 * Handle POST requests (signin, signup, signout)
 */
export async function POST(req: NextRequest) {
  const url = new URL(req.url)
  const pathname = url.pathname

  try {
    // Handle sign-in requests
    if (pathname.includes("/signin") || pathname.includes("/sign-in")) {
      const { email, password } = await req.json()
      const response = await customSignIn(email, password)
      return NextResponse.json(response, { status: 200 })
    }

    // Handle sign-up requests
    if (pathname.includes("/signup") || pathname.includes("/sign-up")) {
      const { email, password } = await req.json()
      const response = await customSignUp(email, password)
      return NextResponse.json(response, { status: 201 })
    }

    // Handle sign-out requests
    if (pathname.includes("/signout") || pathname.includes("/sign-out") || pathname.includes("/logout")) {
      await customSignOut()
      return NextResponse.json({ success: true }, { status: 200 })
    }

    // Handle session check requests
    if (pathname.includes("/session")) {
      const user = await syncSession()
      return NextResponse.json({ user, session: user ? { user } : null }, { status: 200 })
    }

    // Unknown endpoint
    return NextResponse.json({ error: "Endpoint not found" }, { status: 404 })
  } catch (error: any) {
    console.error('[Better Auth API] Error:', error)
    return NextResponse.json(
      { error: error.message || "Authentication failed" },
      { status: error.response?.status || 500 }
    )
  }
}

/**
 * Handle GET requests (session validation)
 */
export async function GET(req: NextRequest) {
  const url = new URL(req.url)
  const pathname = url.pathname

  try {
    // Handle session check
    if (pathname.includes("/session")) {
      const user = await syncSession()
      return NextResponse.json({ user, session: user ? { user } : null }, { status: 200 })
    }

    // Unknown endpoint
    return NextResponse.json({ error: "Endpoint not found" }, { status: 404 })
  } catch (error: any) {
    console.error('[Better Auth API] Error:', error)
    return NextResponse.json(
      { error: error.message || "Request failed" },
      { status: 500 }
    )
  }
}
