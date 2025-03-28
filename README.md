# Cliente - Aplicacao Cliente-Servidor em Django

## 📌 Objetivo Geral

Desenvolver uma aplicação cliente-servidor capaz de fornecer um transporte confiável de dados na camada de aplicação, considerando um canal com perdas de dados e erros.

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
- Django 4.0+
- Virtualenv (opcional, mas recomendado)

### 2️⃣ Configuração do Ambiente

1. Clone o repositório:
   ```sh
   git clone https://github.com/SUA-ORGANIZACAO/cliente-django.git
   cd cliente-django
   ```
2. Crie e ative um ambiente virtual (opcional, mas recomendado):
   ```sh
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate  # Windows
   ```
3. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```

### 3️⃣ Configuração do Cliente

1. Configure as variáveis de ambiente no arquivo `.env`:
   ```env
   SERVER_HOST=127.0.0.1  # Endereço do servidor
   SERVER_PORT=8000        # Porta do servidor
   MESSAGE_LIMIT=3         # Número máximo de caracteres por pacote
   ```

### 4️⃣ Executando a Aplicação Cliente

1. Execute o cliente:
   ```sh
   python manage.py runserver
   ```
2. Envie mensagens para o servidor:
   ```sh
   python cliente.py "Mensagem para o servidor"
   ```
