import collections
from typing import Dict, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ... import GENESIS_HASH, REWARD
from ..model import Block, Transaction


class DBManager:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.sessionmaker = sessionmaker(bind=self.engine)
        self.session = None

    def get_session(self):
        if not self.session:
            self.session = self.sessionmaker()
        return self.session

    def search_block(self, block_hash: str) -> Optional[Block]:
        """
        Step 1
        """
        session = self.get_session()
        for block in session.query(Block).all():
            header = block.get_header()
            if header['hash'] == block_hash:
                return block

        return None

    def get_height(self, block_hash: str) -> Optional[int]:
        """
        Step 2
        """
        curblk = self.search_block(block_hash)
        if curblk is None:
            return None

        height = 0
        while curblk.parent != GENESIS_HASH:
            # print(curblk)
            # print(curblk.parent)
            curblk = self.search_block(curblk.parent)
            height += 1

        return height

    def get_current(self) -> Block:
        """
        Step 3
        """
        maxhgt = -1
        maxblk = None

        session = self.get_session()
        for block in session.query(Block).all():
            header = block.get_header()
            hgt = self.get_height(header['hash'])
            if hgt > maxhgt:
                maxhgt = hgt
                maxblk = block

        return maxblk

    def _get_chain(self, block_hash: str) -> list:
        curhash = block_hash
        chain = []
        while curhash != GENESIS_HASH:
            curblk = self.search_block(curhash)
            chain.append(curblk)
            curhash = curblk.parent

        chain = list(reversed(chain))
        return chain

    def _get_length(self, block_hash: str) -> Optional[int]:
        """
        block_hash should be hash of existing block
        """
        chain = self._get_chain(block_hash)
        length = sum([blk.difficulty for blk in chain])

        return (length, chain)

    def get_longest(self) -> List[Block]:
        """
        Step 4
        """
        session = self.get_session()

        maxlength = 0
        maxchain = []
        for block in session.query(Block).all():
            header = block.get_header()
            (length, chain) = self._get_length(header['hash'])
            if length > maxlength:
                maxlength = length
                maxchain = chain

        return chain

    def search_transaction(self, tx_hash: str) -> Optional[Transaction]:
        """
        Step 5
        """
        session = self.get_session()
        for tx in session.query(Transaction).all():
            header = tx.get_header()
            if header['hash'] == tx_hash:
                return tx

        return None

    def get_block_balance(self, block_hash: str) -> Dict[str, int]:
        """
        Step 6
        """
        ## block = self.search_block(block_hash)
        chain = self._get_chain(block_hash)
        balances = {}

        for blk in chain:
            p = blk.miner
            balances[p] = balances.get(p, 0) + REWARD
            for tx in blk.txs:
                amount = tx.amount
                p = tx.sender
                balances[p] = balances.get(p, 0) - amount
                p = tx.receiver
                balances[p] = balances.get(p, 0) + amount

        return balances

    def insert_block(self, block: Block) -> bool:
        session = self.get_session()
        session.add(block)
        session.commit()

        return True
