import os
import csv
import re
from prettytable import PrettyTable


class PriceMachine:
    def __init__(self):
        self.data = []
        self.result = ''

    def load_prices(self, file_path='./'):
        pattern = re.compile(r'price')
        for root, dirs, files in os.walk(file_path):
            for file in files:
                if pattern.search(file):
                    self._process_file(os.path.join(root, file))

    def _process_file(self, file_path):
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                header = next(csv_reader)

                name_index, price_index, weight_index = self._search_product_price_weight(header)

                for row in csv_reader:
                    if len(row) > max(name_index, price_index, weight_index):
                        name = row[name_index]
                        price = int(row[price_index])
                        weight = int(row[weight_index])
                        price_per_kg = price/weight

                        self.data.append({
                            'name': name,
                            'price': price,
                            'weight': weight,
                            'file': os.path.basename(file_path),
                            'price_per_kg': price_per_kg
                        })

        except Exception as e:
            print(f"Ошибка при чтении файла {file_path}: {e}")

    def _search_product_price_weight(self, headers):

        name_columns = ['название', 'продукт', 'товар', 'наименование']
        price_columns = ['цена', 'розница']
        weight_columns = ['фасовка', 'масса', 'вес']

        name_index = -1
        price_index = -1
        weight_index = -1

        for i, header in enumerate(headers):
            if any(name in header.lower() for name in name_columns):
                name_index = i
            elif any(price in header.lower() for price in price_columns):
                price_index = i
            elif any(weight in header.lower() for weight in weight_columns):
                weight_index = i

        return name_index, price_index, weight_index

    def find_text(self, text):
        self.result = [entry for entry in self.data if text.lower() in entry['name'].lower()]
        self.result = sorted(self.result, key=lambda x: x['price_per_kg'])
        return self.result

    def export_to_html(self, fname='output.html'):

        result = """
        <html>
        <head><title>Позиции продуктов</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
        </head>
        <body>
        <table class="table">
            <tr>
                <th scope="col">Номер</th>
                <th scope="col">Название</th>
                <th scope="col" style:"text-aling:center">Цена</th>
                <th scope="col">Фасовка</th>
                <th scope="col">Файл</th>
                <th scope="col">Цена за кг.</th>
            </tr>
        """

        headers = ["№", "Наименование", "Цена", "Вес", "Файл", "Цена за кг."]
        table_items = []

        for idx, item in enumerate(self.result, 1):
            table_items.append(
                [idx, item['name'], item['price'], item['weight'], item['file'], round(item['price_per_kg'], 2)])

        for row in table_items:
            result += f"<tr>{''.join([f'<td>{cell}</td>' for cell in row])}</tr>"

        result += """
        </table>
        </body>
        </html>
        """

        with open(fname, 'w', encoding='utf-8') as file:
            file.write(result)

        print(f"Данные успешно экспортированы в {fname}")


pm = PriceMachine()
pm.load_prices()

while True:
    search_text = input("Введите текст для поиска (или 'exit' для выхода): ")

    if search_text.lower() == 'exit':
        print("Работа завершена.")
        break

    results = pm.find_text(search_text)
    table = PrettyTable()
    table.field_names = ["№", "Наименование", "Цена", "Вес", "Файл", "Цена за кг."]

    if results:
        for index, item in enumerate(results, 1):
            table.add_row([
                index,
                item['name'],
                item['price'],
                item['weight'],
                item['file'],
                item['price_per_kg']
            ])
        print(table)
        pm.export_to_html()
    else:
        print("Товары не найдены.")


