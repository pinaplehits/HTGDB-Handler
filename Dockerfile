FROM pinaplehits/htgdb-dependencies:latest

WORKDIR /app

COPY . .

CMD ["python", "build.py"]
