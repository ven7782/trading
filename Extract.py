from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# from fpdf import FPDF
import sys
import time

args = sys.argv

# List of codes
# codes = ['838699']  # Replace with your actual codes
codes = [args[1]]

# Suppress WebDriver log messages
chrome_options = Options()
chrome_options.add_argument("--log-level=3")  # Suppress logs (1: INFO, 2: WARNING, 3: ERROR)
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Exclude DevTools logging

# Initialize WebDriver with service to suppress logs
# service = Service('path_to_chromedriver')  # Specify the correct path to your ChromeDriver executable
driver = webdriver.Chrome(options=chrome_options)

# Initialize WebDriver
# driver = webdriver.Chrome()  # or use the appropriate driver for your browser
driver.get('https://www.mometrix.com/academy/')

# Create a PDF document
# pdf = FPDF()
# pdf.set_auto_page_break(auto=True, margin=15)
# pdf.add_page()
# pdf.set_font("Arial", size=12)

for code in codes:
    # driver.get('https://www.mometrix.com/academy/')
    # Find the search box using its ID
    search_box = driver.find_element(By.ID, 'hero-s')
    search_box.clear()
    search_box.send_keys(code)
    
    # Submit the search form
    search_box.send_keys(Keys.RETURN)
    
    time.sleep(3)  # Wait for the page to load

    # Extract practice questions
    questions = driver.find_elements(By.CSS_SELECTOR, '#PQs-spoiler .PQ')  # Get all question containers

    heading = driver.find_element(By.CSS_SELECTOR, '#PQs-spoiler h2').text
    print("Heading:", heading)
    
    for question in questions:
        try:
            # Try to extract the question text (some questions may not have 'strong')
            question_text = ""
            try:
                question_text = question.find_element(By.CSS_SELECTOR, 'strong').text
            except:
                pass  # If there's no strong tag, skip this part

            question_text += " " + question.find_element(By.CSS_SELECTOR, 'div > p').text
            # print("aa:", question_text)

            # Extract answer choices
            # answer_choices = question.find_elements(By.CSS_SELECTOR, '.PQ-Choices .PQ p')

            # Print the question and choices
            print(question_text)
            # print("Answer Choices:")
            # for choice in answer_choices:
            #     print("-", choice.text)

            # print()  # For better readability

        except Exception as e:
            print(f"Error processing question: {e}")
    
    # Optionally, go back to search again
    # driver.back()
    # time.sleep(2)  # Wait before the next search

# Save the PDF
# pdf.output("practice_questions.pdf")

# Clean up
print()
driver.quit()