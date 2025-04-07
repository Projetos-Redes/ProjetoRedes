import socket

#Útil para estilizar o terminal
def print_titulo(texto):
    print("\n" + "=" * 80)
    print(f"{texto.center(80)}")
    print("=" * 80 + "\n")


#Realizando representação do handshake
def handshake(client_socket):
    print_titulo("INICIANDO HANDSHAKE COM O SERVIDOR")

    #Escolhendo Modo de Operação
    while (1):
        print(">> [CLIENTE] Escolha o Modo de Operacao para SYN:\n>> [CLIENTE] (1) GoBackN\n>> [CLIENTE] (2) Repetição Seletiva")
        escolha = input(">> [CLIENTE] Digite sua escolha: ")
        if escolha == "1":
            modo = "GoBackN"
            break
        elif escolha == "2":
            modo = "RepetiçãoSeletiva"
            break
        else:
            print("Opção inexistente! Tente novamente\n")

    # Solicitando ao usuário o tamanho máximo da mensagem
    global tam_max

    while (1):
        tam_input = input(">> [CLIENTE] Digite o tamanho máximo da mensagem: ")
        if tam_input.isdigit() and int(tam_input) > 0:
            tam_max = int(tam_input)
            break
        else:
            print(">> [CLIENTE] Valor inválido! Digite um número inteiro positivo.\n")

    #1. Enviando SYN ao servidor
    print(f"\n>> [CLIENTE] Tamanho definido: {tam_max}")

    mensagem = f"SYN|{modo}|{tam_max}"
    print(f"\n>> [CLIENTE] Enviando SYN para o servidor: {mensagem}")
    client_socket.send(mensagem.encode('utf-8'))
    

    #2. Recebendo o SYN-ACK do Servidor
    print("\n>> [CLIENTE] Aguardando resposta SYN-ACK do servidor...")
    resposta = client_socket.recv(tam_max).decode('utf-8')
    print(f">> [CLIENTE] Resposta recebida: {resposta}")

    #Conferindo resposta
    if resposta.startswith("SYN-ACK") and resposta.split("|")[1] == modo and int(resposta.split("|")[2]) == tam_max:
        #3. Enviando ACK ao servidor
        print("\n>> [CLIENTE] Enviando ACK para o servidor...")
        client_socket.send("ACK".encode('utf-8'))
        print_titulo("HANDSHAKE COM O SERVIDOR ESTABELECIDO")
    else:
        print_titulo("ERRO NO HANDSHAKE")


#Troca de mensagens com o Servidor
def comunicacao_server(client_socket, message):
    #Enviando mensagem ao servidor
    msg = f"MSG|{message}"
    client_socket.send(msg.encode('utf-8'))

    #Recebendo resposta do servidor
    resposta = client_socket.recv(tam_max).decode('utf-8')
    print("Resposta do servidor:", resposta)


def cliente():
    #Conectando com servidor
    host = '127.0.0.1'  
    port = 8080

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

    except ConnectionRefusedError as error:
        print(f">> [CLIENTE] Aconteceu um erro ao tentar conectar ao servidor: {error}")
        print("Encerrando o programa...")

    else:
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