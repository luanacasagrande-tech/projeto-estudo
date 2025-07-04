# Use uma imagem base oficial do Python.
# python:3.10-slim é uma boa escolha por ser leve e segura.
FROM python:3.10-slim

# Define o diretório de trabalho dentro do contêiner.
WORKDIR /app

# Copia o arquivo de dependências primeiro para aproveitar o cache de camadas do Docker.
# Se o requirements.txt não mudar, o Docker não reinstalará as dependências.
COPY requirements.txt .

# Instala as dependências.
# --no-cache-dir: Desativa o cache do pip para manter a imagem menor.
# --upgrade pip: Garante que a versão mais recente do pip seja usada.
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o diretório de trabalho.
COPY . .

# Expõe a porta 8000 para que a aplicação possa ser acessada de fora do contêiner.
EXPOSE 8000

# Comando para executar a aplicação quando o contêiner for iniciado.
# --host 0.0.0.0 é essencial para tornar a aplicação acessível externamente.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
