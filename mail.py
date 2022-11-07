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

min_interval_minutes = 30  # minimum interval between notices

max_restart_count = 5  # maximum restart count in 3 minutes


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


def check(container_name):
    status = subprocess.getoutput("docker inspect --format '{{.State.Status}}' " + container_name)
    exist = subprocess.getoutput("docker inspect --format '{{.State.Running}}' " + container_name)
    restart_count_str = subprocess.getoutput("docker inspect --format '{{.RestartCount}}' " + container_name)
    restart_count = int(restart_count_str)
    envs = subprocess.getoutput("docker inspect --format '{{json .Config.Env}}' " + container_name)
    env_obj = json.loads(envs)
    node_version = ""
    for field in env_obj:
        if field.startswith("NODE_VERSION"):
            node_version = field.split("=")[1]
            node_version = node_version.split("_")[0]

    if "SATURN_HOME" in os.environ:
        home = os.environ["SATURN_HOME"]
    else:
        home = os.environ["HOME"]
    fil_addr = os.environ["FIL_WALLET_ADDRESS"]
    node_id = subprocess.getoutput("cat {}/shared/nodeId.txt".format(home))
    node_id = node_id[0:8]

    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S.%f")

    ok = False
    record_file = '/tmp/saturn-monitor'
    try:
        record = {}
        with open(record_file) as f:
            last_check_time = datetime.fromtimestamp(0)
            last_alert_time = datetime.fromtimestamp(0)
            last_restart_count = 0
            try:
                record = json.load(f)
            except Exception as exp:
                pass
            if record.get("check_time"):
                last_check_time_str = record["last_check_time"]
                last_check_time = datetime.strptime(last_check_time_str, "%Y-%m-%d %H:%M:%S.%f")
            if record.get("restart_count"):
                last_restart_count = record["restart_count"]
            if record.get("last_alert_time"):
                last_alert_time_str = record["last_alert_time"]
                last_alert_time = datetime.strptime(last_alert_time_str, "%Y-%m-%d %H:%M:%S.%f")

            if exist != "true":
                ok = True
            if now - last_check_time > timedelta(minutes=3):
                if restart_count - last_restart_count > max_restart_count:
                    ok = True
                record["last_check_time"] = now_str
                record["restart_count"] = restart_count
            if now - last_alert_time < timedelta(minutes=min_interval_minutes):
                ok = False
    except Exception as e:
        # if read file failed, as first time
        record["last_check_time"] = now_str
        record["restart_count"] = restart_count

    if ok:
        logs = subprocess.getoutput("docker logs -n 50 " + container_name)
        send_mail(receivers, "[Saturn-Monitor] Alert",
                  "Node: {} \nVersion: {} \nWallet: {}\nStatus: {}\nRestartCount: {}\n\n\nlogs:\n{}".
                  format(node_id, node_version, fil_addr, status, restart_count - last_restart_count, logs))
        record["last_alert_time"] = now_str

    f = open(record_file, "w")
    json.dump(record, f)
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
        exit(0)
    check("saturn-node")
