import { NextResponse } from 'next/server';

/**
 * Health check endpoint for Docker container health monitoring
 * Returns 200 OK when the Next.js server is running and ready to serve requests
 */
export async function GET() {
  return NextResponse.json(
    {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      service: 'todo-frontend'
    },
    { status: 200 }
  );
}
