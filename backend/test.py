session = {'email': 'j@example.com'}

def auth(func: function):
    def wrapper(user_data: dict):
        print('checando...')
        user_email = user_data.get('email')

        if user_email == session.get('email'):
            print('autorizado')
            return func()
        else:
            print('Usuário não autorizado')
    return wrapper


@auth
def ola_mundo():
    print('olá, mundo!')


# Simula um usuário
user_data = {'email': 'z@example.com'}

# Chama a função decorada
ola_mundo(user_data)