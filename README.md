iphone_messages_dump
====================

A python script to dump texts from iMessage from an iPhone backup to a csv file.

Originally based on Jehiah Czebotar's script to dump iMessages to a csv file for dashboard parsing.

This script now runs on Python 3 and fixes several bugs.

See the iphonewiki for more information on how this script works. http://theiphonewiki.com/wiki/IMessage#References

TODO:

- When privacy is enabled, write a different file. Currently writing with and without privacy will cause duplicate items.
- Proper error handling for Madrid flags 32773, 77825, 102405.
- Unit tests with Nose.
- Performance improvements.
- Output choice. Need to add support for JSON.
- Proper license file


List of done:

- Dynamically determine OS (Mac/Windows) and use default location.
- Refactor to patterns.
- Create dictionaries explicitly instead of implicitly.
- Use argparse instead of optparse.
- PEP8 compliance.
- After refactor, encoding should be better handled so encoding hack shouldn't be required.
- Python 3 support
- Date time stamp! (Replaced by compare logic.)
- Better unicode handling
- Python 3.x style string format.


Backlog:

- Proper installation (via pip)
- Add feature to dump parsed data?
