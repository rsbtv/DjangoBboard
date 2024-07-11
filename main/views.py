from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.base import TemplateView

from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.urls import reverse_lazy
from django.core.signing import BadSignature

from .models import AdvUser
from .forms import ChangeUserInfoForm, RegisterUserForm

from .utilities import signer  # используем уже созданный экземпляр класса для экономии оперативной памяти


# Create your views here.
def user_activate(request, sign):  # sign - подписанный идентификатор пользователя
    try:
        username = signer.unsign(sign)  # извлекаем имя пользователя
    except BadSignature:  # если цифровая подпись скомпрометирована
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)  # ищем пользователя с этим именем
    if user.is_activated:  # если пользователь активирован ранее
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя изменён'


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser  # запись представляющая текущего пользователя, предварительно ключ получается из user объекта
    # запроса
    template_name = 'main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Данные пользователя изменены'

    def setup(self, request, *args, **kwargs):
        """
        Метод, наследуемый всеми контроллерами-классами от общего суперкласса View.
        Выполняется в самом начале исполнения класса и получает объект запроса в качестве одного из параметров.
        Здесь получаем ключ пользователя и сохраняем в user_id.
        """
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """
        Извлечение исправляемой записи. Набор записей из которого следует извлечь искомую запись может быть передан
        методу с параметром queryset. Может быть и не передан, поэтому вызываем get_queryset()
        """
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class BBLoginView(LoginView):
    template_name = 'main/login.html'


@login_required()
def profile(request):
    return render(request, 'main/profile.html')


def other_page(request, page):  # из page получаем имя выводимой страницы
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


def index(request):
    return render(request, 'main/index.html')
