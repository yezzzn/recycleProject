from django.shortcuts import render, redirect
from item.models import Category, Item, Database, PointDB, Image ,Video, Apartdb , Aparterror , Apartdatabase #item/models.py에서 해당하는 이름의 필드를 가져옴 
from django.http import HttpResponse
from .forms import SignupForm , AptInfo # core/forms.py 에서 회원가입 폼과 AptInfo 폼 가져옴 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # 페이지 넘김을 구성하기 위한 peginator 
from django.http import JsonResponse 
import json , random
from django.views.decorators.csrf import csrf_exempt #POST 방식의 사용을 위해 필요
from django.contrib.auth.models import User 
from twilio.rest import Client 
from django.db import transaction

from collections import defaultdict


account_sid = "twillo sid"  
auth_token = "twillo token"   

Client = Client(account_sid, auth_token) 
 
# Create your views here.
def index(request): # 관리자 페이지 
    #------------------------------------ Django 에 존재하는 Paginator 사용-----------------------------------
    page = request.GET.get('page')
    items_per_page = 9 # 한페이지에 존재할 item 개수 

    recycle_data = Database.objects.all().order_by("-id")
    paginator = Paginator(recycle_data, items_per_page)
    
    try:
        recycle_data = paginator.page(page)
    except PageNotAnInteger:
        recycle_data = paginator.page(1)
    except EmptyPage:
        recycle_data = paginator.page(paginator.num_pages)
        
    
    #-----------------------------------------------------------------------
    
    items = Item.objects.filter(is_sold=False)[0:6]  # Django 공부 하며 구성한 예제에서 사용한 코드 
    categories = Category.objects.all() # Django 공부 하며 구성한 예제에서 사용한 코드 
    database = Database.objects.all() # item_database의 모든 내용을 가져옴 
    video = Video.objects.all() #item_video의 모든 내용을 가져옴 
    #recycle_data = Database.objects.all().order_by("-id")[0:9]
    
    # ------------------------------------- Database의 field 중 kind(종류) 가 해당하는 것의 수를 셈 ------------------
    plastic = Database.objects.filter(kind="plastic").count()
    glass = Database.objects.filter(kind="glass").count()
    paper = Database.objects.filter(kind="paper").count()
    can = Database.objects.filter(kind="can").count()
    plasticlb = Database.objects.filter(kind="plasticlabel").count()
    glasscap = Database.objects.filter(kind="nocapglass").count()
    
    doughnuterror = int(plasticlb) + int(glasscap)
    doughnutgood = int(paper)+int(glass)+int(can)+int(plastic)
    
    all = int(plastic) + int(glass)+int(paper)+int(can)+int(plasticlb)+int(glasscap)
    if all != 0:
        percent=doughnuterror/all*100
        percent_good = doughnutgood/all*100
    else :
        percent = 0
        percent_good=0
    doughnutpercent_error = round(percent, 2)
    doughnutpercent_good = round(percent_good,2)
    
    #----------------------------------------------------------------
    
    
    apt = Apartdatabase.objects.all()
    
    apartment_defect_rates = {}

    # 데이터베이스 내의 모든 아파트 정보를 가져옵니다.
    all_apartments = Apartdatabase.objects.all()
    all_dong = {}
    processed_apartments = set()
    # 각 아파트를 순회합니다.
    for apartment in all_apartments:
        if apartment.apartment in processed_apartments:
            continue
    
        apartments = Apartdatabase.objects.values_list('citizen', flat=True).filter(apartment=apartment)

        total_glass_data = 0
        total_plasticlb_data = 0
        totaldata = 0

        for i in apartments:
            glassdata = Database.objects.filter(created_by=i, kind='nocapglass').count()
            plasticlbdata = Database.objects.filter(created_by=i, kind='plasticlabel').count()
            alldata = Database.objects.filter(created_by=i).count()

            totaldata += alldata
            total_glass_data += glassdata
            total_plasticlb_data += plasticlbdata
            

        error = int(total_glass_data) + int(total_plasticlb_data)
        
        # 이 아파트의 불량률을 계산합니다.
        if totaldata != 0:
            percent = error / totaldata * 100
        else:
            percent = 0
        percent_error = round(percent, 2)
        
        # 이 아파트의 불량률을 딕셔너리에 저장합니다.
        apartment_defect_rates[apartment] = percent_error
        
        processed_apartments.add(apartment.apartment)
        
    for apartment, defect_rate in apartment_defect_rates.items():
        print(f"아파트: {apartment}, 불량률: {defect_rate}%")   
        
        apartment_error = Aparterror.objects.get(apartment=apartment)
        apartment_error.error = defect_rate  # 이름이 동일한 행의 pointuser라는 필드에 새로운 값 할당
        apartment_error.save()
            
    echapart_error = [item.error for item in Aparterror.objects.all()]
    echapart = [item.apartment for item in Aparterror.objects.all()]
    # print(echapart)
    # print(echapart_error)
   
    odkind = request.GET.get('odkind')
    oddata = Database.objects.filter(kind=odkind).order_by("-id")
    
    odpage= request.GET.get('odpage')

    paginator2 = Paginator(oddata, 9)
    
    try:
        oddata = paginator2.page(odpage)
    except PageNotAnInteger:
        oddata = paginator2.page(1)
    except EmptyPage:
        oddata = paginator2.page(paginator2.num_pages)
        
  
    
    
    #---------------------------------------차트를 바꾸기 위한 값 변경을 위함 ------------------------------------------
    
    apart_apartment = Apartdatabase.objects.values_list('apartment', flat=True)
    apart_apartment = set(apart_apartment)
    getapt= request.GET.get('apartment')
    apart_info = Apartdatabase.objects.values_list('dong', flat=True).filter(apartment=getapt)
    apart_info = set(apart_info) #set은 중복값을 허용하지 않음 
    getdong= request.GET.get('dong')
    dongperson =  Apartdatabase.objects.values_list('citizen', flat=True).filter(apartment=getapt,dong=getdong)
    
    total_glass_dong = 0
    total_plasticlb_dong = 0
    totaldong = 0
    total_goodglass_dong=0
    total_plastic_dong=0
    total_paper_dong=0
    total_can_dong=0
    
    for i in dongperson:
        glassdong=Database.objects.filter(created_by=i, kind='nocapglass').count() # 재활용품 DB의 입력한이의 이름과 종류가 glasscap인 것들만 필터링 한 후 수를 셈 
        plasticlbdong=Database.objects.filter(created_by=i, kind='plasticlabel').count()
        
        #재활용 데이터 
        plasticdong = Database.objects.filter(created_by=i , kind="plastic").count()
        goodglassdong = Database.objects.filter(created_by=i , kind="glass").count()
        paperdong = Database.objects.filter(created_by=i , kind="paper").count()
        candong = Database.objects.filter(created_by=i , kind="can").count()
        
        #모든 데이터 
        alldong = Database.objects.filter(created_by=i).count() # 재활용품의 DB에서 아파트 구성원에 대한 모든 재활용품 건수를 가져옴 
        
        totaldong += alldong 
        total_glass_dong += glassdong #총 값을 구하기 위해 저장할 변수를 선언 
        total_plasticlb_dong += plasticlbdong
        
        total_goodglass_dong += goodglassdong
        total_plastic_dong += plasticdong
        total_paper_dong += paperdong
        total_can_dong += candong
        
    recycledong = int( total_goodglass_dong)+int(total_plastic_dong)+int(total_paper_dong)+int(total_can_dong)
    errordong = int( total_glass_dong)+int(total_plasticlb_dong) # 불량 검출의 총 건수 
    if totaldong != 0:
        percentdong = errordong/totaldong*100 #불량검출 / 해당 아파트의 총 재활용품 건수
        goodpercentdong = recycledong/totaldong*100
    else :
        percentdong = 0
        goodpercentdong = 0
    percent_error_dong = round(percentdong, 2)
    goodpercent_apt_dong = round(goodpercentdong,2)
        
    #---------------------------------------------------------------------------------
        
    return render(
        request,
        "core/index.html",
        {
            "categories": categories,
            "items": items,
            "video":video,
            "database": database,
            "recycle_data": recycle_data,
            "plastic": plastic,
            "glass": glass,
            "paper": paper,
            "can": can,
            "plasticlb": plasticlb,
            "glasscap": glasscap,
            'apt':apt,
            "all":all,
            "doughnuterror":doughnuterror,
            "doughnutpercent_error":doughnutpercent_error,
            "echapart_error":echapart_error,
            "echapart":echapart,
            "oddata":oddata,
            "doughnutpercent_good":doughnutpercent_good,
            "doughnutgood":doughnutgood,
            "apart_apartment":apart_apartment,
            "percent_error_dong":percent_error_dong,
            "goodpercent_apt_dong":goodpercent_apt_dong,
            "apart_info":apart_info,
            "recycledong":recycledong,
            "errordong":errordong,
            "totaldong":totaldong,
        },
    )


