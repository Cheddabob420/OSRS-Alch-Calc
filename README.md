# Osrs GrandExchange Alch Profit Scripts



after setting up the needed directorys and virt env for pthon add to cron tab to make sure the server stays persistant.

```bash
crontab -e
```

```bash
# Update the data every 5 minutes
*/5 * * * * /home/path/to/python/.venv/bin/python3 /home/path/to/osrs/dashboard_updater.py

# On reboot: Run a fresh update, THEN start the web server in the background
@reboot /home/path/to/python/bin/python3 /home/path/to/dashboard_updater.py && cd /home/path/to/osrs && /usr/bin/python3 -m http.server 8000 &
```


