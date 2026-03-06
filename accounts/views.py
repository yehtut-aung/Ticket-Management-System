from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm 

def login_view(request):
    if request.method == 'POST':

        # Get Username and Password From Form
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:

            # Login Successful
            login(request, user)
            messages.success(request, f'Welcome Back, {username}!')
            return redirect('dashboard')
        
        else:
            # Login Failed
            messages.error(request,'Invalid username or password')

    # If GET request or login failed, show login page
    return render(request,'accounts/login.html')


def signup_view(request):
    print("=" * 50)
    print("Signup view called")
    print(f"Request method: {request.method}")
    
    if request.method == 'POST':
        print("Processing POST request")
        form = UserCreationForm(request.POST)
        print(f"Form is valid: {form.is_valid()}")
        
        if form.is_valid():
            print("Form is valid - saving user")
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            print("Redirecting to dashboard")
            return redirect('dashboard')
        else:
            print(f"Form errors: {form.errors}")
            # This will continue to the render below
    else:
        print("GET request - creating empty form")
        form = UserCreationForm()
    
    print("Rendering signup template")
    # Make sure this line is NOT indented and is at the same level as the function
    return render(request, 'accounts/signup.html', {'form': form})
    

# Logout
def logout_view(request):
    logout(request)
    messages.success(request, ' You have been logged out successfully.')
    return redirect('login')





