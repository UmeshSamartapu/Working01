from django.urls import path
from . import views

urlpatterns = [
        path('', views.index),
        path('logout', views.logout),      

        path('Register', views.Register),
        path('RegAction', views.RegAction),
        path('index', views.index),
        path('LogAction', views.LogAction),
        path('home', views.home),

        path('Test', views.Test),
        path('Upload', views.Upload),
        path('imageAction', views.imageAction),
         path('HA/', views.HeartView),

        path('StudentLogin/', views.StudentLogin, name='StudentLogin'),
        path('StudentDashboard/', views.StudentDashboard, name='StudentDashboard'),
        path('ECGModule/', views.ECGModule),
        path('HeartAnatomy/', views.HeartAnatomy), 
        path('QuizModule/', views.QuizModule),
        path('Certificate/', views.Certificate),

        path('Profile',views.Profile),
        path('checkdb', views.checkdb),
        path('prediction/<int:record_id>/', views.PredictionDetail, name='PredictionDetail'),  # View saved prediction

        path('AdminAction/', views.AdminAction, name='AdminAction'),
]

