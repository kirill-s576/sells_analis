from django.db import models
import datetime
from django.utils import timezone
import ast

# Create your models here.


class Report(models.Model):
    datestart = models.DateTimeField(default=timezone.now)
    datefinish = models.DateTimeField(default=timezone.now)


class Shop(models.Model):
    name = models.CharField(max_length=50)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    unique_clients = models.IntegerField(default=0)
    unique_clients_more_one = models.IntegerField()
    favorite_shop = models.IntegerField()
    favorite_shop_more_one = models.IntegerField()
    other_shops_object = models.CharField(max_length=10000)
    percent_object = models.CharField(max_length=10000)

    def __str__(self):
        return self.name


    def percents(self):
        return ast.literal_eval(self.percent_object)

    def regular_percent(self):
        try:
            return int(self.favorite_shop_more_one/self.unique_clients*100)
        except:
            return 0

    def other_shops_filtered_object(self):
        def client_filter(item):
            if (item["clients"] > 0):
                return 1
            else:
                return 0
        filtered = filter(client_filter, ast.literal_eval(self.other_shops_object))
        return list(filtered)



class OrderReport(models.Model):
    type = models.CharField(max_length=500)
    create_date = models.DateTimeField(default=timezone.now)
    complete_date = models.DateTimeField(null=True)
    parameters = models.CharField(max_length=1000)
    complete = models.BooleanField(default=False)

class Order(models.Model):

    number = models.CharField(max_length=50)
    date_time = models.DateTimeField(default=timezone.now)
    shop = models.CharField(max_length=200, null=True)
    client = models.CharField(max_length=200, null=True)
    bonus_card = models.CharField(max_length=200, null=True)
    price = models.FloatField(default=0, null=True)
    worker = models.CharField(max_length=200, null=True)

    def date(self):
        return self.date_time.date()






