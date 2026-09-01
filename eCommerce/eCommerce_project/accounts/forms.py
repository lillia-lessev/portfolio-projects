from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class RegisterForm(UserCreationForm):
    """
    Custom registration form that also captures the user type
    (Vendor or Buyer) and email address.
    """
    name = forms.CharField(
        max_length=100,
        required=True,
        label="Full Name",
        help_text=""
        )
    
    email = forms.EmailField(
        required=True, 
        label="Email Address",
        help_text=""
        )
    
    user_type = forms.ChoiceField(
        choices=Profile.USER_TYPES,
        label="Account Type",
        help_text=""
    )

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2', 'user_type']

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remove help texts
        self.fields['username'].help_text = "Be sure to choose a username that you will remember, as you will need it to login."
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        
        # Labels
        self.fields['username'].label = "Username"
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm Password"
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email
    
    def save(self, commit=True):
        """
        Save the User and also set the related Profile.user_type.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']
        if commit:
            user.save()
            # Update the profile that was automatically created by the signal
            user.profile.user_type = self.cleaned_data['user_type']
            user.profile.save()
        return user