import json
import datetime
from datetime import date
import hmac
import hashlib
from time import strptime
from guest.models import *
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from User.models import *
from Student.decorators import *
# Create your views here.
from Student.decorators import *
import razorpay
from django.views.decorators.csrf import csrf_exempt


client = razorpay.Client(auth=("rzp_test_wVJXbmu0rqhHN5", "u8MQ0rSaBtfyJloFK5YNEpIc"))
client.set_app_details({"title" : "Django", "version" : "3.2"})

@studentonly
def load_index(request):
    id =request.session.get('userid')
    user = student.objects.get(sd_id=id)
    return render(request,'student_templates/index.html',{'user':user})
def logout(request):
    request.session.flush()
    return redirect('student_login')
@studentonly
def student_profile(request):
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)

    if request.method == "POST":
        print(request.POST)
        print(request.FILES)
        try:
            user.sd_name = request.POST['sd_name']
            user.sd_address = request.POST['sd_address']
            user.sd_email = request.POST['sd_email']
            user.sd_phone = request.POST['sd_phone']
            user.sd_university_register = request.POST['sd_university_register']
            user.sd_password = request.POST['sd_password']
            if len(request.FILES) != 0:
                user.sd_pic = request.FILES['sd_pic']
            user.save()
            return render(request, 'student_templates/profile.html',
                          {'user': user, 'media_url': settings.MEDIA_URL, 'success': True})
        except Exception as e:
            return render(request, 'student_templates/profile.html',
                          {'user': user, 'media_url': settings.MEDIA_URL, 'err': True})

    return render(request,'student_templates/profile.html',{'user':user,'media_url': settings.MEDIA_URL})

@studentonly
def student_parent_show(request):
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)

    return render(request,'student_templates/parent.html',{'user':user})

@studentonly
def table(request):
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)
    return render(request,'student_templates/table.html' ,{'user':user})
@studentonly
def students_view(request):
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)
    obj = student.objects.all()
    return render(request, 'student_templates/students_list.html',{'user':user,'obj':obj})

@studentonly
def student_today_attendance(request):
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)
    today = date.today().strftime("%Y-%m-%d")
    obj = attendance.objects.filter(date=today).values("sd_id")
    res = [sub['sd_id'] for sub in obj]
    st_obj = student.objects.all()
    if id in res:
        present =True
    else:
        present=False

    return render(request,'student_templates/today_attendance.html',{'user':user,'today':today,'attendace_obj': res,'obj':st_obj,'present':present})

@studentonly
def student_pending_fee(request):
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)
    obj = fees.objects.filter(status=0,sd_id=id).all()

    for i in obj:
        order_amount = ""+str(i.total*100)
        i.amount_paise=i.total*100
        order_currency = 'INR'
        order_receipt = ""+str(i.id)
        notes = {'Shipping address': 'Bommanahalli, Bangalore'}  # OPTIONAL
        payment = client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes))
        i.orderid=payment['id']
        i.save()
        print(i.orderid)
    return render(request,'student_templates/pending_fee.html',{'user':user,'obj':obj,})

def test(request):

    order_id= 'order_H9Dcd7d9kCtYUJ'
    payment_id= 'pay_H9DcjPK9hms0pH'
    secret=b'u8MQ0rSaBtfyJloFK5YNEpIc'
    signature='8444f1554e74ef9eedc28462821d5ec5f6e45b698bff5037010235201c3b2c7a'
    param=order_id+"|"+payment_id
    param=bytes(param,"utf-8")
    generated_signature = hmac.new(secret,param, hashlib.sha256).hexdigest()
    if(generated_signature==signature):
        print("success")
        print(generated_signature)
        print(signature)

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=401)

    # payment=None
    # # print(client.order.fetch("order_H8gdXgOXLRTWAk"))
    # try:
    #     order_amount = 50000
    #     order_currency = 'INR'
    #     order_receipt = 'order_rcptid_11'
    #     notes = {'Shipping address': 'Bommanahalli, Bangalore'}  # OPTIONAL
    #     payment=client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes))
    #     print(payment)
    # except Exception as e:
    #     print(e)
    # return  render(request,'student_templates/payment.html',{'payment':payment})

