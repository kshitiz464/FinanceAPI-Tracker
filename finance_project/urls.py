from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
)
from api.views.page_views import home_view, login_view, register_page_view, logout_view

urlpatterns = [
    # ─── Web Pages (session-based auth) ───────────────────
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('register-page/', register_page_view, name='register-page'),
    path('logout/', logout_view, name='logout'),

    # ─── Admin ────────────────────────────────────────────
    path('admin/', admin.site.urls),

    # ─── API ──────────────────────────────────────────────
    path('api/', include('api.urls')),

    # ─── API Documentation ────────────────────────────────
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
