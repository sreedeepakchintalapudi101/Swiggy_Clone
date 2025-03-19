from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import User_Authentication, Restaurants, MenuItems, Cart, Address
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
def register(request):
    try:
        if request.method == "POST":
            print(f"The request data is {request}")
            firstname = request.POST.get("firstname")
            lastname = request.POST.get("lastname")
            email = request.POST.get("email")
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            if not firstname or not lastname:
                messages.error(request, "First Name and Last Name cannot be empty.")
                return redirect("register")
            if password1 != password2:
                messages.error(request, "Password does not match")
                return redirect("register")
            if User_Authentication.objects.filter(email=email).exists():
                messages.error(request, "Email already Exists")
                return redirect("register")
            else:
                user = User_Authentication(
                    firstname=firstname,
                    lastname=lastname,
                    email = email,
                    password1 = make_password(password1),
                    password2 = make_password(password2),
                    password = make_password(password1)
                )
                user.save()
                messages.success(request, "User saved Successfully!")
        return render(request, "register.html")
    except Exception as e:
        print(f"An error occurred: {e}")
        messages.error(request, "An unexpected error occurred.")
        return redirect("register")

from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib import messages
from swiggy_main_app.models import User_Authentication

def login_view(request):
    try:
        if request.method == "POST":
            print(f"The Login data is {request.POST}")
            email = request.POST.get("email")
            password = request.POST.get("password")

            if not email or not password:
                messages.error(request, "Email and Password should not be null")
                return render(request, "login.html")

            user_email = User_Authentication.objects.filter(email=email).first()

            if user_email:
                print(f"Stored hashed password: {user_email.password}")
                print(f"Raw password entered: {password}")
                print(f"Password match: {check_password(password, user_email.password)}")

            if user_email and check_password(password, user_email.password):  
                login(request, user_email)  # ✅ Correct way to authenticate
                messages.success(request, "Login Successful!")
                return redirect("home")

            messages.error(request, "Invalid email or password")
            return redirect("login")

        return render(request, "login.html")
    
    except Exception as e:
        print(f"Error Occurred: {e}")
        messages.error(request, "An unexpected error occurred")
        return redirect("login")

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")


def home_view(request):
    restaurants = Restaurants.objects.all()
    context = {"restaurants": restaurants}
    return render(request, "home.html", context)

restaurant = ""
def main_menu_view(request, restaurant_id):
    try:
        restaurant = Restaurants.objects.get(id=restaurant_id)
        menu_items = MenuItems.objects.filter(restaurant_id=restaurant_id)
        cart_items = Cart.objects.filter(user=request.user) if request.user.is_authenticated else []
    except Restaurant.DoesNotExist:
        error_message = "Restaurant not found"
    context = {
        "restaurant": restaurant,
        "menu_items": menu_items,
        "cart_items": cart_items,
    }
    return render(request, "main_menu.html", context)

@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItems, id=item_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, item=item)

    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    return redirect('main_menu_view', restaurant_id=item.restaurant.id)

@login_required
def view_cart(request):
    user_email = request.user
    cart_items = Cart.objects.filter(user=request.user)
    cart_count = sum(item.quantity for item in cart_items)
    
    total_bill = sum(item.quantity * item.item.price for item in cart_items)
    order_id = None
    order = Order.objects.filter(customer_email=user_email, status="Pending").first()
    if order:
        order_id = order.id

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"cart_count": cart_count})

    return render(request, 'cart.html', {'cart_items': cart_items, 'cart_count': cart_count, 'total_bill': total_bill, 'order_id' : order_id})


@login_required
def update_cart(request, item_id, action):
    cart_item = get_object_or_404(Cart, user=request.user, item_id=item_id)
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, user=request.user, item_id=item_id)
    cart_item.delete()
    return redirect('view_cart')

def cart_count_view(request):
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
    else:
        cart_count = 0
    return JsonResponse({'cart_count': cart_count})

@login_required
def payment_gateway(request):
    addresses = Address.objects.filter(user=request.user)
    context = {
        "addresses": addresses
    }
    return render(request, "payment_gateway.html", context)

# @login_required
# def select_address(request):
#     saved_addresses = Address.objects.filter(user=request.user)
#     return render(request, 'select_address.html', {'saved_addresses': saved_addresses})

