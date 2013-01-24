iphone_messages_dump
====================

A python script to dump an iPhone backup to a csv file.

Originally based on Jehiah Czebotar's script to dump iMessages to a csv file for dashboard parsing.

This script now runs on Python 3.3 and fixes several bugs.

New features:

- Python 3.x support
- Date time stamp!
- Better unicode handling
- Python 3.x style string format.

See the iphonewiki for more information on how this script works. http://theiphonewiki.com/wiki/IMessage#References

TODO:

- Refactor to patterns.
- Dynamically determine OS (Mac/Windows) and use default location.
- Create dictionaries explicitly instead of implicitly.
- Use argparse instead of optparse.
- PEP8 compliance.
- Proper error handling for Madrid flags 32773, 77825, 102405.
- After refactor, encoding should be better handled so encoding hack shouldn't be required.
- Unit tests with Nose.

Future TODO:

- Add feature to dump parsed data?
