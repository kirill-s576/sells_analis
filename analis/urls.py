from django.urls import path
from analis import views

urlpatterns = [
    path('make_report', views.make_report, name="make_report"),
    path('make_by_orders', views.make_by_order, name="make_by_order"),
    path('create_new_order_report', views.create_new_order_report, name="create_new_order_report"),
    path('new_report', views.new_report, name="new_report"),
    path('lost_report', views.lost_report, name="lost_report"),
    path('base_report', views.base_report, name="base_report"),
    path('add', views.add_orders, name="add_orders"),
    path('', views.sells_analis, name="sells_analis")
]