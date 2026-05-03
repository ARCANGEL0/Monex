from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator


@method_decorator(login_not_required, name="dispatch")
class LoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