def cindex(request):
    items = Item.objects.filter(is_sold=False)[0:6]
    categories = Category.objects.all()
    database = Database.objects.all()
    user=request.user
    recycle_data = Database.objects.filter(created_by=user).order_by("-id")[0:9]
    plastic = Database.objects.filter(created_by=user , kind="plastic").count()
    glass = Database.objects.filter(created_by=user , kind="glass").count()
    paper = Database.objects.filter(created_by=user , kind="paper").count()
    can = Database.objects.filter(created_by=user , kind="can").count()
    plasticlb = Database.objects.filter(created_by=user , kind="plasticlabel").count()
    glasscap = Database.objects.filter(created_by=user , kind="nocapglass").count()
    
    apt_name = Apartdatabase.objects.get(citizen=request.user).apartment 
    user_exists = Aparterror.objects.filter(apartment=apt_name).exists()
    
    if not user_exists:
        Aparterror.objects.create(
        apartment=apt_name,
    )
    #-------------------------------유저의 불량률 ------------------------------------
    public_all = Database.objects.filter(created_by = user).count()
    public_error = int(plasticlb)+int(glasscap)
    public_good = int(glass)+int(paper)+int(can)+int(plastic)
    
    if public_all != 0:
        public_percent = public_error/public_all*100 #불량검출 / 나의 총 재활용품 건수
        public_good_percent = public_good/public_all*100
    else :
        public_percent = 0
        public_good_percent =0
    public_percent = round(public_percent, 2)
    public_good_data= round(public_good_percent,2)
    
    #------------------------------유저의 불량률 끝-------------------------
    citizen_pay=Apartdatabase.objects.get(citizen=request.user)
    if public_percent >= 30:
        if citizen_pay.badcitizen == False:
            citizen_pay.pay += 3000
            citizen_pay.badcitizen = True
    else:
        citizen_pay.pay = 30000
        citizen_pay.badcitizen = False
    citizen_pay.save()
    
    citizenpay=citizen_pay.pay
    
    #-----------------------------아파트 불량률 ----------------------------------------
    citizen_detect = Apartdatabase.objects.filter(citizen=request.user) #접속한 유저에 대한 DB정보를 가져옴 
    apartment = citizen_detect.first().apartment # 해당 유저의 아파트 정보를 추출 
    # citizen_data = citizen_detect.first() # 해당 유저의 아파트 정보를 추출 
    # if citizen_data is not None:
    #     apartment = citizen_data.apartment
    # else:
    #     print('해당하는 아파트 정보가 없습니다.')
    # 해당 유저 정보가 DB에 없을 때 처리할 내용 추가
    apartments = Apartdatabase.objects.values_list('citizen', flat=True).filter(apartment=apartment) #아파트 정보가 DB와 동일한  citizen값 을 리스트로 가져옴 
    
    # 확인을 위한 코드 
    #print(apartment)
    
    total_glass_data = 0
    total_plasticlb_data = 0
    totaldata = 0
    total_goodglass_data=0
    total_plastic_data=0
    total_paper_data=0
    total_can_data=0
    
    for i in apartments: # 유저의 이름만큼 반복하는데 
        #print(i)
        #불량품 데이터 
        glassdata=Database.objects.filter(created_by=i, kind='nocapglass').count() # 재활용품 DB의 입력한이의 이름과 종류가 glasscap인 것들만 필터링 한 후 수를 셈 
        plasticlbdata=Database.objects.filter(created_by=i, kind='plasticlabel').count()
        
        #재활용 데이터 
        plasticdata = Database.objects.filter(created_by=i , kind="plastic").count()
        goodglassdata = Database.objects.filter(created_by=i , kind="glass").count()
        paperdata = Database.objects.filter(created_by=i , kind="paper").count()
        candata = Database.objects.filter(created_by=i , kind="can").count()
        
        #모든 데이터 
        alldata = Database.objects.filter(created_by=i).count() # 재활용품의 DB에서 아파트 구성원에 대한 모든 재활용품 건수를 가져옴 
        
        totaldata += alldata 
        total_glass_data += glassdata #총 값을 구하기 위해 저장할 변수를 선언 
        total_plasticlb_data += plasticlbdata
        
        total_goodglass_data += goodglassdata 
        total_plastic_data += plasticdata
        total_paper_data += paperdata 
        total_can_data += candata
    
    
    recycle = int( total_goodglass_data)+int(total_plastic_data)+int(total_paper_data)+int(total_can_data)
    # 확인을 위한 코드 
    # print(totaldata)
    # print(total_glass_data)
    # print(total_plasticlb_data)
    error = int( total_glass_data)+int(total_plasticlb_data) # 불량 검출의 총 건수 
    if totaldata != 0:
        percent = error/totaldata*100 #불량검출 / 해당 아파트의 총 재활용품 건수
        goodpercent = recycle/totaldata*100
    else :
        percent = 0
        goodpercent = 0
    percent_error = round(percent, 2)
    goodpercent_apt_data = round(goodpercent,2)
    
    #----------------------------------- 아파트 불량률 끝 -------------------------------------------------
    odkind = request.GET.get('odkind')
    oddata = Database.objects.filter(kind=odkind, created_by=request.user).order_by("-id")[0:9]
    
    #---------------------------------------차트를 바꾸기 위한 값 변경 ------------------------------------------
    apart_name = Apartdatabase.objects.get(citizen=request.user).apartment
    apart_info = Apartdatabase.objects.values_list('dong', flat=True).filter(apartment=apart_name)
    apart_info = set(apart_info) #set은 중복값을 허용하지 않음 
    
    getdong= request.GET.get('dong')
    dongperson =  Apartdatabase.objects.values_list('citizen', flat=True).filter(apartment=apart_name,dong=getdong)
    
    
    total_glass_dong = 0
    total_plasticlb_dong = 0
    totaldong = 0
    total_goodglass_dong=0
    total_plastic_dong=0
    total_paper_dong=0
    total_can_dong=0
    
    for i in dongperson:
        glassdong=Database.objects.filter(created_by=i, kind='nocapglass').count() # 재활용품 DB의 입력한이의 이름과 종류가 glasscap인 것들만 필터링 한 후 수를 셈 
        plasticlbdong=Database.objects.filter(created_by=i, kind='plasticlabel').count()
        
        #재활용 데이터 
        plasticdong = Database.objects.filter(created_by=i , kind="plastic").count()
        goodglassdong = Database.objects.filter(created_by=i , kind="glass").count()
        paperdong = Database.objects.filter(created_by=i , kind="paper").count()
        candong = Database.objects.filter(created_by=i , kind="can").count()
        
        #모든 데이터 
        alldong = Database.objects.filter(created_by=i).count() # 재활용품의 DB에서 아파트 구성원에 대한 모든 재활용품 건수를 가져옴 
        
        totaldong += alldong 
        total_glass_dong += glassdong #총 값을 구하기 위해 저장할 변수를 선언 
        total_plasticlb_dong += plasticlbdong
        
        total_goodglass_dong += goodglassdong
        total_plastic_dong += plasticdong
        total_paper_dong += paperdong
        total_can_dong += candong
        
    recycledong = int( total_goodglass_dong)+int(total_plastic_dong)+int(total_paper_dong)+int(total_can_dong)
    errordong = int( total_glass_dong)+int(total_plasticlb_dong) # 불량 검출의 총 건수 
    if totaldong != 0:
        percentdong = errordong/totaldong*100 #불량검출 / 해당 아파트의 총 재활용품 건수
        goodpercentdong = recycledong/totaldong*100
    else :
        percentdong = 0
        goodpercentdong = 0
    percent_error_dong = round(percentdong, 2)
    goodpercent_apt_dong = round(goodpercentdong,2)
        
    #---------------------------------------------------------------------------------
    if not citizen_detect.exists():
        return redirect("/save_apt_info/")
    else:
        return render(
            request,
            "core/cindex.html",
            {
                "user":user,
                "categories": categories,
                "items": items,
                "database": database,
                "recycle_data": recycle_data,
                "plastic": plastic,
                "glass": glass,
                "paper": paper,
                "can": can,
                "plasticlb": plasticlb,
                "glasscap": glasscap,
                "error":error,
                "percent_error":percent_error,
                "public_error":public_error,
                "public_percent":public_percent,
                "citizenpay":citizenpay,
                "oddata":oddata,
                "citizen_detect":citizen_detect,
                "goodpercent_apt_data":goodpercent_apt_data,
                "recycle":recycle,
                "public_good_data":public_good_data,
                "public_good":public_good,
                "apart_info":apart_info,
                "percent_error_dong":percent_error_dong,
                "goodpercent_apt_dong":goodpercent_apt_dong,
                "recycledong":recycledong,
                "errordong":errordong,
            },
        )
    
   


