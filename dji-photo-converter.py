from PIL import Image, ImageDraw, ImageFont
from PIL import Image
from tkinter import Tk, filedialog
import os
import subprocess
import numpy as np
import platform  # Para detectar el SO

from tqdm import tqdm


def seleccionar_imagen():
    root = Tk()
    root.withdraw()  # Ocultar la ventana principal de Tkinter
    file_path = filedialog.askopenfilename(title="Seleccionar imagen térmica",
                                           filetypes=[("JPG Files", "*.jpg"), ("All Files", "*.*")])
    return file_path
def seleccionar_directorio():
    root = Tk()
    root.withdraw()  # Ocultar la ventana principal de Tkinter
    path = filedialog.askdirectory()
    return path

def cambiar_paleta_dji(name_img,path,path_temp, palette):
    folder_temp = path_temp

    # Generar un nombre de archivo único para el archivo temporal
    output_file = f"{path_temp}/{name_img}"

    # Comando para ejecutar el procesamiento térmico con el cambio de paleta
    so = platform.system()

    # Configurar el comando dependiendo del sistema operativo
    if so == "Windows":
        # Comando para Windows
        cmd = [
            "dji_thermal_sdk_v1.4_20220929/utility/bin/windows/release_x86/dji_irp.exe",
            "-s", path,
            "-a", "process",
            "-o", output_file,
            "-p", palette,
        ]
    elif so == "Darwin":  # Darwin es macOS
        # Comando para macOS
        cmd = [
            "wine", "dji_thermal_sdk_v1.4_20220929/utility/bin/windows/release_x86/dji_irp.exe",
            "-s", path,
            "-a", "process",
            "-o", output_file,
            "-p", palette,
        ]
    else:
        raise RuntimeError(f"El sistema operativo {so} no es compatible con este script.")

    # Ejecutar el comando
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Verificar si el comando se ejecutó correctamente
    if result.returncode != 0:
        #print(f"Error ejecutando el comando: {result.stderr}")
        raise RuntimeError(f"Fallo en la ejecución del comando para {path}")

    #print(f"Paleta de colores cambiada con éxito para la imagen: {path}")

    # Verificar si el archivo de salida se ha generado correctamente
    if not os.path.exists(output_file):
        raise FileNotFoundError(f"Archivo de salida {output_file} no encontrado para {path}")

    #print(f"Imagen con nueva paleta de colores guardada en: {output_file}")
    return output_file

def convertir_raw_a_jpg(raw_file, output_jpg, width, height, channels):
    # Leer los datos del archivo raw
    with open(raw_file, "rb") as file:
        raw_data = file.read()

    # Verificar el tamaño esperado de la imagen en función de los canales (RGB por defecto)
    expected_size = width * height * channels
    if len(raw_data) != expected_size:
        raise ValueError(f"Tamaño inesperado del archivo .raw: {len(raw_data)} bytes (esperado {expected_size} bytes)")

    # Convertir los datos raw a un array numpy
    img_array = np.frombuffer(raw_data, dtype=np.uint8).reshape((height, width, channels))

    # Crear una imagen a partir del array numpy
    img = Image.fromarray(img_array)

    # Guardar la imagen en formato JPG
    img.save(output_jpg, "JPEG")
    #print(f"Imagen guardada en: {output_jpg}")

def draw_text_with_border(draw, position, text, font, text_color, border_color):
    """
    Función auxiliar para dibujar texto con un borde.
    """
    x, y = position
    # Dibujar el texto con borde
    draw.text((x - 1, y - 1), text, font=font, fill=border_color)
    draw.text((x + 1, y - 1), text, font=font, fill=border_color)
    draw.text((x - 1, y + 1), text, font=font, fill=border_color)
    draw.text((x + 1, y + 1), text, font=font, fill=border_color)
    # Dibujar el texto principal
    draw.text((x, y), text, font=font, fill=text_color)


