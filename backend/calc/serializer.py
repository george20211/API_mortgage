from rest_framework import serializers
from .models import Mortgage
from django.core.exceptions import ValidationError


class FiltersSerializer(serializers.ModelSerializer):

    payment = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Mortgage
        fields = '__all__'

    def to_representation(self, instance):
        if ('price' and 'deposit' and 'term') in self.context:
            price = int(self.context['price'])
            obj = super().to_representation(instance)
            if obj.get('payment_max') < price or obj.get('payment_min') > price:
                pass
            else:
                return obj
        obj = super().to_representation(instance)
        return obj

    def get_payment(self, obj):
        if ('price' and 'deposit' and 'term') in self.context:
            price = int(self.context['price'])
            deposit = int(self.context['deposit'])
            term = int(self.context['term'])
            if obj.payment_max < price or obj.payment_min > price:
                return None
            else:
                deposit_in_rub = (price / 100) * deposit
                remainder = price - deposit_in_rub
                month = term * 12
                coefficient = ((obj.rate_min/12) / 100)
                coefficient_1 = (coefficient*(1+coefficient)**month)
                coefficient_2 = ((1+coefficient)**month-1)
                final_coefficient = coefficient_1 / coefficient_2
                result = final_coefficient * remainder
                return int(result)
        return 0


class MortgageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mortgage
        fields = '__all__'

    def validate(self, data):
        try:
            term_min = data['term_min']
            term_max = data['term_max']
            rate_min = data['rate_min']
            rate_max = data['rate_max']
            payment_min = data['payment_min']
            payment_max = data['payment_max']
            if term_min > term_max:
                raise serializers.ValidationError(
                    'мин. срок больше максимального!'
                )
            if rate_min > rate_max:
                raise serializers.ValidationError(
                    'мин. ставка больше максимальной!'
                )
            if payment_min > payment_max:
                raise serializers.ValidationError(
                    'мин. платеж больше максимального!'
                )
            return data
        except KeyError:
            raise serializers.ValidationError(
                    'Заполните все поля для обновления условий кредитования'
                )

    def update(self, instance, validated_data):
        instance.bank_name = validated_data.get('bank_name', instance.bank_name)
        instance.term_min = validated_data.get('term_min', instance.term_min)
        instance.term_max = validated_data.get('term_max', instance.term_max)
        instance.rate_min = validated_data.get('rate_min', instance.rate_min)
        instance.rate_max = validated_data.get('rate_max', instance.rate_max)
        instance.payment_min = validated_data.get('payment_min', instance.payment_min)
        instance.payment_max = validated_data.get('payment_max', instance.payment_max)
        instance.save()
        return instance

    def create(self, validated_data):
        objects = Mortgage.objects.create(**validated_data)
        return objects
