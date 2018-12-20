from typing import Dict

from ... import DIFFICULTY, GENESIS_HASH, REWARD
from ..model import Block, Transaction
from .dbmanager import DBManager
from .verifier import Verifier


class Blockchain:
    def __init__(self, db_connection_string: str,
                 difficulty: int = DIFFICULTY):

        self.verifier = Verifier()
        self.dbmanager = DBManager(db_connection_string)

    def append(self, block: Block) -> bool:
        if self.verifier.verify_block(block) and self.validate_block(block):
            self.dbmanager.insert_block(block)
            return True
        else:
            return False

    def validate_transaction(self, tx: Transaction, block: Block) -> bool:
        tx_header = tx.get_header()
        blk_header = block.get_header()
        
        # Check if exists
        tx2 = self.dbmanager.search_transaction(tx_header['hash'])
        if tx2 is not None and tx2.block_s != block.hash:
            # print("already exists and in another block")
            # print(tx2.block_s)
            return False

        # Check balance
        balances = self.dbmanager.get_block_balance(blk_header['hash'])
        if tx2 is not None and balances[tx.sender] < 0:
            # print("not sufficient funds, already in the block")
            return False
        elif tx2 is None and balances[tx.sender] < tx.amount:
            # print("not sufficient funds, not in the block (new)")
            return False

        return True

    def validate_block(self, block: Block) -> bool:
        """
        check difficulty
        """

        # Check parent exists
        blk_par = self.dbmanager.search_block(block.parent)
        if block.parent != GENESIS_HASH and blk_par is None:
            # print("parent doesn't exist")
            return False

        ### Check block's txs are valid
        ##for tx in block.txs:
        ##    if not self.validate_transaction(tx, block):
        ##        print("block's some txs are not valid")
        ##        return False

        # Check balance
        header = block.get_header()
        balances2 = self.dbmanager.get_block_balance(block.parent)
        balances = {}
        p = block.miner
        balances[p] = balances.get(p, 0) + REWARD
        for tx in block.txs:
            amount = tx.amount
            p = tx.sender
            balances[p] = balances.get(p, 0) - amount
            p = tx.receiver
            balances[p] = balances.get(p, 0) + amount

        for key in balances:
            if balances[key] + balances2.get(key, 0) < 0:
                # print('insufficient funds after some transaction')
                return False

        return True

    def get_balance(self) -> Dict[str, int]:
        block = self.dbmanager.get_current()
        balance = self.dbmanager.get_block_balance(block.hash)
        return balance

    def get_current(self):
        return self.dbmanager.get_current()
