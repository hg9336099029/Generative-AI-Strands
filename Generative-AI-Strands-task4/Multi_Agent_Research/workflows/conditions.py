MAX_RETRIES = 3

def should_retry(review: dict, retries: int) -> bool:
    """
    Returns True if another research iteration is needed.
    """
    if review["status"] == "PASS":
        return False
    
    if retries >= MAX_RETRIES:
        return False
    
    return True


def get_next_node(review: dict, retries: int) -> str:
    """
    Decide which node executes next.
    """
    if should_retry(review, retries):
        return "coordinator"

    return "writer"