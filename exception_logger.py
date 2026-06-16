import traceback
from django.utils.deprecation import MiddlewareMixin
import os

class ExceptionLoggingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        with open(os.path.join(r"C:\Users\VICTUS\Desktop\A.RISK ERM - V2", "traceback.log"), "w", encoding="utf-8") as f:
            f.write("Exception caught:\n")
            traceback.print_exc(file=f)
            f.write(str(exception) + "\n")
        return None
