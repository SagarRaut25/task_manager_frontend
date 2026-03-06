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
            # Send data to Backend /api/register/
            try:
                response = requests.post(f"{API_BASE_URL}register/", data=form.cleaned_data)
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
            # Send credentials to Backend /api/login/
            try:
                response = requests.post(f"{API_BASE_URL}login/", data=form.cleaned_data)
                if response.status_code == 200:
                    data = response.json()
                    # Save Token and Username in Frontend Session
                    request.session['auth_token'] = data['token']
                    request.session['username'] = data['username']
                    return redirect('dashboard')
                else:
                    messages.error(request, "Invalid username or password.")
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

    headers = {'Authorization': f'Token {token}'}
    
    # Handle Task Creation
    form = TaskForm()
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            requests.post(f"{API_BASE_URL}tasks/", data=form.cleaned_data, headers=headers)
            return redirect('dashboard')

    # GET all tasks from Backend to display
    try:
        response = requests.get(f"{API_BASE_URL}tasks/", headers=headers)
        tasks = response.json() if response.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        tasks = []
        messages.error(request, "Could not connect to Backend to fetch tasks.")

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
    
    # 1. First get the current task status from the API
    try:
        task_res = requests.get(f"{API_BASE_URL}tasks/{pk}/", headers=headers).json()
        # 2. Toggle the 'completed' status and PATCH it back to Backend
        requests.patch(
            f"{API_BASE_URL}tasks/{pk}/", 
            data={'completed': not task_res['completed']}, 
            headers=headers
        )
    except Exception as e:
        messages.error(request, "Failed to update task.")
        
    return redirect('dashboard')