def first(request):
    return render(request, "core/first.html")


def contact(request):
    return render(request, "core/contact.html")


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("/login/")
    else:
        form = SignupForm()

    return render(request, "core/signup.html", {"form": form})



def milli(request):
    #마일리지 페이지에 접속 했을 때 PointDB에 접속자의 이름이 등록되있지 않다면 새로 데이터를 만듦
    
    up = User.objects.get(username=request.user).pointuser
    # point_objects, created = User.objects.get_or_create(username=up)
    # if not point_objects.point:
    #     point_objects.pointuser = 100  # 예를 들어, 0으로 초기화
    #     point_objects.save()  
        
    apt_name = Apartdatabase.objects.get(citizen=request.user).apartment 
    user_exists = PointDB.objects.filter(user=apt_name).exists()
    
    if not user_exists:
        PointDB.objects.create(
        user=apt_name,
        pointuser=100,
    )
        
    # 포인트 출력을 위해 DB에서 가져온 것
    datapoint = PointDB.objects.all()
    # 현재 접속한 유저의 이름을 가져옴
    username = request.user.username
    # data 2 는 유저의 이름을 가져오기 위한 코드
    datapoint_user = PointDB.objects.filter(user=apt_name).values("user")
    user_list = [item["user"] for item in datapoint_user]
    first_user_name = user_list[0] if user_list else None
    # 이미지 데이터 베이스 가져온 것
    image = Image.objects.all()

    return render(
        request,
        "core/milli.html",
        {
            "datapoint": datapoint,
            "username": username,
            "first_user_name": first_user_name,
            "image": image,
            "userpoint":up,
        },
    )


