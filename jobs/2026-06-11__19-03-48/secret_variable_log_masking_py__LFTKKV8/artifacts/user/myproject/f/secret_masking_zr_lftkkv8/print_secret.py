import wmill

def main():
    secret = wmill.get_variable("f/secret_masking_zr_lftkkv8/api_key")
    print(secret)
    return secret
