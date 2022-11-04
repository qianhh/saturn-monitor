# saturn-monitor
[![LICENSE](https://img.shields.io/github/license/qianhh/saturn-monitor)](./LICENSE "LICENSE")

Language: [Chinese](./README-cn.md)

A monitoring tool for Filecoin Saturn L1 node.

## Requirement
Python3

## Configure
1. Edit mail.py:
```python
smtp_server = 'smtp.office365.com'  # smtp server
smtp_port = 587  # smtp port
sender = 'xxx@outlook.com'  # user
password = '********'  # password

receivers = ['your_receive_email1', 'your_receive_email2']

min_interval_minutes = 30  # minimum interval between notices

max_restart_count = 5  # maximum restart count in 3 minutes
```
If ```receivers``` are not set, the email address in the environment variable ```NODE_OPERATOR_EMAIL``` is used.

##### Note: Only support TLS encryption, the smtp port is 587. (Gmail/Outlook/QQ)

2. Make it executable
```bash
chmod +x ./mail.py
```

3. Test

Send a test email:
```bash
./mail.py test
```

4. Setup the cron to run every 3 minutes:
```bash
crontab -e
```

Add the following text replacing the path:
```
*/3 * * * * /path/to/mail.py
```

## License
MIT