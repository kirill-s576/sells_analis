from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from .excel import ExcelOrder
from .models import Order, Report, Shop, OrderReport
from django.db import transaction
import datetime
from .classes import ShopClass, MoveReport
import ast
from django.http import HttpResponseRedirect

# Create your views here.

@transaction.non_atomic_requests
def add_orders(request):
    ex = ExcelOrder("F:/DjangoProjects/Sells/static/excel/February.xlsx")
    with transaction.atomic():
        for i in range(2, 19975, 1):
            print(i)
            order = ex.set_order(i)
            o = Order()
            o.client = order.client
            o.date_time = order.date_time
            o.price = order.price
            o.shop = order.shop
            o.bonus_card = order.bonus_card
            o.number = order.number
            o.worker = order.worker
            o.save()
    return render(request, 'main.html', locals())


# Главная страница
def sells_analis(request):
    return render(request, 'main.html', locals())


# Показывает страницу базовых отчетов, по умолчанию рендерит последний заказанный
def base_report(request):
    reports = Report.objects.all().order_by("id").reverse()
    return render(request, 'reports/base.html', locals())


def lost_report(request):
    date = datetime.datetime.strptime("2019-09-05", '%Y-%m-%d')
    shops = Order.objects.all().values_list("shop").distinct()
    shops = [shop[0] for shop in shops]
    moves = []
    for shop in shops:
        move = MoveReport(shop, date)
        if len(move.clients_before) >1:
            moves.append(move)

    return render(request, 'reports/lost.html', locals())


# Показывает страницу заказа отчетов
def new_report(request):
    return render(request, 'new_report/new_report.html', locals())


# Создает новый заказ на отчет и редиректит обратно на страницу заказа
def create_new_order_report(request):
    type = request.GET["type"]

    order = OrderReport()
    order.type = type

    params = request.GET
    order.parameters = params

    order.save()

    return HttpResponseRedirect("/sells/new_report")


# Показывает страницу с заказами.
def make_by_order(request):
    orders = OrderReport.objects.all().order_by("create_date").reverse()
    return render(request, 'new_report/make_by_order.html', locals())


def make_report(request):
    order_id = request.GET["id"]
    order = OrderReport.objects.get(id=order_id)
    order_type = order.type
    if order_type == "base":
        make_base_report(order_id)
    return HttpResponseRedirect("/sells/make_by_orders")


def make_base_report(order_id):
    order_report = OrderReport.objects.get(id=order_id)
    params = ast.literal_eval(order_report.parameters[12:-1])

    # Надо поменять дату начала и конца из параметров заказа на отчет
    date_start = datetime.datetime.strptime(params["datestart"][0], '%Y-%m-%d')
    date_finish = datetime.datetime.strptime(params["datefinish"][0], '%Y-%m-%d')
    date_orders = Order.objects.filter(date_time__range=(date_start, date_finish))
    shops_list = date_orders.values_list("shop").distinct()

    new_report = Report()
    new_report.datestart = date_start
    new_report.datefinish = date_finish
    new_report.save()

    for s in shops_list:
        print("Начали считать" + str(s[0]))
        shop = ShopClass(s[0], date_start, date_finish).make()
        new_shop = Shop()
        new_shop.name = shop.shop_name
        new_shop.report = new_report
        new_shop.unique_clients = len(shop.unique_clients())
        new_shop.unique_clients_more_one = len(shop.unique_clients_more_one)
        new_shop.favorite_shop = len(shop.favorite_shop)
        new_shop.favorite_shop_more_one = len(shop.favorite_shop_more_one)
        new_shop.other_shops_object = shop.other_shops_object
        new_shop.percent_object = shop.percent_object
        new_shop.save()
        print("Закончили считать" + str(s[0]))
    order_report.complete = True
    order_report.complete_date = datetime.datetime.now()