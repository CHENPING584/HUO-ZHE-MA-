print("Testing Flask installation...")
try:
    import flask
    print(f"Flask version: {flask.__version__}")
    print("Flask is installed correctly.")
except ImportError as e:
    print(f"Error importing Flask: {e}")
    print("Please install Flask using: pip install Flask")

print("\nTesting webapp.py syntax...")
try:
    with open("webapp.py", "r") as f:
        code = f.read()
    compile(code, "webapp.py", "exec")
    print("webapp.py has no syntax errors.")
except SyntaxError as e:
    print(f"Syntax error in webapp.py: {e}")
except Exception as e:
    print(f"Error reading webapp.py: {e}")
