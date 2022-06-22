from django.db import models

class Mortgage(models.Model):
    bank_name =  models.CharField(max_length=50, null=False)
    term_min =  models.IntegerField(null=False)
    term_max =  models.IntegerField(null=False)
    rate_min =  models.FloatField(null=False)
    rate_max = models.FloatField(null=False)
    payment_min = models.IntegerField(null=False)
    payment_max = models.IntegerField(null=False)

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Калькулятор'
        verbose_name_plural = 'Калькуляторы'

    def __str__(self) -> str:
        return self.bank_name