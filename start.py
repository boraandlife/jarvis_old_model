import speech_recognition as sr
import pyttsx3
import webbrowser
import subprocess
import os
import re

# =========================
# VOICE ENGINE
# =========================
engine = pyttsx3.init()

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# Adjust speaking speed if you want
engine.setProperty("rate", 170)

# Select a voice if available
voices = engine.getProperty("voices")
if voices:
    engine.setProperty("voice", voices[0].id)

# =========================
# MICROPHONE / LISTENING
# =========================
recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.7)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="en-US")
        print("You:", text)
        return text.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("There is a problem with the internet connection or the speech service.")
        return ""

# =========================
# HELPER FUNCTIONS
# =========================
def normalize_text(text):
    text = text.lower().strip()

    replacements = {
        "you tube": "youtube",
        "chat g p t": "chatgpt",
        "chat gpt": "chatgpt",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text

def has_any(text, words):
    return any(word in text for word in words)

def open_website(name, url):
    speak(f"Opening {name}.")
    webbrowser.open(url)

def open_app(app_name):
    try:
        if app_name == "notepad":
            subprocess.Popen("notepad.exe")
            speak("Opening Notepad.")
        elif app_name == "calculator":
            subprocess.Popen("calc.exe")
            speak("Opening Calculator.")
        elif app_name == "chrome":
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
            for path in chrome_paths:
                if os.path.exists(path):
                    subprocess.Popen(path)
                    speak("Opening Chrome.")
                    return
            speak("Chrome was not found on this computer.")
        else:
            speak("I cannot open that application yet.")
    except Exception as e:
        print("Application open error:", e)
        speak("There was an error while opening the application.")

def search_google(query):
    speak(f"Searching Google for {query}.")
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)

def search_youtube(query):
    speak(f"Searching YouTube for {query}.")
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)

# =========================
# INTENT PARSING
# =========================
def parse_command(text):
    text = normalize_text(text)

    if not text:
        return ("empty", None)

    # Exit
    if has_any(text, ["exit", "quit", "close program", "stop assistant", "goodbye"]):
        return ("exit", None)

    # Greetings / general
    if has_any(text, ["hello", "hi", "are you there", "can you hear me"]):
        return ("greet", None)

    # Time
    if "what time is it" in text or "tell me the time" in text:
        return ("time", None)

    # Website-related intents
    youtube_words = ["youtube"]
    google_words = ["google", "browser", "internet"]
    chatgpt_words = ["chatgpt"]

    open_words = ["open", "start", "launch", "go to"]

    if has_any(text, youtube_words) and has_any(text, open_words):
        return ("open_youtube", None)

    if has_any(text, google_words) and has_any(text, open_words):
        return ("open_google", None)

    if has_any(text, chatgpt_words) and has_any(text, open_words):
        return ("open_chatgpt", None)

    # Open applications
    if "notepad" in text and has_any(text, open_words):
        return ("open_notepad", None)

    if ("calculator" in text or "calc" in text) and has_any(text, open_words):
        return ("open_calculator", None)

    if "chrome" in text and has_any(text, open_words):
        return ("open_chrome", None)

    # Search on YouTube
    match = re.search(r"search (.+) on youtube", text)
    if match:
        return ("search_youtube", match.group(1).strip())

    # Search on Google
    match = re.search(r"search (.+) on google", text)
    if match:
        return ("search_google", match.group(1).strip())

    # Looser matching: "... search"
    if "search" in text:
        if "youtube" in text:
            cleaned = text.replace("youtube", "").replace("search", "").replace("on", "").strip()
            if cleaned:
                return ("search_youtube", cleaned)
        elif "google" in text:
            cleaned = text.replace("google", "").replace("search", "").replace("on", "").strip()
            if cleaned:
                return ("search_google", cleaned)

    # Smarter fallback intent guesses
    if "youtube" in text:
        return ("open_youtube", None)

    if "google" in text:
        return ("open_google", None)

    if "chatgpt" in text:
        return ("open_chatgpt", None)

    return ("unknown", text)

# =========================
# EXECUTE COMMAND
# =========================
def execute_command(intent, payload):
    if intent == "empty":
        speak("I did not understand you. Please say it again.")

    elif intent == "greet":
        speak("I am here. I am listening.")

    elif intent == "open_youtube":
        open_website("YouTube", "https://www.youtube.com")

    elif intent == "open_google":
        open_website("Google", "https://www.google.com")

    elif intent == "open_chatgpt":
        open_website("ChatGPT", "https://chat.openai.com")

    elif intent == "open_notepad":
        open_app("notepad")

    elif intent == "open_calculator":
        open_app("calculator")

    elif intent == "open_chrome":
        open_app("chrome")

    elif intent == "search_google":
        search_google(payload)

    elif intent == "search_youtube":
        search_youtube(payload)

    elif intent == "time":
        from datetime import datetime
        now = datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")

    elif intent == "exit":
        speak("Alright. Shutting down.")
        return False

    elif intent == "unknown":
        speak("I could not fully understand what you meant.")
        print("Unrecognized phrase:", payload)

    return True

# =========================
# MAIN LOOP
# =========================
def main():
    speak("Voice assistant is ready. I am listening.")

    running = True
    while running:
        text = listen()
        intent, payload = parse_command(text)
        running = execute_command(intent, payload)

if __name__ == "__main__":
    main()
