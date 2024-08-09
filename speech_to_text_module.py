import speech_recognition as sr
import requests
import json
import time
import sys

WEBHOOK_URL = "https://discord.com/api/webhooks/1271094165035286539/5TIfvt427-DBcyXy1_DtrtLy3AryGC3SZmoY5-h3vEabP56wWtUFxxAr-xioTJ7X7HwO"

def main():
    r = sr.Recognizer()
    is_recording = False

    while True:
        user_input = input("Enter 'Start' to begin recording or 'Exit' to go back to main menu: ").strip().lower()
        
        if user_input == 'exit':
            print("Returning to main menu...")
            break
        
        if user_input == 'start':
            if not is_recording:
                print("Voice transcribing has started. Say 'Stop' to end recording.")
                is_recording = True
                while is_recording:
                    with sr.Microphone() as source:
                        r.adjust_for_ambient_noise(source)
                        print("Recording in progress...")
                        audio = r.listen(source)
                        try:
                            output = r.recognize_google(audio)
                            if output.lower() == "stop":
                                print("Recording and voice transcribing has stopped.")
                                is_recording = False
                            else:
                                print(f"You said: {output}")
                                send_to_discord(output)
                        except sr.UnknownValueError:
                            print("Sorry, I did not understand that.")
                        except sr.RequestError as e:
                            print(f"Error with the speech recognition service: {e}")
            elif user_input == 'stop':
                if is_recording:
                    print("Recording and voice transcribing is not active. Please use 'start' to begin.")
                else:
                    print("Recording and voice transcribing is already stopped.")
            else:
                print("Invalid command. Please enter 'Start' or 'Exit'.")
        else:
            print("Invalid command. Please enter 'Start' or 'Exit'.")

def send_to_discord(message):
    data = {"content": message}
    response = requests.post(WEBHOOK_URL, data=json.dumps(data), headers={"Content-Type": "application/json"})
    if response.status_code != 204:
        print(f"Failed to send message to Discord: {response.status_code}")

if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting...")
            sys.exit()
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Restarting...")
            time.sleep(2)  # Optional: delay before restarting
