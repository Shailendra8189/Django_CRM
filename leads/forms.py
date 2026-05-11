from django import forms
from .models import Lead, Category

# from agent.models import Agent
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField

User = get_user_model()


class LeadModelForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
            "first_name",
            "last_name",
            "age",
            "agent",
            "description",
            "phone_number",
            "email",
        )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        super(LeadModelForm, self).__init__(*args, **kwargs)
        if request.user.role == "agent":
            self.fields.pop("agent")


class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("type",)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")
        field_classes = {
            "username": UsernameField,
        }


class LeadCategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ("category",)

class LeadUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    age = forms.IntegerField(min_value=0)
    phone_number = forms.CharField(max_length=20)
    owner = forms.ModelChoiceField(queryset=User.objects.filter(role="organizer"), label="Select an Organizer")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "age", "phone_number", "owner")
        field_classes = {
            "username": UsernameField,
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "lead"
        if commit:
            user.save()
            Lead.objects.create(
                user=user,
                first_name=self.cleaned_data.get("first_name"),
                last_name=self.cleaned_data.get("last_name"),
                age=self.cleaned_data.get("age"),
                phone_number=self.cleaned_data.get("phone_number"),
                email=self.cleaned_data.get("email"),
                owner=self.cleaned_data.get("owner"),
            )
        return user

class LeadMessageForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ("msg",)

class LeadReplyForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ("reply",)
