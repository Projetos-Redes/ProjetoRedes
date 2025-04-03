import socket

#Realizando representação do handshake
def handshake(client_socket):
    #Escolhendo Modo de Operação
    while (1):
        print("Escolha o Modo de Operacao:\n(1) GoBackN\n(2) Repetição Seletiva")
        escolha = input("Digite sua escolha: ")
        if escolha == "1":
            modo = "GoBackN"
            break
        elif escolha == "2":
            modo = "RepetiçãoSeletiva"
            break
        else:
            print("Opição inesistente! Tente novamento\n")

    #1. Enviando SYN ao servidor
    tam_max = "1025"
    mensagem = f"SYN|{modo}|{tam_max}"
    client_socket.send(mensagem.encode('utf-8'))
    print("\nEnviando SYN...")

    #2. Recebendo o SYN-ACK do Servidor
    resposta = client_socket.recv(1024).decode('utf-8')
    print("Resposta recebida do servidor: ", resposta)

    #Conferindo resposta
    if resposta.startswith("SYN-ACK") and resposta.split("|")[1] == modo and resposta.split("|")[2] == tam_max:
        #3. Enviando ACK ao servidor
        client_socket.send("ACK".encode('utf-8'))
        print("Enviando ACK...")
        print("Handshake feito! Conexão feita com sucesso com o Servidor")
    else:
        print("Erro no handshake")


#Troca de mensagens com o Servidor
def comunicacao_server(client_socket, message):
    #Enviando mensagem ao servidor
    msg = f"MSG|{message}"
    client_socket.send(msg.encode('utf-8'))

    #Recebendo resposta do servidor
    resposta = client_socket.recv(1024).decode('utf-8')
    print("Resposta do servidor:", resposta)


def cliente():
    #Conectando com servidor
    host = '127.0.0.1'  
    port = 8081

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    #Realiza o handshake com o servidor
    handshake(client_socket)

    #Troca de mensagem com o Servidor
    while True:
        #Recebendo mensagem do cliente
        message = input("\nDigite sua mensagem (ou 'sair' para encerrar): ")

        #Enviando mensagem para o servidor
        comunicacao_server(client_socket, message)

        #Se o usuário digitar 'sair', o loop é interrompido
        if message.lower() == 'sair':
            print("Desconectando do servidor...")
            break

    #Fecha a conexão
    client_socket.close()

if __name__ == '__main__':
    cliente()