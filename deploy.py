import os
import glob
import snowflake.connector
from cryptography.hazmat.primitives import serialization

# Load the private key
with open("rsa_key.p8", "rb") as key_file:
    p_key = serialization.load_pem_private_key(
        key_file.read(),
        password=os.environ["SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"].encode(),
    )

pkb = p_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

# Connect to Snowflake
conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    user=os.environ["SNOWFLAKE_USER"],
    role=os.environ["SNOWFLAKE_ROLE"],
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    database=os.environ["SNOWFLAKE_DATABASE"],
    schema=os.environ["SNOWFLAKE_SCHEMA"],
    private_key=pkb,
)

cs = conn.cursor()

# Run every .sql file in the sql/ folder, in order
for filepath in sorted(glob.glob("sql/*.sql")):
    print(f"Running {filepath}...")
    with open(filepath) as f:
        sql = f.read()
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            cs.execute(statement)
    print(f"Finished {filepath}")

print("All scripts executed successfully.")

cs.close()
conn.close()
