from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.conf import settings
import os

# Create client views here.
def Login(request):
    if "client" in request.session:
            return redirect("index")
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        with connection.cursor() as cursor:
            query = "SELECT * FROM register WHERE email = %s AND password = %s"
            cursor.execute(query, [email, password])
            user = cursor.fetchone()
            if user:
                request.session["client"] = user[1]
                request.session.modified = True

                next_url=request.session.pop('next_url',None)
                messages.success(request, 'Login successful!')
                # User exists, redirect to index page
                return redirect(next_url if next_url else 'index')
            else:
                messages.error(request, 'Invalid credentials!')
                # Invalid credentials, redirect back to login page
                return redirect('login')
    return render(request, 'login.html')

def Register(request):
    if request.method == 'POST':
        # Handle form submission and save user data
        # You can access form data using request.POST dictionary
        name = request.POST.get('fullname')
        email = request.POST.get('email')
        mobile = request.POST.get('mb')
        password = request.POST.get('password')
        cpassword = request.POST.get('confirm_password')
        if password != cpassword:
            messages.success(request,'both password are not same')
            return redirect('register')  # Redirect back to register page if passwords don't match
        with connection.cursor() as cursor:
            query = "INSERT INTO register (name, email, mobile, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, [name, email, mobile, password])
            messages.success(request, 'Registration successful!')
            return redirect('login')  # Redirect to login page after successful registration
    return render(request, 'register.html')

def Index(request):
    return render(request, "index.html")

def Menu(request): 
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM services")
        menu_items = cursor.fetchall()

    datalist = []

    for item in menu_items:
        datalist.append({
            'id': item[0],
            'name': item[1],
            'category': item[2],
            'price': item[3],
            'description': item[4],
            'image': item[5],
        })

    return render(request, "menu.html", {'datas': datalist})

def Details(request,id):
    with connection.cursor() as cursor:
        query="select * from services where id=%s"
        cursor.execute(query,[id])
        data=cursor.fetchone()

    return render(request, "details.html", {"datas":data})

def addtocart(request,id):
    if "client" not in request.session:
         request.session['next_url']=request.get_full_path()
         messages.success(request,"Access starts wuth a login")
         return redirect("login")

    with connection.cursor() as cursor:
        query = "select * from services where id=%s"
        cursor.execute(query,[id])
        data=cursor.fetchone()
        if data is None:
             return redirect("index")

        useremail=request.session.get("client")
        prname=data[1]
        prcat=data[2]
        prprice=data[3]
        primage=data[5]

        Cart_query="insert into cart (pname,cat,price,user,image) values (%s,%s,%s,%s,%s)"
        cursor.execute(Cart_query,[prname,prcat,prprice,useremail,primage])
        messages.success(request,"product added in your cart")
        return redirect("cart")

def Cart(request):
    if "client" not in request.session:
        return redirect("login")
    with connection.cursor() as cursor:
        query = "select * from cart where user=%s"
        cursor.execute(query,[request.session.get("client")])
        data=cursor.fetchall()
        datalist=[
             {
                  'id':row[0],
                  'nm':row[1],
                  'cat':row[2],
                  'pr':row[3],
                  'user':row[4],
                  'img':row[5],
             }
             for row in data
        ]
        total_price=0
        for item in datalist:
            total_price=total_price+int(item["pr"])
        final_total=total_price+20
    return render(request, "cart.html", {"datas":datalist, "subtotal":total_price, "total":final_total})

def remove_cart(request, id): 
    if "client" not in request.session: 
        return redirect("login")
    with connection.cursor() as cursor:
        query = "DELETE FROM cart WHERE id=%s AND user=%s"
        cursor.execute( query, [id, request.session.get("client")] ) 
        return redirect("cart")

