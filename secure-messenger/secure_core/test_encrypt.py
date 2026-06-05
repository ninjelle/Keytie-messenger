import secure_core as sc
import os

key = os.urandom(32)
header = b"DH-pubkey|N=0"

ciphertext = sc.encrypt(key, b"privet, Bob!", header)
print("шифртекст (hex):", ciphertext.hex())

plaintext = sc.decrypt(key, ciphertext, header)
print("расшифровано:", plaintext.decode())

try:
    sc.decrypt(key, ciphertext, b"podmena")
    print("ПЛОХО: подмену не заметили")
except Exception as e:
    print("подмена заголовка обнаружена:", e)