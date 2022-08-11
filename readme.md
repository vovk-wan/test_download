Тестовое задание по вакансии https://irkutsk.hh.ru/vacancy/67764198

#   Задача

Написать сервис на Python, который имеет 3 REST ендпоинта:
* получает по HTTP имя CSV-файла (пример файла во вложении) в хранилище и суммирует каждый 10й столбец
* показывает количество задач на вычисление, которые на текущий момент в работе
* принимает ID задачи из п.1 и отображает результат в JSON-формате

Сервис должен поддерживать обработку нескольких задач от одного клиента одновременно.
Сервис должен иметь возможность горизонтально масштабироваться и загружать данные из AWS S3 и/или с локального диска.
Количество строк в csv может достигать 3*10^6.
Подключение к хранилищу может работать нестабильно.

Нужно следовать изложенным в задаче условиям. 
Если что-то не указано прямо — можно делать на свой вкус.

Вот такое задание. Ответ отправляйте ссылкой в гитхаб, пожалуйста)). 
Даём на выполнение задания неделю. Успехов вам!)

Для выполнения задания были выбраны:
1) DRF (Django REST framework) 
2) Celery
3) RabbitMQ
4) Postgresql
5) Doker
6) Docker-compose