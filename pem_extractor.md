A `.pem` file can contain different types of data (certificate, private key, or both). Let me show you how to extract `.crt` and `.key` files from your `.pem` file.I've created a script to extract `.crt` and `.key` files from your `.pem` file. Here are also the manual OpenSSL commands you can use:

## Using the Python Script:

```bash
# Analyze what's in your PEM file
python pem_extractor.py your_file.pem --analyze

# Extract certificate and key
python pem_extractor.py your_file.pem --output client
```

## Using OpenSSL Commands:

### 1. **If your PEM contains both certificate and private key:**

```bash
# Extract certificate
openssl x509 -in qa-challenge-20-.pem -out client.crt

# Extract private key
openssl pkey -in qa-challenge-20-.pem -out client.key
```

### 2. **If you need to check what's in the PEM file:**

```bash
# View certificate details
openssl x509 -in your_file.pem -text -noout

# View private key details
openssl pkey -in your_file.pem -text -noout
```

### 3. **Alternative extraction methods:**

```bash
# For RSA private key specifically
openssl rsa -in your_file.pem -out client.key

# For EC private key specifically
openssl ec -in your_file.pem -out client.key
```

### 4. **If the PEM file contains multiple certificates:**

```bash
# Split multiple certificates
csplit -f cert- your_file.pem '/-----BEGIN CERTIFICATE-----/' '{*}'
```

## Common PEM File Formats:

1. **Combined format** (certificate + private key in one file)
2. **Certificate only** (just the public certificate)
3. **Private key only** (just the private key)
4. **Certificate chain** (multiple certificates)

## Usage with the TLS Client:

Once you have the `.crt` and `.key` files:

```bash
python tls_client.py --cert client.crt --key client.key
```

The Python script will automatically:
- Analyze your PEM file contents
- Extract the certificate to `client.crt`
- Extract the private key to `client.key`
- Set proper permissions (600) on the private key file

Try running the script first to see what's in your PEM file!