def texto_en_imagen(path_img_new, nameimagen, directorio_metadata):
    """
    Agrega el texto de la metadata (fecha, coordenadas, altitud) a la imagen.

    :param path_img_new: Ruta de la imagen a la que se le agregará el texto.
    :param nameimagen: Nombre de la imagen.
    :param directorio_metadata: Directorio donde se encuentra el archivo de metadata.
    """

    # Construir la ruta del archivo de metadata
    archivo_metadata = os.path.join(directorio_metadata, f"{nameimagen}.txt")

    # Leer la metadata del archivo de texto
    with open(archivo_metadata, "r") as file:
        lineas = file.readlines()

    hora_fecha = lineas[0].strip()  # Primera línea: Fecha y hora
    coordenadas_altura = lineas[1].strip()  # Segunda línea: Coordenadas y altura

    # Cargar la imagen
    image = Image.open(path_img_new)

    # Crear un objeto de dibujo
    draw = ImageDraw.Draw(image)

    # Elegir la fuente y el tamaño (asegúrate de tener la fuente 'arial.ttf')
    font = ImageFont.truetype("fuente/Verdana.ttf", 21)
    #font = ImageFont.truetype("C:/Users/Adentu/Desktop/Fotos DJI/fuente/Verdana.ttf", 20)
    #font = ImageFont.truetype("C:/Users/Adentu/Desktop/Fotos DJI/fuente/Courier.ttf", 19)
    #font = ImageFont.truetype("C:/Users/Adentu/Desktop/Fotos DJI/fuente/Courier_New.ttf", 19)

    # Definir la posición del texto
    text_position = (26, 17)  # Coordenadas (x, y) para la fecha y hora
    text_position1 = (26, 47)  # Coordenadas (x, y) para las coordenadas y altura

    # Definir el color del texto y el borde
    text_color = (255, 255, 255)  # Blanco
    border_color = (0, 0, 0)  # Negro para el borde

    # Agregar el texto con borde a la imagen
    draw_text_with_border(draw, text_position, hora_fecha, font, text_color, border_color)
    draw_text_with_border(draw, text_position1, coordenadas_altura, font, text_color, border_color)

    # Guardar la imagen con el texto añadido
    new_name = os.path.splitext(path_img_new)[0] + ".JPG"
    image.save(new_name)

def extraer_info_y_guardar(imagen_origen, output_dir):
    """
    Extrae la fecha, hora, coordenadas GPS y altitud de una imagen utilizando ExifTool
    y guarda la información en un archivo de texto con el nombre de la foto.

    :param imagen_origen: Ruta de la imagen que contiene los metadatos a extraer.
    :param output_dir: Directorio donde se guardará el archivo de texto.
    """

    # Comando para extraer la fecha, hora, GPS y altitud usando ExifTool
    cmd_extraer = [
        "exiftool",
        "-DateTimeOriginal",  # Fecha y hora
        "-GPSLatitude",  # Latitud
        "-GPSLongitude",  # Longitud
        "-GPSAltitude",  # Altitud
        imagen_origen
    ]

    # Ejecutar el comando para extraer los metadatos
    result = subprocess.run(cmd_extraer, capture_output=True, text=True)

    # Verificar si el comando se ejecutó correctamente
    if result.returncode != 0:
        print(f"Error extrayendo metadatos de {imagen_origen}: {result.stderr}")
        return

    # Procesar la salida para obtener los datos de interés
    output_lines = result.stdout.splitlines()
    info = {}

    for line in output_lines:
        if "Date/Time Original" in line:
            info["FechaHora"] = line.split(": ", 1)[1]
        elif "GPS Latitude" in line:
            info["Latitud"] = line.split(": ", 1)[1]
        elif "GPS Longitude" in line:
            info["Longitud"] = line.split(": ", 1)[1]
        elif "GPS Altitude" in line:
            info["Altitud"] = line.split(": ", 1)[1].replace(" m Above Sea Level", "m")

    # Modificar el formato de la fecha de YYYY:MM:DD a YYYY-MM-DD
    fecha, hora = info['FechaHora'].split(" ")
    fecha = fecha.replace(":", "-")
    info["FechaHora"] = f"{fecha} {hora}"

    # Reemplazar "deg" con "°" en las coordenadas
    info["Latitud"] = info["Latitud"].replace(" deg", "°").replace(" ", "")  # Eliminar espacios en las coordenadas
    info["Longitud"] = info["Longitud"].replace(" deg", "°").replace(" ", "")  # Eliminar espacios en las coordenadas

    # Formatear los datos extraídos con un solo espacio entre las coordenadas y la altitud
    datos_extraidos = f"{info['FechaHora']}\n{info['Latitud']} {info['Longitud']} {info['Altitud']}"

    # Obtener el nombre de la imagen sin la extensión
    nombre_imagen = os.path.splitext(os.path.basename(imagen_origen))[0]

    # Crear la ruta completa para el archivo de texto
    archivo_texto = os.path.join(output_dir, f"{nombre_imagen}.txt")

    # Guardar los datos extraídos en un archivo de texto
    with open(archivo_texto, "w") as file:
        file.write(datos_extraidos)

    #print(f"Información guardada en {archivo_texto}")

