# Cliente - Aplicacao Cliente-Servidor em Django

## 📌 Objetivo Geral

Desenvolver uma aplicação cliente-servidor capaz de fornecer um transporte confiável de dados na camada de aplicação, considerando um canal com perdas de dados e erros.

## 📅 Entregas

<details>
  <summary>07/04/2025</summary>
  Aplicações cliente e servidor devem se conectar via socket e realizar o handshake inicial (trocando, pelo menos, modo de operação e tamanho máximo).
</details>

<details>
  <summary>28/04/2025</summary>
  Troca de mensagens entre cliente e servidor considerando um canal de comunicação onde erros e perdas não ocorrem.
</details>

<details>
  <summary>19/05/2025</summary>
  Inserção de erros e perdas simulados, bem como a implementação do correto comportamento dos processos.
</details>

## 🔍 Descrição do Funcionamento

O cliente conecta-se ao servidor e envia mensagens de texto respeitando um limite máximo de caracteres por pacote. Cada pacote de mensagem conterá no máximo 3 caracteres de carga útil.

## ✨ Características Principais

- Conexão ao servidor via **localhost** ou **endereço IP** utilizando **sockets**;
- Implementação de um **protocolo de aplicação** para requisições e respostas;
- Suporte a todas as **características do transporte confiável de dados**:
  - Soma de verificação;
  - Temporizador;
  - Número de sequência;
  - Reconhecimento e reconhecimento negativo;
  - Janela e paralelismo;
- Simulação de **falhas de integridade e perdas de mensagens**;
- Envio de pacotes isolados ou em lote;
- Configuração de confirmação de mensagens individualmente ou em grupo.

## 🛠️ Como Rodar o Cliente em Django

### 1️⃣ Pré-requisitos

Certifique-se de ter instalado:

- Python 3.8+
- Virtualenv (opcional, mas recomendado)

### 2️⃣ Configuração do Ambiente

1. Clone o repositório:
   ```sh
   git clone https://github.com/Projetos-Redes/ProjetoRedes.git
   cd ProjetoRedes
   ```
2. Crie e ative um ambiente virtual (opcional, mas recomendado):
   ```sh
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate  # Windows
   ```

### 3️⃣ Configuração do Cliente

1. Configure as variáveis de ambiente no arquivo `.env`:
   ```env
   host=127.0.0.1  # Endereço do servidor
   port=8000        # Porta do servidor
   ```

### 4️⃣ Executando o Servidor

1. Execute o cliente:
   ```sh
   python3 servidor.py
   ```
2. Envie mensagens para o servidor:
   ```sh
   python3 cliente.py
   ```
