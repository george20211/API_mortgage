# API кредитного калькулятора для сайта на React c кастомными фильтрами + тестирование

Пример api запроса со всеми фильтрами:
http://localhost:8000/api/offer/?rate_min=&rate_max=&payment_min=50000&payment_max=70000&order=-rate&price=10000000&deposit=10&term=20
rate_min - минимальная ставка банка
rate_max - максимальная ставка банка
payment_min - минимальный платеж в месяц
payment_max - максимальный плаже в месяц
order - (rate,-rate по возрастанию или убыванию ставки) (payment, -payment по возрастанию или убыванию месячного платежа)
price - сумма кредитования
deposit - сумма первоначального взноса
term - срок кредитования

Локальный запуск приложения

Что бы поднять контейнеры
 - docker stop $(docker ps -aq)
 - docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build

Что бы зайти внутрь контейнера бекенда
 - docker-compose exec backend sh

Сделать миграции
 - python3 manage.py makemigrations
 - python3 manage.py migrate
#Запуск тестов
 - python3 manage.py test
Сервис будет доступен по ссылке http://localhost:8000/api/offer/
