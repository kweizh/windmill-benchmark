import wmill


def main():
    secret = wmill.get_variable("f/secret_masking_zr_buj3tws/api_key")
    print(secret)
    return secret
