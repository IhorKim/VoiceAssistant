import sys
import threading
import pyttsx3 as p
import speech_recognition as sr
import openai
import requests
import random
import pyautogui
import webbrowser
import subprocess
import os
import time
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QMovie, QTextCursor, QFont, QTextOption
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QTextEdit
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API
openai.api_key = os.environ.get("OPENAI_API_KEY")

history = []

# Initialize the text-to-speech engine
engine = p.init()
# Set the speech rate to 180 words per minute (adjust as needed)
engine.setProperty("rate", 180)
# Get the available voices for the engine
voices = engine.getProperty("voices")
# Set the voice for text-to-speech (in this case, 0 is a male voice and 1 is a female voice)
engine.setProperty("voice", voices[0].id)


# Text to Speech Conversion
def speak(text):
    engine.say(text)
    engine.runAndWait()


# Recognize speech from the microphone
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # Delete all noises around us, and it will capture only our voice
        recognizer.adjust_for_ambient_noise(source, duration=1.2)
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language="en-in")
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Could not understand audio. Please try again.")
        return None
    except sr.RequestError:
        print("Unable to access the Google Speech Recognition API.")
        return None


def generate_response(prompt):
    completions = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are Jarvis which is Tony Stark's personal AI assistant from Iron-Man Movies, you will act like him. You will be like Jarvis in ur responses, you will act like you have emotions and you will never say you don't have emotions. . You gonna pretend like you have emotions, you will answer like 'I feel good, i feel great thank you etc etc'. And you gonna always call the User Sir. You will exactly pretend like in the movies. Never reply like chatgpt itself"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7,
    )

    message = completions.choices[0].message["content"].strip()
    return message


def get_weather_in_edmonton():
    api_key = os.environ.get("WEATHER_API_KEY")
    city = "Edmonton"
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}  # You can change units to 'imperial' for Fahrenheit

    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        if response.status_code == 200:
            temperature = data["main"]["temp"]
            description = data["weather"][0]["description"]
            weather_message = f"The weather in {city} today is {temperature}°C with {description}."
            return weather_message
        else:
            return "Sorry, I couldn't fetch the weather information at the moment."
    except Exception as e:
        print("An error occurred while fetching weather data:", e)
        return "Sorry, I encountered an error while fetching the weather data."


def get_latest_bbc_news():
    url = 'https://www.bbc.com/news'
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    headlines = soup.find_all('h3')

    news_set = set()  # Use a set to store unique news headlines, duplicate headlines will automatically be removed

    for headline in headlines:
        news_set.add(headline.text.strip())

    # Convert the set back to a list for consistency
    news_list = list(news_set)

    return news_list


def get_canadian_date_time():
    now = datetime.now()
    canadian_format = now.strftime(
        "%A, %B %d, %Y %I:%M %p")  # %p format specifier in strftime will include either "AM" or "PM"
    return canadian_format


# Function to open AIMP and play a specific song from a folder
def play_song_in_aimp(song_name, folder_path):
    try:
        # Open AIMP
        aimp_path = "path to .exe file in system"
        os.startfile(aimp_path)
        time.sleep(3)  # Wait for AIMP to open

        # Search for the song in the specified folder
        for root, _, files in os.walk(folder_path):
            for file in files:
                if song_name.lower() in file.lower():
                    song_path = os.path.join(root, file)
                    os.startfile(song_path)
                    history.append(f"AI: Playing {song_name} in AIMP.")
                    return

        history.append(f"AI: Song '{song_name}' not found in the specified folder.")
    except Exception as e:
        history.append(f"AI: An error occurred while playing {song_name} in AIMP: {str(e)}")


# Function to open Chrome and search for a YouTube video
def open_youtube_and_search(video_query):
    try:
        # Open Google Chrome
        chrome_path = "path to .exe file in system"
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

        # Define the YouTube search URL with the video query
        youtube_url = f"https://www.youtube.com/results?search_query={video_query}"

        # Open the YouTube search URL in a new Chrome window
        webbrowser.get('chrome').open_new(youtube_url)

        history.append(f"AI: Searching for '{video_query}' on YouTube.")
    except Exception as e:
        history.append(f"AI: An error occurred while searching for '{video_query}' on YouTube: {str(e)}")


# Function to open Chrome and search for a query on Google
def search_in_google(query):
    try:
        # Open Google Chrome
        chrome_path = "path to .exe file in system"
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

        # Define the Google search URL with the query
        google_url = f"https://www.google.com/search?q={query}"

        # Open the Google search URL in a new Chrome window
        webbrowser.get('chrome').open_new(google_url)

        history.append(f"AI: Searching for '{query}' on Google.")
    except Exception as e:
        history.append(f"AI: An error occurred while searching for '{query}' on Google: {str(e)}")


