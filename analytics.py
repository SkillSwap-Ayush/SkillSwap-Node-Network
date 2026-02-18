def calc_percentage(part, total):
    """
    Ye function dashboard par dikhane ke liye 
    percentage calculate karta hai.
    """
    if total == 0: 
        return 0
    # Result ko 2 decimal tak round kar rahe hain
    return round((part / total) * 100, 2)