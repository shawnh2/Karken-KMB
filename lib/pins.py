""" All kinds of atom operations for custom pins. """
import os
import sqlite3

from cfg import UCP_LOC

# file for User Custom Pin
UCP_FILE = UCP_LOC + 'pins.sqlite'


# ----------MAIN----------

def write_custom_pin(*pin_args):
    """ Write pin in file.
    The ucp file has field:
    PIN_NAME   PIN_ARGS            CATEGORY   ORG_IDX
    str        str                 str        int
               [name=value;...]    [PINS]     [# idx in org node db]
    """
    if not os.path.exists(UCP_LOC):
        os.mkdir(UCP_LOC)
    if not os.path.exists(UCP_FILE):
        create_ucp()
    # collect all the needs.
    pin_nm, args, org_nm = pin_args
    # start insert pin item
    ucp = sqlite3.connect(UCP_FILE)
    cur = ucp.cursor()
    cur.execute(
        """ INSERT INTO UCP(
            PIN_NAME, PIN_ARGS, CATEGORY, ORG_NAME
            ) VALUES (?, ?, ?, ?)
        """,
        (pin_nm, args, 'Pins', org_nm))
    ucp.commit()
    ucp.close()


def read_custom_pin():
    """ Load pin from file. """
    if (
            not os.path.exists(UCP_LOC) or
            not os.path.exists(UCP_FILE)
    ):
        return None
    ucp = sqlite3.connect(UCP_FILE)
    cur = ucp.cursor()
    cur.execute('SELECT * FROM UCP')
    for pin in cur.fetchall():
        yield pin
    ucp.close()


def remove_custom_pin(pin_id):
    """ Remove one pin from file. """
    ucp = sqlite3.connect(UCP_FILE)
    cur = ucp.cursor()
    cur.execute('DELETE FROM UCP WHERE ID=?', (pin_id, ))
    ucp.commit()
    ucp.close()


def update_custom_pin(pin_id: int, pin_args: str):
    """ Update one existing pin's args. """
    ucp = sqlite3.connect(UCP_FILE)
    cur = ucp.cursor()
    cur.execute('UPDATE UCP SET PIN_ARGS=? WHERE ID=?',
                (pin_args, pin_id))
    ucp.commit()
    ucp.close()


# ----------UTILS----------


def create_ucp():
    """ Create user custom pin table. """
    ucp = sqlite3.connect(UCP_FILE)
    cur = ucp.cursor()
    cur.execute(""" CREATE TABLE UCP(
        ID         INTEGER PRIMARY KEY AUTOINCREMENT ,
        PIN_NAME   TEXT NOT NULL ,
        PIN_ARGS   TEXT NOT NULL ,
        CATEGORY   TEXT NOT NULL ,
        ORG_NAME   TEXT NOT NULL ); """)
    ucp.commit()
    ucp.close()


def _pin_args_split(pin_args: str, equation_split=True):
    """ The generator of splitting pin args. """
    for arg in pin_args.split(';'):
        yield arg.split('=') if equation_split else arg


def create_ucp_tip(pin):
    """ Make a tooltip for one pin. """
    _, pin_name, pin_args, _, org_name = pin
    tip_head = "<b>{}</b><br>".format(pin_name)
    tip_subs = "src: [<i>{}</i>]<br>" \
               "args:<br>".format(org_name)
    tip_body = "<br>".join(["{} = <i>{}</i>".format(*arg)
                            for arg in _pin_args_split(pin_args)])
    return tip_head + tip_subs + tip_body


def pin_args_dict(pin_args: str):
    """ Convert pin_args string to pin_args dict. """
    args_dict = {}
    for arg_name, arg_value in _pin_args_split(pin_args):
        args_dict[arg_name] = arg_value
    return args_dict