def Checkout(request,t):
    if "client" not in request.session:
        return redirect("login")
    username = request.session.get("client")
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        city = request.POST.get("city")
        pin = request.POST.get("pin")

        with connection.cursor() as cursor:
            selectcart = "SELECT * FROM cart WHERE user = %s"
            cursor.execute(selectcart, [username])
            data = cursor.fetchall()
            datalist=[
                  {
                        'id':row[0],
                        'nm':row[1],
                        'cat':row[2], 
                        'pr':row[3], 
                        'user':row[4], 
                        'img':row[5], 
                        } 
                        for row in data
                    ]

            insertorder = "INSERT INTO orders (pname, cat, price, user, image,total) VALUES (%s, %s, %s, %s, %s, %s)"
            for product in datalist:
                cursor.execute(insertorder,[product['nm'],product['cat'],product['pr'],product['user'],product['img'],t])

            query= "INSERT INTO address(name,email,mobile,address,city,pin) values(%s,%s,%s,%s,%s,%s)"
            delete_query="DELETE FROM cart WHERE user=%s"
            cursor.execute(delete_query, [username])
            cursor.execute(query, [name,email,mobile,address,city,pin])
            messages.success(request, "Order placed successfully!")
        return render(request,"index.html")
    else:
        with connection.cursor() as cursor:
            sql="SELECT * FROM address WHERE name=%s"
            cursor.execute(sql, [username])
            data=cursor.fetchone()
            if data:
                datalist={
                        "id": data[0],
                        "name": data[1],
                        "email": data[2],
                        "mobile": data[3],
                        "address": data[4],
                        "city": data[5],
                        "pin": data[6],
                    }
                
                return render(request, "checkout.html", {"dt":datalist, "u":username})
            else:
                return render(request, "checkout.html",{"u":username})


def Logout(request):
    if "client" in request.session:
            request.session.flush()
            messages.success(request,"logout success")
            return redirect("login")


# Create admin views here.
def AdminLogin(request):
    if "aduser" in request.session:
        return redirect("adminhome")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        with connection.cursor() as cursor:
            query = """
                SELECT * FROM admin
                WHERE email = %s AND password = %s
            """
            cursor.execute(query, [email, password])
            admin = cursor.fetchone()
        if admin:
            request.session["aduser"]=admin[1]
            messages.success(request, "Admin Login Successful!")
            return redirect("adminhome")

        else:
            messages.error(request, "Invalid Admin Email or Password!")
            return redirect("adminlogin")

    return render(request, "admin/adlogin.html")

def adminhome(request):
    if "aduser" not in request.session:
        return redirect("adlogin")
    return render(request, "admin/adminhome.html")

def addmenu(request):
    if "aduser" not in request.session:
            return redirect("adlogin")
    if request.method == 'POST':
        # Handle form submission and save menu data
        name = request.POST.get('mname')
        category = request.POST.get('category')
        price = request.POST.get('price')
        description = request.POST.get('description')
        img=request.FILES.get('image')
        if img:
            image_path=os.path.join(settings.MEDIA_ROOT,"dishes",img.name)
            os.makedirs(os.path.dirname(image_path),exist_ok=True)
            with open(image_path,"wb") as f:
                for chunk in img.chunks():
                    f.write(chunk)
            image_r_p="/cafeapp/static/images/dishes/"+img.name

        with connection.cursor() as cursor:
            query = "INSERT INTO services (name, category, price, description, image) VALUES (%s, %s, %s, %s,%s)"
            cursor.execute(query, [name, category, price, description,image_r_p])
            messages.success(request, 'Menu item added successfully!')
            return redirect('managemenu')  # Redirect to manage menu page after successful addition
    return render(request, "admin/addmenu.html")



def managemenu(request):
    if "aduser" not in request.session:
            return redirect("adlogin")
    with connection.cursor() as cursor:
        query = "SELECT * FROM services"
        cursor.execute(query)
        menu_items = cursor.fetchall()
        datalist = [ 
            
            {
                'id': item[0],
                'name': item[1],
                'category': item[2],
                'price': item[3],
                'description': item[4],
                'image': item[5],
            }
            for item in menu_items
        ]
    return render(request, "admin/managemenu.html", {'datas': datalist})

def delete_menu(request, id):
    if "aduser" not in request.session:
            return redirect("adlogin")
    with connection.cursor() as cursor:
        query = "DELETE FROM services WHERE id = %s"
        cursor.execute(query, [id])
        messages.success(request, 'Menu item deleted successfully!')
        return redirect('managemenu')

