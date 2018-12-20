from ..crypto import get_hash, verify
from ..model import Block, Transaction
from Crypto.PublicKey import RSA
from blends.node.blockchain.dbmanager import DBManager

class Verifier:
    def verify_transaction(self, tx: Transaction) -> bool:
        """
        Step 1 : verify transaction
        """
        payload = tx.get_payload()
        header = tx.get_header()
        dbmanager = DBManager("sqlite:///scenario.db")

        # Check timestamp
        tx2 = dbmanager.search_transaction(header['hash'])
        if tx2 is not None and tx2.timestamp != tx.timestamp:
            return False

        # Check hash
        if tx.hash != get_hash(payload):
            return False

        # Check balance
        balances = dbmanager.get_block_balance(tx.block_s)
        
        if balances[tx.sender] < tx.amount:
            print('balance')
            return False

        # Check sender vs receiver
        if tx.sender == tx.receiver:
            print('sender vs receiver')
            return False

        ### Check signature
        ##sender_n = int(tx.sender, 16)
        ##pk = RSA.construct((sender_n, 0x10001))
        ##
        ##if not verify(pk, payload, tx.sign):
        ##    print('sign')
        ##    print("payload", payload)
        ##    print("sender (modulo)", tx.sender)
        ##    print("sign", tx.sign)
        ##    #  print(sender_n)
        ##    #  print(0x10001)
        ##    return False

        return True

    def verify_block(self, blk: Block) -> bool:
        """
        Step 2 : verify block
        """
        payload = blk.get_payload()
        header = blk.get_header()

        # Check hash
        if blk.hash != get_hash(payload):
            return False

        # Check difficulty
        if int(blk.hash, 16) >= 2**(512-20-blk.difficulty):
            return False

        return True
