""" All kinds of atom operations for custom pins. """
import os
import sqlite3

from cfg import UCP_LOC

# file for User Custom Pin
UCP_FILE = UCP_LOC + 'pins.sqlite'


def create_ucp():
    ucp = sqlite3.connect(UCP_FILE)
    cur = ucp.cursor()
    cur.execute(""" CREATE TABLE UCP(
        ID         INTEGER PRIMARY KEY AUTOINCREMENT ,
        PIN_NAME   TEXT NOT NULL ,
        PIN_ARGS   TEXT NOT NULL ,
        CATEGORY   TEXT NOT NULL ,
        ORG_NAME   TEXT NOT NULL ,
        ORG_SORT   TEXT NOT NULL ); """)
    ucp.commit()
    ucp.close()


def create_ucp_tip(pin):
    """ Make a tooltip for one pin. """
    id_, pin_name, pin_args, category, org_name, org_sort = pin
    tip_head = "<strong>{}</strong><br>".format(pin_name)
    tip_subs = "src: [{}:{}]<br>" \
               "args:<br>".format(org_sort, org_name)
    tip_body = "<br>".join(["{} = {}".format(*arg.split('='))
                            for arg in pin_args.split(';')])
    return tip_head + tip_subs + tip_body


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
    pin_nm, args, org_nm, org_sr = pin_args
    # start insert pin item
    ucp = sqlite3.connect(UCP_FILE)
    cur = ucp.cursor()
    cur.execute(
        """ INSERT INTO UCP(
            PIN_NAME, PIN_ARGS, CATEGORY, ORG_NAME, ORG_SORT
            ) VALUES (?, ?, ?, ?, ?)
        """,
        (pin_nm, args, 'Pins', org_nm, org_sr))
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


def remove_custom_pin(pin):
    """ Remove one pin from file. """


def update_custom_pin(pin):
    """ Update one existing pin in file. """