# from django.contrib import messages

# from django.shortcuts import redirect, reverse

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Address

@login_required
def select_address(request):
    saved_addresses = Address.objects.filter(user=request.user)
    try:
        if request.method == "POST":
            full_name = request.POST.get("full_name")
            phone_number = request.POST.get("phone_number")
            street_address = request.POST.get("street_address")
            city = request.POST.get("city")
            state = request.POST.get("state")
            postal_code = request.POST.get("postal_code")

            if full_name and phone_number and street_address:
                Details = Address.objects.create(
                    user=request.user,
                    full_name=full_name,
                    phone_number=phone_number,
                    street_address=street_address,
                    city=city,
                    state=state,
                    postal_code=postal_code
                )
                Details.save()
                messages.success(request, "Address added successfully!")
                return redirect('select_address')
            else:
                messages.error(request, "Please fill in all required fields!")
    except Exception as e:
        print(f"Error Occured with Exception {e}")

    return render(request, 'select_address.html', {'saved_addresses': saved_addresses})

from django.shortcuts import redirect
from django.contrib import messages
from .models import Order, Cart, Address, User_Authentication, Restaurants

# def confirm_order(request):
#     # try:
#     print(f"The Request is {request}")
    
#     if request.method == "POST":
#         print(f"Received POST data: {request.POST}")
        
#         selected_address_id = request.POST.get("selected_address")
#         print(f"The Selected Address ID is {selected_address_id}")

#         user = request.user
#         print(f"The user is {user}")

#         if not selected_address_id:
#             print("Address Not Found")
#             return redirect("select_address")

#         try:
#             user_auth = User_Authentication.objects.get(email=request.user.email)
#             print(f"The User Auth Data is {user_auth}")
#             print(f"The User ID is {user_auth.id}")
#         except Exception as e:
#             print(f"Error Occurred with Exception {e}")
#             return redirect("select_address")

#         try:
#             selected_address = Address.objects.get(id=selected_address_id, user_id=user_auth.id)
#             print(f"The Selected Address is {selected_address}")
#         except Exception as e:
#             print(f"Error Occurred with Exception {e}")
#             return redirect("select_address")

#         try:
#             cart_items = Cart.objects.select_related("item").filter(user_id=request.user.id)
#             print(f"The Cart Items are {cart_items}")
            
#             if not cart_items.exists():
#                 messages.error(request, "Your cart is empty!")
#                 return redirect("view_cart")

#             for item in cart_items:
#                 print(f"Price: {item.item.price}, Quantity: {item.quantity}")
#         except Exception as e:
#             print(f"Error Occurred with Exception {e}")
#             return redirect("select_address")

#         # Calculate total price
#         total_price = sum(item.quantity * item.item.price for item in cart_items)
#         print(f"The Total Price is {total_price}")

#         # Get the restaurant from the first cart item (Assuming all items are from the same restaurant)
#         restaurant = cart_items.first().item.restaurant if cart_items.exists() else None

#         # Create order
#         order = Order.objects.create(
#             order_id=Order.generate_order_id(),  # Unique Order ID
#             restaurant=restaurant,
#             customer_name=user_auth.firstname + " " + user_auth.lastname,
#             customer_email=user_auth.email,
#             total_price=total_price,
#             status="Pending"
#         )

#         # Associate items with the order
#         for cart_item in cart_items:
#             order.items.add(cart_item.item)

#         return redirect("order_confirmation", order_id=order.id)

#     return redirect("select_address")

#     # except Exception as e:
#     #     print(f"Error Occurred with Exception {e}")
#     #     return redirect("select_address")


from django.shortcuts import redirect
from django.contrib import messages
from .models import Order, OrderItem, Cart, Address, User_Authentication, Restaurants, MenuItems

