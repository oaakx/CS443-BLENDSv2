import sys
import json
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15 
from Crypto.Hash import SHA512

def sign(sk, msg):
    '''
    sign string msg with corresponding secret key (RsaKey object) in pycryptodome library
    return hex value of signature with RSA pkcs1 v1.5
    '''
    sigscheme = pkcs1_15.new(sk)
    h = SHA512.new(msg.encode('utf8'))
    signed = sigscheme.sign(h)

    return "%x" % int.from_bytes(signed, byteorder="big")


def verify(pk, msg, signed):
    '''
    check sign is made for msg using public key PK, string MSG, 
    and byte string SIGN.
    suppose publicExponent is fixed at 0x10001.
    return boolean
    '''
    signed = bytes([int('0x' + signed, 16)])
    sigscheme = pkcs1_15.new(pk)
    h = SHA512.new(msg)
    try:
        sigscheme.verify(h, signed)
        return True
    except:
        return False


def load_secret_key(fname):
    '''
    load json information of secret key from fname. 
    This returns RSA key object of pycrytodome library.
    '''
    with open(fname) as f:
        key_dict = json.load(f)

    n = int(key_dict['modulus'], 16)
    e = int(key_dict['publicExponent'], 16)
    d = int(key_dict['privateExponent'], 16)
    sk = RSA.construct((n, e, d))
    return sk


def create_secret_key(fname):
    '''
    Create a secret key: [hint] RSA.generate().
    Save the secret key in json to a file named "fname". 
    This returns RSA key object of pycrytodome library.
    '''
    # Generate RSA private key
    key = RSA.generate(2048)
    modulus = "0x%x" % key.n # convert to hex
    publicExponent = "0x%x" % key.e
    privateExponent = "0x%x" % key.d

    # Save in json format in given fname
    values = {
            "modulus": modulus,
            "publicExponent": publicExponent,
            "privateExponent": privateExponent,
    }
    with open(fname, "w") as f:
        json.dump(values, f)

    return key


def get_hash(msg):
    '''
    return hash hexdigest for string msg with 0x. ex) 0x1a2b...
    '''
    h = SHA512.new(msg)
    hexdigest = h.hexdigest()
    return hexdigest


def get_pk(sk):
    '''
    return pk using modulus of given RsaKey object sk.
    '''
    pk = sk.publickey()
    return pk
