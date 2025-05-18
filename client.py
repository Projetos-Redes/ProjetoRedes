import socket
import time

# Estilizar o terminal
def print_titulo(texto):
    print("\n" + "=" * 80)
    print(f"{texto.center(80)}")
    print("=" * 80 + "\n")

# Realizando representação do handshake
def handshake(client_socket):
    print_titulo("INICIANDO HANDSHAKE COM O SERVIDOR")
    tam_max = 0
    modo = ""

    while True:
        print(">> [CLIENTE] Escolha o Modo de Operacao para SYN:\n>> [CLIENTE] (1) GoBackN\n>> [CLIENTE] (2) stop-and-wait")
        escolha = input(">> [CLIENTE] Digite sua escolha: ")
        if escolha == "1":
            modo = "GoBackN"
            break
        elif escolha == "2":
            modo = "stop-and-wait"
            break
        else:
            print("Opção inexistente! Tente novamente\n")

    while True:
        tam_input = input(">> [CLIENTE] Digite o tamanho máximo da mensagem: ")
        if tam_input.isdigit() and int(tam_input) > 0:
            tam_max = int(tam_input)
            break
        else:
            print(">> [CLIENTE] Valor inválido! Digite um número inteiro positivo.\n")

    while True:
        selecao = input("\n>> [CLIENTE] Escolha se quer simular erros:\n(1) Sim\n(2) Não\nDigite sua escolha: ")
        if selecao == "1":
            erroEscolha = input("\tSelecione o Erro a ser simulado\n\t(1) Timeout Erro\n\t(2) Pacote Duplicado\n\tdigite sua escolha: ")
            if erroEscolha == "1":
                print("\tErro de TimeOut escolhido")
                break
            elif erroEscolha == "2":
                print("\tErro de Duplicação de Pacotes escolhido")
                break
            else:
                print("\tOpição inválida! Tente novamente")
        elif selecao == "2":
            erroEscolha = None
            break
        else:
            print("Opição inválida! Tente Novamente")

    mensagem = f"SYN|{modo}|{tam_max}"
    print(f"\n>> [CLIENTE] Enviando SYN para o servidor: {mensagem}")
    client_socket.send(mensagem.encode('utf-8'))

    print("\n>> [CLIENTE] Aguardando resposta SYN-ACK do servidor...")
    resposta = client_socket.recv(1024).decode('utf-8')
    print(f">> [CLIENTE] Resposta recebida: {resposta}")

    if resposta.startswith("SYN-ACK") and resposta.split("|")[1] == modo and int(resposta.split("|")[2]) == tam_max:
        print("\n>> [CLIENTE] Enviando ACK para o servidor...")
        client_socket.send("ACK".encode('utf-8'))
        print_titulo("HANDSHAKE COM O SERVIDOR ESTABELECIDO")
    else:
        print_titulo("ERRO NO HANDSHAKE")

    return modo, tam_max, erroEscolha

# Recebendo mensagens 
def receber_mensagem_completa(socket_conexao):
    mensagem_completa = b''
    while b'\n' not in mensagem_completa:
        parte = socket_conexao.recv(1024)
        if not parte:
            return mensagem_completa
        mensagem_completa += parte
    return mensagem_completa.split(b'\n')[0]