@csrf_exempt
def callback(request):
    print(request.POST)
    try:
        obj = Razorpay()
        fee_obj=fees.objects.get(orderid=request.POST['razorpay_order_id'])
        obj.razorpay_payment_id=request.POST['razorpay_payment_id']
        obj.razorpay_order_id=request.POST['razorpay_order_id']
        obj.razorpay_signature=request.POST['razorpay_signature']
        obj.fee_info=fee_obj
        obj.save()
        print("razorpay details saved")
        secret = b'u8MQ0rSaBtfyJloFK5YNEpIc'
        param = obj.razorpay_order_id + "|" + obj.razorpay_payment_id
        param = bytes(param, "utf-8")
        generated_signature = hmac.new(secret, param, hashlib.sha256).hexdigest()
        if (generated_signature == obj.razorpay_signature):
            print("success")
            fee_obj.status=True
            fee_obj.transaction="Online"
            fee_obj.paid_by="student-self"
            fee_obj.save()
        else:
            print("failed")
    except Exception:
        print("exception")
    return redirect('student_all_fee')
@studentonly
def all_fee(request):
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)
    obj = fees.objects.filter(sd_id=id)
    return render(request,'student_templates/all_fee.html',{'user':user,'obj':obj})

@studentonly
def complaints(request):
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)
    obj = complaint.objects.filter(auther_ID=id)
    return render(request,'student_templates/complaint.html',{'user':user,'obj':obj})

@studentonly
def add_complaints(request):
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)

    if request.method=="POST":
        print(request.POST)
        try:
            reg = complaint()
            reg.auther=user.sd_name
            reg.auther_phone=user.sd_phone
            reg.auther_ID=user.sd_id
            reg.status='open'
            reg.date=request.POST['date']
            reg.subject=request.POST['subject']
            reg.body=request.POST['body']
            reg.save()
            return redirect('student_complaints')
        except Exception as e:
            print(e)
    return render(request,'student_templates/add_complaint.html',{'user':user})

@studentonly
def apply_leave(request):
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)
    if request.method =="POST":
        print(request.POST)
        f = request.POST['datepickerstart']
        l = request.POST['datepickerend']
        if (f<=l):
            print("valid")
            try:
                lve = leave()
                lve.sd_id = user.sd_id
                lve.student_info=user
                lve.sd_name=user.sd_name
                lve.leave_type=request.POST['leave-type']
                lve.start_date=request.POST['datepickerstart']
                lve.end_date=request.POST['datepickerend']
                lve.reason=request.POST['reason']
                if 'half_day' in request.POST:
                    lve.half_day=True
                else:
                    lve.half_day=False
                start=datetime.datetime.strptime(request.POST['datepickerstart'], '%Y-%m-%d')
                end = datetime.datetime.strptime(request.POST['datepickerend'], '%Y-%m-%d')
                no_day =(end-start).days +1
                lve.no_of_day = no_day
                lve.save()
            except Exception as e:
                print(e)
                return render(request,'student_templates/leaveform.html',{'user':user,'media_url': settings.MEDIA_URL,'err':True})
    return render(request,'student_templates/leaveform.html',{'user':user,'media_url': settings.MEDIA_URL})

def list_leave(request):
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)
    lve = leave.objects.filter(sd_id=id)
    return render(request,'student_templates/list_leave.html',{'user':user,'obj':lve})

@studentonly
def guest(request):
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)
    obj = register_guest.objects.filter(status=1)
    return render(request,'student_templates/guest.html',{'user':user,'obj':obj})

@studentonly
def request_service(request):
    today = date.today().strftime('%Y-%m-%d')
    print(today)
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)
    if request.method.upper() == "POST":
        print(request.POST)
        try:
            reg = service()
            reg.auther=user.sd_name
            reg.auther_phone=user.sd_phone
            reg.auther_ID=user.sd_id
            reg.status='open'
            reg.date=today
            reg.subject=request.POST['subject']
            reg.body=request.POST['body']
            if 'important' in request.POST:
                reg.important = True
            else:
                reg.important = False
            reg.save()
        except Exception as e:
            print(e)
    return render(request,'student_templates/service_request.html',{'user':user,'today':today})

@studentonly
def list_service_requested(request):
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)
    obj = service.objects.filter(auther_ID=id)
    return render(request,'student_templates/list_service.html',{'user':user,'obj':obj})

@studentonly
def show_calender(request):
    id = request.session.get('userid')
    user = student.objects.get(sd_id=id)

    return  render(request,'student_templates/calender.html',{'user':user})