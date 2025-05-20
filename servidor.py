import socket
import time

# Útil para estilizar o terminal
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
        resposta_ack = client_socket.recv(1024).decode('utf-8')
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
# Recebendo mensagens  
def receber_mensagem_completa(socket_conexao):
    mensagem_completa = b''
    while b'\n' not in mensagem_completa:
        parte = socket_conexao.recv(1024)
        if not parte:
            print(">> [SERVIDOR] Conexão fechada pelo cliente.")
            return mensagem_completa  
        mensagem_completa += parte
    return mensagem_completa.split(b'\n')[0]  

# Recebendo mensagens do cliente - STOP-AND-WAIT
def comunicacao_cliente_stop_and_wait(client_socket):
    print_titulo("INICIANDO RECEPÇÃO STOP-AND-WAIT")

    mensagem_final = "" 

    proximo_esperado = 1

    while True:
        try:
            segmento_recebido_bytes_completo = client_socket.recv(1024)
            if not segmento_recebido_bytes_completo:
                break  
            
            # Segmento recebido
            segmento_recebido_str = segmento_recebido_bytes_completo.decode('utf-8')

            # Separando em indice e dados
            parts = segmento_recebido_str.split('|', 1)
            if len(parts) == 2:
                try:
                    num_sequencia = int(parts[0])
                    dados = parts[1]
                    print(f"\n>> [SERVIDOR] Recebeu segmento {num_sequencia}: '{dados}'")

                    # Se for o segmento esperado
                    if num_sequencia == proximo_esperado:
                        print(f">> [SERVIDOR] Segmento {num_sequencia} recebido na ordem esperada.")
                        mensagem_final += dados
                        ack_enviar = f"{num_sequencia}\n"
                        client_socket.send(ack_enviar.encode('utf-8'))
                        print(f">> [SERVIDOR] Enviou ACK {num_sequencia} para o cliente.")
                        proximo_esperado += 1

                    # Se não for o esperado
                    else:
                        print(f">> [SERVIDOR] Segmento inesperado. Esperava {proximo_esperado}, recebeu {num_sequencia}. Ignorando.")

                except ValueError:
                    print(f">> [SERVIDOR] Erro ao converter número de sequência: {parts[0]}")
            else:
                print(f">> [SERVIDOR] Formato de segmento inválido: {segmento_recebido_str}")

        except socket.error as e:
            print(f">> [SERVIDOR] Erro ao receber dados: {e}")
            break
        except Exception as e:
            print(f">> [SERVIDOR] Erro inesperado: {e}")
            break

    print_titulo("TRANSMISSÃO STOP-AND-WAIT CONCLUÍDA PELO SERVIDOR")
    print(f">> [SERVIDOR] Mensagem completa recebida: {mensagem_final}\n")


# Recebendo mensagens do cliente - GoBackN
def comunicacao_cliente(client_socket):
    print_titulo("INICIANDO RECEPÇÃO GO-BACK-N")

    # Criando buffer
    buffer = {}  
    proximo_esperado = 1

    while True:
        try:
            segmento_recebido_bytes_completo = receber_mensagem_completa(client_socket)
            if not segmento_recebido_bytes_completo:
                break  
            
            # Segmento recebido
            segmento_recebido_str = segmento_recebido_bytes_completo.decode('utf-8')

            # Separando em indice e dados
            parts = segmento_recebido_str.split('|', 1)
            if len(parts) == 2:
                try:
                    num_sequencia = int(parts[0])
                    dados = parts[1]
                    print(f"\n>> [SERVIDOR] Recebeu segmento {num_sequencia}: '{dados}'")

                    # Se o segmento recebido estiver fora de ordem
                    if num_sequencia > proximo_esperado:
                        print(f">> [SERVIDOR] Segmento {num_sequencia} recebido fora de ordem. Esperando {proximo_esperado}.")
                        buffer[num_sequencia] = dados
                        ack_reenviar = f"{proximo_esperado - 1}\n"
                        client_socket.send(ack_reenviar.encode())
                        print(f">> [SERVIDOR] Reenviou ACK {proximo_esperado - 1} para cliente.")

                    if num_sequencia < proximo_esperado:
                        print(f">> [SERVIDOR] Segmento {num_sequencia} já recebido (reenvio?).")
                        ack_reenviar = f"{num_sequencia}\n"
                        client_socket.send(ack_reenviar.encode())
                        print(f">> [SERVIDOR] Reenviou ACK {num_sequencia} para cliente.")


                    # Se for o segmento esperado
                    if num_sequencia == proximo_esperado:
                        print(f">> [SERVIDOR] Segmento {num_sequencia} recebido na ordem correta.")
                        buffer[num_sequencia] = dados
                        ack_enviar = f"{num_sequencia}\n"
                        client_socket.send(ack_enviar.encode())
                        print(f">> [SERVIDOR] Enviou ACK {num_sequencia} para cliente.")
                        proximo_esperado += 1

                        while proximo_esperado in buffer:
                            print(f">> [SERVIDOR] Entregando segmento {proximo_esperado} da mensagem.")
                            proximo_esperado += 1
                        print(f">> [SERVIDOR] Próximo esperado: {proximo_esperado}")

                    
                    

                except ValueError:
                    print(f">> [SERVIDOR] Erro ao converter número de sequência: {parts[0]}")
            else:
                print(f">> [SERVIDOR] Formato de segmento inválido: {segmento_recebido_str}")

        except socket.error as e:
            print(f">> [SERVIDOR] Erro ao receber dados: {e}")
            break
        except Exception as e:
            print(f">> [SERVIDOR] Erro inesperado: {e}")
            break

    # Montar a mensagem final recebida
    mensagem_final = ""
    for i in sorted(buffer.keys()):
        mensagem_final += buffer[i]

    print_titulo("TRANSMISSÃO GO-BACK-N CONCLUÍDA PELO SERVIDOR")
    print(f"[MENSAGEM FINAL RECEBIDA]: {mensagem_final}\n")


def servidor():
    # Definindo o endereço do servidor
    host = '127.0.0.1'
    port = 8080
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))

    # Recebendo entrada do usuário
    server_socket.listen(1)
    print(f"\n>> [SERVIDOR] Ouvindo em {host}:{port}")

    # Aceitando conexão com o cliente
    client_socket, endereco = server_socket.accept()

    # Realiza o handshake
    modo, tam_max = process_handshake(client_socket)

    if modo and tam_max:
        print(f">> [SERVIDOR] Cliente de endereço: {endereco} conectado!")
        print(f">> [SERVIDOR] Modo de operação: {modo}, Tamanho máximo de pacote: {tam_max}")

        # Inicia a troca de mensagens
        if modo == "GoBackN":
            comunicacao_cliente(client_socket)
        elif modo == "stop-and-wait":
            comunicacao_cliente_stop_and_wait(client_socket)
        else:
            print(f">> [SERVIDOR] Modo de operação {modo} não reconhecido.")


    # Fecha a conexão
    client_socket.close()

if __name__ == '__main__':
    servidor()
