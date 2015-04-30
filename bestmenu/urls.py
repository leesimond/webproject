from django.conf.urls import patterns, url
from bestmenu import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^add_category/$', views.add_category, name='add_category'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/add_restaurant/$', views.add_restaurant, name='add_restaurant'),
    url(r'^restricted/', views.restricted, name='restricted'),
    url(r'^register/$', views.register, name='register'),
    url(r'^search/$', views.search, name='search'),
    url(r'^goto/$', views.track_url, name='goto'),
    url(r'^add_profile/$', views.register_profile, name='add_profile'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^like_category/$', views.like_category, name='like_category'),
    url(r'^suggest_category/$', views.suggest_category, name='suggest_category'),
    url(r'^auto_add_restaurant/$', views.auto_add_restaurant, name='auto_add_restaurant'),
    url(r'^all_categories/$', views.all_categories, name='all_categories'),
    url(r'^all_restaurants/$', views.all_restaurants, name='all_restaurants'),
)
