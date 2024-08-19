#!/usr/bin/env python

import subprocess
import speech_recognition as sr
import pyttsx3
import pyaudio
import numpy as np
from scipy.fft import fft
import wave
import matplotlib.pyplot as plt
from pydub import AudioSegment
from datetime import datetime
import display_art_copy
import os
import json
import requests
import sys
import soundfile as sf
import logging
import socket
import threading
import time
import visualize
from datetime import datetime
from scapy.all import ARP, Ether, srp
from logging.handlers import RotatingFileHandler
from speech_to_text_module import main as speech_to_text_main

# Constants
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1263902529490518077/sZCrWTe17rbYTggqY3WgdGEqIZ7Ylf4zMZpTG15xxERebonD6mtcZRB4vyjM3RsH50Lr"
# 1.1.3.py
def main_function():
    # Your script's main logic here
    return "Output from the script"

if sys.stdout.isatty():
    R = '\033[31m'  # Red
    G = '\033[32m'  # Green
    C = '\033[36m'  # Cyan
    W = '\033[0m'   # Resetw
    Y = '\033[33m'  # Yellow
    M = '\033[35m'  # Magenta
    B = '\033[34m'  # Blue
else:
    R = G = C = W = Y = M = B = ''




def detect_anomalies(data, reference_spectrum=None, threshold_factor=0.8):
    """
    Detect anomalies in the audio data based on the deviation from a reference spectrum.
    """
    if not isinstance(data, np.ndarray):
        raise ValueError("Input data must be a numpy array.")
    if data.size == 0:
        raise ValueError("Input data must not be empty.")
    if reference_spectrum is not None and not isinstance(reference_spectrum, np.ndarray):
        raise ValueError("Reference spectrum must be a numpy array or None.")
    if not (0 <= threshold_factor <= 1):
        raise ValueError("Threshold factor must be between 0 and 1.")
    
    current_spectrum = np.abs(fft(data))
    if reference_spectrum is None:
        return [], current_spectrum
    
    if len(current_spectrum) != len(reference_spectrum):
        raise ValueError("Current spectrum and reference spectrum must have the same length.")
    
    deviation = np.abs(current_spectrum - reference_spectrum)
    threshold = np.max(reference_spectrum) * threshold_factor
    anomalies = [i for i, val in enumerate(deviation) if val > threshold]
    
    return anomalies, current_spectrum

def plot_waveform(audio_samples, sample_rate, plot_path):
    """
    Plot the waveform of audio samples and save it to a file.
    """
    if audio_samples is None:
        print("Error: No audio samples provided.")
        return

    plt.figure(figsize=(10, 4))
    if audio_samples.ndim == 2 and audio_samples.shape[1] == 2:
        audio_samples = audio_samples[:, 0]
    if audio_samples.ndim != 1:
        raise ValueError("audio_samples must be a 1D array")

    plt.plot(audio_samples)
    plt.title("Waveform")
    plt.xlabel("Sample")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.savefig(plot_path)
    plt.close()
    print(f"{B}Waveform plot saved to {plot_path}{W}")

def read_wave_file(file_path):
    """
    Read a WAV file and return audio samples, sample rate, and number of channels.
    """
    try:
        with wave.open(file_path, 'rb') as wave_file:
            sample_rate = wave_file.getframerate()
            num_channels = wave_file.getnchannels()
            sampwidth = wave_file.getsampwidth()
            n_frames = wave_file.getnframes()
            audio_data = wave_file.readframes(n_frames)
            audio_samples = np.frombuffer(audio_data, dtype=np.int16)
            if num_channels == 2:
                audio_samples = np.reshape(audio_samples, (-1, 2))
            return audio_samples, sample_rate, num_channels
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None, None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None

