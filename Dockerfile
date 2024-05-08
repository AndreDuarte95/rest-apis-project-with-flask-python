FROM python:3.12
# EXPOSE 5000 --> FOI REMOVIDO PORQUE APOS O DEPLOY NO WEB SERVICES A PORTA JA NAO VAI SER ESSA MAS SIM A PORTA 80
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
# CMD ["flask", "run", "--host", "0.0.0.0"] --> ANTES DE FAZER O DEPLOY
# CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:create_app()"]
CMD ["/bin/bash", "docker-entrypoint.sh"]