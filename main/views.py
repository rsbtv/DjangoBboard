from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required  # для ограничения доступа к функциям
from django.contrib.auth.mixins import LoginRequiredMixin  # для ограничения доступа к классам
from django.contrib.messages.views import SuccessMessageMixin

from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.base import TemplateView  # для работы с шаблонами

from django.template import TemplateDoesNotExist
from django.template.loader import get_template  # для загрузки шаблонов

from django.core.signing import BadSignature
from django.core.paginator import Paginator

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.urls import reverse_lazy  # для получения URL по имени
from django.db.models import Q  # для выполнения сложных запросов

from .models import AdvUser, SubRubric, Bb
from .forms import ChangeUserInfoForm, RegisterUserForm, SearchForm

from .utilities import signer  # используем уже созданный экземпляр класса для экономии оперативной памяти


@login_required()
def profile_bb_detail(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additionalimage_set.all()
    context = {'bb': bb, 'ais': ais}
    return render(request, 'main/detail.html', context)


def detail(request, rubric_pk, pk):
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additionalimage_set.all()
    context = {'bb': bb, 'ais': ais}
    return render(request, 'main/detail.html', context)


def by_rubric(request, pk):
    """
    Представление для отображения объявлений по рубрикам.
    """
    rubric = get_object_or_404(SubRubric, pk=pk)  # получение рубрики по первичному ключу
    bbs = Bb.objects.filter(is_active=True, rubric=pk)  # фильтрация объявлений по рубрике
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(
            content__icontains=keyword)  # поиск по ключевому слову в заголовке и содержимом
        bbs = bbs.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})  # создание формы поиска с текущим ключевым словом
    paginator = Paginator(bbs, 2)  # пагинация объявлений, по 2 на страницу
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)  # получение текущей страницы
    context = {'rubric': rubric, 'page': page, 'bbs': page.object_list, 'form': form}  # контекст для шаблона
    return render(request, 'main/by_rubric.html', context)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удалён')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


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


def other_page(request, page):  # из page получаем имя выводимой страницы
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


def index(request):
    bbs = Bb.objects.filter(is_active=True)[:10]
    context = {'bbs': bbs}
    return render(request, 'main/index.html', context)


@login_required
def profile(request):
    bbs = bbs = Bb.objects.filter(author=request.user.pk)
    context = {'bbs': bbs}
    return render(request, 'main/profile.html', context)
