from .models import Order
import datetime
from django.utils import timezone

class ShopClass(object):
    def __init__(self, shop_name, datestart, datefinish):
        self.shop_name = shop_name
        self.date_start = datestart
        self.date_finish = datefinish
        self.date_orders = Order.objects.filter(date_time__range=(self.date_start, self.date_finish)).exclude(client="Розничный покупатель")
        self.all_orders = Order.objects.all()

        self.unique_clients_more_one = []
        self.favorite_shop = []
        self.other_shops_object = []
        self.favorite_shop_more_one = []

        self.percent_object = {}


    def unique_clients(self):
        unique_clients = self.date_orders.filter(shop=self.shop_name).exclude(client="Розничный покупатель").values_list("client").distinct()
        return unique_clients

    def unique_clients_favorite_shop(self):

        return ""

    def make(self):
        unique_clients = self.unique_clients()
        percents_list = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        for p in percents_list[:-1]:
            self.percent_object[str(p + 1) + "-" + str(p + 10)] = 0

        other_shops = []
        for client in unique_clients:

            val_in_shop_by_date = len(self.date_orders.filter(client=client[0], shop=self.shop_name))
            #
            orders_other_shop_by_date = self.date_orders.filter(client=client[0]).exclude(shop=self.shop_name)
            #
            val_other_shop_by_date = len(orders_other_shop_by_date)
            #
            other_shops_by_date = orders_other_shop_by_date.values_list("shop")
            #
            other_shops.extend(other_shops_by_date.distinct())

            # val_in_shop_all_period = len(self.all_orders.filter(client=client[0], shop=self.shop_name)).exclude(client="Розничный покупатель")
            # val_other_shop_all_period = len(self.all_orders.filter(client=client[0]).exclude(shop=self.shop_name)).exclude(client="Розничный покупатель")

            percent_by_date = val_in_shop_by_date/(val_in_shop_by_date+val_other_shop_by_date)*100

            if val_in_shop_by_date > 1:
                self.unique_clients_more_one.append(client[0])
            if percent_by_date > 50:
                self.favorite_shop.append(client[0])

            for p in percents_list:
                if (percent_by_date >= (p+1)) and (percent_by_date <= (p+10)) and (val_in_shop_by_date > 1):
                    self.percent_object[str(p+1)+"-"+str(p+10)] = self.percent_object[str(p+1)+"-"+str(p+10)] +1

        for k in self.percent_object:
           value = self.percent_object[k]

        for client in self.unique_clients_more_one:
            if client in self.favorite_shop:
                self.favorite_shop_more_one.append(client)

        for shop in Order.objects.all().values_list("shop").distinct():
            self.other_shops_object.append({"name": shop[0], "clients": other_shops.count(shop)})
        self.other_shops_object = sorted(self.other_shops_object, key=lambda x: x["clients"], reverse=True)

        return self


