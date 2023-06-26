import subprocess
import datetime

# Comando SSH
ssh_command = ["ssh", "root@192.168.100.241"]

# Obtener la fecha y hora actual en formato militar
fecha_actual = datetime.datetime.now().strftime("%A, %d %B %Y, %H:%M:%S")

# Comando a ejecutar después de iniciar sesión
update_mister = "/media/fat/Scripts/update_all.sh"

mister_password = "1"

try:
    # Ejecutar el comando SSH con entrada de contraseña
    ssh_process = subprocess.Popen(
        ssh_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    ssh_process.communicate(input=f"{mister_password}\n", timeout=10)

    # Ejecutar el comando después de iniciar sesión
    resultado = subprocess.run(
        update_mister, capture_output=True, text=True, check=True
    )

    # Formatear el contenido a agregar al archivo de registro
    contenido = f"\n--- {fecha_actual} ---\n{resultado.stdout}\n"

    # Abrir el archivo en modo de lectura y escritura
    with open("latest_mister_update.log", "r+") as f:
        contenido_anterior = f.read()
        f.seek(0, 0)  # Mover el puntero al principio del archivo
        f.write(contenido + contenido_anterior)

except subprocess.CalledProcessError as e:
    print(f"Error al ejecutar el comando: {e}")
except subprocess.TimeoutExpired as e:
    print(e)
    ssh_process.kill()
