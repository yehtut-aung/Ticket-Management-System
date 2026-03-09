from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    # Role choices - Admin is excluded (only assign via admin panel)
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('agent', 'Support Agent'),
    )
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        required=True,
        label='Register as',
        widget=forms.RadioSelect,  # Use radio buttons for better UX
        initial='customer'
    )
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role']
    
    def save(self, commit=True):
        # Create user but don't save yet
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create or update user profile with selected role
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            profile.save()
        
        return user