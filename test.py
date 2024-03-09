import threading
from threading import Thread
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import os
import re
from bs4 import BeautifulSoup
import cv2
from moviepy.editor import VideoFileClip
import requests
from urllib.parse import urlencode

# Global stop event
stop_event = threading.Event()



# Initialize WebDriver
def setup_driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    return driver

# Cleanup function to close WebDriver
def cleanup_driver(driver, driver2):
    driver.quit()
    driver2.quit()
    print("Driver closed")

def extract_numbers(s):
    return re.findall(r'\d+', s)

# Assuming play_video is defined to start video playback in a new thread


def play_video_with_sound(filepath):
    video = VideoFileClip(filepath)
    video.preview()

def play_video_in_thread(filepath):
    video_thread = threading.Thread(target=play_video_with_sound, args=(filepath,))
    video_thread.start()




# Your main task function
def repeat_function(driver, driver2):
    # Your Selenium interactions here...
    try:

        rows = driver2.find_elements(By.CSS_SELECTOR, "#h_exams_gridExamList_bodytable tbody tr")
        checked_row_ids = []
        for index, row in enumerate(rows):
            # For each row, check if the checkbox is checked
            # This looks for an input element of type checkbox that is checked within the row
            checkbox = row.find_elements(By.CSS_SELECTOR, "input[type='checkbox']:checked")
            
            # If the checkbox is checked, add the row index (or any other identifier) to the list
            if checkbox:
                row_id = row.get_attribute('id')
                checked_row_ids.append(row_id)

        # Print or return the list of rows with checked checkboxes
        print("Row IDs with checked checkboxes:", checked_row_ids)

        driver.get("https://www-h.neptun.unideb.hu/hallgato/main.aspx?ismenuclick=true&ctrl=0401")
        dropdown_element = driver.find_element(By.ID, "h_exams_gridExamList_ddlPageSize")
        select = Select(dropdown_element)
        select.select_by_value("200")
        # More Selenium actions...
        print("Page title:", driver.title)

        exam_table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "h_exams_gridExamList_bodytable"))
        )
        table_html = exam_table.get_attribute('outerHTML')
        
        # Navigate to local_page.html with driver2 if not already done
        # Make sure to replace the path with the actual path to your local HTML file
        #1: subject 5: date time 7: student number
        soup = BeautifulSoup(table_html, 'html.parser')


        header_row = soup.find('thead').find('tr')
        header_cells = header_row.find_all(['th', 'td'])  # This gets all cells in the header row

        if len(header_cells) > 5:
            # Update the string of the cell at index 5
            header_cells[5].string = "Date and Time"
            existing_styles = header_cells[5].get('style', '')
            new_padding_style = 'padding-left: 20px; padding-right: 20px;'
            header_cells[5]['style'] = existing_styles + ("" if existing_styles.endswith(";") else ";") + new_padding_style


        # Check if index 7 exists to avoid IndexError
        if len(header_cells) > 7:
            # Update the string of the cell at index 7
            header_cells[7].string = "Seat"

        new_header_th = soup.new_tag('th')
        new_header_th.string = 'Select'
        header_row.append(new_header_th)
        for index in [14, 13, 12, 11, 10, 9, 8, 6, 4, 3, 2, 0]:  # Reverse order to avoid shifting indices
            header_cells = header_row.find_all('th')
            if len(header_cells) > index:  # Check if the index exists
                header_cells[index].decompose()  # Remove the cell at the index

        # Add a checkbox in a new <td> to each row in the table body
        for row in soup.find_all('tbody')[0].find_all('tr'):


            row_id = row.get('id')
            student_number_cell = row.find_all('td')[7] if len(row.find_all('td')) > 7 else None
            if student_number_cell:
                # Use regular expression to find all numbers in the cell text
                student_numbers = extract_numbers(student_number_cell.text)
                if len(student_numbers) >= 2:
                    numerator, denominator = student_numbers[:2]
                    if numerator != denominator:
                        if row_id in checked_row_ids:
                            print(f"Row ID {row_id} is checked. There is (a) seat(s): {student_number_cell.text}")
                            #play_video("C:\\Users\\user\\Videos\\Captures\\video.mp4")
                            
                            email = "@gmail.com"
                            email_message = row.find_all('td')[1].text + " " + row.find_all('td')[5].text
                            password = ""

                            # Encode URL parameters
                            params = {
                                'pass': password,
                                'message': email_message,
                                'email': email
                            }
                            encoded_params = urlencode(params)

                            # The base URL
                            base_url = "https://example.com"

                            # Complete URL with query parameters
                            url = f"{base_url}?{encoded_params}"

                            # Make the GET request
                            response = requests.get(url)

                            # Check if the request was successful
                            if response.status_code == 200:
                                print("Email sent successfully")
                            else:
                                print("Failed to send email")

                            # Print the final URL (optional)
                            print(url)
                            #play_video_in_thread("E:\\priapism másolata.mp4")
                        #else:
                            #print(f"Row ID {row_id} has different numerator and denominator in student numbers and is not checked.")
                    else:
                        # If the numerator and denominator are the same but the row ID is in checked_row_ids, notify
                        if row_id in checked_row_ids:
                            print(f"Row ID {row_id} is checked. No seat: {student_number_cell.text}")
                else:
                    # Notify if the row ID is in checked_row_ids regardless of the student number condition
                    if row_id in checked_row_ids:
                        print(f"Row ID {row_id} is checked but does not have a clear student number format.")
            else:
                # Additional notification if the row is checked but there's no student number cell
                if row_id in checked_row_ids:
                    print(f"Row ID {row_id} is checked but lacks a student number cell.")
                    

                    # Remove the 1st and 3rd columns
            for index in [14, 13, 12, 11, 10, 9, 8, 6, 4, 3, 2, 0]:  # Reverse order to avoid shifting indices
                row_cells = row.find_all(['td', 'th'])  # 'th' is included in case there are header cells in the body
                if len(row_cells) > index:  # Check if the index exists
                    row_cells[index].decompose()  # Remove the cell at the index

            new_td = soup.new_tag('td')
            new_checkbox = soup.new_tag('input', type='checkbox')
            new_td.insert(0, new_checkbox)
            row.append(new_td)

            existing_classes = row.get('class', [])  # Get existing classes, if any
            existing_classes.append('modified-row')  # Add 'modified-row' to the class list
            row['class'] = existing_classes  # Set the modified class list back on the <tr>

            

        # Output the modified HTML
        modified_html = str(soup)
        driver2.execute_script("""
        var tableContainer = document.getElementById('tableContainer');
        tableContainer.innerHTML = arguments[0];
        var rowIds = arguments[1];
        rowIds.forEach(function(id) {
            var row = document.getElementById(id);
            if (row) {
                var checkbox = row.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.checked = true;
                }
            }
        });
        
        // Select every 'tr' element within the tableContainer
        var rows = tableContainer.querySelectorAll('tr');

        // Iterate through each row and attach an event listener
        rows.forEach(function(row) {
             row.addEventListener('click', function() {
                console.log('Row clicked:', this.id);
                // Find the checkbox within the clicked row
                var checkbox = this.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    // Toggle the checkbox's checked state
                    checkbox.checked = !checkbox.checked;
                    
                    // Optionally, prevent the event from affecting parent elements if the checkbox is directly clicked
                    checkbox.addEventListener('click', function(e) {
                        e.stopPropagation();
                    });
                }
            });
        });
        """, modified_html, checked_row_ids)

    


    except Exception as e:
        print(f"An error occurred: {e}")

