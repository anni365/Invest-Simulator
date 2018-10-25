# Invest Simulator

INSTRUCCIONES PARA LA INSTALACIÓN

Especificamos los comandos utilizados para el correcto funcionamiento del
proyecto.

1- Se debe usar Python3 junto con Django 2.1.
  python3 -- version (Para ver la versión actual de Python)
  python3 -m django --version (Para ver la versión actual de Django)

  Para verificar versión de pip:
  pip --version

  Si alguno de éstos no está instalado, continuar con:
  Python - https://www.python.org/downloads/
  Django - https://docs.djangoproject.com/en/2.1/topics/install
  Si se desea instalar pip3, solo reemplazar 'pip' por 'pip3'.
  Pip Linux: sudo apt-get install python3-pip
  Pip MacOS: brew install pip

2- Descargar la carpeta contenedora de todos los archivos necesarios desde el
repositorio de GitLab con el link:
    git clone https://gitlab.com/veronicadias/invest-simulator.git

3- Luego, ir al directorio del proyecto con:
  cd Desktop/invest-simulator/TestInvest
  Suponiendo que dicho directorio está en Desktop.
  Luego hacer:
  python3 manage.py makemigrations
  python3 manage.py migrate
  Eso es únicamente la primera vez para poder migrar los datos del proyecto
  a la base de datos.

4- Finalmente, para correr el proyecto:
  python3 manage.py runserver

En este punto, ya puede ingresar a http://localhost:8000 para comenzar a usar
el programa.

Si al correr alguno de esos comandos se tiene un error de instalación, hacer:

- Instalar virtualenv en algún lugar fuera del directorio del proyecto,
  para tener una mejor organización.
  python3 -m venv virtual
  Donde 'virtual' es el nombre de la máquina virtual que estamos creando.

- Continuar con (Suponiendo que la carpeta 'virtual' está en Desktop):
  source Desktop/virtual/bin/activate
  Esto inicia con la máquina virtual. Ahora hay que instalar django y Pillow.
  (pip o) pip3 install django
  (pip o) pip3 install Pillow

- Por último, continuar desde el paso 3 comentado arriba.
