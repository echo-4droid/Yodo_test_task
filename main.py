import requests
import base64

#
# 1. Получение свободного чата и запись в базу данных
#
base_url = 'https://dev.whatsapp.sipteco.ru/v3/'
headers = {'X-Whatsapp-Token': '5d8af8faaeb61680883a850be0c577e2',
           'User-Agent': 'WhatsApp/2.18.61 i'}
response = requests.get(base_url + 'chat/spare?crm=HUBSPOT', headers=headers)
json_response = response.json()
id_ = str(json_response.get('id'))
token = json_response.get('token')

if response.ok:
    if response.json().get('error_code') is not None:
        print(f'Непредвиденная ошибка\n'
              f'Error code: {response.json().get("error_code")}\n'
              f'Error text: {response.json().get("error_text")}')
        exit(1)
else:
    print(f'При попытке отправки сообщения получен ответ {response.status_code}\n'
          f'Запрос POST url {response.url}')
#
# 2. Получению QR кода
#
state = ''
while state != 'got qr code':
    response = requests.get(base_url + 'instance' + id_ + '/status?full=1&no_wakeup=0&token=' + token,
                            headers=headers)
    json_response = response.json()
    state = json_response.get('state')

json_response = response.json()
qr_data = json_response.get('qrCode').split(',')
qr_image_type = qr_data[0].split(';')[0].split('/')[-1]
qr_image_data = qr_data[1]
with open(f'qr_code.{qr_image_type}', 'wb') as file:
    file.write(base64.b64decode(qr_image_data))

input(f'QR код сохранён в файл "qr_code.{qr_image_type}", в каталоге, из которого запущен данный скрипт.\n'
      f'Для подключения вам необходимо сканировать данный QR код.\n'
      f'У вас есть одна минута.\n\n'
      f'Нажмите Enter для продолжения.')

#
# 2.5 Пользователь сканирует QR код в приложении WhatsApp на своём смартфоне
#
# 3. Получение статуса, что WhatsApp подключен, запись имени и телефона
#
user_name, user_phone_number, account_status = None, None, None

response = requests.get(base_url + 'instance' + id_ + '/status?full=1&token=' + token, headers=headers)
if response.ok:
    if response.json().get('error_code') is not None:
        print(f'Непредвиденная ошибка\n'
              f'Error code: {response.json().get("error_code")}\n'
              f'Error text: {response.json().get("error_text")}')
    else:
        json_response = response.json()
        account_status = json_response.get('accountStatus')
else:
    print(f'При попытке отправки сообщения получен ответ {response.status_code}\n'
          f'Запрос POST url {response.url}')

response = requests.get(base_url + 'instance' + id_ + '/me?token=' + token, headers=headers)
if response.ok:
    if response.json().get('error_code') is not None:
        print(f'Непредвиденная ошибка\n'
              f'Error code: {response.json().get("error_code")}\n'
              f'Error text: {response.json().get("error_text")}')
    else:
        json_response = response.json()
        user_name = json_response.get('name')
        user_phone_number = json_response.get('number')
else:
    print(f'При попытке отправки сообщения получен ответ {response.status_code}\n'
          f'Запрос POST url {response.url}')

if account_status is None:
    print(f'Вы не прошли авторизацию, перезапустите скрипт')
    exit(1)
else:
    print(f'User: {user_name}\nPhone number: {user_phone_number}\nAccount Status: {account_status}')

#
# 4. Отправка сообщения
#
phone_numbers = [
    79872745052,
    79195188515
]

for number in phone_numbers:
    payload = {
        'body': f'Привет!\nЭто сообщение из тестового задания для Yodo на номер @{number}',
        'phone': number,
        'mentionedPhones': str(number)
    }

    response = requests.post(base_url + 'instance' + id_ + '/sendMessage?token=' + token, data=payload,
                             headers=headers)

    if response.ok:
        if response.json().get('error_code') is not None:
            print(f'Сообщение не отправлено\n'
                  f'Error code: {response.json().get("error_code")}\n'
                  f'Error text: {response.json().get("error_text")}')
        elif response.json().get('sent'):
            print(f'Сообщение успешно отправлено')
        else:
            print(f'Не удалось отправить сообщение')
    else:
        print(f'При попытке отправки сообщения получен ответ {response.status_code}\n'
              f'Запрос POST url {response.url}')