# Отчет по движению клиентов
# Класс принимает название магазина, дату отсчета, объект orders со всеми чеками, на основании которых будем анализировать
class MoveReport(object):
    def __init__(self, shop_name: str, start_date: datetime.datetime):
        self.shop_name = shop_name
        self.start_date = start_date
        current_tz = timezone.get_current_timezone()
        self.start_date = current_tz.localize(self.start_date)
        self.orders = Order.objects.all()

        # Результирующие переменные.
        self.clients_before = []
        self.clients_after = []
        self.clients_more_than_one = []
        self.clients_every_month = []
        self.which_stores = []

        self.clients_lost_more_than_one = []
        self.clients_lost_every_month = []
        self.clients_save_in_this_more_than_one = []
        self.clients_save_in_this_every_month = []
        self.clients_save_in_other = []
        self.stores = ""

        self.all_month_list = []

        self._before()
        self._after()
        self._more_than_one()
        self._every_month()
        self._lost()
        self._save_in_this()
        self._save_in_other()
        # self._stores()

    def _before(self):
        delta = datetime.timedelta(days=60)
        date_before = self.start_date - delta
        # Result
        self.clients_before = list(self.orders.filter(date_time__range=(date_before, self.start_date), shop=self.shop_name).values_list("client"))
        self.clients_before = [client[0] for client in self.clients_before]
        return self

    def _after(self):
        date_now = timezone.now()
        # Result
        self.clients_after = list(self.orders.filter(date_time__range=(self.start_date, date_now), shop=self.shop_name).values_list("client"))
        self.clients_after = [client[0] for client in self.clients_after]
        return self

    def _more_than_one(self):
        self.clients_more_than_one = list(set(list(filter(lambda client: self.clients_before.count(client) > 1, self.clients_before))))
        return self

    def _every_month(self):
        # Можно выбрать 2 или 3 месяца на рассчёт
        months_value = 2

        one_month_list = self.clients_before = self.orders.filter(
            date_time__range=(self.start_date - datetime.timedelta(days=29), self.start_date),
            shop=self.shop_name).values_list("client").distinct()
        second_month_list = self.clients_before = self.orders.filter(
            date_time__range=(self.start_date - datetime.timedelta(days=59), self.start_date - datetime.timedelta(days=30)),
            shop=self.shop_name).values_list("client").distinct()
        third_month_list = self.clients_before = self.orders.filter(
            date_time__range=(self.start_date - datetime.timedelta(days=90), self.start_date - datetime.timedelta(days=60)),
            shop=self.shop_name).values_list("client").distinct()

        one_month_list = [client[0] for client in list(one_month_list)]
        second_month_list = [client[0] for client in list(second_month_list)]
        third_month_list = [client[0] for client in list(third_month_list)]

        # Объединяем все месяцы в 1 массив
        one_month_list.extend(second_month_list)
        if months_value >2:
            one_month_list.extend(third_month_list)

        self.all_month_list = one_month_list

        # Считаем клиентов, которых 2 в массиве - и есть наши.
        self.clients_every_month = list(set(list(filter(lambda client: self.all_month_list.count(client) == months_value, self.all_month_list))))
        return self

    def _lost(self):
        # Критерий: если клиент больше ни разу не купили ни в одном из магазинов
        # Выводим всех клиентов во всех магазинах, которые совершили хотя бы одну покупку
        date_now = timezone.now()
        clients_all_after = list(self.orders.filter(date_time__range=(self.start_date, date_now)).values_list("client").distinct())
        clients_all_after = [client[0] for client in clients_all_after]

        self.clients_lost_more_than_one = [client for client in self.clients_more_than_one if client not in clients_all_after]
        self.clients_lost_every_month = [client for client in self.clients_every_month if client not in clients_all_after]
        return self

    def _save_in_this(self):
        # Критерий: если клиент после этого купил именно в этом магазине хоть раз
        date_now = timezone.now()
        clients_all_after_in_this = list(self.orders.filter(date_time__range=(self.start_date, date_now), shop=self.shop_name).values_list("client").distinct())
        clients_all_after_in_this = [client[0] for client in clients_all_after_in_this]

        self.clients_save_in_this_more_than_one = [client for client in self.clients_more_than_one if client in clients_all_after_in_this]
        self.clients_save_in_this_every_month = [client for client in self.clients_every_month if client in clients_all_after_in_this]
        return self

    def _save_in_other(self):
        # Критерий: если клиент после этого купил в другом магазине хоть раз
        date_now = timezone.now()
        clients_all_after_in_other = list(self.orders.filter(date_time__range=(self.start_date, date_now)).exclude(shop=self.shop_name).values_list("client").distinct())
        clients_all_after_in_other = [client[0] for client in clients_all_after_in_other]

        self.clients_save_in_other_more_than_one = [client for client in self.clients_more_than_one if (client in clients_all_after_in_other) and (client not in self.clients_save_in_this_more_than_one)]
        self.clients_save_in_other_every_month = [client for client in self.clients_every_month if (client in clients_all_after_in_other) and (client not in self.clients_save_in_this_every_month)]
        return self

    def stores(self):
        # Формируем пулл клиентов, которые нам нужны.
        one = self.clients_save_in_other_more_than_one
        every = self.clients_save_in_other_every_month
        one.extend(every)
        target_clients = list(set(one))
        # И смотрим в каких магазинах они покупали после этой даты.
        date_now = timezone.now()
        all_shops = []
        all_orders_simple = []
        for client in target_clients:
            # Выводим список магазинов для одного клиента(без дублей)
            all_orders = self.orders.filter(date_time__range=(self.start_date+datetime.timedelta(days=1), date_now), client=client).values_list("shop")
            all_orders_s = [order[0] for order in list(all_orders)]
            shops = list(all_orders.distinct())
            shops = [shop[0] for shop in shops]
            all_shops.extend(shops)
            all_orders_simple.extend(all_orders_s)

        unique_shops = list(set(all_shops))

        result = []
        for shop in unique_shops:
            result.append({"shop": shop, "clients": all_shops.count(shop), "orders": all_orders_simple.count(shop)})
        result.sort(key=lambda x: x["orders"], reverse=True)
        return result




# !Отчет по динамике уникальных клиентов в магазине от месяца к месяцу!
