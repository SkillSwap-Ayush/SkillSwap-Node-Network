import hashlib

def hash_pass(password):
    """
    Ye function user ke simple password (12345) ko 
    ek lambe secret code mein badal deta hai.
    """
    return hashlib.sha256(password.encode()).hexdigest()