"""
Skill FE-004: Create API Client

Creates an Axios-based API client with authentication and error handling.
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
class CreateAPIClientSkill(Skill):
    """Create API client for backend communication."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="FE-004",
            name="Create API Client",
            description="Create Axios-based API client with authentication and error handling",
            category="frontend",
            version="1.0.0",
            dependencies=["FE-001", "FE-003"],
            inputs_schema={
                "type": "object",
                "properties": {
                    "backend_url": {
                        "type": "string",
                        "default": "http://localhost:8000"
                    },
                    "api_prefix": {
                        "type": "string",
                        "default": "/api"
                    }
                },
                "required": []
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "client_path": {"type": "string"},
                    "types_path": {"type": "string"}
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
        api_prefix = params.get("api_prefix", "/api")

        try:
            frontend_path = Path("frontend")
            lib_path = frontend_path / "lib"
            lib_path.mkdir(parents=True, exist_ok=True)

            # Create TypeScript types
            types_path = lib_path / "types.ts"
            types_code = """export interface User {
  id: number
  email: string
  created_at: string
  updated_at: string
}

export interface Task {
  id: number
  user_id: number
  description: string
  completed: boolean
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface SignUpRequest {
  email: string
  password: string
}

export interface SignInRequest {
  email: string
  password: string
}

export interface CreateTaskRequest {
  description: string
}

export interface UpdateTaskRequest {
  description?: string
  completed?: boolean
}

export interface APIError {
  detail: string
}
"""

            types_path.write_text(types_code, encoding="utf-8")
            self.logger.info(f"Created types: {types_path}")

            # Create API client
            client_path = lib_path / "api-client.ts"
            client_code = f"""import axios, {{ AxiosInstance, AxiosError }} from 'axios'
import {{ AuthResponse, User, Task, SignUpRequest, SignInRequest, CreateTaskRequest, UpdateTaskRequest, APIError }} from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '{backend_url}'
const API_PREFIX = '{api_prefix}'

class APIClient {{
  private client: AxiosInstance

  constructor() {{
    this.client = axios.create({{
      baseURL: `${{API_BASE_URL}}${{API_PREFIX}}`,
      headers: {{
        'Content-Type': 'application/json',
      }},
      withCredentials: false,
    }})

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {{
        const token = this.getToken()
        if (token) {{
          config.headers.Authorization = `Bearer ${{token}}`
        }}
        return config
      }},
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError<APIError>) => {{
        if (error.response?.status === 401) {{
          // Unauthorized - clear token and redirect to signin
          this.clearToken()
          if (typeof window !== 'undefined') {{
            window.location.href = '/signin'
          }}
        }}
        return Promise.reject(this.formatError(error))
      }}
    )
  }}

  private getToken(): string | null {{
    if (typeof window === 'undefined') return null
    return localStorage.getItem('access_token')
  }}

  private setToken(token: string): void {{
    if (typeof window !== 'undefined') {{
      localStorage.setItem('access_token', token)
    }}
  }}

  private clearToken(): void {{
    if (typeof window !== 'undefined') {{
      localStorage.removeItem('access_token')
    }}
  }}

  private formatError(error: AxiosError<APIError>): Error {{
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    return new Error(message)
  }}

  // Auth endpoints
  async signUp(data: SignUpRequest): Promise<AuthResponse> {{
    const response = await this.client.post<AuthResponse>('/auth/signup', data)
    this.setToken(response.data.access_token)
    return response.data
  }}

  async signIn(data: SignInRequest): Promise<AuthResponse> {{
    const response = await this.client.post<AuthResponse>('/auth/signin', data)
    this.setToken(response.data.access_token)
    return response.data
  }}

  async signOut(): Promise<void> {{
    this.clearToken()
  }}

  async getMe(): Promise<User> {{
    const response = await this.client.get<User>('/auth/me')
    return response.data
  }}

  // Task endpoints
  async getTasks(userId: number): Promise<Task[]> {{
    const response = await this.client.get<Task[]>(`/${{userId}}/tasks`)
    return response.data
  }}

  async getTask(userId: number, taskId: number): Promise<Task> {{
    const response = await this.client.get<Task>(`/${{userId}}/tasks/${{taskId}}`)
    return response.data
  }}

  async createTask(userId: number, data: CreateTaskRequest): Promise<Task> {{
    const response = await this.client.post<Task>(`/${{userId}}/tasks`, data)
    return response.data
  }}

  async updateTask(userId: number, taskId: number, data: UpdateTaskRequest): Promise<Task> {{
    const response = await this.client.put<Task>(`/${{userId}}/tasks/${{taskId}}`, data)
    return response.data
  }}

  async deleteTask(userId: number, taskId: number): Promise<void> {{
    await this.client.delete(`/${{userId}}/tasks/${{taskId}}`)
  }}

  async toggleTaskComplete(userId: number, taskId: number): Promise<Task> {{
    const response = await this.client.patch<Task>(`/${{userId}}/tasks/${{taskId}}/complete`)
    return response.data
  }}
}}

// Export singleton instance
export const apiClient = new APIClient()
"""

            client_path.write_text(client_code, encoding="utf-8")
            self.logger.info(f"Created API client: {client_path}")

            artifacts = [str(types_path), str(client_path)]

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "client_path": str(client_path),
                    "types_path": str(types_path)
                },
                artifacts=artifacts,
                logs=[f"Created API client with {len(artifacts)} files"]
            )

        except Exception as e:
            self.logger.exception("Failed to create API client")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "TypeScript types defined for all entities",
            "Axios client configured with base URL",
            "Request interceptor adds JWT token",
            "Response interceptor handles 401 errors",
            "All auth endpoints implemented (signup, signin, signout, me)",
            "All task CRUD endpoints implemented",
            "Token stored in localStorage",
            "Error formatting and handling implemented"
        ]
