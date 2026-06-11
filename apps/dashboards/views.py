from django.shortcuts import render, redirect

def home(request):
    if request.GET.get('all_modules') == '1':
        if request.user.is_authenticated and request.user.is_superuser:
            request.session['show_all_modules'] = True
        return redirect('home')
    elif request.GET.get('erm') == '1':
        if 'show_all_modules' in request.session:
            del request.session['show_all_modules']
        return redirect('home')
        
    return render(request, 'dashboards/home.html')
