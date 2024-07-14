from .models import SubRubric


def bboard_context_processor(request):
    context = {}
    context['rubrics'] = SubRubric.objects.all()
    context[
        'keyword'] = ''  # с GET-параметром keyword,
    # понадобится для генерации интернет-адресов в гиперссылках пагинатора
    context['all'] = ''  # с GET-параметрами keyword и page, которые добавляем к адресам гиперссылок
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            context['keyword'] = '?keyword=' + keyword
            context['all'] = context['keyword']
    if 'page' in request.GET:
        page = request.GET['page']
        if page != '1':
            if context['all']:
                context['all'] += '&page=' + page
            else:
                context['all'] = '?page=' + page

    return context
