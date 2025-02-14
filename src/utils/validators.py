def is_valid_task(task: str) -> bool:
    """
    Validate that the task:
    1. Is not empty
    2. Contains meaningful content
    3. Doesn't contain dangerous operations
    """
    if not task or len(task.strip()) < 5:
        return False
        
    # List of dangerous operations to check for
    dangerous_ops = ["rm ", "remove", "delete", "chmod", "chown"]
    return not any(op in task.lower() for op in dangerous_ops)
