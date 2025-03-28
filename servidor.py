import socket

# Realizando o handshake
def process_handshake(client_socket):

    # Recebe o handshake inicial do cliente
    handshake_data = client_socket.recv(1024).decode('utf-8')
    print("Recebido handshake:", handshake_data)

    # Confere o handshake e separa o modo de operação e o tamanho máximo
    parts = handshake_data.split('|')
    if parts[0] == "HANDSHAKE" and len(parts) == 3:
        mode = parts[1]  # Tipo de operação
        max_size = int(parts[2])  # Tamanho máximo do pacote

        # Envia a resposta de OK para o cliente
        response = f"OK|Modo de operação: {mode}|Tamanho máximo: {max_size}"
        client_socket.send(response.encode('utf-8'))

        return mode, max_size
    else:
        client_socket.send("Erro no handshake".encode('utf-8'))
        return None, None

# Recebendo mesnagens cliente
def comunicacao_cliente(client_socket):

    while True:
        # Recebe a mensagem do cliente
        data = client_socket.recv(1024).decode('utf-8')
        # Se não houver nada, já quebra
        if not data:
            break

        print("Mensagem recebida:", data)

        # Se o cliente enviar 'sair', termina a comunicação
        if data.lower() == 'sair':
            print("Cliente desconectado...")
            break

        # Verifica o tipo da mensagem e responde
        parts = data.split('|')
        if parts[0] == "MSG":
            # Mensagem recebida com sucesso, envia a resposta
            response = "RESPONSE|Mensagem recebida com sucesso!"
            client_socket.send(response.encode('utf-8'))
        elif parts[0] == "NACK":
            response = "NACK|Erro no pacote"
            client_socket.send(response.encode('utf-8'))
        else:
            response = "NACK|Formato de mensagem inválido"
            client_socket.send(response.encode('utf-8'))

def servidor():

    # Definindo o endereço do servidor
    host = '127.0.0.1'  
    port = 8080  
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))

    # Esperando mensagem do cliente
    server_socket.listen(1)
    print(f"Servidor ouvindo em {host}:{port}...")

    # Aceitando conexão com o cliente
    client_socket, endereco = server_socket.accept()
    print("Conectado cliente no endereço:", endereco)

    # Realiza o handshake
    mode, max_size = process_handshake(client_socket)

    if mode and max_size:
        print(f"Modo de operação: {mode}, Tamanho máximo de pacote: {max_size}")
        # Inicia a troca de mensagens
        comunicacao_cliente(client_socket)
    
    # Fecha a conexão
    client_socket.close()

