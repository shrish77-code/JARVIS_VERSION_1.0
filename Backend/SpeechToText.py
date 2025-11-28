from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")

HtmlCode = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition();
            recognition.lang = '@LANG';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent = transcript;
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
        }
    </script>
</body>
</html>
"""

HtmlCode = HtmlCode.replace("@LANG", InputLanguage)

os.makedirs("Data", exist_ok=True)
with open("Data/Voice.html", "w", encoding="utf-8") as file:
    file.write(HtmlCode)

current_dir = os.getcwd()
Link = f"{current_dir}/Data/Voice.html"

chrome_options = Options()
chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
chrome_options.add_argument("--use-fake-ui-for-media-stream")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def UniversalTranslator(Text):
    return mt.translate(Text, "en", "auto").capitalize()

def SpeechRecognition():
    driver.get("file://" + Link)
    driver.find_element(By.ID, "start").click()

    last_text = ""
    while True:
        text = driver.find_element(By.ID, "output").text
        if text != last_text and text.strip():
            return text.strip()
        last_text = text

if __name__ == "__main__":
    print("🎙 Listening...")
    while True:
        result = SpeechRecognition()
        print("You said:", result)
