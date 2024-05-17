# Лабораторна робота №3
# ФБ-25 Голубєва Ірина
from spyre import server
import pandas as pd
import urllib.request
import os
import seaborn as sns
import matplotlib.pyplot as plt
import re
from glob import glob


# Функція для завантаження та очищення даних VHI
def download_and_clean_vhi_data(index, year_start=1981, year_end=2024, data_folder='lab3/data'):
    # Створюємо директорію, якщо вона не існує
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    # Складаємо шлях до файлу з даними
    filename = f'vhi_id_{index}.csv'
    filepath = os.path.join(data_folder, filename)

    # Якщо файл уже існує, пропускаємо завантаження
    if os.path.isfile(filepath):
        print(f"Файл {filename} вже існує, пропускаю завантаження.")
        return filepath

    # Завантажуємо дані з вебсайту
    url = f'https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={index}&year1={year_start}&year2={year_end}&type=Mean'
    with urllib.request.urlopen(url) as response, open(filepath, 'wb') as out_file:
        out_file.write(response.read())
    print(f'Дані індексу VHI для регіону {index} завантажені і збережені як {filename}')

    # Очищення даних
    df = pd.read_csv(filepath, index_col=False, header=1)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.applymap(lambda x: re.sub(r'<.*?>', '', x) if isinstance(x, str) else x)
    df.to_csv(filepath, index=False)
    print(f'Дані індексу VHI для регіону {index} очищені і збережені як {filename}')

    return filepath


# Завантажуємо та очищаємо дані для всіх індексів
def process_all_indices():
    for index in range(1, 28):
        download_and_clean_vhi_data(index)


# Функція для створення та відображення даних
def create_and_map_data(folder_path='lab3/data'):
    csv_files = glob(os.path.join(folder_path, '*.csv'))
    frames = []
    for file in csv_files:
        df = pd.read_csv(file, header=0)
        # Визначаємо ідентифікатор регіону з назви файлу
        df['Region'] = os.path.basename(file).split('_')[2].split('.')[0]
        frames.append(df)

    # Об'єднуємо всі дані в один DataFrame
    combined_data = pd.concat(frames).drop_duplicates().reset_index(drop=True)
    return combined_data

def month_to_week(month_start, month_end):
    week_start = (month_start - 1) * 4 + 1
    week_end = month_end * 4
    return week_start, week_end

# Словник для відображення індексу на назву регіону
index_to_region_name = {
    1: "Вінницька", 2: "Волинська", 3: "Дніпропетровська", 4: "Донецька",
    5: "Житомирська", 6: "Закарпатська", 7: "Запорізька", 8: "Івано-Франківська",
    9: "Київська", 10: "Кіровоградська", 11: "Луганська", 12: "Львівська",
    13: "Миколаївська", 14: "Одеська", 15: "Полтавська", 16: "Рівненська",
    17: "Сумська", 18: "Тернопільська", 19: "Харківська", 20: "Херсонська",
    21: "Хмельницька", 22: "Черкаська", 23: "Чернігівська", 24: "Чернівецька",
    25: "Республіка Крим"
}


# Клас інтерфейсу веб-додатку
class VHIApp(server.App):
    title = "NOAA Data Visualization"

    inputs = [{
        "type": 'dropdown',
        "label": 'Choose Indicator',
        "options": [{"label": "VCI", "value": "VCI"},
                    {"label": "TCI", "value": "TCI"},
                    {"label": "VHI", "value": "VHI"}],
        "key": 'indicator',
        "action_id": "update_data"
    }, {
        "type": 'dropdown',
        "label": "Choose Region",
        "options": [{"label": name, "value": str(index)}
                    for index, name in index_to_region_name.items()],
        "key": 'region',
        "action_id": "update_data"
    }, {
        "type": 'text',
        "label": "Year",
        "value": "2024",
        "key": 'year',
        "action_id": "update_data"
    }, {
        "type": 'text',
        "label": "Month Range (e.g., 1-12)",
        "value": "1-12",
        "key": 'month_range',
        "action_id": "update_data"
    }]

    controls = [{
        "type": "hidden",
        "id": "update_data"
    }]

    outputs = [{
        "type": "plot",
        "id": "plot",
        "control_id": "update_data",
        "tab": "Plot"
    }, {
        "type": "table",
        "id": "table",
        "control_id": "update_data",
        "tab": "Table",
        "on_page_load": True
    }]

    def getData(self, params):
        # Отримуємо дані згідно з вибраними параметрами
        indicator = params['indicator']
        region = params['region']
        year = params['year']
        month_range = params['month_range']
        month_start, month_end = [int(x) for x in month_range.split('-')]
        week_start, week_end = month_to_week(month_start, month_end)

        data = create_and_map_data()
        # Фільтруємо дані для вибраного регіону та індикатора
        filtered_data = data[
            (data['Region'] == region) &
            (data['year'] == int(year)) &
            (data['week'].between(week_start, week_end))
            ]
        return filtered_data[['year', 'week', indicator]]

    def getPlot(self, params):
        # Створюємо графік для вибраних параметрів
        data = self.getData(params)
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=data, x='week', y=params['indicator'])
        plt.title(f"Time Series for {params['indicator']} in {params['year']}")
        plt.xlabel('Week')
        plt.ylabel(params['indicator'])
        plt.tight_layout()
        return plt.gcf()


# Запуск додатка з портом 5005 для локальної роботи
if __name__ == "__main__":
    process_all_indices()  # Завантаження та очищення даних при запуску додатка
    app = VHIApp()
    app.launch(port=5005)