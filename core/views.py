import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm, TaskForm  # Imported correctly now

BACKEND_API_URL = "http://127.0.0.1:8000/api/"

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Calling the Backend on port 8000
            try:
                api_response = requests.post(
                    f"{BACKEND_API_URL}login/", 
                    data=form.cleaned_data
                )
                
                if api_response.status_code == 200:
                    data = api_response.json()
                    # Store Token in Frontend Session
                    request.session['auth_token'] = data['token']
                    request.session['username'] = data['username']
                    return redirect('dashboard')
                else:
                    messages.error(request, "Invalid Credentials on Backend Server")
            except requests.exceptions.ConnectionError:
                messages.error(request, "Backend Server (8000) is Offline!")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def dashboard(request):
    token = request.session.get('auth_token')
    if not token:
        return redirect('login')

    headers = {'Authorization': f'Token {token}'}
    try:
        response = requests.get(f"{BACKEND_API_URL}tasks/", headers=headers)
        tasks = response.json() if response.status_code == 200 else []
    except:
        tasks = []
    
    return render(request, 'dashboard.html', {'tasks': tasks})

def logout_view(request):
    request.session.flush()
    return redirect('login')