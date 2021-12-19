from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import CreateForm


class SignUp(CreateView):
    form_class = CreateForm
    success_url = reverse_lazy('posts:main')
    template_name = 'users/signup.html'
