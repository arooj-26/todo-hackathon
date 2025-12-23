"""Add a diagnostic endpoint to check what code is loaded."""
from fastapi import APIRouter

diagnostic_router = APIRouter()

@diagnostic_router.get("/diagnostic/auth-imports")
async def check_auth_imports():
    """Check what imports are loaded in the auth module."""
    import app.routers.auth as auth_module
    import inspect
    
    # Get the source code
    source = inspect.getsource(auth_module)
    
    # Check for key indicators
    has_integrity_error_import = "IntegrityError" in source[:1000]
    has_integrity_error_handler = "except IntegrityError" in source
    has_logging = "import logging" in source[:500]
    
    return {
        "has_integrity_error_import": has_integrity_error_import,
        "has_integrity_error_handler": has_integrity_error_handler,
        "has_logging": has_logging,
        "first_500_chars": source[:500],
        "module_file": auth_module.__file__
    }
