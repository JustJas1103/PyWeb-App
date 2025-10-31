import bcrypt

hashed = bcrypt.hashpw(b"123", bcrypt.gensalt()).decode("utf-8")
print("Your hashed password is:\n", hashed)
