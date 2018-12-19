import json
from blends.node.crypto import load_secret_key, sign, verify, get_pk

MESSAGE = "This is a test message"

print("Part I")
print()

print("Problems: 2 3 4")
print("===============")

for i in range(3):
    key_fname = "key{}.json".format(i)
    sk = load_secret_key(key_fname)
    sig_computed = sign(sk, MESSAGE)
    sig_fname = "sig{}.json".format(i)
    with open(sig_fname, "r") as sig_f:
        data = json.loads(sig_f.readline())
        sig = data["sig"]
        if sig_computed == sig:
            print("PASS")
        else:
            print("FAIL\nExpected: {}\n     Got: {}".format(sig, sig_computed))

print()
print("Problems: 5")
print("===============")

# Test  for Problem 5
WRONG_SIG = "wrong signature"

for i in range(3):
    key_fname = "key{}.json".format(i)
    sk = load_secret_key(key_fname)
    pk = get_pk(sk)
    sig_fname = "sig{}.json".format(i)
    with open(sig_fname, "r") as sig_f:
        data = json.loads(sig_f.readline())
        sig = data["sig"]
        if verify(pk, MESSAGE, sig):
            print("PASS")
        else:
            print("FAIL")
