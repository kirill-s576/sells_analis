from django.contrib import admin
from .models import Order, Shop, Report, OrderReport
# Register your models here.
admin.site.register(Order)
admin.site.register(Shop)
admin.site.register(Report)
admin.site.register(OrderReport)