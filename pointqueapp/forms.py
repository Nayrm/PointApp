from django import forms
from .models import PointPiece, User, RepairType, PartType, DC, Associate
from django.utils import timezone

class InitialPointPieceForm(forms.ModelForm):
    class Meta:
        model = PointPiece
        fields = ['lp', 'stock_type', 'route']

    def save(self, commit=True, selected_dc=None):
        instance = super(InitialPointPieceForm, self).save(commit=False)
        instance.line_time = timezone.now()  # Set the line_time upon saving
        if selected_dc:
            instance.dc = selected_dc
        if commit:
            instance.save()
        return instance

class CompletePointPieceForm(forms.Form):
    lp = forms.ModelChoiceField(
        queryset=PointPiece.objects.filter(status='Repair In Progress'),
        empty_label="Select LP",
        to_field_name="lp"
    )
    associate = forms.ModelChoiceField(queryset=Associate.objects.none())  # Initially empty queryset
    repair = forms.ModelMultipleChoiceField(
        queryset=RepairType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    part = forms.ModelMultipleChoiceField(
        queryset=PartType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        selected_dc = kwargs.pop('selected_dc', None)
        super(CompletePointPieceForm, self).__init__(*args, **kwargs)
        self.fields['lp'].label_from_instance = lambda obj: f"{obj.lp}"
        if selected_dc:
            self.fields['associate'].queryset = Associate.objects.filter(dc=selected_dc)


class DCSelectForm(forms.Form):
    dc = forms.ModelChoiceField(queryset=DC.objects.order_by('dc'), label="Select Distribution Center")