# url에 연결된 example?kind=원하는종류&num=원하는숫자 를 입력하면 데이터 베이스에 저장되어 data 홈페이지로 이동하여 보여줌
def get(request):
    if request.method == "GET":  # request의 방식이 GET 방식일 때
        kind = request.GET["kind"]  # url에서 get 방식으로 종류를 가져옴
        num = request.GET["num"]  # url에서 get 방식으로 숫자를 가져옴
        image = request.GET["image"]
        confidence = request.GET["confidence"]
        created_by = request.GET["created_by"]
        
        if kind == "glass":
            pluspoint = 5 * int(num)
        elif kind == "paper":
            pluspoint = int(num)
        elif kind == "can":
            pluspoint = 3 * int(num)
        elif kind == "plastic":
            pluspoint = 2 * int(num)
        else :
            pluspoint = 0

        try:
            with transaction.atomic():
                apt_name = Apartdatabase.objects.get(citizen=created_by).apartment 
                user = PointDB.objects.get(user=apt_name)
                user.pointuser += pluspoint  # 이름이 동일한 행의 pointuser라는 필드에 새로운 값 할당
                user.save()
                
                up = User.objects.get(username=created_by)
                up.pointuser += pluspoint
                up.save()
        except Exception as e:
            # 트랜잭션 실패 시 실행할 코드 (예를 들어 오류 처리)
            print(f"트랜잭션 실패: {str(e)}")
            
            
        Database.objects.create(  # DB에 새로 추가함
            kind=kind,  # DB의 kind 라는 곳에 get방식으로 얻어온 kind를 저장
            num=num,  # DB의 num 라는 곳에 get방식으로 얻어온 num을 저장
            image=image,
            confidence=confidence,
            created_by=created_by,
        )
    return render(request, 'core/cindex.html')


