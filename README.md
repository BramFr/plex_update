# plex_update
Update your plex automatic. With this script.

Create a crontab entry to run this file.\
Example:
```
# vim /etc/crontab
18 1     * * * root python3 /path/to/script/plex_update.py
```

If you have a lifetime pass then define `token` like this. You can find your token [here](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/):
```
plex = Plex(logging_level='INFO', token='Sd123kdj29sj')
```

if you don't have any just leave at its.
```
plex = Plex(logging_level='INFO')
```

Run this script like:
```
# python3 /path/to/script/plex_update.py
```

# Troubleshooting
For any troubles you can define DEBUG mode to find your issue.
You can find your logs file within the current dir.
```
plex = Plex(logging_level='DEBUG')
```