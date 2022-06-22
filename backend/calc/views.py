from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Mortgage
from .serializer import MortgageSerializer, FiltersSerializer
from django.db.models import Q
from .calculator import CalcMortgage


calcs = CalcMortgage.calc_mortgages

class MortgageViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = Mortgage.objects.all()
        obj = request._request.GET
        if len(obj) > 0 and len(obj) <= 8: #Если параметров запроса больше 0 и ме ньше 9
            context = {}
            try:
                if 'rate_min' in obj: #Если параметр существует и он не пустой -> фильтруем кверисет
                    rate_min =  obj.get('rate_min')
                    if rate_min != '':
                        queryset = queryset.filter(rate_min__lte=float(rate_min))
                if 'rate_max' in obj: #Если параметр существует и он не пустой -> фильтруем кверисет
                    rate_max = obj.get('rate_max')
                    if rate_max != '':
                        queryset = queryset.filter(rate_max__lte=float(rate_max))
                if 'price' and 'deposit' and 'term' in obj: #Если параметры существует и они не пустые -> фильтруем кверисет
                    term = obj.get('term')
                    deposit = obj.get('deposit')
                    price = obj.get('price')
                    if term != '' and deposit != '' and price != '':
                        term = int(term)
                        deposit = int(deposit)
                        price = int(price)
                        if 'payment_min' in obj: #Если параметр существует и он не пустой -> фильтруем кверисет
                            payment_min = obj.get('payment_min')
                            if payment_min != '':
                                data = queryset
                                for obj_query in data:
                                    result = calcs(price, deposit, term, obj_query)
                                    if result < int(payment_min):
                                        queryset = queryset.exclude(id=obj_query.id)
                        if 'payment_max' in obj: #Если параметр существует и он не пустой -> фильтруем кверисет
                            payment_max = obj.get('payment_max')
                            if payment_max != '':
                                data = queryset
                                for obj_query in data:
                                    result = calcs(price, deposit, term, obj_query)
                                    if result > int(payment_max):
                                        queryset = queryset.exclude(id=obj_query.id)
                        if ((price <= 100000000) and (term <= 50) and (deposit < 100)): #Сумма не более 100м + срок не более 50 лет + первоначальный взнос МЕНЕЕ 100%
                            if price > 0 and term > 0 and deposit > 0: # срок + сумма + взнос должны быть больше 0 -> фильтруем кверисет
                                queryset = queryset.filter(Q(payment_min__lte=price) & Q(payment_max__gte=price) & Q(term_max__gte=term))
                                #Добавим данные в контекст для отправки в  сериализатор
                                context['term'] = term
                                context['deposit'] = deposit
                                context['price'] = price
                            else:
                                msg = 'Цена, первоначальный взнос и срок не могут быть меньше 0'
                                return Response(msg, status=status.HTTP_200_OK)
                        else:
                            msg = 'цена не более 100м, срок не более 50 лет, первоначальный взнос МЕНЕЕ 100%'
                            return Response(msg, status=status.HTTP_200_OK)
                if 'order' in obj:  #Если параметр существует и он не пустой -> сортируем кверивет
                    how_filter = obj.get('order')
                    if how_filter != '':
                        if how_filter == 'rate':
                            queryset = queryset.order_by('-rate_min')
                        elif how_filter == '-rate':
                            queryset = queryset.order_by('rate_min')
                        elif how_filter == 'payment' or '-payment':
                            if 'price' and 'deposit' and 'term' in obj:
                                serializer = FiltersSerializer(queryset, context=context, many=True)
                                objects = serializer.data
                                for i in range(len(objects)):
                                    for j in range(len(objects)-i-1):
                                        if objects[j]['payment'] > objects[j+1]['payment']:
                                            objects[j], objects[j+1] = objects[j+1], objects[j]
                                if how_filter == 'payment': #Вернем отфильтрованный результат по размеру платежа
                                    return Response(objects, status=status.HTTP_200_OK) 
                                elif how_filter == '-payment': #Вернем перевернутый результат по размеру платежа
                                    return Response(objects[::-1], status=status.HTTP_200_OK)
                            else:
                                msg = ('Для сортировки результата нужны данные: '
                                        ' сумма кредита + депозит + срок')
                                return Response(msg, status=status.HTTP_200_OK)
                        else:
                            msg = 'Не существующий ключ сортировки'
                            return Response(msg, status=status.HTTP_200_OK)
                serializer = FiltersSerializer(queryset, context=context, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except TypeError as e:
                msg = 'Не верное значение поля фильтра'
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            except ValueError as e:
                msg = 'Не верное значение поля фильтра'
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        serializer = MortgageSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            int(pk)
        except:
            msg = 'id должен быть целым числом'
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        queryset = Mortgage.objects.all()
        object = get_object_or_404(queryset, pk=pk)
        serializer = MortgageSerializer(object, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = MortgageSerializer(data=request.data, many=False)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        msg = 'Не валидные данные'
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk:str):
        try:
            int(pk)
        except:
            msg = 'id должен быть целым числом'
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        if Mortgage.objects.filter(id=pk).exists():
            obj = Mortgage.objects.get(id=pk)
            serializer = MortgageSerializer(obj, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            msg = 'Не валидные данные'
            return Response(msg)
        msg = 'Не найден пост'
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk:str):
        try:
            int(pk)
        except:
            msg = 'id должен быть целым числом'
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        if Mortgage.objects.filter(id=pk).exists():
            Mortgage.objects.get(id=pk).delete()
            msg = 'Удалено'
            return Response(msg, status=status.HTTP_200_OK)
        msg = 'Не существует'
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)
