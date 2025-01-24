import os
import requests
from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Обязательно задайте сложный ключ!

# Токен API для аутентификации
PROXMOX_API_TOKEN = "root@pam!mepfpqqfwe=9e3d1f63-916e-4f99-b553-1f3b32b8ede9"
PROXMOX_URL = "https://10.107.4.201:8006/api2/json"
PROXMOX_NODE = "proxmox"  # Укажите имя вашего узла в Proxmox

# Установите пароль через переменные окружения или в коде
APP_PASSWORD = os.environ.get('APP_PASSWORD', 'Password1234')

# Проверка авторизации
def is_logged_in():
    return session.get('logged_in', False)

# Получение списка виртуальных машин



EXCLUDED_VMS = ['Ansible-32', 'Clone','112', 'Win10']



def get_vms():
    headers = {
        'Authorization': f"PVEAPIToken={PROXMOX_API_TOKEN}"
    }
    url = f"{PROXMOX_URL}/nodes/{PROXMOX_NODE}/qemu"
    response = requests.get(url, headers=headers, verify=False)
    
    if response.status_code == 200:
        vms = response.json()['data']
        
        # Фильтрация виртуальных машин
        vms = [vm for vm in vms if vm['name'].strip() not in EXCLUDED_VMS]  # Убираем лишние пробелы
        
        # Сортировка виртуальных машин по имени
        return sorted(vms, key=lambda vm: vm['name'])  # Сортировать по имени
    else:
        print(f"Failed to fetch VMs: {response.status_code}, {response.text}")
    
    return []






# Перезагрузка виртуальной машины
def reboot_vm(vm_id):
    headers = {
        'Authorization': f"PVEAPIToken={PROXMOX_API_TOKEN}"
    }
    url = f"{PROXMOX_URL}/nodes/{PROXMOX_NODE}/qemu/{vm_id}/status/reboot"
    response = requests.post(url, headers=headers, verify=False)
    return response.status_code == 200

# Маршрут логина
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == APP_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Неверный пароль!")
    return render_template('login.html')

# Главная страница
@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    vms = get_vms()
    return render_template('index.html', vms=vms)

# Перезагрузка виртуальной машины
@app.route('/reboot/<vm_id>', methods=['POST'])
def reboot(vm_id):
    if not is_logged_in():
        return redirect(url_for('login'))
    if reboot_vm(vm_id):
        return redirect(url_for('index'))
    else:
        return "Failed to reboot VM", 400

# Выход из системы
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
