import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from main.forms import ProductForm
from main.models import Product
from django.http import HttpResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
from django.db.models import Q
from django.http import JsonResponse
from django.core.serializers import serialize
from .models import Product


def show_main(request):
    context = {
        'tagline': 'Bandung Nice Food',
        'login_user': request.user.username if request.user.is_authenticated else None,
        'last_login': request.COOKIES.get('last_login', 'No recent login'),
    }

    return render(request, "main.html", context)

def show_main_admin(request):
    context = {
        'tagline': 'Bandung Nice Food',
        'login_user': request.user.username if request.user.is_authenticated else None,
        'last_login': request.COOKIES.get('last_login', 'No recent login'),
    }

    return render(request, "main_admin.html", context)


@login_required(login_url='/login')
def create_product(request):
    # Use request.FILES to handle uploaded files (like images)
    form = ProductForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)  # Create the product instance but don't save yet
        product.user = request.user  # Associate the product with the current user
        product.save()  # Now save the product instance to the database
        return redirect('main:show_main_admin')  # Redirect to the main page after saving

    context = {
        'form': form,
        'name': 'Daniel Ferdiansyah',
        'class': 'PBP F'
    }
    return render(request, "create_product.html", context)


def show_xml(request):
    data = Product.objects.all()
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")


def show_json(request):
    data = Product.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")


def show_xml_by_id(request, id):
    data = Product.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")


def show_json_by_id(request, id):
    data = Product.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")


@login_required(login_url='/login')
def edit_product(request, id):
    product = Product.objects.get(pk=id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('main:show_main_admin')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'edit_product.html', {'form': form})


@login_required(login_url='/login')
def delete_product(request, id):
    product = Product.objects.get(pk=id)
    product.delete()
    return HttpResponseRedirect(reverse('main:show_main_admin'))

@csrf_exempt
@require_POST
@login_required(login_url='/login')
def add_product_ajax(request):
    name = strip_tags(request.POST.get("name"))
    price = request.POST.get("price")
    restaurant = strip_tags(request.POST.get("restaurant"))
    location = strip_tags(request.POST.get("location"))
    contact = strip_tags(request.POST.get("contact"))
    cat = request.POST.get("cat")
    image = request.FILES.get("image")
    user = request.user
    
    new_product = Product(
        name=name, 
        price=price,
        restaurant=restaurant,
        location=location,
        contact=contact,
        cat=cat,
        image=image,
        user=user
    )
    new_product.save()

    return HttpResponse(b"CREATED", status=201)

def product_list(request):
    products = Product.objects.all()
    data = serialize('json', products)
    return JsonResponse(data, safe=False)



