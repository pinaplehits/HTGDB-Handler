import paramiko

# Establecer los detalles de conexión SSH
host = "192.168.100.241"
username = "root"
password = "1"
timeout = 10

# Crear una instancia de SSHClient
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Conectar al servidor remoto
    client.connect(hostname=host, username=username, password=password, timeout=timeout)
    print("Conexión exitosa al servidor SSH")

    # Ejecutar el comando para ejecutar el archivo .sh
    command = "/media/fat/Scripts/update_all.sh"
    stdin, stdout, stderr = client.exec_command(command)

    # Leer y mostrar la salida en tiempo real
    for line in stdout:
        print(line.strip())


except TimeoutError:
    print("Error: No se pudo conectar al servidor")

finally:
    # Cerrar la conexión SSH
    client.close()