def confirm_order(request):
    try:
        print(f"The Request is {request}")
        
        order_status = ""

        if request.method == "POST":
            print(f"Received POST data: {request.POST}")

            selected_address_id = request.POST.get("selected_address")
            print(f"The Selected Address ID is {selected_address_id}")
            
            payment_method = request.POST.get("payment_method")
            print(f"The Payment Method is {payment_method}")

            user = request.user
            print(f"The user is {user}")

            if not selected_address_id or not payment_method:
                print("Address Not Found")
                return redirect("select_address")

            try:
                user_auth = User_Authentication.objects.get(email=request.user.email)
                print(f"The User Auth Data is {user_auth}")
                print(f"The User ID is {user_auth.id}")
            except Exception as e:
                print(f"Error Occurred with Exception {e}")
                return redirect("select_address")

            try:
                selected_address = Address.objects.get(id=selected_address_id, user_id=user_auth.id)
                print(f"The Selected Address is {selected_address}")
            except Exception as e:
                print(f"Error Occurred with Exception {e}")
                return redirect("select_address")

            try:
                cart_items = Cart.objects.select_related("item").filter(user_id=request.user.id)
                print(f"The Cart Items are {cart_items}")

                if not cart_items.exists():
                    messages.error(request, "Your cart is empty!")
                    return redirect("view_cart")

                for item in cart_items:
                    print(f"Price: {item.item.price}, Quantity: {item.quantity}")
            except Exception as e:
                print(f"Error Occurred with Exception {e}")
                return redirect("select_address")
            total_price = sum(item.quantity * item.item.price for item in cart_items)
            print(f"The Total Price is {total_price}")
            
            if payment_method:
                order_status = "Success"
            
            restaurant = cart_items.first().item.restaurant if cart_items.exists() else None
            order = Order.objects.create(
                order_id=Order.generate_order_id(),
                restaurant=restaurant,
                customer_name=user_auth.firstname + " " + user_auth.lastname,
                customer_email=user_auth.email,
                total_price=total_price,
                street_address = selected_address.street_address,
                city = selected_address.city,
                pincode = selected_address.postal_code,
                payment_method = payment_method,
                status = order_status,
            )
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item.item,
                    quantity=cart_item.quantity,
                    price=cart_item.item.price * cart_item.quantity
                )
            cart_items.delete()
            return redirect("order_confirmation", order_id=order.id)

        return redirect("select_address")

    except Exception as e:
        print(f"Error Occurred with Exception {e}")
        return redirect("select_address")
    

def order_confirmation(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order)

        # Compute total price in Python
        for item in order_items:
            item.total_price = item.quantity * item.menu_item.price  # Add total_price dynamically

        return render(request, "order_confirmation.html", {"order": order, "order_items": order_items})
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect("view_cart")

@login_required
def edit_profile(request):
    user_email = request.user
    print(f"The User is {user_email}")
    updated = False
    try:
        user_auth = User_Authentication.objects.get(email = user_email)
        print(f"The User Authentication Details are {user_auth}")
    except Exception as e:
        print(f"Error Occured with Exception {e}")
        return redirect("home")
    
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")
        
        if firstname and firstname != user_auth.firstname:
            user_auth.firstname = firstname
            updated = True
            
        if lastname and lastname != user_auth.lastname:
            user_auth.lastname = lastname
            updated = True
            
        if email and email != user_auth.email:
            if not User_Authentication.objects.filter(email=email).exclude(id=user_auth.id).exists():
                user_auth.email = email
                updated = True
            else:
                print("Email already Exists. Choose another field")
                return render(request, "edit_profile.html", {"user_auth": user_auth})
            
        if updated:
            user_auth.save()
            print("The User Saved Successfully!")
        else:
            print("There are no changes Detected.")
        return redirect("edit_profile")
    context = {
        "user_auth": user_auth
    }
    
    return render(request, "edit_profile.html", context)

from django.shortcuts import render
from .models import Order

