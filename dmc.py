import os
import wave
import argparse
import time
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from pydub import AudioSegment


def procesar_comandos():
    parser = argparse.ArgumentParser(description="Convierte archivos de audio a diferentes formatos.")
    parser.add_argument("-f", "--file", required=True, help="Archivo de entrada o carpeta.")
    parser.add_argument("-e", "--encoding", nargs="?", help="Opción de codificación para la carpeta.")
    args = parser.parse_args()

    if os.path.isdir(args.file):
        if not args.encoding:
            print("Error: Se debe especificar la opción -e al convertir una carpeta.")
            return

        archivos = [os.path.join(args.file, f) for f in os.listdir(args.file) if os.path.isfile(os.path.join(args.file, f)) and f.lower().endswith(('.mp3', '.wav', '.aif', '.aiff'))]
        
        if not archivos:
            print("No se encontraron archivos válidos en la carpeta especificada.")
            return

        print(f"Convirtiendo los archivos en la carpeta {args.file} a la opción de codificación {args.encoding}...")

        # Calcular el número de hilos según la cantidad de archivos en la carpeta
        num_archivos = len(archivos)
        num_hilos = calcular_num_hilos(num_archivos)

        # Utilizar un ThreadPoolExecutor para manejar la conversión de archivos
        with ThreadPoolExecutor(max_workers=num_hilos) as executor:
            print(f"Número de hilos utilizados: {executor._max_workers}")
            inicio = time.time()  # Registrar el tiempo de inicio
            for archivo in archivos:
                executor.submit(procesar_archivo, archivo, args.encoding)
            executor.shutdown(wait=True)  # Esperar a que todos los hilos terminen
            fin = time.time()  # Registrar el tiempo de finalización
            print(f"Tiempo transcurrido: {fin - inicio:.2f} segundos")
    else:
        audio = leer_archivo(args.file)
        if not audio:
            print("No se pudo leer el archivo de audio.")
            return

        nombre_archivo, _ = os.path.splitext(os.path.basename(args.file))

        if args.encoding:
            print(f"Convirtiendo el archivo {args.file} a la opción de codificación {args.encoding}...")
            inicio = time.time()  # Registrar el tiempo de inicio
            convertir(audio, os.path.dirname(args.file), nombre_archivo, args.encoding)
            fin = time.time()  # Registrar el tiempo de finalización
            print(f"Tiempo transcurrido: {fin - inicio:.2f} segundos")
        else:
            solicitar_formato_conversion(audio, os.path.dirname(args.file), nombre_archivo)

def leer_archivo(input_file):
    try:
        extension = os.path.splitext(input_file)[1].lower()

        if extension == ".mp3":
            audio = AudioSegment.from_file(input_file, format="mp3")
        elif extension == ".wav":
            with wave.open(input_file, "rb") as wave_file:
                audio_data = wave_file.readframes(wave_file.getnframes())
                audio = AudioSegment(
                    audio_data,
                    frame_rate=wave_file.getframerate(),
                    sample_width=wave_file.getsampwidth(),
                    channels=wave_file.getnchannels()
                )
        elif extension == ".aif" or extension == ".aiff":
            audio = AudioSegment.from_file(input_file, format="aiff")
        else:
            print(f"Formato de archivo no compatible: {extension}")
            return None

        return audio
    except Exception as e:
        print(f"Error al leer el archivo de audio: {str(e)}")
        return None
        
def convertir(audio, carpeta_origen, nombre_archivo, encoding):
    archivos_convertidos = []

    if not isinstance(encoding, list):
        encoding = [encoding]

    for enc in encoding:
        archivo_salida = os.path.join(carpeta_origen, f"{nombre_archivo}.{enc}")
        
        # Verificar si el archivo de salida ya existe
        if os.path.exists(archivo_salida):
            # Generar un nombre único para el nuevo archivo
            idx = 1
            while True:
                nuevo_nombre = f"{nombre_archivo}_{idx}.{enc}"
                archivo_salida = os.path.join(carpeta_origen, nuevo_nombre)
                if not os.path.exists(archivo_salida):
                    break
                idx += 1
        
        try:
            if enc == "aif":
                enc = "aiff"
            audio.export(archivo_salida, format=enc)
            archivos_convertidos.append(archivo_salida)
            print(f"Archivo convertido guardado como: {archivo_salida}")
        except Exception as e:
            print(f"Error al convertir el archivo al formato {enc}: {str(e)}")

    return archivos_convertidos

def calcular_tamanio_estimado(audio, formato):
    # Exportar el audio a un archivo temporal
    temp_file = "temp_audio_conversion." + formato
    if formato == "aif":
        formato = "aiff"
    audio.export(temp_file, format=formato)

    # Obtener el tamaño del archivo temporal
    tamanio_bytes = os.path.getsize(temp_file)
    tamanio_mb = tamanio_bytes / (1024 * 1024)

    # Eliminar el archivo temporal después de obtener el tamaño
    os.remove(temp_file)

    print(f"Tamaño estimado del archivo {formato.upper()}: {tamanio_mb:.2f} MB")

def procesar_archivo(archivo, encoding):
    audio = leer_archivo(archivo)
    if audio:
        nombre_archivo, _ = os.path.splitext(os.path.basename(archivo))
        convertir(audio, os.path.dirname(archivo), nombre_archivo, encoding)
    else:
        print(f"No se pudo leer el archivo de audio: {archivo}")

def solicitar_formato_conversion(audio, carpeta_origen, nombre_archivo):
    # Obtener tamaños estimados para cada formato en hilos separados
    mp3_thread = Thread(target=calcular_tamanio_estimado, args=(audio, 'mp3'))
    wav_thread = Thread(target=calcular_tamanio_estimado, args=(audio, 'wav'))
    aif_thread = Thread(target=calcular_tamanio_estimado, args=(audio, 'aif'))

    mp3_thread.start()
    wav_thread.start()
    aif_thread.start()

    mp3_thread.join()
    wav_thread.join()
    aif_thread.join()

    opcion = input("Por favor, elija en qué formato desea guardar el archivo convertido (1: WAV, 2: AIF, 3: MP3): ")
    try:
        opcion = int(opcion)
        if opcion == 1:                    
            convertir(audio, carpeta_origen, nombre_archivo, "wav")
        elif opcion == 2:
            convertir(audio, carpeta_origen, nombre_archivo, "aif")
        elif opcion == 3:
            convertir(audio, carpeta_origen, nombre_archivo, "mp3")
        else:
            print("Opción no válida.")
    except ValueError:
        print("Opción no válida.")

def calcular_num_hilos(num_archivos):
    if 0 <= num_archivos <= 10:
        return 5  # Usar 5 hilos para 10-20 archivos
    elif 11 <= num_archivos <= 20:
        return 8  # Usar 8 hilos para 11-20 archivos
    elif 21 <= num_archivos <= 40:
        return 10  # Usar 10 hilos para 21-40 archivos
    elif 41 <= num_archivos <= 60:
        return 15  # Usar 15 hilos para 41-60 archivos
    else:
        return 20  # Usar 15 hilos para más de 60 archivos (ajustar según la necesidad)

if __name__ == "__main__":
    #del *.wav
    procesar_comandos()
