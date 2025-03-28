import socket

# Realizando o handshake
def process_handshake(client_socket):

    # Recebe o handshake inicial do cliente (SYN)
    resposta_syn = client_socket.recv(1024).decode('utf-8')
    print("Recebido handshake:", resposta_syn)

    # Confere o handshake e separa o modo de operação e o tamanho máximo
    parts = resposta_syn.split('|')
    if parts[0] == "SYN" and len(parts) == 3:
        modo = parts[1]  # Tipo de operação
        tam_max = int(parts[2])  # Tamanho máximo do pacote

        # Envia a resposta para o cliente (SYN-ACK)
        mensagem_syn_ack = f"SYN-ACK|{modo}|{tam_max}"
        client_socket.send(mensagem_syn_ack.encode('utf-8'))


        # Recebendo confirmação (ACK)
        resposta_ack = client_socket.recv(1024).decode('utf-8')

        if resposta_ack == "ACK":
            print("Conexão feito estabelecida - handshake de 3 vias!")
            return modo, tam_max
        else:
            print("Erro: ACK não recebido corretamente.")
            return None, None
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
            resposta = "RESPONSE|Mensagem recebida com sucesso!"
            client_socket.send(resposta.encode('utf-8'))
        elif parts[0] == "NACK":
            resposta = "NACK|Erro no pacote"
            client_socket.send(resposta.encode('utf-8'))
        else:
            resposta = "NACK|Formato de mensagem inválido"
            client_socket.send(resposta.encode('utf-8'))

def servidor():

    # Definindo o endereço do servidor
    host = '127.0.0.1'  
    port = 8081
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))

    # Esperando mensagem do cliente
    server_socket.listen(1)
    print(f"Servidor ouvindo em {host}:{port}...")

    # Aceitando conexão com o cliente
    client_socket, endereco = server_socket.accept()
    print("Conectado cliente no endereço:", endereco)

    # Realiza o handshake
    modo, tam_max = process_handshake(client_socket)

    if modo and tam_max:
        print(f"Modo de operação: {modo}, Tamanho máximo de pacote: {tam_max}")
        # Inicia a troca de mensagens
        comunicacao_cliente(client_socket)
    
    # Fecha a conexão
    client_socket.close()

if __name__ == '__main__':
    servidor()