from crispy_forms.helper import FormHelper
from django import forms
from django.urls import reverse_lazy
from .models import User
from django.forms import TextInput
from crispy_forms.layout import Submit

class TelInput(TextInput):
    input_type = 'tel'

class LoginForm(forms.Form):

    email = forms.EmailField(widget=forms.EmailInput)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse_lazy('login')
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Login', css_class='btn-primary'))
    
        # 'hx-post': reverse_lazy('check_email')
        # 'hx-trigger': 'keyup changed delay:500ms'

class RegisterForm(forms.ModelForm):

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse_lazy('register')
        self.helper.form_method = 'POST'
        # self.helper.form_id = 'register-form'
        # self.helper.attrs = {
        #     'hx-post': reverse_lazy('register'),    
        #     'hx-target': '#register-form',
        #     'hx-swap': 'outerHTML',
        #     'hx-redirect': reverse_lazy('index')
        # }
        self.helper.add_input(Submit('submit', 'Register', css_class='btn-primary'))

    class Meta:
        model = User
        fields = ('name', 'email', 'phone')
        widgets = {
            'name': forms.TextInput(),
            'email': forms.EmailInput(),
            'phone': TelInput()
        }
    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 5:
            raise forms.ValidationError("Name is too short!")
        return name
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if len(email) <= 15:
            raise forms.ValidationError("Email is too short!")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(phone) < 10:
            raise forms.ValidationError(f"Phone number is {len(phone)} digits!")
        return phone
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError("Password should be of 8 characters!")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError("Password and Confirm Password does not match!")   

        if len(password2) < 8:
            raise forms.ValidationError("Confirm Password should be of 8 characters!")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
