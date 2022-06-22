class CalcMortgage:

    @classmethod
    def calc_mortgages(self, price:int, deposit:int, term:int, queryset) -> int:
        deposit_in_rub = (price / 100) * deposit
        remainder = price - deposit_in_rub
        month = term * 12
        coefficient = ((queryset.rate_min/12) / 100)
        coefficient_1 = (coefficient*(1+coefficient)**month)
        coefficient_2 = ((1+coefficient)**month-1)
        final_coefficient = coefficient_1 / coefficient_2
        result = final_coefficient * remainder
        return int(result)