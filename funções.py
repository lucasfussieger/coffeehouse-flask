import json
import smtplib
from email.message import EmailMessage
from werkzeug.security import check_password_hash

def confirmacao_email(dest, name_cliente):
    remetente = ''
    senha = ''

    with open('confirmacao.html', 'r') as file:
        html_content = file.read()

    html_content = html_content.replace('{{nome}}', name_cliente)

    msg = EmailMessage()

    msg['subject'] = '=== CADASTRO REALIZADO COM SUCESSO ==='
    msg['from'] = remetente
    msg['to'] = dest
    msg.set_content('olá! seu cadastro foi realizado com sucesso! muito bem vindo ao nosso sistema!')

    msg.add_alternative(html_content, subtype = 'html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(remetente, senha)
            smtp.send_message(msg)
        print('email enviado com sucesso!')

    except Exception as e:
        print(' erro ao enviar:', e)
