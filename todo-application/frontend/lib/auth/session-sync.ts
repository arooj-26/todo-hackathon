/**
 * Session synchronization between FastAPI tokens and Better Auth session state
 * This utility bridges the gap between FastAPI JWT tokens and Better Auth session management
 */
import { getCurrentUser } from '@/lib/api/auth'
import { User } from '@/types/auth'

/**
 * Session synchronization singleton class
 * Manages session state and validation between FastAPI and Better Auth
 */
export class SessionSync {
  private static instance: SessionSync
  private user: User | null = null
  private isValidating = false
  private lastValidation: number = 0
  private readonly VALIDATION_CACHE_MS = 60000 // Cache for 1 minute

  /**
   * Get singleton instance of SessionSync
   */
  static getInstance(): SessionSync {
    if (!SessionSync.instance) {
      SessionSync.instance = new SessionSync()
    }
    return SessionSync.instance
  }

  /**
   * Validate current session with FastAPI
   * Caches result for VALIDATION_CACHE_MS to avoid unnecessary API calls
   *
   * @param force - Force validation even if cached result exists
   * @returns Current user if authenticated, null otherwise
   */
  async validate(force: boolean = false): Promise<User | null> {
    const now = Date.now()

    // Return cached result if still valid
    if (!force && this.user && (now - this.lastValidation) < this.VALIDATION_CACHE_MS) {
      return this.user
    }

    // Prevent multiple simultaneous validations
    if (this.isValidating) {
      return this.user
    }

    this.isValidating = true

    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
      if (!token) {
        this.user = null
        this.lastValidation = now
        return null
      }

      // Validate with FastAPI /auth/me endpoint
      const user = await getCurrentUser()
      this.user = user
      this.lastValidation = now
      return user
    } catch (error) {
      // Token invalid or expired
      this.user = null
      this.lastValidation = now
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token')
      }
      return null
    } finally {
      this.isValidating = false
    }
  }

  /**
   * Get current user from cache (doesn't validate with server)
   *
   * @returns Cached user or null
   */
  getUser(): User | null {
    return this.user
  }

  /**
   * Set current user in cache
   *
   * @param user - User to cache
   */
  setUser(user: User | null): void {
    this.user = user
    this.lastValidation = Date.now()
  }

  /**
   * Clear session cache and remove token from localStorage
   */
  clear(): void {
    this.user = null
    this.lastValidation = 0
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
    }
  }

  /**
   * Check if session is currently being validated
   *
   * @returns true if validation is in progress
   */
  isValidationInProgress(): boolean {
    return this.isValidating
  }

  /**
   * Check if cached session is still fresh
   *
   * @returns true if cache is fresh (within VALIDATION_CACHE_MS)
   */
  isCacheFresh(): boolean {
    return (Date.now() - this.lastValidation) < this.VALIDATION_CACHE_MS
  }
}

/**
 * Export singleton instance for convenience
 */
export const sessionSync = SessionSync.getInstance()
