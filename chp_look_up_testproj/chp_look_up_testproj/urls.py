"""chp_look_up_testproj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from chp_look_up.views import meta_knowledge_graph, curies, query

urlpatterns = [
    path('admin/', admin.site.urls),
    path('meta_knowledge_graph/', meta_knowledge_graph.as_view()),  # type: ignore
    path('curies/', curies.as_view()),  # type: ignore
    path('query/', query.as_view())  # type: ignore
]
