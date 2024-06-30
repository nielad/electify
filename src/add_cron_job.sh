#!/bin/bash

# Add the cron job to the crontab
(echo "* * * * * /usr/local/bin/python /src/get_current_polls.py >> /var/log/get_current_polls.log 2>&1"
 echo "* * * * * /usr/local/bin/python /src/merge_dataframes.py >> /var/log/merge_dataframes.log 2>&1") | crontab -