from django import forms

class LoginForm(forms.Form):
    run = forms.CharField(max_length=12, label="RUN")
    contraseña = forms.CharField(widget=forms.PasswordInput, label="Contraseña")


