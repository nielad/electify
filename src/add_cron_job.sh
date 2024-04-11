#!/bin/bash

# Add the cron job to the crontab
echo "* * * * * /usr/bin/python3 /src/hello.py >> /var/log/hello.log 2>&1" | crontab -
