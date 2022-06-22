from .models import Mortgage
from rest_framework import status
from rest_framework.test import APITestCase


class CalcTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        id = 1
        rate = 0.3
        for counter in range(50):
            if counter == 35: #примерно 'по середине' создадим банк c выгодными
                              #условиями по которому можно легко проверить фильтрацию
                Mortgage.objects.create(
                        id = id,
                        bank_name = 'profitable_bank',
                        term_min =  1,
                        term_max =  50,
                        rate_min = 1.5,
                        rate_max = 6.5,
                        payment_min = 10000,
                        payment_max = 100000000
                        )
                id += 1
            else:
                Mortgage.objects.create(
                        id = id,
                        bank_name = f'test_bank_{id}',
                        term_min =  5,
                        term_max =  51,
                        rate_min = (6.0+rate),
                        rate_max = 34.5,
                        payment_min = 900000,
                        payment_max = 100000000
                        )
                id += 1
                rate += 0.3

    def test_read(self): #Тест GET запроса одной и всех записей
        url_one = "/api/offer/10/"
        url_all = "/api/offer/"
        data_one =  self.client.get(url_one)
        data_all =  self.client.get(url_all)
        self.assertEqual(len(data_one.data), 8) #Тут 8 так как в одном объекте 8 записей, так что одну запись - получили
        self.assertEqual(len(data_all.data), 50) #Получили все 50 записей

    def test_create(self):
        Mortgage.objects.filter(id=1).delete()
        count_objects = len(Mortgage.objects.all())
        url = "/api/offer/"
        data = {
                'bank_name': 'test_bank_create',
                'term_min':  5,
                'term_max':  51,
                'rate_min': 6.0,
                'rate_max': 24.5,
                'payment_min': 900000,
                'payment_max': 100000000
                }
        self.client.post(url, data, format='json')
        new_count_obj = len(Mortgage.objects.all())
        self.assertEqual(count_objects+1, new_count_obj) #Количество объектов ДО создания записи стало +1, все ок

    def test_update(self):
        url = "/api/offer/10/"
        old_data =  self.client.get(url)
        data = {'id': 10,
                'bank_name': 'NEW_BANK',
                'term_min':  10,
                'term_max':  40,
                'rate_min': 8.0,
                'rate_max': 23.5,
                'payment_min': 100000,
                'payment_max': 10000000
                }
        self.assertEqual(False, bool(data==old_data.data)) #Объекты в data не совпадают с записями в базе
        self.client.patch(url, data, format='json')
        new_old_data =  self.client.get(url)
        self.assertEqual(True, bool(data==new_old_data.data)) #После Patch запроса с данными из data, данные из базы совпадают с записями в data

    def test_delete(self):
        count_objects = len(Mortgage.objects.all())
        url = "/api/offer/50/"
        self.client.delete(url)
        new_count_obj = len(Mortgage.objects.all())
        self.assertEqual(count_objects-1, new_count_obj) #После Delete запроса объектов в базе стало на 1 меньше

    def test_filter(self):
        """"При любом не заполненном поле фильтра (либо заполнен частично, но валидными ключами-значениями)
             - страницы будут доступны"""
        data_OK = [
                [10.0, 50.0, 500, 9999999999, 'payment', 25000000, 20, 20],
                [0.0, 99.0, 500, 999999999, 'payment', 25000000, 20, 20],
                [10.0, 20, '', '', 'payment', 10000000, 20, 20],
                [10.0, 20, '', '', '-payment', 10000000, 20, 20],
                ['', '', '', '', '-payment', 10000000, 20, 20],
                ['', '', '', '', 'payment', 10000000, 20, 20],
                [1.0, '', '', '', '', '', '', ''],
                [99.0, '' , '', '', '', '', '', ''],
                ['', 1.0, '', '', '', '', '', ''],
                ['', '', '', 140000, 'payment', 10000000, 20, 20],
                ['', '', '', '', '', '', '', ''],
                ['', '', '', '', 'payment', '', 20, 20],
                ['', '', '', '', 'payment', 10000000, '', 20],
                ['', '', '', '', 'payment', 10000000, 20, ''],
        ]
        for value in data_OK:
            url = f'/api/offer/?rate_min={value[0]}&rate_max={value[1]}&payment_min={value[2]}'\
                  f'&payment_max={value[3]}&order={value[4]}&price={value[5]}'\
                  f'&deposit={value[6]}&term={value[7]}'
            response =  self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        """"Тесты на правильность порядка сортировки по платежу и по мин. проценту банка"""

        best_rate = ['', '', '', '', '-rate',  '', '', ''] #Фильтра по худшей ставке
        url = f'/api/offer/?rate_min={best_rate[0]}&rate_max={best_rate[1]}&payment_min={best_rate[2]}'\
              f'&payment_max={best_rate[3]}&order={best_rate[4]}&price={best_rate[5]}'\
              f'&deposit={best_rate[6]}&term={best_rate[7]}'
        response =  self.client.get(url)
        self.assertEqual('profitable_bank', response.data[0]['bank_name']) #Банк с лучшей минимальной ставкой идет первым

        bad_rate = ['', '', '', '', 'rate',  '', '', ''] #Фильтра по лучшей ставке
        url = f'/api/offer/?rate_min={bad_rate[0]}&rate_max={bad_rate[1]}'\
              f'&payment_min={bad_rate[2]}&payment_max={bad_rate[3]}'\
              f'&order={bad_rate[4]}&price={bad_rate[5]}'\
              f'&deposit={bad_rate[6]}&term={bad_rate[7]}'
        response =  self.client.get(url)
        self.assertEqual('test_bank_50', response.data[0]['bank_name']) #Банк с ХУДШЕЙ минимальной ставкой идет первым

        best_payment = ['', '', '', '', 'payment',  10000000, 20, 20] #Фильтр по увеличению платежа
        url = f'/api/offer/?rate_min={best_payment[0]}&rate_max={best_payment[1]}'\
              f'&payment_min={best_payment[2]}&payment_max={best_payment[3]}'\
              f'&order={best_payment[4]}&price={best_payment[5]}'\
              f'&deposit={best_payment[6]}&term={best_payment[7]}'
        response =  self.client.get(url)
        self.assertEqual('profitable_bank', response.data[0]['bank_name']) #Банк с меньшим ежемес. платежом идет первым

        bad_payment = ['', '', '', '', '-payment',  10000000, 20, 20] #Фильтр по уменьшению платежа
        url = f'/api/offer/?rate_min={bad_payment[0]}&rate_max={bad_payment[1]}'\
              f'&payment_min={bad_payment[2]}&payment_max={bad_payment[3]}'\
              f'&order={bad_payment[4]}&price={bad_payment[5]}'\
              f'&deposit={bad_payment[6]}&term={bad_payment[7]}'
        response =  self.client.get(url)
        self.assertEqual('test_bank_50', response.data[0]['bank_name']) #Банк с БОЛЬШИМ ежемес. платежом идет первым