@csrf_exempt
def update_point(request):
    # POST 요청일 때
    if request.method == "POST":
        data = json.loads(
            request.body
        )  # dictinary 타입의 data {'uspoint': 0, 'user_id': '나는'}와 같은 값이 나옴

        # do something
        uspoint = data["uspoint"]  # dictionary의 key값을 줌으로 value를 가져옴
        user_id = data["user_id"]  # dictionary의 key값을 줌으로 value를 가져옴
        print(uspoint)  # 서버 실행창에서 확인할 수 있는 값
        print(data)  # 서버 실행창에서 확인할 수 있는 값
        user = User.objects.get(
            username=user_id
        )  # pointDB의 user필드의 user_id와 이름이 같은 행 가져옴
        user.pointuser = uspoint  # 이름이 동일한 행의 pointuser라는 필드에 새로운 값 할당
        user.save()  # DB저장

        context = {
            "result": data,
        }
        return JsonResponse(context)
    
def save_apt_info(request):
    citizen_detect = Apartdatabase.objects.filter(citizen=request.user)
    if not citizen_detect.exists():
        if request.method == 'POST':
            user = str(request.user)
            form = AptInfo(request.POST)
            
            if form.is_valid():
                    apt_info = form.save(commit=False)  # 폼 데이터를 데이터베이스에 저장하지 않음
                    apt_info.citizen = user  # citizen 필드에 사용자 객체 할당
                    apt_info.save() # 폼 데이터를 데이터베이스에 저장
                    return redirect('/cindex/')  # 원하는 성공 페이지로 이동
        form = AptInfo()
        return render(request, 'core/apart.html', {'form': form})
    else:
        return redirect('/cindex/')



def email_comp(request):
    if request.method == "GET":
        # GET 요청 시에만 랜덤 코드 생성
        phonenum = User.objects.get(username = request.user).phone
        random_code = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(6))
        request.session['random_code'] = random_code
        print(phonenum)
        
        #아래 코드를 주석 해제 하면 핸드폰으로 코드 문자가 옴 
        # messege = Client.messages.create(
        #     to="+8210"+phonenum ,  # 문자를 받을 번호  # ex) +82(내 번호)
        #     from_="twillophonenum",  # 회원가입시 발급받는 번호 
        #     body=random_code,  # 문자로 받을 내용
        # )
    else:
        random_code = request.session.get('random_code', '')

    if request.method == "POST":
        email = request.POST['email']
        if email == random_code:
            return redirect('/save_apt_info/')  # 인증 성공 시 리디렉션할 페이지
    return render(request, 'core/email.html', {'random_code': random_code})
