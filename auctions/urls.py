from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("bookmark/<int:listing_id>", views.bookmark, name="bookmark"),
    path("rmbookmark/<int:listing_id>", views.rmbookmark, name="rmbookmark"),
    path("watchlist/<username>", views.watchlist, name="watchlist"),
    path("close/<int:listing_id>", views.close, name="close"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.category, name="category"),
]
