import sqlite3

from lib import split_args_id


class DataBase4Args:
    """ Get arguments from Database. """

    DATABASE = sqlite3.connect('lib/node.db')
    CURSOR = DATABASE.cursor()

    def get_args_id(self, node_name: str):
        res = self.CURSOR.execute(
            f'SELECT ORI_ARGS, INH_ARGS FROM nodes WHERE NAME="{node_name}"'
        )
        return res.fetchone()

    def get_inh_args(self, inh_id: str):
        res = self.CURSOR.execute(
            f'SELECT * FROM inh_args WHERE ID={inh_id}'
        )
        for i, r in enumerate(res.fetchall()):
            yield i, r

    def get_org_args(self, org_id: str):
        split_id = split_args_id(org_id)
        for i, id_ in enumerate(split_id):
            res = self.CURSOR.execute(
                f'SELECT * FROM org_args WHERE ID={id_}'
            )
            yield i, res.fetchone()

    def get_box_args(self, box_id: int):
        res = self.CURSOR.execute(
            f'SELECT "VALUES" FROM box_args WHERE ID={box_id}'
        )
        return res.fetchone()[0]
