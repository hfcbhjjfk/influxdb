import paramiko
import requests
import time

INFLUXDB_URL = 'http://3.138.183.34:8086/api/v2/write?org=self&bucket=server_metrics&precision=s'
INFLUXDB_TOKEN = 'muqeHUZRbmjNIRshg7m7NmCrsixHxck0k-HauD5JRvHMPw39-0Ky5HKwgpdjMkDxRu3vXa7Z7EhdSr020gf9cA=='

def get_metrics(ip, username, private_key):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username, key_filename=private_key)

    # Commands to gather system metrics
    commands = {
        'cpu': 'cat /proc/stat | grep "cpu "',
        'memory': 'free -m',
        'disk': 'df -h'
    }

    metrics = {}
    for key, cmd in commands.items():
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        metrics[key] = output

    ssh.close()
    return metrics

def format_metrics(instance_id, metrics):
    data = f"cpu_usage,host={instance_id} value={metrics['cpu']}\n" \
           f"memory_usage,host={instance_id} value={metrics['memory']}\n" \
           f"disk_usage,host={instance_id} value={metrics['disk']}"
    return data

def send_metrics_to_influxdb(data):
    headers = {
        'Authorization': f'Token {INFLUXDB_TOKEN}',
        'Content-Type': 'text/plain; charset=utf-8'
    }
    response = requests.post(INFLUXDB_URL, headers=headers, data=data)
    if response.status_code == 204:
        print("Metrics successfully sent to InfluxDB")
    else:
        print(f"Failed to send metrics to InfluxDB: {response.status_code}, {response.text}")

def monitor_server(ip, instance_id, private_key):
    metrics = get_metrics(ip, 'ubuntu', private_key)
    formatted_data = format_metrics(instance_id, metrics)
    send_metrics_to_influxdb(formatted_data)

# Monitor all servers
servers = [
    {"ip": "3.145.161.116", "id": "server1", "key": r"C:\Users\gopic\Downloads\ohio_keypair.ppk"},
    {"ip": "3.12.85.37", "id": "server2", "key": r"C:\Users\gopic\Downloads\ohio_keypair.ppk"},
    {"ip": "18.220.173.32", "id": "server2", "key": r"C:\Users\gopic\Downloads\ohio_keypair.ppk"},
]

for server in servers:
    monitor_server(server['ip'], server['id'], server['key'])
    time.sleep(5)  # To avoid overwhelming InfluxDB

