from django.shortcuts import render, redirect
from apps.hotel_app.models import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.contrib import messages
import math

# from .models import User, Payment, Room, Reservation 

###### Home Page ###########################
def index(request):
    if request.session.keys():
        request.session.clear()
    data = Room.objects.all()
    if not data:
        Room.objects.create(name="king",rate=280.00)
        Room.objects.create(name="queen",rate=280.00)
        Room.objects.create(name="deluxe",rate=450.00)
    else:
        print(data)
    return render(request,"hotel_app/index.html")

############# Room Type List #########################
def rooms(request):
    return render(request, "hotel_app/rooms.html")

############# Room Info for Each Room #########################
def room_info(request,name):
    context = {
        "this_room": Room.objects.get(name=name)
    }
    return render(request, "hotel_app/room_info.html", context)

################# goes to Reservation Form ######################
def reservation(request):
    return render(request, "hotel_app/reservation.html")

#################### calculate subtotal ##########################
def calculate_subtotal(request):
    if request.method == "POST":
        name=request.POST["room"]
        this_room = Room.objects.get(name=name)
        check_in = datetime.strptime(request.POST['check_in'], "%Y-%m-%d")
        check_out = datetime.strptime(request.POST['check_out'], "%Y-%m-%d")
        rdelta = relativedelta(check_out, check_in)
        total_nights = rdelta.days
        subtotal = int(this_room.rate) * total_nights
        request.session['subtotal'] = subtotal
        request.session['check_in'] = request.POST['check_in']
        request.session['check_out'] = request.POST['check_out']
        request.session['total_nights'] = total_nights
        request.session['room_name'] = this_room.name
        return redirect('/total_cost')

############# shows page that shows total cost #################
def total_cost(request):
    context = {
        "total": request.session['subtotal'],
        "this_room": Room.objects.get(name=request.session['room_name']),
        "total_nights": request.session['total_nights'],
    }
    return render(request, "hotel_app/total_cost.html", context)

#################### shows form where you input payment info #######
def payment(request):
    return render(request, "hotel_app/payment.html")

############### function that enters payment info into session ######
def enter_payment(request):
    request.session['first_name'] = request.POST['first_name']
    request.session['last_name'] = request.POST['last_name']
    request.session['email'] = request.POST['email']
    request.session['street'] = request.POST['street']
    request.session['city'] = request.POST['city']
    request.session['zipcode'] = request.POST['zipcode']
    request.session['state'] = request.POST['state']
    request.session['credit_card'] = request.POST['credit_card']
    request.session['cvv'] = request.POST['cvv']
    request.session['month'] = request.POST['month']
    request.session['year'] = request.POST['year']
    return redirect('/confirmation')

############# confirmation page for payment, total nights #####
def confirmation(request):
    this_room = Room.objects.get(name=request.session['room_name'])
    rate = math.floor(this_room.rate)
    request.session['rate'] = rate
    return render(request, "hotel_app/confirmation.html")

########## delete information from session #############
def cancel(request):
    request.session.clear()
    return redirect('/rooms')

########## update information from session ###############
def change(request):
    return render(request, "hotel_app/reservation.html")


######### enters the reservation info into database ########
def enter_reservation(request):
    this_room = Room.objects.get(name=request.session['room_name'])

    this_user = User.objects.create(first_name = request.session['first_name'], last_name=request.session['last_name'], email=request.session['email'])

    this_payment = Payment.objects.create(credit_card_number=request.session['credit_card'], expiration_month=request.session['month'],expiration_year=request.session['year'], cvv=request.session['cvv'],street=request.session['street'],city=request.session['city'], zip_code=request.session['zipcode'], state=request.session['state'], paid_by=this_user)

    this_reservation = Reservation.objects.create(start_date=request.session['check_in'], end_date=request.session['check_out'], cost=request.session['subtotal'], created_by=this_user, payment_info=this_payment, room_type=this_room)
    return redirect(f'/success/{this_reservation.id}')

######## shows confirmation of your reservation ID and that email got sent to user's email ################ 
def success(request,id):
    this_reservation = Reservation.objects.get(id=id)
    context= {
        "reservation_id": this_reservation.id,
        "email": this_reservation.created_by.email,
    }
    request.session.clear()
    return render(request,"hotel_app/success.html",context)

#################form to look up your existing reservation #####
def update(request):
    return render(request,"hotel_app/update.html")

######## function that looks up your existing reservation in the database ############
def lookup(request):
    if len(request.POST['email']) == 0 or len(request.POST['reservation_number']) == 0:
        context = {
            "error": "Email Address and Reservation Number is required, please try again",
        }
        return render(request,"hotel_app/update.html", context)
    reservation = Reservation.objects.filter(id=request.POST['reservation_number'])
    # reservation.exists() only works with .filter command, could not use .get
    if reservation.exists():
        # needed to enter another query that has .get to access a field within that query, .filter would not allow access to a field within a query, .filter returns a queryset
        reservation2 = Reservation.objects.get(id=request.POST['reservation_number'])
        request.session['reservation_id']= reservation2.id
        if request.POST['email'] == reservation2.created_by.email:
            return redirect(f'/existing/{reservation2.id}')
        else:
            context = {
            "error": "Email does not match reservation number, please try again",
        }
        return render(request,"hotel_app/update.html", context)
    else:
        context = {
            "error": "Reservation does not exist, please try again",
        }
        return render(request,"hotel_app/update.html", context)

########### info page that shows your existing reservation ########
def existing(request,id):
    this_reservation = Reservation.objects.get(id=id)
    context = {
        "reservation": this_reservation,
    }
    return render(request,"hotel_app/existing.html",context)

########### goes back to reservation page to change existing room type and check in/check out dates ##############
def edit(request,id):
    this_reservation = Reservation.objects.get(id=id)
    context = {
        "reservation": this_reservation,
        "check_in": this_reservation.start_date.strftime('%Y-%m-%d'),
        "check_out": this_reservation.end_date.strftime('%Y-%m-%d'),
    }
    return render(request,"hotel_app/edit.html",context)
    
############################## shows updated existing reservation in the database after you made changes #####################

def reupdate(request): 
    this_reservation = Reservation.objects.get(id = request.session['reservation_id'])
    context ={
        "reservation": this_reservation,
    }
    return render(request,"hotel_app/reupdate.html", context)

################## function that actually updates the existing reservation in database ############
def update_reservation(request):
    reservation = Reservation.objects.get(id=request.session['reservation_id'])
    reservation.start_date = request.session['check_in']
    reservation.end_date = request.session['check_out']
    reservation.cost = request.session['subtotal']
    room = Room.objects.get(name = request.session['room_name'])
    reservation.room_type = room
    reservation.save()
    return redirect(f"/success/{reservation.id}")

######### deletes entire reservation, user information, and payment information in the database ###############
def delete(request,id):
    reservation = Reservation.objects.get(id=id)
    user = reservation.created_by
    payment = reservation.payment_info
    user.delete()
    payment.delete()
    reservation.delete()
    request.session.clear()
    return redirect('/')

############## shows dining options #######################
def dining(request):
    return render(request, "hotel_app/dining.html")

############## show wellness information #######################
def wellness(request):
    return render(request, "hotel_app/wellness.html")

############## show spa information #######################
def spa(request):
    return render(request, "hotel_app/spa.html")

############## show fitness information #######################
def fitness(request):
    return render(request, "hotel_app/fitness.html")

############## show special events information #######################
def wedding(request):
    return render(request, "hotel_app/wedding.html")

############## show contact information #######################
def contact(request):
    return render(request, "hotel_app/contact.html")








