import csv
import ipaddress
import paramiko
import time as time
import signal


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
is_connected_to_server = False
number_of_servers = 0


def handler(signum, frame):
    client.close()

def is_valid_ip(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_valid_login(server_ip, username, password):
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(3)  # Set the parameter to the amount of seconds you want to wait
    try:
        client.connect(server_ip, username=username, password=password)
        time.sleep(3)
        client.close()
        return True
    except Exception as e:
        print(f'Connection failed: {e}')
        return False

def get_servers_data():
    servers = []
    with open('servers.txt') as csv_file:
        print(f'>>Getting server list from {csv_file.name}')
        csv_reader = csv.reader(csv_file, delimiter=',')
        for line_count, row in enumerate(csv_reader):
            if line_count > 0:
                servers.append(row)
        print(f'\t-Processed {line_count} servers.')
    return servers

def add_server(server_ip, username, password, sender, time):
    with open('servers.txt', 'a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow([server_ip, username, password, sender, time])

def del_server(server_number):
    with open("servers.txt", "r") as f:
        lines = f.readlines()
    with open("servers.txt", "w") as f:
        for i, line in enumerate(lines):
            if i != int(server_number):
                f.write(line)

def do_command(client, given_command):
    output = ""
    try:
        stdin, stdout, stderr = client.exec_command(given_command)
        output = ''.join(stdout.readlines())
    except Exception as e:
        print(f'Command execution failed: {e}')
    return output

