"""
URL configuration for cafeproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from cafeapp import views

urlpatterns = [
    # create client urls here.
    # path('admin/', admin.site.urls),
    path('', views.Login, name='login'),
    path('register/', views.Register, name='register'),
    path("index/", views.Index, name="index"),
    path("menu/",views.Menu,name="menu"),
    path("details/<int:id>/",views.Details,name="details"),
    path("addtocart/<int:id>/",views.addtocart,name="adcart"),
    path("cart/",views.Cart, name="cart"),
    path('remove-cart/<int:id>/', views.remove_cart, name='remove_cart'),
    path("checkout/<int:t>/",views.Checkout, name="checkout"),
    path("logout/",views.Logout,name="Logout"),

    


    # Create admin Urls here.
    path('adlogin/', views.AdminLogin, name='adlogin'),
    path('adminhome/', views.adminhome, name='adminhome'),
    path('addmenu/', views.addmenu, name='addmenu'),
    path('managemenu/', views.managemenu, name='managemenu'),
    path('delete_menu/<int:id>/', views.delete_menu, name='delete_menu'),
    path('editmenu/<int:id>/', views.editmenu, name='editmenu'),
    path('manageuser/', views.manageuser, name='manageuser'),
    path('delete_user/<int:id>/', views.delete_user, name='delete_user'),
    path('edituser/<int:id>/', views.edituser, name='edituser'),
    path('manageorder/', views.manageorder, name='manageorder'),
    path('viewaddress/<str:nm>/',views.viewaddress, name='viewaddress'),
    path('delete_order/<int:id>',views.delete_order,name='delete_order'),
    path('adminlogout/', views.logout_view, name='logout'),

    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    