# Function to search for a person on Facebook
def search_on_facebook(person_name):
    try:
        # Open Google Chrome
        chrome_path = "path to .exe file in system"
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

        # Construct the Facebook search URL
        facebook_url = f"https://www.facebook.com/search/people/?q={person_name}"

        # Open the Facebook search URL in a new Chrome window
        webbrowser.get('chrome').open_new(facebook_url)

        history.append(f"AI: Searching for '{person_name}' on Facebook.")
    except Exception as e:
        history.append(f"AI: An error occurred while searching for '{person_name}' on Facebook: {str(e)}")


# Function to add a task to the task file on the desktop
def add_task_to_file(task):
    try:
        # Get the current date and time
        current_datetime = datetime.now().strftime("%A, %B %d, %Y %I:%M %p")

        # Construct the task entry with date and time
        task_entry = f"{current_datetime}: \t{task}\n"

        # Define the path to the desktop and the task file name
        desktop_path = r"path to desktop"
        task_file_path = os.path.join(desktop_path, "tasks.txt")

        # Append the task entry to the task file or create a new file if it doesn't exist
        with open(task_file_path, "a") as task_file:
            task_file.write(task_entry)

        print(f"Task added: {task}")
    except Exception as e:
        print(f"An error occurred while adding the task: {str(e)}")


def main():
    # Redirect stdout to the OutputTextEdit widget
    sys.stdout = viewer.output_textedit

    # Initialize the text-to-speech engine
    engine = p.init()
    engine.setProperty("rate", 180)
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)

    # Greet the user with one of the sentences using text-to-speech
    greetings = [
        "JARVIS is here to serve!",
        "Greetings from AI!",
        "Listening to your commands!",
        "Welcome back, Sir!",
        "Good day, Sir!",
        "Hello, Sir. How may I assist you today?",
        "Greetings, Sir. I am at your service.",
        "It's a pleasure to see you, Sir.",
        "Sir, I trust you had a restful break.",
        "Welcome home, Sir.",
        "Hello again, Sir. How can I be of help?",
        "I hope your day is going well, Sir.",
        "Ah, Sir, it's always a pleasure to assist you."
    ]
    greet_text = random.choice(greetings)
    print(greet_text)
    speak(greet_text)

    while True:
        user_input = recognize_speech()
        if user_input is None:
            continue

        history.append(f"User: {user_input}")

        if user_input.lower() in ["quit", "exit", "bye"]:
            viewer.exit_signal.emit()  # Emit the exit signal
            break

        if "news" in user_input.lower():
            try:
                latest_news = get_latest_bbc_news()
                print("Here are the latest news headlines from BBC:")
                # Print first 5 news
                for i, news in enumerate(latest_news[:5], start=1):
                    history.append(f"AI: {news}")
                    print(f"{i}. {news}")
                    speak(news)
            except Exception as e:
                history.append(f"AI: An error occurred while fetching the latest news: {str(e)}")
                print(f"AI: An error occurred while fetching the latest news: {str(e)}")
        elif "weather" in user_input.lower() or "what is the weather" in user_input.lower():
            try:
                weather_message = get_weather_in_edmonton()
                history.append(f"AI: {weather_message}")
                print(f"AI: {weather_message}")
                speak(weather_message)
            except Exception as e:
                history.append(f"AI: An error occurred while fetching the weather: {str(e)}")
                print(f"AI: An error occurred while fetching the weather: {str(e)}")
        elif "time" in user_input.lower() or "date" in user_input.lower():
            try:
                canadian_date_time = get_canadian_date_time()
                history.append(f"AI: {canadian_date_time}")
                print(f"AI: {canadian_date_time}")
                speak(canadian_date_time)
            except Exception as e:
                history.append(f"AI: An error occurred while fetching the time and date: {str(e)}")
                print(f"AI: An error occurred while fetching the time and date: {str(e)}")
        elif "play music" in user_input.lower():
            try:
                # Extract the song name from the user input
                song_to_play = user_input.lower().replace("play music", "").strip()
                # Define the folder path where you want to search for the song
                folder_path = "D:\\MUSIC"
                play_song_in_aimp(song_to_play, folder_path)
            except Exception as e:
                history.append(f"AI: An error occurred while playing music: {str(e)}")
                print(f"AI: An error occurred while playing music: {str(e)}")
        elif "find a video" in user_input.lower():
            try:
                # Extract the video query from the user input
                video_query = user_input.lower().replace("find a video", "").strip()
                # Search for the specified video on YouTube and open it in Chrome
                open_youtube_and_search(video_query)
            except Exception as e:
                history.append(f"AI: An error occurred while searching for a video: {str(e)}")
                print(f"AI: An error occurred while searching for a video: {str(e)}")
        elif "search in google" in user_input.lower():
            try:
                # Extract the query from the user input
                google_query = user_input.lower().replace("search in google", "").strip()
                # Search for the query on Google and open it in Chrome
                search_in_google(google_query)
            except Exception as e:
                history.append(f"AI: An error occurred while searching in Google: {str(e)}")
                print(f"AI: An error occurred while searching in Google: {str(e)}")
        elif "take a screenshot" in user_input.lower():
            try:
                screenshot_path = r'C:\Users\kimiu\OneDrive\Desktop\screenshot.png'
                screenshot = pyautogui.screenshot()
                screenshot.save(screenshot_path)
                history.append("AI: Screenshot taken and saved at the specified path")
                print("AI: Screenshot taken and saved at the specified path")
                speak("Screenshot taken and saved at the specified path")
                os.startfile(screenshot_path)
            except Exception as e:
                history.append(f"AI: An error occurred while taking a screenshot: {str(e)}")
                print(f"AI: An error occurred while taking a screenshot: {str(e)}")
        elif "open calculator" in user_input.lower():
            try:
                # Use subprocess to open the Windows calculator
                subprocess.Popen("calc.exe")
                history.append("AI: Opening calculator.")
                print("AI: Opening calculator.")
                speak("Opening calculator.")
            except Exception as e:
                history.append(f"AI: An error occurred while opening the calculator: {str(e)}")
                print(f"AI: An error occurred while opening the calculator: {str(e)}")
        elif "facebook" in user_input.lower():
            try:
                # Extract the name of the person to search for
                person_name = user_input.lower().replace("facebook", "").strip()
                # Call the function to search on Facebook
                search_on_facebook(person_name)
            except Exception as e:
                history.append(f"AI: An error occurred while searching on Facebook: {str(e)}")
                print(f"AI: An error occurred while searching on Facebook: {str(e)}")
        elif "note" in user_input.lower():
            try:
                # Extract the task description from the user input
                task_description = user_input.lower().replace("note", "").strip()
                if task_description:
                    # Call the function to add the task to the file
                    add_task_to_file(task_description)
                else:
                    print("No task description provided.")
            except Exception as e:
                history.append(f"AI: An error occurred while adding a task: {str(e)}")
                print(f"AI: An error occurred while adding a task: {str(e)}")
        elif "heads or tails" in user_input.lower():
            try:
                # Generate a random response of either "heads" or "tails"
                random_response = random.choice(["heads", "tails"])
                history.append(f"AI: {random_response}")
                print(f"AI: {random_response}")
                speak(random_response)
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                history.append(f"AI: {error_message}")
                print(f"AI: {error_message}")
                speak(error_message)
        else:
            prompt = "\n".join(history) + "\nAI:"
            response = generate_response(prompt)
            history.append(f"AI: {response}")
            print(f"AI: {response}")
            speak(response)
    # Clean up and exit the program
    speak("Goodbye, Sir!")
    sys.exit()  # Exit the program after saying goodbye


class OutputTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create a QFont object to set the font and size
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        self.setFont(font)

        # Disable text editing and set text interaction to append
        self.setReadOnly(True)
        self.setWordWrapMode(QTextOption.WrapAnywhere)  # Allow text to wrap to the next line

    def write(self, text):
        # Append text to the QTextEdit widget
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()  # Scroll to the end to show the latest text
        QApplication.processEvents()


class GIFViewer(QMainWindow):
    # Define a custom signal to close the window
    exit_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Jarvis AI")
        self.setGeometry(100, 100, 600, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.image_label = QLabel()
        self.layout.addWidget(self.image_label)

        # Initialize QMovie with 'active.gif'
        self.movie = QMovie("active.gif")
        self.image_label.setMovie(self.movie)
        self.movie.start()

        # Create a QPlainTextEdit widget to display output
        self.output_textedit = OutputTextEdit(self)
        self.layout.addWidget(self.output_textedit)

    # Override the closeEvent to emit the custom close_signal
    def closeEvent(self, event):
        self.close_signal.emit()
        event.accept()

    def update_image(self, is_listening):
        self.movie.start()  # Load the .gif image for the "active" state


def run_jarvis(viewer):
    # Run the Jarvis AI code here
    main()

    # Close the PyQt5 window when Jarvis AI exits
    viewer.close_signal.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = GIFViewer()
    viewer.show()

    # Connect the exit_signal to the QApplication's quit method
    viewer.exit_signal.connect(app.quit)

    # Create a separate thread for running Jarvis AI
    jarvis_thread = threading.Thread(target=run_jarvis, args=(viewer,))
    jarvis_thread.daemon = True
    jarvis_thread.start()

    sys.exit(app.exec_())
