#!/bin/bash

# Add the cron job to the crontab
echo "* */23 * * * /usr/local/bin/python /src/get_current_polls.py >> /var/log/get_current_polls.log 2>&1" | crontab -
	