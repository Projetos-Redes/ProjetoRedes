import socket

#Útil para estilizar o terminal
def print_titulo(texto):
    print("\n" + "=" * 80)
    print(f"{texto.center(80)}")
    print("=" * 80 + "\n")


#Realizando representação do handshake
def process_handshake(client_socket):
    print_titulo("AGUARDANDO HANDSHAKE DO CLIENTE")

    #1. Recebendo o SYN do cliente
    print(">> [SERVIDOR] Recebendo SYN do cliente...")
    resposta_syn = client_socket.recv(1024).decode('utf-8')
    print(f">> [SERVIDOR] SYN recebido: {resposta_syn}")

    #Confere o Handshake e separa o modo de operação e o tamanho máximo
    parts = resposta_syn.split('|')
    if parts[0] == "SYN" and len(parts) == 3:
        modo = parts[1]  
        global tam_max
        tam_max = int(parts[2])  

        #2. Envia SYN-ACK para o cliente
        mensagem_syn_ack = f"SYN-ACK|{modo}|{tam_max}"
        print(f"\n>> [SERVIDOR] Enviando SYN-ACK para o cliente: {mensagem_syn_ack}")
        client_socket.send(mensagem_syn_ack.encode('utf-8'))

        #3. Recebendo ACK
        print("\n>> [SERVIDOR] Aguardando ACK...")
        resposta_ack = client_socket.recv(tam_max).decode('utf-8')
        print(">> [SERVIDOR] ACK recebido")

        if resposta_ack == "ACK":
            print_titulo("HANDSHAKE DE 3 VIAS COMPLETO")
            return modo, tam_max
        else:
            print(">> [SERVIDOR] ERRO: ACK não recebido corretamente.")
            return None, None
    else:
        client_socket.send("Erro no handshake\n".encode('utf-8'))
        print(">> [SERVIDOR] ERRO: Formato de SYN inválido.")
        return None, None

#Recebendo mesnagens cliente
def comunicacao_cliente(client_socket):
    while True:
        print("\nAguardando mensagem do Client...")
        #Recebe a mensagem do cliente
        data = client_socket.recv(tam_max).decode('utf-8')
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
    port = 8080
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))

    #Recebendo entrada do usuário
    server_socket.listen(1)
    print(f"\n>> [SERVIDOR] Ouvindo em {host}: {port}")

    #Aceitando conexão com o cliente
    client_socket, endereco = server_socket.accept()

    #Realiza o handshake
    modo, tam_max = process_handshake(client_socket)

    if modo and tam_max:
        print(f">> [SERVIDOR] Cliente de endereço: {endereco}, conectado!")

        print(f">> [SERVIDOR] Modo de operação: {modo}, Tamanho máximo de pacote: {tam_max}")
        #Inicia a troca de mensagens
        comunicacao_cliente(client_socket)
    
    #Fecha a conexão
    client_socket.close()

if __name__ == '__main__':
    servidor()