from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from articles.models import Article

# Create your views here.


@login_required
def home(request):

    # Only shoe Readers published Articles
    if request.user.role == "Reader":
        articles = Article.objects.filter(published=True)
    else:
        articles = Article.objects.all()

    return render(request, "core/home.html", {"articles": articles})
