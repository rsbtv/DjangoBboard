from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from .models import AdvUser
from .forms import ChangeUserInfoForm


# Create your views here.

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
