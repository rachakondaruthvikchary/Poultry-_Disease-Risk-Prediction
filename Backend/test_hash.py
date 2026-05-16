from app.services.security import get_password_hash

try:
    hashed = get_password_hash("test1234")
    print("Success!")
    print(f"Hashed: {hashed}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
