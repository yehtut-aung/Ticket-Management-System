from django import forms
from .models import Ticket, TicketComment
from django.contrib.auth.models import User

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'assigned_to']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show agents in the assigned_to dropdown
        if user and user.profile.is_admin():
            self.fields['assigned_to'].queryset = User.objects.filter(profile__role='agent')
        else:
            self.fields['assigned_to'].widget = forms.HiddenInput()

class CommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }