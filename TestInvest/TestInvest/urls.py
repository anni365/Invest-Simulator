from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from perfiles.views import SignUpView, BienvenidaView, SignInView, SignOutView, WalletView, PriceView
from TestInvest import settings
from perfiles import views
from django.conf.urls.static import static


def anonymous_required(func):
    def as_view(request, *args, **kwargs):
        redirect_to = kwargs.get('next', settings.LOGIN_REDIRECT_URL)
        if request.user.is_authenticated:
            return redirect(redirect_to)
        response = func(request, *args, **kwargs)
        return response
    return as_view


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', BienvenidaView.as_view(), name='home'),
    url(r'^signup/$', anonymous_required(SignUpView.as_view()),
        name='sign_up'),
    url(r'^login/$', anonymous_required(SignInView.as_view()),
        name='sign_in'),
    url(r'^logout/$', SignOutView.as_view(), name='sign_out'),
    url(r'^password/$', login_required(views.change_password),
        name='change_password'),
    url(r'^wallet/$', views.show_wallet, name= "wallet"),
    url(r'^price/$', PriceView.as_view(), name='price'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
