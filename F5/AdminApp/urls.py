from django.urls import path
from . import views

urlpatterns = [
        path('', views.index),
        path('hack', views.index),

        path('AdminAction',views.AdminAction),
        path('Adminhome', views.Adminhome),

        path('ViewAllUsers', views.ViewAllUsers),

        path('UploadDataset', views.UploadDataset),

        path('DataGenerate', views.DataGenerate),
        path('GenerateCNN', views.GenerateCNN),

        path('GenerateANN', views.GenerateANN),

        path('comparison', views.comparison),
        path('logout', views.logout),

        path('Delete', views.Delete, name='Delete'),
]