@login_required
def my_orders(request):
    orders = Order.objects.filter(customer_email=request.user.email).prefetch_related("order_items__menu_item")
    context = {
        "orders": orders,
    }
    return render(request, "my_orders.html", context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, Cart, Address, User_Authentication, Restaurants, MenuItems

@login_required
def checkout(request):
    """
    Handles both selecting payment method and selecting an address in a single request.
    Saves the order if both are provided and redirects to confirmation page.
    """
    saved_addresses = Address.objects.filter(user=request.user)
    print(f"The Saved Addresses are {saved_addresses}")
    
    if request.method == "POST":
        print(f"Received POST data: {request.POST}")
        selected_address_id = request.POST.get("selected_address")
        print(f"The Selected Address is {selected_address_id}")
        full_name = request.POST.get("full_name")
        print(f"The Full Name is {full_name}")
        phone_number = request.POST.get("phone_number")
        print(f"The Phone Number is {phone_number}")
        street_address = request.POST.get("street_address")
        print(f"The Street Address is {street_address}")
        city = request.POST.get("city")
        print(f"The City is {city}")
        state = request.POST.get("state")
        print(f"The State is {state}")
        postal_code = request.POST.get("postal_code")
        print(f"The Postal Code is {postal_code}")
        payment_method = request.POST.get("payment_method")
        print(f"The Payment Method is {payment_method}")
        user_email = request.user
        print(f"The user is {user_email}")
        user_auth = User_Authentication.objects.get(email=user_email)
        print(f"The User Auth is {user_auth}")
        if selected_address_id:
            try:
                selected_address = Address.objects.get(id=selected_address_id, user_id = user_auth.id)
                print(f"Using selected address: {selected_address}")
            except Address.DoesNotExist:
                messages.error(request, "Invalid address selected.")
                return redirect("checkout")
        elif full_name and phone_number and street_address:
            selected_address = Address.objects.create(
                user=user,
                full_name=full_name,
                phone_number=phone_number,
                street_address=street_address,
                city=city,
                state=state,
                postal_code=postal_code
            )
            print(f"New address added: {selected_address}")
        else:
            messages.error(request, "Please select an address or enter new address details.")
            return redirect("checkout")
        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return redirect("checkout")
        print(f"Selected Payment Method: {payment_method}")
        try:
            user_auth = User_Authentication.objects.get(email=request.user.email)
            print(f"User Auth Data: {user_auth}")
        except Exception as e:
            print(f"The Error Occured with Exception {e}")
            return redirect("checkout")
        try:
            cart_items = Cart.objects.select_related("item").filter(user_id = request.user.id)
            print(f"The Cart Items available are {cart_items}")
            if not cart_items.exists():
                messages.error(request, "Your cart is empty!")
                return redirect("view_cart")
            for item in cart_items:
                print(f"Price: {item.item.price}, Quantity: {item.quantity}")
        except Exception as e:
            print(f"Error occured with Exception {e}")
            return redirect("checkout")
        total_price = sum(item.quantity * item.item.price for item in cart_items)
        print(f"Total Cart Price: {total_price}")
        
        if payment_method:
            order_status = "Success"
            
        restaurant = cart_items.first().item.restaurant if cart_items.exists() else None
        order = Order.objects.create(
            order_id=Order.generate_order_id(),
            restaurant=restaurant,
            customer_name=user_auth.firstname + " " + user_auth.lastname,
            customer_email=user_auth.email,
            total_price=total_price,
            street_address=selected_address.street_address,
            city=selected_address.city,
            pincode=selected_address.postal_code,
            payment_method=payment_method,
            status=order_status,
        )
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                menu_item=cart_item.item,
                quantity=cart_item.quantity,
                price=cart_item.item.price * cart_item.quantity
            )
        cart_items.delete()
        return redirect("order_confirmation", order_id=order.id)
    return render(request, "checkout.html", {"saved_addresses": saved_addresses})

import pandas as pd
from .models import Order
import datetime
from io import BytesIO
import xlsxwriter

@login_required
def download_my_orders_excel(request):
    orders = Order.objects.prefetch_related("order_items__menu_item").all()
    data = []
    for order in orders:
        print(f"The Order is {order}")
        for item in order.order_items.all():
            print(f"The Item is {item}")
            data.append({
                "Order ID": order.order_id,
                "Restaurant": order.restaurant.name,
                "Total Price": order.total_price,
                "Payment Method": order.payment_method,
                "Status": order.status,
                "Order Date": order.created_at.strftime("%d-%m-%Y %H:%M"),
                "Item Name": item.menu_item.name,
                "Quantity": item.quantity,
                "Item Price": item.price,
            })
    print(f"The Data is {data}")
    df = pd.DataFrame(data)
    current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename=f"my_orders_{current_time}.xlsx"

    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Orders")
    response = HttpResponse(output.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    filename = f"my_orders_{current_time}.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response