# Scheduler function
def start_scheduler(interval, task, driver, driver2, stop_event):
    while not stop_event.is_set():
        task(driver, driver2)  # Pass the driver to your task
        time.sleep(interval)

# Start the scheduler in a background thread
def run_periodic_task(interval, task, driver, driver2):
    threading.Thread(target=start_scheduler, args=(interval, task, driver, driver2, stop_event)).start()

# Main function to orchestrate the setup, execution, and cleanup
def main():


    driver2 = setup_driver()  # Setup driver
    script_directory = os.path.dirname(__file__)
    local_file_path = os.path.join(script_directory, "local_page.html")
    local_file_url = f"file:///{os.path.abspath(local_file_path)}"
    driver2.get(local_file_url)


    driver = setup_driver()  # Setup driver
    driver.get("https://www-h.neptun.unideb.hu/hallgato/login.aspx")
    lang_btn = driver.find_element(By.ID, "btnLang_1")
    lang_btn.click()
    user_id = driver.find_element(By.ID, "user")
    user_id.send_keys("")
    pwd= driver.find_element(By.ID, "pwd")
    pwd.send_keys("")
    login_btn = driver.find_element(By.ID, "btnSubmit")
    login_btn.click()
    time.sleep(20)

    driver.get("https://www-h.neptun.unideb.hu/hallgato/main.aspx?ismenuclick=true&ctrl=0401")
    dropdown_element = driver.find_element(By.ID, "h_exams_gridExamList_ddlPageSize")
    select = Select(dropdown_element)
    select.select_by_value("200")

    run_periodic_task(180, repeat_function, driver, driver2)  # Run periodic task every 300 seconds

    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        stop_event.set()

    cleanup_driver(driver, driver2)  # Cleanup driver

if __name__ == "__main__":
    main()
