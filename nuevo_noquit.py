import os
import csv
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import threading

# Read patents from CSV file
patentes = []
with open('volateomaleta_scrapper/p2000.csv', newline='') as File:  
    reader = csv.reader(File)
    for row in reader:
        patentes.append(row[0])

def get_car_info(driver, patente):
    try:
        # Open the webpage
        driver.get("https://www.volanteomaleta.com")
        
        # Wait for the input field to be present before interacting with it
        patente_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="valid"]/div/input'))
        )
        patente_input.send_keys(patente)
        
        # Send Enter key to perform the search
        patente_input.send_keys(u'\ue007')  # Enter key
        time.sleep(random.uniform(2, 5))  # Random wait to avoid being detected as a bot

        # Wait for results to load
        resultados = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".table.table-hover tbody tr"))
        )
        if not resultados:
            print(f"No results found for patent {patente}.")
            return None

        # Extract data from the first row
        patente = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(1)").text
        tipo = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
        marca = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(3)").text
        modelo = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(4)").text
        rut = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(5)").text
        numero_motor = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(6)").text
        año = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(7)").text
        nombre = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(8) a").text
        
        # Return the data
        return {
            "Patente": patente,
            "Tipo": tipo,
            "Marca": marca,
            "Modelo": modelo,
            "RUT": rut,
            "Número de Motor": numero_motor,
            "Año": año,
            "Nombre a Rutificador": nombre
        }

    except Exception as e:
        print(f"Error obtaining information for patent {patente}: {e}")
        return None

def lista_a_excel(data, nombre_archivo='datos_autos.xlsx'):
    if not data:
        print("The data list is empty. Excel file will not be created.")
        return

    df = pd.DataFrame(data)
    df.to_excel(nombre_archivo, index=False)
    print(f"Excel file '{nombre_archivo}' created successfully.")

# Configure browser options
chrome_options = uc.ChromeOptions()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--incognito")  # Open in private mode

# Initialize undetected_chromedriver
driver = uc.Chrome(options=chrome_options)

# Shared flag to stop the loop
stop_scraping = threading.Event()

def check_for_exit():
    input("Press Enter to stop the scraping process...\n")
    stop_scraping.set()

# Start the thread that listens for Enter key press
exit_thread = threading.Thread(target=check_for_exit)
exit_thread.start()

try:
    # Collect data for each patent
    data = []
    for patente in patentes:
        if stop_scraping.is_set():
            print("Stopping the scraping process...")
            break
        info = get_car_info(driver, patente)
        if info:
            data.append(info)
        time.sleep(random.uniform(1, 3))  # Add a random delay between requests

    # Create Excel file with the data
    lista_a_excel(data, 'datos_autos.xlsx')

finally:
    # Ensure the driver is closed after all operations
    driver.quit()
    exit_thread.join()  # Ensure the input thread has finished
