import socket

# Realizando o handshake
def handshake(client_socket):

    # 1. Enviando mensagem ao servidor (SYN)
    modo = "modo_texto"
    tam_max = "1025"
    mensagem = f"SYN|{modo}|{tam_max}"
    client_socket.send(mensagem.encode('utf-8'))

    # 2. Recebendo a resposta do servidor (SYN-ACK)
    resposta = client_socket.recv(1024).decode('utf-8')
    print("Resposta do servidor:", resposta)

    # Conferindo resposta 
    if resposta.startswith("SYN-ACK") and resposta.split("|")[1] == modo and resposta.split("|")[2] == tam_max:
        # 3. Manda o (ACK)
        client_socket.send("ACK".encode('utf-8'))
        print("3° via do handshake feito!")
    else:
        print("Erro no handshake")

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
    port = 8081

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

if __name__ == '__main__':
    cliente()