# Troca de mensagens - GoBackN
def comunicacao_server(client_socket, mensagem, tam_max, erroSelecao):
    print_titulo("INICIANDO COMUNICAÇÃO GO-BACK-N")

    segmentos = {}
    num_sequencia = 1

    # Dividindo a mensagem em segmentos
    for i in range(0, len(mensagem), tam_max):
        segmento = mensagem[i:i + tam_max]
        segmentos[num_sequencia] = segmento
        num_sequencia += 1

    print(f">> [CLIENTE] Mensagem original: {mensagem}")
    for seq, seg in segmentos.items():
        print(f">> [CLIENTE]        Segmento {seq}: {seg}")

    tamanho_janela_envio = 3
    janela_envio = {}
    prox_segmento = 1
    base = 1
    total_segmentos = len(segmentos)

    print(f"\n>> [CLIENTE] Janela de envio inicial (tamanho: {tamanho_janela_envio})\n")
    print("=*" * 40)

    # Enviar os segmentos
    while base <= total_segmentos:
        print(f"\n>> [CLIENTE] Inicializando envio (base: {base}):")

        # Colocando na janela de envio
        while len(janela_envio) < tamanho_janela_envio and prox_segmento <= total_segmentos:
            num_seq = prox_segmento

            # Verifica se o segmento já foi enviado
            if num_seq in segmentos:
                segmento = segmentos[num_seq]
                mensagem_enviar = f"{num_seq}|{segmento}\n".encode()

                # Envia o segmento
                try:
                    if erroSelecao == "1" and num_seq == 2:
                        print(f"Iniciando simulação do Erro TimeOut no segmento {num_seq}")
                        janela_envio[num_seq] = (segmento, time.time())
                        prox_segmento += 1
                        continue

                    client_socket.send(mensagem_enviar)
                    janela_envio[num_seq] = (segmento, time.time())
                    print(f">> [CLIENTE] Enviando segmento {num_seq}: '{segmento}'")
                    prox_segmento += 1

                    if erroSelecao == "2" and num_seq == 3:
                        print(f"Iniciando simulação do Erro de Pacote Duplicado no segmento {num_seq}")
                        client_socket.send(mensagem_enviar)
                        print(f"\n{mensagem_enviar} reenviado com sucesso \n")

                except socket.error as e:
                    print(f">> [CLIENTE] Erro ao enviar segmento {num_seq}: {e}")
                    break
            else:
                prox_segmento += 1
                break

        print(f"\n>> [CLIENTE] Janela de envio atual: {list(janela_envio.keys())}")

        # Aguardar ACK do servidor
        if janela_envio:
            client_socket.settimeout(10)
            try:
                # Receber ACK do servidor
                ack_recebido_bytes_completo = receber_mensagem_completa(client_socket)
                if not ack_recebido_bytes_completo:
                    print(">> [CLIENTE] Conexão fechada pelo servidor.")
                    break
                ack_recebido_str = ack_recebido_bytes_completo.decode('utf-8')

                # Verifica se o ACK recebido é válido
                try:
                    ack_recebido = int(ack_recebido_str)
                    print(f"\n>> [CLIENTE] Recebeu ACK para o segmento: {ack_recebido}")

                    # Se está dentro da janela de envio
                    if ack_recebido >= base:
                        base = ack_recebido + 1
                        chaves_remover = [chave for chave in list(janela_envio.keys()) if chave < base]
                        for chave in chaves_remover:
                            del janela_envio[chave]
                        print(f">> [CLIENTE] Janela de envio após ACK: {list(janela_envio.keys())}")
                        print(f">> [CLIENTE] Base atualizada para: {base}\n")
                        print("=*" * 40)
                    else:
                        print(f">> [CLIENTE] ACK recebido para segmento antigo ou inválido: {ack_recebido}")

                except ValueError:
                    print(f">> [CLIENTE] ACK recebido em formato inválido: '{ack_recebido_str}'")

            except socket.timeout:
                print(f">> [CLIENTE] Timeout! Nenhum ACK recebido para o segmento {base}. Reenviando...")
                for seq_reenviar in list(janela_envio.keys()):
                    segmento_reenviar, _ = janela_envio[seq_reenviar]
                    mensagem_reenviar = f"{seq_reenviar}|{segmento_reenviar}\n".encode()  # <-- corrigido com \n
                    try:
                        client_socket.send(mensagem_reenviar)
                        janela_envio[seq_reenviar] = (segmento_reenviar, time.time())
                        print(f">> [CLIENTE] Reenviando segmento {seq_reenviar}: '{segmento_reenviar}'")
                    except socket.error as e:
                        print(f">> [CLIENTE] Erro ao reenviar segmento {seq_reenviar}: {e}")
                        break
        else:
            break

    print_titulo("TRANSMISSÃO GO-BACK-N CONCLUÍDA PELO CLIENTE")

# Troca de mensagens - stop and wait
def comunicacao_servidor_stop_and_wait(client_socket, mensagem, tam_max, erroSelecao):
    print_titulo("INICIANDO TRANSMISSÃO STOP-AND-WAIT")

    num_sequencia = 1 

    client_socket.settimeout(2)  

    while mensagem:
        # Prepara o próximo segmento
        dados_segmento = mensagem[0:tam_max]  
        mensagem = mensagem[tam_max:]  

        segmento = f"{num_sequencia}|{dados_segmento}"
        segmento_bytes = segmento.encode('utf-8')

        enviado = False

        while not enviado:
            try:
                # Enviando o segmento
                print(f">> [CLIENTE] Enviando segmento {num_sequencia}: '{dados_segmento}'\n")
                client_socket.send(segmento_bytes)

                ack_recebido_bytes = client_socket.recv(1024)
                ack_recebido = ack_recebido_bytes.decode('utf-8').strip()
                print(f">> [CLIENTE] ACK recebido: {ack_recebido}")

                # Verifica se o ACK recebido é o esperado
                if ack_recebido == str(num_sequencia):
                    print(f">> [CLIENTE] ACK {ack_recebido} recebido corretamente.")
                    enviado = True
                    num_sequencia += 1
                else:
                    print(f">> [CLIENTE] ACK inesperado ({ack_recebido}). Reenviando segmento.")

            except socket.timeout:
                print(f">> [CLIENTE] Timeout esperando ACK {num_sequencia}. Reenviando segmento.")

            except socket.error as e:
                print(f">> [CLIENTE] Erro de socket: {e}")
                return

    print_titulo("TRANSMISSÃO STOP-AND-WAIT CONCLUÍDA PELO CLIENTE")

# Começar a comunicação com o servidor
def iniciar_comunicacao(client_socket, tam_max, modo, erroSelecao):

    message = input("\nDigite sua mensagem (ou 'sair' para encerrar): ")
    if message.lower() == 'sair':
        print("Desconectando do servidor...")
        return

    if modo.upper() == "GOBACKN":
        comunicacao_server(client_socket, message, tam_max, erroSelecao)
    elif modo.upper() == "STOP-AND-WAIT":
        comunicacao_servidor_stop_and_wait(client_socket, message, tam_max, erroSelecao)
    else:
        print("Modo de operação não reconhecido.")

def cliente():
    host = '127.0.0.1'
    port = 8080

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

    except ConnectionRefusedError as error:
        print(f">> [CLIENTE] Erro ao conectar: {error}")
        print("Encerrando o programa...")
        return

    else:
        modo, tam_max, erroSelecao = handshake(client_socket)

        if modo and tam_max:
            iniciar_comunicacao(client_socket, tam_max, modo, erroSelecao)
                


    client_socket.close()


if __name__ == '__main__':
    cliente()
