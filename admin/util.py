import string, secrets

PASSWORD_LENGTH = 14

def generate_strong_password(length: int = PASSWORD_LENGTH):
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits

    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits)
    ]

    all_chars = lowercase + uppercase + digits
    password += [secrets.choice(all_chars) for _ in range(length-3)]

    secrets.SystemRandom().shuffle(password)

    return ''.join(password)
