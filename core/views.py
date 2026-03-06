# task_manager_frontend/core/views.py
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm, LoginForm, TaskForm

# The URL of your Backend API (Running on Port 8000)
API_BASE_URL = "http://127.0.0.1:8000/api/"

# --- AUTHENTICATION VIEWS ---

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Use json= instead of data= to talk to the REST API
            try:
                response = requests.post(f"{API_BASE_URL}register/", json=form.cleaned_data)
                if response.status_code == 201:
                    messages.success(request, "Registration successful! Please login.")
                    return redirect('login')
                else:
                    messages.error(request, "Registration failed. Username might be taken.")
            except requests.exceptions.ConnectionError:
                messages.error(request, "Backend Server is Offline!")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Use json= instead of data= to talk to the REST API
            try:
                response = requests.post(f"{API_BASE_URL}login/", json=form.cleaned_data)
                if response.status_code == 200:
                    data = response.json()
                    # Save Token and Username in Frontend Session
                    request.session['auth_token'] = data['token']
                    request.session['username'] = data['username']
                    return redirect('dashboard')
                else:
                    messages.error(request, "Invalid login credentials.")
            except requests.exceptions.ConnectionError:
                messages.error(request, "Backend Server is Offline!")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    request.session.flush() # Clears the token and logs the user out
    return redirect('login')

# --- TASK MANAGEMENT VIEWS (CRUD) ---

def dashboard(request):
    token = request.session.get('auth_token')
    if not token: 
        return redirect('login')

    # The 'Token' prefix is required for DRF TokenAuthentication
    headers = {'Authorization': f'Token {token}'}
    
    # 1. HANDLE POST (Creating a New Task)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            # CRITICAL FIX: Use json= instead of data= for REST APIs
            res = requests.post(f"{API_BASE_URL}tasks/", json=form.cleaned_data, headers=headers)
            if res.status_code == 201:
                messages.success(request, "Task saved to cloud!")
                return redirect('dashboard') 
            else:
                messages.error(request, "API Error: Could not save task.")
    else:
        form = TaskForm()

    # 2. HANDLE GET (Fetching Task List to Show on UI)
    try:
        response = requests.get(f"{API_BASE_URL}tasks/", headers=headers)
        if response.status_code == 200:
            tasks = response.json() # This is the data that fills your UI
        else:
            tasks = []
            messages.warning(request, "Could not retrieve tasks from API.")
    except Exception as e:
        tasks = []
        messages.error(request, f"Backend Connection Error: {e}")

    return render(request, 'dashboard.html', {'tasks': tasks, 'form': form})

def delete_task(request, pk):
    token = request.session.get('auth_token')
    if not token: 
        return redirect('login')
        
    headers = {'Authorization': f'Token {token}'}
    requests.delete(f"{API_BASE_URL}tasks/{pk}/", headers=headers)
    return redirect('dashboard')

def toggle_task(request, pk):
    token = request.session.get('auth_token')
    if not token: 
        return redirect('login')
        
    headers = {'Authorization': f'Token {token}'}
    
    try:
        # 1. First get the current task status from the API
        task_res = requests.get(f"{API_BASE_URL}tasks/{pk}/", headers=headers).json()
        
        # 2. Toggle status and PATCH it back using json=
        requests.patch(
            f"{API_BASE_URL}tasks/{pk}/", 
            json={'completed': not task_res['completed']}, 
            headers=headers
        )
    except Exception as e:
        messages.error(request, "Failed to update task.")
        
    return redirect('dashboard')