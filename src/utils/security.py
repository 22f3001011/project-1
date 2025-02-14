from pathlib import Path

def validate_path(path: str) -> bool:
    """
    Validate that the path:
    1. Is within the /data directory
    2. Actually exists
    3. Is a file (not a directory)
    4. Contains no path traversal attempts
    """
    try:
        # Resolve the absolute path
        file_path = Path(path).resolve()
        data_dir = Path("/data").resolve()
        
        # Check if path is within data directory
        if not str(file_path).startswith(str(data_dir)):
            return False
        
        # Check if path exists and is a file
        if not file_path.is_file():
            return False
            
        return True
    except Exception:
        return False
