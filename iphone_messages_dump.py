
"""
Copyright Jehiah Czebotar 2013
http://jehiah.cz/

Modifications by Ryan Forsythe 2013:
* Switch to stdlib's optparse rather than relying on tornado's option parsing
* Add new-style backup database parsing.

Modifications by David Echols 2013:
* Port to Python 3.
* Started refactor to patterns.

NOTE: This is broken for SMS phone numbers. Currently researching a fix.
"""

import optparse
import glob
import os
import sqlite3
import datetime
import time
import csv

"""
The madrid offset is the offset from 1 Jan 1970 to 1 Jan 2001.
Some database fields use the 2001 format, so it's necessary to
create an offset for these.

Madrid flags in the message table:
NULL: not an iMessage
12289: received
32773: send error
36869, 45061: sent
77825: received message containing parsed data
102405: sent message containing parsed data
"""
MADRID_OFFSET = 978307200
MADRID_FLAGS_SENT = [36869, 45061]
DEFAULT_BACKUP_LOCATION_MAC = "~/Library/Application Support/MobileSync/Backup/*/3d0d7e5fb2ce288813306e4d4636395e047a3d28"
DEFAULT_BACKUP_LOCATION_WIN = "C:\\Users\\David\\AppData\\Roaming\\Apple Computer\\MobileSync\\Backup\\*\\3d0d7e5fb2ce288813306e4d4636395e047a3d28"
# Command line args will get parsed into this:
options = None


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DB(object):
    def __init__(self, *args, **kwargs):
        self._db = sqlite3.connect(*args, **kwargs)
        self._db.row_factory = dict_factory

    def query(self, sql, params=None):
        try:
            c = self._db.cursor()
            c.execute(sql, params or [])
            res = c.fetchall()
            self._db.commit()
        except:
            if self._db:
                self._db.rollback()
            raise

        c.close()
        return res


def extract_messages(db_file):
    db = DB(db_file)
    skipped = 0
    found = 0

    for row in db.query('select * from message'):
        ts = row['date']
        is_imessage = False
        if not 'is_madrid' in row:
            # New-style (?) backups
            is_imessage = row['service'] == 'iMessage'
            sent = row['is_sent']
        else:
            is_imessage = row['is_madrid']
            if is_imessage:
                sent = row['madrid_flags'] in MADRID_FLAGS_SENT
            else:
                sent = row['flags'] in [3, 35]

        if 'is_madrid' in row:
            if row['is_madrid']:
                ts += MADRID_OFFSET
        else:
            ts += MADRID_OFFSET
        if not row['text']:
            skipped += 1
            continue
        dt = datetime.datetime.utcfromtimestamp(ts)

        #print('[%s] %r %r' % (dt, row.get('text'), row)) -- debug

        if options.sent_only and not sent:
            skipped += 1
            continue
        if dt.year != options.year:
            skipped += 1
            continue
        found += 1

        address = ''
        if 'madrid_handle' in row:
            address = row.get('address') or row['madrid_handle']
        else:
            address = row.get('address') or row['account']

        yield dict(
            sent='1' if sent else '0',
            service='iMessage' if is_imessage else 'SMS',
            subject=(row['subject'] or ''),
            text=(row['text'] or '').replace('\n', r'\n'),
            ts=ts,
            address=address,
        )

    print('found {0} skipped {1}'.format(found, skipped))


def run():
    assert not os.path.exists(options.output_file)
    print('writing out to {0}'.format(options.output_file))
    with open(options.output_file, 'w', encoding="utf8") as f:
        columns = ["ts", "service", "sent", "address", "subject", "text"]
        writer = csv.DictWriter(f, columns)
        writer.writerow(dict([[x, x] for x in columns]))
        pattern = os.path.expanduser(options.input_pattern)
        for db_file in glob.glob(pattern):
            print("reading {0}. use --input-patern to select only this file".format(db_file))
            for row in extract_messages(db_file):
                if not options.include_message_text:
                    row['text'] = ''
                writer.writerow(row)

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-i", "--input_pattern", type=str, default=DEFAULT_BACKUP_LOCATION_WIN)
    parser.add_option("-o", "--output_file", type=str, default=("txt_messages" + time.strftime("%d%m%Y%H%M%S", time.localtime()) + ".csv"))
    parser.add_option("-y", "--year", type=int, default=2012)
    parser.add_option("-s", "--sent_only", action="store_true", default=False)
    parser.add_option("-t", "--include_message_text", action="store_true", default=True)
    (options, args) = parser.parse_args()
    run()
