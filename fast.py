import os
import csv
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import random

# Leer patentes desde un archivo CSV
patentes = []
with open('p2000.csv', newline='') as File:  
    reader = csv.reader(File)
    for row in reader:
        patentes.append(row[0])

def get_car_info(patente):
    # Configurar las opciones del navegador
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--incognito")  # Abrir en modo privado

    # Iniciar undetected_chromedriver
    driver = None
    try:
        driver = uc.Chrome(options=chrome_options)
        
        # Abrir la página web
        driver.get("https://www.volanteomaleta.com")
        
        # Encontrar el campo de entrada para la patente e ingresar la patente de una vez
        patente_input = driver.find_element(By.XPATH, '//*[@id="valid"]/div/input')
        patente_input.send_keys(patente)
        
        # Enviar la tecla Enter para realizar la búsqueda
        patente_input.send_keys(u'\ue007')  # Tecla Enter
        time.sleep(random.uniform(2, 5))  # Espera aleatoria para evitar ser detectado como bot

        # Esperar a que los resultados se carguen y extraer los datos de la página
        resultados = driver.find_elements(By.CSS_SELECTOR, ".table.table-hover tbody tr")
        if not resultados:
            print(f"No se encontraron resultados para la patente {patente}.")
            return None  # Si no hay resultados, retornar None y continuar con la siguiente patente

        if resultados:
            # Extraer los datos de la primera fila
            patente = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(1)").text
            tipo = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
            marca = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(3)").text
            modelo = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(4)").text
            rut = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(5)").text
            numero_motor = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(6)").text
            año = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(7)").text
            nombre = resultados[0].find_element(By.CSS_SELECTOR, "td:nth-child(8) a").text
            print(nombre)
            print(modelo)
            print(marca)
            # Devolver los datos
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
        print(f"Error al obtener información para la patente {patente}: {e}")
        return None

    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"Error al cerrar el driver: {e}")

# Recopilar datos de cada patente
data = []
for patente in patentes:
    info = get_car_info(patente)
    if info:
        data.append(info)

# Función para convertir la lista de diccionarios a un archivo Excel
def lista_a_excel(data, nombre_archivo='datos_autos.xlsx'):
    if not data:
        print("La lista de datos está vacía. No se creará el archivo Excel.")
        return

    df = pd.DataFrame(data)
    df.to_excel(nombre_archivo, index=False)
    print(f"Archivo Excel '{nombre_archivo}' creado exitosamente.")

# Crear el archivo Excel con los datos
lista_a_excel(data, 'datos_autos.xlsx')
