import socket

#Realizando representação do handshake
def process_handshake(client_socket):
    #Recebe o HandShake do cliente
    resposta_syn = client_socket.recv(1024).decode('utf-8')
    print("\nServidor recebendo SYN...")
    print("SYN recebido: ", resposta_syn)

    #Confere o Handshake e separa o modo de operação e o tamanho máximo
    parts = resposta_syn.split('|')
    if parts[0] == "SYN" and len(parts) == 3:
        modo = parts[1]  #Tipo de operação
        tam_max = int(parts[2])  #Tamanho máximo do pacote

        #Envia SYN-ACK para o cliente
        mensagem_syn_ack = f"SYN-ACK|{modo}|{tam_max}"
        client_socket.send(mensagem_syn_ack.encode('utf-8'))
        print("Servidor enviando SYN-ACK...")

        #Recebendo ACK
        resposta_ack = client_socket.recv(1024).decode('utf-8')
        print("Recebendo ACK...")
        if resposta_ack == "ACK":
            print("Conexão estabelecida - handshake de 3 vias!\n")
            return modo, tam_max
        else:
            print("Erro: ACK não recebido corretamente.\n")
            return None, None
    else:
        client_socket.send("Erro no handshake\n".encode('utf-8'))
        return None, None

#Recebendo mesnagens cliente
def comunicacao_cliente(client_socket):
    while True:
        print("\nAguardando menssagem do Client...")
        #Recebe a mensagem do cliente
        data = client_socket.recv(1024).decode('utf-8')
        #Se estiver vazia, encerra a conexão
        if not data:
            break
        print("Mensagem recebida:", data)

        #Verifica o tipo da mensagem e responde
        parts = data.split('|')
        if parts[0] == "MSG":
            resposta = "RESPONSE|Mensagem recebida com sucesso!"
            client_socket.send(resposta.encode('utf-8'))
        elif parts[0] == "NACK":
            resposta = "NACK|Erro no pacote"
            client_socket.send(resposta.encode('utf-8'))
        else:
            resposta = "NACK|Formato de mensagem inválido"
            client_socket.send(resposta.encode('utf-8'))
    print("Cliente desconectado!")

def servidor():
    #Definindo o endereço do servidor
    host = '127.0.0.1'  
    port = 8081
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))

    #Recebendo entrada do usuário
    server_socket.listen(1)
    print(f"Servidor ouvindo em {host}: {port}")

    #Aceitando conexão com o cliente
    client_socket, endereco = server_socket.accept()
    print("Conectado cliente no endereço:", endereco)

    #Realiza o handshake
    modo, tam_max = process_handshake(client_socket)

    if modo and tam_max:
        print(f"Modo de operação: {modo}, Tamanho máximo de pacote: {tam_max}")
        #Inicia a troca de mensagens
        comunicacao_cliente(client_socket)
    
    #Fecha a conexão
    client_socket.close()

if __name__ == '__main__':
    servidor()