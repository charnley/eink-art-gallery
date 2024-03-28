try:
    from magic import Magic
    print("libmagic is installed and accessible.")
except ImportError as e:
    print(f"ImportError: {e}")