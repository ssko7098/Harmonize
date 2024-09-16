from django.http import HttpResponse
from django.template import loader
from .models import User

# Create your views here.
def user_list(request):
    users = User.objects.all()  # Fetch all users from the database
    template = loader.get_template("app/user_list.html")
    context = {
        "users": users,
    }

    return HttpResponse(template.render(context, request))

