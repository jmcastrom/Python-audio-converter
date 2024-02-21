# Python-audio-converter
DMC - Convertidor de Archivos de Audio

DMC es una herramienta de línea de comandos diseñada para convertir archivos de audio a diferentes formatos. Soporta tres tipos principales de archivos de audio: MP3, WAV y AIF/AIFF.

Funcionalidades principales:
- Conversión de archivos de audio MP3 a WAV, AIF/AIFF y viceversa.
- Conversión de archivos de audio WAV a MP3, AIF/AIFF y viceversa.
- Conversión de archivos de audio AIF/AIFF a MP3, WAV y viceversa.

Librerías utilizadas:
- pydub: Para manipulación de archivos de audio.
- wave: Para lectura y escritura de archivos WAV.
- argparse: Para análisis de argumentos de línea de comandos.
- os: Para manipulación de archivos y directorios.

Comandos disponibles:
- -f, --file: Especifica el archivo de entrada o carpeta a convertir. Obligatorio.
- -e, --encoding: Especifica el formato de codificación para la conversión. Opcional.

Ejemplos de uso:
1. Convertir un archivo de audio MP3 a WAV:
   python dmc.py -f archivo.mp3 -e wav

2. Convertir una carpeta de archivos de audio a formato AIF/AIFF:
   python dmc.py -f carpeta -e aif

3. Convertir un archivo de audio WAV a MP3 sin especificar el formato de salida:
   python dmc.py -f audio.wav

Nota: Es importante asegurarse de que los archivos de audio estén correctamente formateados y sean compatibles con las conversiones deseadas.


