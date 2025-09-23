from fastmcp.server.auth.providers.bearer import RSAKeyPair

key_pair = RSAKeyPair.generate()
token = key_pair.create_token(
    subject="juwhitak",
    issuer="https://dev.example.com",
    audience="my-dev-server",
    scopes=["read", "write"]
)

with open('./pubkey.txt', 'w') as f:
    f.write(key_pair.public_key)

with open('./token.txt', 'w') as f:
    f.write(token)