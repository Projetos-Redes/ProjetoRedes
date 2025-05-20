import socket
import time
import random

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
    erro_simulado = None

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
            erro_escolhido = input("\tSelecione o Erro a ser simulado\n\t(1) Timeout Erro\n\t(2) Pacote Duplicado\n\tdigite sua escolha: ")
            if erro_escolhido == "1":
                erro_simulado = "1"
                print("\tErro de TimeOut escolhido")
                break
            elif erro_escolhido == "2":
                erro_simulado = "2"
                print("\tErro de Duplicação de Pacotes escolhido")
                break
            else:
                print("\tOpção inválida! Tente novamente")
        elif selecao == "2":
            break
        else:
            print("Opção inválida! Tente Novamente")

    mensagem = f"SYN|{modo}|{tam_max}"
    print(f"\n>> [CLIENTE] Enviando SYN para o servidor: {mensagem}")
    client_socket.send(mensagem.encode('utf-8'))

    print("\n>> [CLIENTE] Aguardando resposta SYN-ACK do servidor...")
    resposta = client_socket.recv(1024).decode('utf-8')
    print(f">> [CLIENTE] Resposta recebida: {resposta}")

    partes = resposta.split("|")
    if len(partes) == 3 and partes[0] == "SYN-ACK" and partes[1] == modo and partes[2].isdigit() and int(partes[2]) == tam_max:
        print("\n>> [CLIENTE] Enviando ACK para o servidor...")
        client_socket.send("ACK".encode('utf-8'))
        print_titulo("HANDSHAKE COM O SERVIDOR ESTABELECIDO")
    else:
        print_titulo("ERRO NO HANDSHAKE")

    return modo, tam_max, erro_simulado

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
def comunicacao_server(client_socket, mensagem, tam_max, erro_simulado):
    print_titulo("INICIANDO COMUNICAÇÃO GO-BACK-N")

    segmentos = {}
    num_sequencia = 1

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

    segmento_erro_timeout = random.randint(1, total_segmentos) if erro_simulado == "1" else None
    segmento_erro_duplicado = random.randint(1, total_segmentos) if erro_simulado == "2" else None
    

    print(f"\n>> [CLIENTE] Janela de envio inicial (tamanho: {tamanho_janela_envio})\n")
    print("=*" * 40)

    while base <= total_segmentos:
        print(f"\n>> [CLIENTE] Inicializando envio (base: {base}):")

        while len(janela_envio) < tamanho_janela_envio and prox_segmento <= total_segmentos:
            num_seq = prox_segmento
            if num_seq in segmentos:
                segmento = segmentos[num_seq]
                mensagem_enviar = f"{num_seq}|{segmento}\n".encode()

                try:
                    if erro_simulado == "1" and num_seq == segmento_erro_timeout:
                        print(f"Iniciando simulação do Erro TimeOut no segmento {num_seq}")
                        janela_envio[num_seq] = (segmento, time.time())
                        prox_segmento += 1
                        continue

                    client_socket.send(mensagem_enviar)
                    janela_envio[num_seq] = (segmento, time.time())
                    print(f">> [CLIENTE] Enviando segmento {num_seq}: '{segmento}'")
                    prox_segmento += 1

                    if erro_simulado == "2" and num_seq == segmento_erro_duplicado:
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

        if janela_envio:
            client_socket.settimeout(10)
            try:
                ack_recebido_bytes_completo = receber_mensagem_completa(client_socket)
                if not ack_recebido_bytes_completo:
                    print(">> [CLIENTE] Conexão fechada pelo servidor.")
                    break
                ack_recebido_str = ack_recebido_bytes_completo.decode('utf-8')

                if ack_recebido_str.isdigit():
                    ack_recebido = int(ack_recebido_str)
                    print(f"\n>> [CLIENTE] Recebeu ACK para o segmento: {ack_recebido}")
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
                else:
                    print(f">> [CLIENTE] ACK recebido em formato inválido: '{ack_recebido_str}'")

            except socket.timeout:
                print(f">> [CLIENTE] Timeout! Nenhum ACK recebido para o segmento {base}. Reenviando...")
                for seq_reenviar in list(janela_envio.keys()):
                    segmento_reenviar, _ = janela_envio[seq_reenviar]
                    mensagem_reenviar = f"{seq_reenviar}|{segmento_reenviar}\n".encode()
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
def comunicacao_servidor_stop_and_wait(client_socket, mensagem, tam_max, erro_simulado):
    print_titulo("INICIANDO TRANSMISSÃO STOP-AND-WAIT")

    num_sequencia = 1 
    total_segmentos = (len(mensagem) + tam_max) // tam_max
    segmento_erro = random.randint(1, total_segmentos) if erro_simulado in ["1","2"] else None

    while mensagem:
        dados_segmento = mensagem[0:tam_max]  
        mensagem = mensagem[tam_max:]  
        segmento = f"{num_sequencia}|{dados_segmento}"
        segmento_bytes = segmento.encode('utf-8')
        enviado = False

        while not enviado:

            if erro_simulado == "2" and num_sequencia == segmento_erro:
                print(f">> [CLIENTE] Simulando DUPLICAÇÃO no segmento {num_sequencia} (não enviado)")
                client_socket.send(segmento_bytes)
                erro_simulado = None
            if erro_simulado == "1" and num_sequencia == segmento_erro:
                print(f">> [CLIENTE] Simulando TIMEOUT no segmento {num_sequencia} (não enviado)")
                time.sleep(3)
                erro_simulado = None
            
            else:
                try:
                    print(f">> [CLIENTE] Enviando segmento {num_sequencia}: '{dados_segmento}'\n")
                    client_socket.send(segmento_bytes)
                except socket.error as e:
                    print(f">> [CLIENTE] Erro ao enviar: {e}")
                    return

            try:
                client_socket.settimeout(2)
                ack = client_socket.recv(1024).decode('utf-8')
                print(f">> [CLIENTE] ACK recebido: {ack}")
                if ack.strip() == f"{num_sequencia}":
                    enviado = True
                    num_sequencia += 1
                else:
                    print(f">> [CLIENTE] ACK incorreto. Reenviando segmento {num_sequencia}")
            except socket.timeout:
                print(f">> [CLIENTE] Timeout! Reenviando segmento {num_sequencia}")
            except socket.error as e:
                print(f">> [CLIENTE] Erro de socket: {e}")
                return

    try:
        print(">> [CLIENTE] Enviando sinal de fim de transmissão.")
        client_socket.send("FIM".encode('utf-8'))
    except socket.error as e:
        print(f">> [CLIENTE] Erro ao enviar FIM: {e}")

    print_titulo("TRANSMISSÃO STOP-AND-WAIT CONCLUÍDA PELO CLIENTE")


# Começar a comunicação com o servidor
def iniciar_comunicacao(client_socket, tam_max, modo, erro_simulado):
    while True:
        message = input("\nDigite sua mensagem (ou 'sair' para encerrar): ")
        if message.lower() == 'sair':
            print("Desconectando do servidor...")
            return

        if modo.upper() == "GOBACKN":
            comunicacao_server(client_socket, message, tam_max, erro_simulado)
        elif modo.upper() == "STOP-AND-WAIT":
            comunicacao_servidor_stop_and_wait(client_socket, message, tam_max, erro_simulado)
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
        modo, tam_max, erro_simulado = handshake(client_socket)

        if modo and tam_max:
            iniciar_comunicacao(client_socket, tam_max, modo, erro_simulado)

    client_socket.close()


if __name__ == '__main__':
    cliente()


