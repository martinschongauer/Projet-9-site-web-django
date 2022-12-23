
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from blog import views

urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
    path('index/', views.index, name="index"),
    path('logout/', views.user_logout, name="logout"),
    path('flux/', views.flux, name="flux"),
    path('follow/', views.follow, name="follow"),
    path('follow/delete/<int:id>', views.follow_delete, name="follow_delete"),
    path('my_posts/', views.my_posts, name="my_posts"),
    path('review/', views.review, name="review"),
    path('review/answer/<int:id>', views.review_answer, name="review_answer"),
    path('review/update/<int:id>', views.review_update, name="review_update"),
    path('review/delete/<int:id>', views.review_delete, name="review_delete"),
    path('subscribe/', views.subscribe, name="subscribe"),
    path('ticket/', views.ticket, name="ticket"),
    path('ticket/update/<int:id>', views.ticket_update, name="ticket_update"),
    path('ticket/delete/<int:id>', views.ticket_delete, name="ticket_delete")
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)