def copiar_metadatos(imagen_origen, imagen_destino):
    """
    Copia los metadatos de una imagen a otra utilizando ExifTool y elimina la miniatura (thumbnail) incrustada.

    :param imagen_origen: Ruta de la imagen que contiene los metadatos a copiar.
    :param imagen_destino: Ruta de la imagen a la que se copiarán los metadatos.
    """
    cmd_copiar_metadatos = [
        "exiftool",
        "-tagsfromfile", imagen_origen,  # Copia los metadatos desde la imagen origen
        "-all:all",  # Copia todos los metadatos
        "--MakerNotes",  # Excluye MakerNotes
        "-overwrite_original",  # Sobrescribe la imagen destino
        imagen_destino  # Imagen destino
    ]

    result_metadatos = subprocess.run(cmd_copiar_metadatos, capture_output=True, text=False)

    # Paso 2: Eliminar la miniatura incrustada (thumbnail)
    cmd_eliminar_thumbnail = ["exiftool", "-ThumbnailImage=", "-overwrite_original", imagen_destino]

    # Ejecutar el comando para eliminar la miniatura
    result_thumbnail = subprocess.run(cmd_eliminar_thumbnail, capture_output=True, text=False)


def escalar_imagen(input_image_path, output_image_path, new_size=(1280, 1024)):
    # Cargar la imagen
    img = Image.open(input_image_path)

    # Escalar la imagen al nuevo tamaño
    img_escalada = img.resize(new_size, Image.Resampling.LANCZOS)  # Usar el método LANCZOS  # Puedes usar otros métodos de interpolación

    # Guardar la imagen escalada
    img_escalada.save(output_image_path)
    #print(f"Imagen escalada guardada en: {output_image_path}")

# ------------------ Inicio
dir_main = seleccionar_directorio()

dir_temp = os.path.join(dir_main,"temp")
if not os.path.exists(dir_temp):
    os.makedirs(dir_temp)

dir_img = os.path.join(dir_main,"img")

dir_img_new = os.path.join(dir_main,"img_new")
if not os.path.exists(dir_img_new):
    os.makedirs(dir_img_new)

dir_metadata = os.path.join(dir_main,"metadata")
if not os.path.exists(dir_metadata):
    os.makedirs(dir_metadata)
"""
with tqdm(total=len(os.listdir(dir_img)), desc="Convirtiendo imagenes") as pbar:
    for img in os.listdir(dir_img):
        # Actualiza la barra con el nombre del archivo actual
        pbar.set_postfix({"Procesando": os.path.basename(img)})

        # Cambiar paleta térmica
        temp_image_path = cambiar_paleta_dji(img, os.path.join(dir_img, img), dir_temp, palette="iron_red")

        # Convertir a JPG
        jpg_output_path = os.path.join(dir_img_new, os.path.basename(img))  # Mantén el mismo nombre

        convertir_raw_a_jpg(temp_image_path, jpg_output_path, width=640, height=512, channels=3)

        extraer_info_y_guardar(os.path.join(dir_img, img), dir_metadata)
        # Actualizar la barra de progreso
        pbar.update(1)
"""
with tqdm(total=len(os.listdir(dir_img_new)), desc="Re-escalando imagenes") as pbar:
    for img in os.listdir(dir_img_new):
        pbar.set_postfix({"Procesando": img})
        escalar_imagen(os.path.join(dir_img_new, img), os.path.join(dir_img_new, img))
        pbar.update(1)


with tqdm(total=len(os.listdir(dir_img_new)), desc="Escribiendo texto en imagen") as pbar:
    for img in os.listdir(dir_img_new):
        texto_en_imagen(os.path.join(dir_img_new,img), img.split(".")[0], dir_metadata)
        pbar.update(1)


with tqdm(total=len(os.listdir(dir_img_new)), desc="Copiando Metadata") as pbar:
    for img in os.listdir(dir_img_new):
        pbar.set_postfix({"Procesando": os.path.basename(img)})
        copiar_metadatos(os.path.join(dir_img, img), os.path.join(dir_img_new, img))
        pbar.update(1)

