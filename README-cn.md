# saturn-monitor
[![LICENSE](https://img.shields.io/github/license/qianhh/saturn-monitor)](./LICENSE "LICENSE")

Language: [English](./README.md)

Filecoin Saturn L1节点的监控工具。

## Requirement
Python3

## Configure
1. 编辑 mail.py:
```python
smtp_server = 'smtp.office365.com'  # smtp server
smtp_port = 587  # smtp port
sender = 'xxx@outlook.com'  # user
password = '********'  # password

receivers = ['your_receive_email1', 'your_receive_email2']

min_interval_minutes = 30  # minimum interval between notices

max_restart_count = 5  # maximum restart count in 3 minutes
```
如果不设置```receivers```，则会使用环境变量```NODE_OPERATOR_EMAIL```中的邮箱地址。

##### 注意: 只支持TLS加密，smtp端口号一般为587. (Gmail/Outlook/QQ)

2. 赋予执行权限
```bash
chmod +x ./mail.py
```

3. 测试

发送测试邮件:
```bash
./mail.py test
```

4. 设置cron每3分钟运行一次:
```bash
crontab -e
```

添加以下文本替换路径:
```
*/3 * * * * /path/to/mail.py
```

## License
MIT
