import socket

# Realizando o handshake
def handshake(client_socket):

    # Enviando mensagem ao servidor
    mensagem = "HANDSHAKE|modo_texto|1024"
    client_socket.send(mensagem.encode('utf-8'))

    # Recebendo a resposta do servidor
    resposta = client_socket.recv(1024).decode('utf-8')
    print("Resposta do servidor:", resposta)

# Trocar mensagens
def comunicacao_server(client_socket, message):

    # Enviando mensagem ao servidor
    msg = f"MSG|{message}"
    client_socket.send(msg.encode('utf-8'))

    # Recebendo resposta do servidor
    resposta = client_socket.recv(1024).decode('utf-8')
    print("Resposta do servidor:", resposta)


def cliente():

    # Conectando ao servidor
    host = '127.0.0.1'  
    port = 8080  

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Realiza o handshake com o servidor
    handshake(client_socket)

    # Conversando com o servidor
    while True:
        # Recebendo mensagem do cliente
        message = input("Digite sua mensagem (ou 'sair' para encerrar): ")

        # Enviando mensagem para o servidor
        comunicacao_server(client_socket, message)

        # Se o usuário digitar 'sair', o loop é interrompido
        if message.lower() == 'sair':
            print("Desconectando do servidor...")
            break

    # Fecha a conexão
    client_socket.close()

