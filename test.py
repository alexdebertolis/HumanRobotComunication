# This Python code is a small example that uses the laptop's microphone 
# to capture audio, convert it to text, and save the audio file for debugging.
# If you experience problems with the code, try changing the mic_index line, 
# as this line controls which microphone is used. 
# Some computers might have multiple microphone inputs. 

# for the index try the next code
# import speech_recognition as sr
# for index, name in enumerate(sr.Microphone.list_microphone_names()):
#     print(f"Microphone {index}: {name}")


import speech_recognition as sr
import noisereduce as nr
import numpy as np
import wave

mic_index = 1  # Índice del micrófono que deseas usar
recognizer = sr.Recognizer()

with sr.Microphone(device_index=mic_index) as source:
    print("Ajustando el ruido ambiental, espera unos segundos...")
    recognizer.adjust_for_ambient_noise(source, duration=2)  # Aumentamos el tiempo de ajuste
    print("Di algo ahora:")

    try:
        # Capturamos el audio
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
        print("Audio capturado. Duración:", len(audio.get_raw_data()) / source.SAMPLE_RATE, "segundos")

        # Convertimos el audio a un formato crudo (array de números)
        audio_data = np.frombuffer(audio.get_raw_data(), np.int16)

        # Aplicamos reducción de ruido
        reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=source.SAMPLE_RATE)

        # Guardamos el audio reducido en un archivo .wav para depuración
        with wave.open("audio_reducido.wav", "wb") as f:
            f.setnchannels(1)  # Estéreo: 2, Mono: 1
            f.setsampwidth(2)   # Tamaño de muestra en bytes
            f.setframerate(source.SAMPLE_RATE)
            f.writeframes(reduced_noise_audio.tobytes())  # Convertimos el array a bytes y lo guardamos

        # Reconstruimos el audio reducido en un formato que el reconocedor pueda entender
        audio_reducido = sr.AudioData(reduced_noise_audio.tobytes(), source.SAMPLE_RATE, 2)

        # Procesamos el audio reducido con reconocimiento de voz
        texto = recognizer.recognize_google(audio_reducido, language="en-US")
        print(f"Has dicho: {texto}")

    except sr.WaitTimeoutError:
        print("No se detectó ningún sonido dentro del tiempo de espera.")
    except sr.UnknownValueError:
        print("No pude entender el audio. Es posible que el reconocimiento de voz no haya captado nada claro.")
    except sr.RequestError as e:
        print(f"Error al solicitar el servicio de reconocimiento de voz: {e}. Revisa tu conexión a internet.")

