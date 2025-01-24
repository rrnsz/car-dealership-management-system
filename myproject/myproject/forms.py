from django import forms # type: ignore
from .models import Staff, Driver, User, Car

class StaffForm(forms.ModelForm):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Staff
        fields = ["full_name", "email", "phone_number", "password"]

    def save(self, commit=True):
        staff = super().save(commit=False)
        user = staff.user
        staff.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            staff.save()
        return staff

class DriverForm(forms.ModelForm):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)
    license_number = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Driver
        fields = ["full_name", "email", "phone_number", "license_number", "password"]

    def save(self, commit=True):
        driver = super().save(commit=False)
        user = driver.user
        driver.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            driver.save()
        return driver
    



class CarForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['category'].choices = Car.CATEGORY_CHOICES

    class Meta:
        model = Car
        fields = ["make", "model", "category", "description", "price", "stock", "image", "type", "transmission", "gas"]