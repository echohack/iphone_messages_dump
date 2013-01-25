"""
This software is released under the MIT License.
http://opensource.org/licenses/MIT

Originially created by Jehiah Czebotar.
Modified by Ryan Forsythe and David Echols.
http://jehiah.cz/
http://dechols.com/
"""

import optparse
import glob
import os
import sqlite3
import datetime
import time
import csv
from collections import OrderedDict

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


class DB():
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
    query_texts = "select * from message"

    for row in db.query(query_texts):
        timestamp = row['date']
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
                timestamp += MADRID_OFFSET
        else:
            timestamp += MADRID_OFFSET
        if not row['text']:
            skipped += 1
            continue
        utc_datetime = datetime.datetime.utcfromtimestamp(timestamp)

        if options.sent_only and not sent:
            skipped += 1
            continue
        if utc_datetime.year != options.year:
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
            timestamp=timestamp,
            address=address,
        )

    print('found {0} skipped {1}'.format(found, skipped))


def set_privacy(item):
    """
    Hide values by default for privacy.
    """

    privacy_text = "Text hidden for privacy. Use -p flag to enable text."
    item['text'] = privacy_text


def write_csv(file_object):
    fieldnames = {"timestamp": None, "service": None, "sent": None, "address": None, "subject": None, "text": None}
    ordered_fieldnames = OrderedDict(sorted(fieldnames.items(), key=lambda t: t[0]))
    writer = csv.DictWriter(file_object, fieldnames=ordered_fieldnames)
    writer.writeheader()
    pattern = os.path.expanduser(options.input_pattern)
    input_pattern_list = glob.glob(pattern)
    for db_file in input_pattern_list:
        print("reading {0}. use --input-pattern to select only this file".format(db_file))
        for item in extract_messages(db_file):
            if options.privacy:
                set_privacy(item)
            writer.writerow(item)


def run():
    print('writing out to {0}'.format(options.output_file))
    with open(options.output_file, 'w', encoding="utf8") as f:
        write_csv(f)


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-i", "--input_pattern", type=str, default=DEFAULT_BACKUP_LOCATION_WIN)
    parser.add_option("-y", "--year", type=int, default=2012)
    parser.add_option("-o", "--output_file", type=str, default=("txt_messages_" + time.strftime("%Y-%m-%d-%H%M%S", time.localtime()) + ".csv"))
    parser.add_option("-s", "--sent_only", action="store_true", default=False)
    parser.add_option("-p", "--privacy", action="store_true", default=True)
    (options, args) = parser.parse_args()
    run()
