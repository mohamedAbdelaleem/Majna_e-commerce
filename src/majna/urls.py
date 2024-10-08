"""
URL configuration for majna project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/users/', include('accounts.urls')),
    path('api/auth/', include('auth.urls')),

    path('api/brands/', include('brands.urls')),
    path('api/brands-applications/', include('brands_applications.urls')),

    path('api/distributors/', include('accounts.distributors.urls')),
    path('api/locations/', include('locations.urls')),
    path('api/products/', include('products.urls')),
    path('api/categories/', include('products.categories.urls')),
    path('api/sub-categories/', include('products.sub_categories.urls')),
    path('api/customers/', include('accounts.customers.urls')),
    path('api/orders/', include('orders.urls')),
]