def editmenu(request, id):
    if "aduser" not in request.session:
            return redirect("adlogin")
    if request.method == 'POST':
        # Handle form submission and update menu data
        name = request.POST.get('mname')
        category = request.POST.get('category')
        price = request.POST.get('price')
        description = request.POST.get('description')
        img=request.FILES.get('image')
        if img:
            image_path=os.path.join(settings.MEDIA_ROOT,"dishes",img.name)
            os.makedirs(os.path.dirname(image_path),exist_ok=True)
            with open(image_path,"wb") as f:
                for chunk in img.chunks():
                        f.write(chunk)
            image_r_p="/cafeapp/static/images/dishes/"+img.name
        
            with connection.cursor() as cursor:
                query = "UPDATE services SET name = %s, category = %s, price = %s, description = %s, image=%s WHERE id = %s"
                cursor.execute(query, [name, category, price, description,image_r_p, id])
                messages.success(request, 'Menu item updated successfully!')
                return redirect('managemenu')
        else:
            with connection.cursor() as cursor:
                query = "UPDATE services SET name = %s, category = %s, price = %s, description = %s WHERE id = %s"
                cursor.execute(query, [name, category, price, description, id])
                messages.success(request, 'Menu item updated successfully!')
                return redirect('managemenu')  # Redirect to manage menu page after successful update
            
    with connection.cursor() as cursor:
        query = "SELECT * FROM services WHERE id = %s"
        cursor.execute(query, [id])
        menu_item = cursor.fetchone()
        if menu_item:
            datalist = {
                'id': menu_item[0],
                'name': menu_item[1],
                'category': menu_item[2],
                'price': menu_item[3],
                'description': menu_item[4],
                'img':menu_item[5],
            }
            return render(request, "admin/editmenu.html", {'data': datalist})
        else:
            return redirect('managemenu')  # Redirect

def manageuser(request):
    if "aduser" not in request.session:
            return redirect("adlogin")
    with connection.cursor() as cursor:
        query = "SELECT * FROM register"
        cursor.execute(query)
        user_items = cursor.fetchall()
        datalist = [ 
            
            {
                'id': item[0],
                'name': item[1],
                'email': item[2],
                'mobile': item[3],
                'password': item[4]
            }
            for item in user_items
        ]
    return render(request, "admin/manageuser.html", {'datas': datalist})

def delete_user(request, id):
    if "aduser" not in request.session:
            return redirect("adminhome")
    with connection.cursor() as cursor:
        query = "DELETE FROM register WHERE id = %s"
        cursor.execute(query, [id])
        return redirect('manageuser')

def edituser(request, id):
    if "aduser" not in request.session:
            return redirect("adminhome")
    if request.method == 'POST':
        # Handle form submission and update user data
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mb')
        password = request.POST.get('password')
        with connection.cursor() as cursor:
            query = "UPDATE register SET name = %s, email = %s, mobile = %s, password = %s WHERE id = %s"
            cursor.execute(query, [name, email, mobile, password, id])
            return redirect('manageuser')  # Redirect to manage user page after successful update
        
    with connection.cursor() as cursor:
        query = "SELECT * FROM register WHERE id = %s"
        cursor.execute(query, [id])
        user_item = cursor.fetchone()
        if user_item:
            datalist = {
                'id': user_item[0],
                'name': user_item[1],
                'email': user_item[2],
                'mobile': user_item[3],
                'password': user_item[4]
            }
            return render(request, "admin/edituser.html", {'data': datalist})
        else:
            return redirect('manageuser')  

def manageorder(request):

    if "aduser" not in request.session:
        return redirect("adlogin")

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM orders")
        rows = cursor.fetchall()

        user_orders = {}

        for item in rows:
            username = item[4]

            if username not in user_orders:
                user_orders[username] = {
                    "user": username,
                    "orders": [],
                    "address": "Address not available",
                    "total": 0
                }

                cursor.execute(
                    "SELECT address FROM address WHERE name = %s",
                    [username]
                )
                address_data = cursor.fetchone()

                if address_data:
                    user_orders[username]["address"] = address_data[0]

            user_orders[username]["orders"].append({
                "id": item[0],
                "pname": item[1],
                "cat": item[2],
                "price": item[3],
                "user": item[4],
                "image": item[5],
                "total": item[6]
            })

            user_orders[username]["total"] += float(item[6] or 0)

    return render(
        request,
        "admin/manageorder.html",
        {"orders": list(user_orders.values())}
    )

def viewaddress(request,nm):
    with connection.cursor() as cursor:
        cursor.execute("select * from address where name=%s",[nm])
        data=cursor.fetchone()
    return render(request,"admin/viewaddress.html", {"a":data})

def delete_order(request,id):
    with connection.cursor() as cursor:
        q=("delete from orders where id=%s")
        cursor.execute(q,[id])
        return redirect('manageorder')

def logout_view(request):
    if "aduser" in request.session:
        request.session.flush()
        messages.success(request,"logout success")
        return redirect("adlogin")