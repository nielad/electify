#!/bin/bash

# Add the cron job to the crontab
echo "* * * * * /usr/local/bin/python /src/hello.py >> /var/log/hello.log 2>&1" | crontab -
