# Usando uma imagem Python base
FROM python:3.9-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos do projeto para o diretório de trabalho
COPY . .

# Instalar as dependências
RUN pip install -r requirements.txt

# Expor a porta do Flask
EXPOSE 5000

# Rodar a aplicação Flask
CMD ["python", "app.py"]
