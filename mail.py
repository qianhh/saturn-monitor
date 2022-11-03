#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import json
import os
import smtplib
import subprocess
import sys
from datetime import datetime, timedelta
from email.header import Header
from email.mime.text import MIMEText

smtp_server = 'smtp.office365.com'  # smtp server
smtp_port = 587  # smtp port
sender = 'xxx@outlook.com'  # user
password = '********'  # password

receivers = []

min_interval_minutes = 60  # minimum interval between notices


# Note: Using TLS encryption, the port is 587. (Gmail/Outlook/QQ)
def send_mail(receivers, subject, content, content_type='plain'):
    msg = MIMEText(content, content_type, 'utf-8')
    msg['From'] = Header(sender)
    if type(receivers) is str:
        msg['To'] = Header(receivers)
    elif type(receivers) is list:
        msg['To'] = Header(";".join(receivers))
    msg['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP(smtp_server, smtp_port)
        smtpObj.starttls()
        smtpObj.login(sender, password)
        smtpObj.sendmail(sender, receivers, msg.as_string())
        smtpObj.quit()
    except smtplib.SMTPException:
        print("send mail failed")


def check(containerName):
    status = subprocess.getoutput("docker inspect --format '{{.State.Status}}' " + containerName)
    exist = subprocess.getoutput("docker inspect --format '{{.State.Running}}' " + containerName)
    envs = subprocess.getoutput("docker inspect --format '{{json .Config.Env}}' " + containerName)
    env_obj = json.loads(envs)
    node_version = ""
    for field in env_obj:
        if field.startswith("NODE_VERSION"):
            node_version = field.split("=")[1]
            node_version = node_version.split("_")[0]
    if exist != "true":
        if "SATURN_HOME" in os.environ:
            home = os.environ["SATURN_HOME"]
        else:
            home = os.environ["HOME"]
        fil_addr = os.environ["FIL_WALLET_ADDRESS"]
        node_id = subprocess.getoutput("cat {}/shared/nodeId.txt".format(home))
        node_id = node_id[0:8]

        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S.%f")

        ok = True
        record_file = '/tmp/saturn-monitor'
        try:
            with open(record_file) as log:
                last_time_str = log.readline()
                last_time = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S.%f")
                if now - last_time < timedelta(minutes=min_interval_minutes):
                    ok = False
        except Exception as e:
            pass
        if ok:
            send_mail(receivers, "[Saturn-Monitor] Alert",
                      "Node: {} \nVersion: {} \nWallet: {}\nStatus: {}".format(node_id, node_version, fil_addr,
                                                                               status))
            f = open(record_file, "w")
            f.write(now_str)
            f.close()


def check_python_version(rv):
    python_ver = sys.version_info
    if python_ver[0] == rv[0] and python_ver[1] >= rv[1]:
        pass
    else:
        sys.stderr.write(
            "[%s] - Error: Your Python interpreter must be %d.%d or greater (within major version %d)\n" % (
                sys.argv[0], rv[0], rv[1], rv[0]))
        exit(-1)
    return 0


if __name__ == '__main__':
    check_python_version((3, 0))
    if len(receivers) == 0:
        receivers.append(os.environ["NODE_OPERATOR_EMAIL"])
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        send_mail(receivers, "Alert Test", "It's a test email.")
    check("saturn-node")