def plot_spectrum(audio_samples, sample_rate, plot_path):
    """
    Plot the frequency spectrum of audio samples and save it to a file.
    """
    if audio_samples is None:
        print("Error: No audio samples provided.")
        return

    n = len(audio_samples)
    fft_result = np.fft.fft(audio_samples)
    fft_freq = np.fft.fftfreq(n, d=1/sample_rate)
    magnitude = np.abs(fft_result)

    plt.figure(figsize=(10, 4))
    plt.plot(fft_freq[:n // 2], magnitude[:n // 2])
    plt.title("Frequency Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.grid(True)
    plt.savefig(plot_path)
    plt.close()
    print(f"{B}Frequency spectrum plot saved to {plot_path}{W}")

def send_log_to_discord(log_message):
    """
    Send a log message to a Discord channel via webhook.
    """
    data = {"content": log_message}
    response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(data), headers={"Content-Type": "application/json"})
    if response.status_code != 204:
        print(f"Failed to send log to Discord: {response.status_code}")

class ControlPanel:
    def __init__(self):
        self.audio_files = {}

    def playback_control(self):
        pass


    def convert_wav_to_mp3(self, wav_file, mp3_file):
        try:
            audio = AudioSegment.from_wav(wav_file)
            audio.export(mp3_file, format="mp3")
            print(f"{Y}Converted {wav_file} to {mp3_file}{W}")
        except Exception as e:
            print(f"{B}Error converting WAV to MP3: {e}{W}")

    def convert_mp3_to_wav(self, mp3_file, wav_file):
        try:
            audio = AudioSegment.from_mp3(mp3_file)
            audio.export(wav_file, format="wav")
            print(f"{Y}Converted {mp3_file} to {wav_file}{W}")
        except Exception as e:
            print(f"{R}Error converting MP3 to WAV: {e}{W}")

    def choose_song(self):
        print(f"{Y}Options:{W}")
        print(f"1. {G}Anomaly Detection{W}")
        print(f"2. {G}Speech To Text{W}")
        print(f"3. {G}Visualizer{W}")
        print(f"4. {G}Honeypot{W}")
        print(f"{R}CTRL+C to exit{W}")

        while True:
            user_input = input("Enter your choice: ").strip()

          
            if user_input == '1':
                file_path = input(f"{B}Enter the path to the file to convert or press 'Enter' to return to main menu: {W}").strip()
                if file_path.lower().endswith('.mp3'):
                    wav_path = file_path.rsplit('.', 1)[0] + '.wav'
                    self.convert_mp3_to_wav(file_path, wav_path)
                    return wav_path
                elif file_path.lower().endswith('.wav'):
                    return file_path
                else:
                    print(f"{R}Returning to main menu...{W}")
                        
            elif user_input == '2':
                speech_to_text_main()
            
            if user_input == '3':
                visualize.visualize_main()

                main()
                
            #initialize the recognaizer again
            elif user_input == '4':
                # Logger setup
                logger = logging.getLogger('NetworkListener')
                logger.setLevel(logging.DEBUG)
                handler = RotatingFileHandler('network_listener.log', maxBytes=1024*1024, backupCount=5)
                handler.setLevel(logging.DEBUG)
                handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                logger.addHandler(handler)

                # Globals
                suspicious_activity_flag = False
                device_list = []
                listening = False

                def create_listener_socket(host='0.0.0.0', port=65432):
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((host, port))
                    s.listen()
                    logger.info(f"Listening on {host}:{port}")
                    return s

                def log_connection(client_address):
                    ip, port = client_address
                    logger.info(f"Connection from {ip}:{port}")
                    device_list.append({'ip': ip, 'port': port, 'timestamp': datetime.now().isoformat()})

                def log_request(request_line):
                    logger.info(f"Request: {request_line}")

                def handle_request(request_data, service):
                    responses = {
                        'http': "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 13\r\nConnection: close\r\n\r\nHello, World!",
                        'ftp': "220 Welcome to the FTP server\r\n",
                        'ssh': "SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3\r\n"
                    }
                    log_request(request_data)
                    return responses.get(service, "Unsupported service")

                def monitor_activity():
                    global suspicious_activity_flag
                    while True:
                        if suspicious_activity_flag:
                            logger.warning("Suspicious activity detected!")
                            suspicious_activity_flag = False
                        time.sleep(10)

                def display_device_list():
                    print("\nList of Devices Interacting with Honeypot:")
                    if not device_list:
                        print("No devices interacted with the honeypot.")
                    for device in device_list:
                        print(f"IP: {device['ip']}, Port: {device['port']}, Timestamp: {device['timestamp']}")

                def scan_network(ip_range="192.168.1.1/24"):
                    arp = ARP(pdst=ip_range)
                    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
                    result = srp(ether/arp, timeout=2, verbose=False)[0]
                    return [{'ip': r.psrc, 'mac': r.hwsrc} for s, r in result]

                def start_listening():
                    global listening
                    listening = True
                    s = create_listener_socket()
                    threading.Thread(target=monitor_activity, daemon=True).start()
                    
                    try:
                        while listening:
                            client_socket, client_address = s.accept()
                            log_connection(client_address)
                            request_data = client_socket.recv(1024).decode('utf-8')
                            service = {80: 'http', 21: 'ftp', 22: 'ssh'}.get(client_address[1], 'unknown')
                            if service == 'unknown':
                                global suspicious_activity_flag
                                suspicious_activity_flag = True
                            response = handle_request(request_data, service)
                            client_socket.sendall(response.encode('utf-8'))
                            client_socket.close()
                    except KeyboardInterrupt:
                        logger.info("Shutting down the server.")
                    finally:
                        s.close()
                        display_device_list()

                def stop_listening():
                    global listening
                    listening = False
                    print("Stopped listening")

                def start_honeypot():
                    global listening
                    listening = True
                    s = create_listener_socket()
                    
                    try:
                        while listening:
                            client_socket, client_address = s.accept()
                            log_connection(client_address)
                            request_data = client_socket.recv(1024).decode('utf-8')
                            # Simulate specific honeypot response
                            if "malicious" in request_data.lower():
                                response = "Honeypot detected a malicious request!"
                                suspicious_activity_flag = True
                            else:
                                response = handle_request(request_data, "http")  # Default response
                            client_socket.sendall(response.encode('utf-8'))
                            client_socket.close()
                    except KeyboardInterrupt:
                        logger.info("Shutting down the honeypot.")
                    finally:
                        s.close()
                        display_device_list()

                def command_interface():
                        while True:
                            command = input(f"{M}Enter 'Honeypot' to activate honeypot. 'CTRL+C' to stop. 'Exit' to go back to main menu: {W}").strip().lower()
                            if command == 'start' and not listening:
                                start_listening()
                                print("Listener has started. Please check the listener log for details.")
                            elif command == 'scan':
                                for device in scan_network():
                                    print(f"IP: {device['ip']}, MAC: {device['mac']}")
                            elif command == 'stop' and listening:
                                stop_listening()
                            elif command == 'honeypot':
                                start_honeypot()
                            elif command == 'exit':
                                print("Returning to main menu...")
                                break
                            else:
                                print(f"{R}Invalid command. Please enter a valid option.{W}")


                        else: "user_input" == '5'
                        print(f"{G}Exiting...{W}")
                       
                if __name__ == "__main__":
                        command_interface()


def generate_report(audio_samples, sample_rate, num_channels, anomalies, waveform_plot_path, spectrum_plot_path, report_path):
    try:
        report_content = (
            "Audio Analysis Report\n"
            "====================\n\n"
            f"Sample Rate: {sample_rate} Hz\n"
            f"Number of Samples: {len(audio_samples)}\n"
            f"Number of Channels: {num_channels}\n\n"
            f"Waveform Analysis:\n"
            f"The waveform plot of the audio sample has been saved as '{os.path.basename(waveform_plot_path)}'. This plot provides a visual representation of the audio signal's amplitude over time.\n\n"
            f"Frequency Spectrum Analysis:\n"
            f"The frequency spectrum plot of the audio sample has been saved as '{os.path.basename(spectrum_plot_path)}'. This plot provides a frequency domain perspective of the audio signal. Peaks in the spectrum can indicate prominent frequencies, while any unexpected peaks or dips can highlight anomalies or unique characteristics in the audio sample.\n\n"
            f"Anomalies Detected:\n"
            f"{'No anomalies detected.' if not anomalies else 'Anomalies detected at the following frequency indices: ' + ', '.join(map(str, anomalies))}\n\n"
        )
        
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w') as report_file:
            report_file.write(report_content)
        print(f"{B}Report generated and saved to {report_path}{W}")

        send_log_to_discord(report_content)
    except Exception as e:
        print(f"{B}Error generating report: {e}{W}")

def main():
    control_panel = ControlPanel()
    song_path = control_panel.choose_song()

    if not song_path:
        print("No song selected or recorded.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    waveform_plot_path = f'/Enter/Folder/Path/waveform_{timestamp}.png'
    spectrum_plot_path = f'/Enter/Folder/Path/spectrum_{timestamp}.png'
    report_path = f'/Enter/Folder/Path/report_{timestamp}.txt'

    audio_samples, sample_rate, num_channels = read_wave_file(song_path)
    if audio_samples is None:
        return

    plot_waveform(audio_samples, sample_rate, waveform_plot_path)
    plot_spectrum(audio_samples, sample_rate, spectrum_plot_path)

    anomalies, reference_spectrum = detect_anomalies(audio_samples)
    generate_report(audio_samples, sample_rate, num_channels, anomalies, waveform_plot_path, spectrum_plot_path, report_path)

if __name__ == "__main__":
    while True:
        main()
        user_input = input("Would you like to return to the menu to do something else? (yes/no): ").strip().lower()
        if user_input != 'yes':
            print("Exiting the application. Goodbye!")
            break  # Exits the loop and ends the program
