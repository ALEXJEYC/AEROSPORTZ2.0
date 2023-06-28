from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto
from django.contrib.auth.models import User
from core.forms import FormProducto
from django.urls import reverse
from django.http.response import HttpResponse
from core.models import *
from django.contrib import messages

# Create your views here.
def inicio(request):
    return render(request, 'core/inicio.html')

def nosotros(request):
    return render(request, 'core/nosotros.html')

def login(request):
    return render(request, 'registration/login.html')

@login_required
def productos(request):
    return render(request, 'core/productos.html')


def register(request):
    data = {
        'form': CustomUserCreationForm()
    }

    if request.method == 'POST':
        user_creation_form = CustomUserCreationForm(data=request.POST)

        if user_creation_form.is_valid():
            user_creation_form.save()

            user = authenticate(username=user_creation_form.cleaned_data['username'], password=user_creation_form.cleaned_data['password1'])
            login(request, user)
            return redirect('inicio')

    return render(request, 'registration/register.html', data)

def logout(request):
    return render(request,'core/inicio.html')





def producto_index(request):
    productos = Producto.objects.all().order_by("-id")
    
    return render(request, "core/productos.html", {
        'categorias' : Categoria.objects.all(),
        'productos_top3' : productos[:3],
        'productos' : productos[3:10]
    })

# PARA ADMINS/MODERADORES
def producto_create(request):
    categorias = Categoria.objects.all()
    if request.method == "POST":
        categoria_del_producto = Categoria.objects.get(id=request.POST["categoria"])
        form = FormProducto(request.POST, request.FILES, instance=Producto(imagen=request.FILES['imagen'], categoria=categoria_del_producto))   
        if form.is_valid():
            form.save()
            return redirect("productos_index")
            #return HttpResponse('Los campos fueron validados y aceptados!!! ' + str(categoria_del_producto))
        else:
            return render(request, 'core/productos.html', {
                'categorias' : categorias,
                'error_message' : 'Ingreso un campo incorrecto, vuelva a intentar'
            })
    else:
        return render(request, 'core/productos.html', {
            'categorias' : categorias
        })

def producto_show(request, producto_id):
    producto =  get_object_or_404(Producto, id=producto_id)

    return render(request, 'core/productos.html',{
        'categorias' : Categoria.objects.all(),
        'producto' : producto
    })

def producto_edit(request, producto_id):
    categorias = Categoria.objects.all()
    producto = Producto.objects.get(id=producto_id)

    if request.method == "POST":
        categoria_del_producto = Categoria.objects.get(id=request.POST["categoria"])
        form = FormProducto(request.POST, request.FILES, instance=Producto(imagen=request.FILES['imagen'], categoria=categoria_del_producto))   
        if form.is_valid():
            producto.titulo = request.POST['titulo']
            producto.categoria = categoria_del_producto
            producto.descripcion = request.POST['descripcion']
            producto.imagen = request.FILES['imagen']
            producto.precio = request.POST['precio']
            producto.save()
            return redirect("productos_index")
        else:
            return render(request, 'core/productos.html', {
                'categorias' : categorias,
                'error_message' : 'Ingreso un campo incorrecto, vuelva a intentar'
            })
    else:
        return render(request, 'core/productos.html',{
            'categorias' : categorias,
            'producto' : producto
        })

def producto_delete(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    producto.delete()
    return redirect('productos_index')
    #return HttpResponse(f'Eliminar producto_id: {producto.id}')



def productos_por_categoria(request, categoria_id):
    
    #categoria = Categoria.objects.get(id=categoria_id)
    categoria = get_object_or_404(Categoria, id = categoria_id)
    productos = categoria.productos.all()
    return render(request, 'core/productos.html',
    {
        'categorias' : Categoria.objects.all(),
        'productos' : productos,
        'categoria' : categoria.descripcion,
        'titulo_seccion' : 'Productos de la categoria',
        'sin_productos' : 'No hay producto de la categoria ' + categoria.descripcion
    })

""" 
    CARRITO
"""
def carrito_index(request):
    categorias = Categoria.objects.all()
    usuario_logeado = User.objects.get(username=request.user)
    productos = Carrito.objects.get(usuario=usuario_logeado.id).items.all()

    carrito = Carrito.objects.get(usuario=usuario_logeado.id)
    nuevo_precio_Carrito = 0
    for item in carrito.items.all():
        nuevo_precio_Carrito += item.producto.precio
    carrito.total = nuevo_precio_Carrito
    carrito.save()

    return render(request, 'core/productos.html', {
        'categorias' : categorias,
        'usuario' : usuario_logeado,
        'items_carrito' : productos
    })

def carrito_save(request):
    #tieneCarrito = Carrito.objects.filter(usuario=8).count()
    # Devuelve un 404 si no encuentra el carrito
    #arrito = get_object_or_404(Carrito, usuario=usuario_logeado.id)

    if request.method == 'POST':
        producto = Producto.objects.get(id=request.POST['producto_id'])
        usuario_logeado = User.objects.get(username=request.user)

        # Agrego producto al carrito
        carrito = Carrito.objects.get(usuario=usuario_logeado.id)
        item_carrito = Carrito_item()
        item_carrito.carrito = carrito
        item_carrito.producto = producto
        item_carrito.save()

        # Sumo el precio del producto al carrito
        carrito.total = producto.precio + carrito.total
        carrito.save()
        messages.success(request, f"El producto {producto.titulo} fue agregado al carrito")
        #return HttpResponse(f"{usuario_logeado.id} | ITEM_CARRITO: {item_carrito} | CARRITO: {carrito}")
        return redirect("productos_index")

    else:
        return redirect("productos_index")

def carrito_clean(request):
    usuario_logeado = User.objects.get(username=request.user)
    carrito = Carrito.objects.get(usuario=usuario_logeado.id)
    carrito.items.all().delete()
    carrito.total = 0
    carrito.save()
    #return HttpResponse(f'Carrito: id({carrito.id}) ${carrito.total} | Usuario: id({usuario_logeado.id}) {usuario_logeado.username} | items_carrito: {carrito.items.all().count()}')
    return redirect('carrito_index')

def item_carrito_delete(request, item_carrito_id):
    item_carrito = Carrito_item.objects.get(id=item_carrito_id)
    carrito = item_carrito.carrito
    
    # Vuelvo a calcular el precio del carrito
    nuevo_precio_Carrito = 0 - item_carrito.producto.precio
    for item in carrito.items.all():
        nuevo_precio_Carrito += item.producto.precio

    # Realizo los cambios en la base de datos
    carrito.total = nuevo_precio_Carrito
    item_carrito.delete()
    carrito.save()
    return redirect("carrito_index")
