from django.views.generic import CreateView
# Функция reverse_lazy позволяет получить URL по параметрам функции path()
from django.urls import reverse_lazy
from .forms import CreationForm


# Для обработки формы BookForm возьмём дженерик CreateView,
# он обрабатывает формы и на основе полученных из формы данных создаёт новые записи в БД

class SignUp(CreateView):
    form_class = CreationForm    # C какой формой будет работать этот view-класс, так же может работать напрямую с моделью model =
    success_url = reverse_lazy('posts:index')   # Куда переадресовать пользователя после того, как он отправит форму
    template_name = 'users/signup.html' # Какой шаблон применить для отображения веб-формы, туда будет передана переменная form()
                                        # с полями, описанными в классе CreationForm.
