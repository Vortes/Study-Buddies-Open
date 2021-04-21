from django import forms
from .models import Post, Tag


class SearchForm(forms.Form):
    search = forms.CharField(label="search", max_length=50)


class CreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)
        self.fields["content"].label = "Group Link"

    class Meta:
        model = Post

        fields = [
            "title",
            "content",
            "subject",
            "max_buddies",
            "quiet_tag",
            "camera_tag",
        ]
