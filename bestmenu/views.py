from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from bestmenu.models import Category, Restaurant, UserProfile
from bestmenu.forms import CategoryForm, RestaurantForm, UserForm, UserProfileForm, EditUserForm, EditUserProfileForm
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from bestmenu.bing_search import run_query
from django.contrib.auth.models import User

def index(request):
    category_list = Category.objects.order_by('-likes', 'name')[:5]
    restaurant_list = Restaurant.objects.order_by('-views', 'title')[:5]
    context_dict = {'categories': category_list, 'restaurants': restaurant_list}

    # Try to obtain UserProfile if it exists
    current_user = request.user
    try:
        context_dict['user_profile'] = UserProfile.objects.get(user_id=current_user.id)
    except:
        pass

    # Cookie to track index visits
    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False
    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
        if (datetime.now() - last_visit_time).seconds > 0:
            visits = visits + 1
            reset_last_visit_time = True
    else:
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits

    response = render(request,'bestmenu/index.html', context_dict)

    return response

def about(request):
    context_dict = {'boldmessage': "Well, what can I say? I am well travelled..."}
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0
    context_dict['visits'] = count
    return render(request, 'bestmenu/about.html', context_dict)

def category(request, category_name_slug):
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
        query = request.POST['query']
        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        context_dict['category_name_url'] = category_name_slug
        restaurants = Restaurant.objects.filter(category=category).order_by('-views', 'title')
        context_dict['restaurants'] = restaurants
        context_dict['category'] = category
    except Category.DoesNotExist:
        #pass
        unslugify = category_name_slug.replace('-', ' ')
        context_dict['category_name'] = unslugify

    return render(request, 'bestmenu/category.html', context_dict)

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse('bestmenu:index'))
        else:
            #print(form.errors)
            pass
    else:
        form = CategoryForm()

    return render(request, 'bestmenu/add_category.html', {'form': form})

@login_required
def add_restaurant(request, category_name_slug):
    context_dict = {}
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            if cat:
                restaurant = form.save(commit=False)
                restaurant.category = cat
                restaurant.views = 0
                restaurant.save()
                return HttpResponseRedirect(reverse('bestmenu:category', args=(category_name_slug,)))
        else:
           #print(form.errors)
            context_dict['form_error'] = form.errors
    else:
        form = RestaurantForm()

    context_dict['form'] = form
    context_dict['category'] = cat
    context_dict['category_name_url'] = category_name_slug

    return render(request, 'bestmenu/add_restaurant.html', context_dict)

def register(request):
    registered = False
    context_dict = {}

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if user_form.is_valid() and profile_form.is_valid():
            if password == password2:
                user = user_form.save()

            # Hash the password with the set_password method.
                user.set_password(user.password)
                user.save()

            # Sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
                profile = profile_form.save(commit=False)
                profile.user = user

                if 'picture' in request.FILES:
                    profile.picture = request.FILES['picture']

                profile.save()
                registered = True
                
        else:
            #print(user_form.errors, profile_form.errors)
            context_dict['user_error'] = user_form.errors
            context_dict['profile_error'] = profile_form.errors

        if password != password2:
            context_dict['password_error'] = 'Passwords do not match.'

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    context_dict['user_form'] = user_form
    context_dict['profile_form'] = profile_form
    context_dict['registered'] = registered
    return render(request, 'bestmenu/register.html', context_dict)

def user_login(request):
    
    if request.method == 'POST':
            # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
            # because the request.POST.get('<variable>') returns None, if the value does not exist,
            # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's module to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('bestmenu:index')
            else:
                # An inactive account was used - no loggin in.
                return HttpResponse("Your Best Menu account is disabled.")
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'bestmenu/login.html', {})

@login_required
def restricted(request):
    return HttpResponse("Members only can see this")

@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('bestmenu:index')

def search(request):
    result_list = []
    if request.method == 'POST':
        query = request.POST['query']
        if query:
            # Run Bing function to get the results list
            result_list = run_query(query)

    return render(request, 'bestmenu/search.html', {'result_list': result_list})

def track_url(request):
    restaurant_id = None
    url = 'bestmenu:index'
    if request.method == 'GET':
        if 'restaurant_id' in request.GET:
            restaurant_id = request.GET['restaurant_id']
            try:
                restaurant = Restaurant.objects.get(id=restaurant_id)
                restaurant.views = restaurant.views + 1
                restaurant.save()
                url = restaurant.url
            except:
                pass

    return redirect(url)

def register_profile(request):
    current_user = request.user
    context_dict = {}
    try:
        context_dict['user_profile'] = UserProfile.objects.get(user_id=current_user.id)
    except:
        pass

    return render(request, 'bestmenu/profile_registration.html', context_dict)

@login_required
def profile(request):
    current_user = request.user
    context_dict = {}
    u = User.objects.get(username=current_user)

    try:
        up = UserProfile.objects.get(user=u)
        context_dict['userprofile'] = up
    except:
        pass

    context_dict['user'] = u

    if request.method == 'POST':
        user_form = EditUserForm(data=request.POST)
        profile_form = EditUserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            if request.POST.get('email'):
                u.email = request.POST.get('email')
                u.save()
            if request.POST.get('website'):
                try:
                    if not request.POST.get('website').startswith('http://'):
                        up.website = 'http://' + request.POST.get('website')
                    else:
                        up.website = request.POST.get('website')
                    up.save()
                except:
                    pass
            if 'picture' in request.FILES:
                up.picture = request.FILES['picture']
                up.save()
        else:
            #print(user_form.errors, profile_form.errors)
            context_dict['user_error'] = user_form.errors
            context_dict['profile_error'] = profile_form.errors

    return render(request, 'bestmenu/profile.html', context_dict)

@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()

    return HttpResponse(likes)

def get_category_list(max_results=0, contains=''):
    cat_list = []
    if contains:
        cat_list = Category.objects.filter(name__icontains=contains)
    else:
        cat_list = Category.objects.all().order_by('-likes', 'name')

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    return cat_list

def suggest_category(request):
    cat_list = []
    contains = ''
    if request.method == 'GET':
        contains = request.GET['suggestion']

    cat_list = get_category_list(0, contains)
    
    return render(request, 'bestmenu/category_list.html', {'cat_list': cat_list})

@login_required
def auto_add_restaurant(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            r = Restaurant.objects.get_or_create(category=category, title=title, url=url)
            restaurants = Restaurant.objects.filter(category=category).order_by('-views')
            context_dict['restaurants'] = restaurants

    return render(request, 'bestmenu/restaurant_list.html', context_dict)

def all_categories(request):
    category_list = Category.objects.order_by('name')
    context_dict = {'categories': category_list}

    return render(request, 'bestmenu/all_categories.html', context_dict)

def all_restaurants(request):
    restaurant_list = Restaurant.objects.order_by('title')
    context_dict = {'restaurants': restaurant_list}

    return render(request, 'bestmenu/all_restaurants.html', context_dict)
