import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from credit_risk.models import CreditOperation
f = CreditOperation._meta.get_field('rate')

print("rate max_digits:", f.max_digits)
print("rate decimal_places:", f.decimal_places)
print("rate context prec:", f.context.prec)

import decimal
value = 19130.05

try:
    dec = decimal.Decimal(str(value))
    print("dec:", dec)
    quantized = dec.quantize(
        f.context.create_decimal("1").scaleb(-f.decimal_places),
        context=f.context
    )
    print("quantized:", quantized)
except decimal.InvalidOperation as e:
    import traceback
    traceback.print_exc()

