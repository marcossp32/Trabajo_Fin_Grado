from django import forms
from .models import StartConfig, ScheduleConfig, PriorityConfig, EventConfig

class StartConfigForm(forms.ModelForm):
    LANGUAGE_CHOICES = [
        ('es', 'Español'),
        ('en', 'Inglés'),
        ('fr', 'Francés'),
        ('de', 'Alemán'),
    ]
    
   
    language = forms.ChoiceField(
        choices=LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'input-box'}),
        required=False
    )
    
    class Meta:
        model = StartConfig
        fields = ['full_name', 'charge', 'language', 'details']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'input-box'}),
            'charge': forms.TextInput(attrs={'class': 'input-box'}),
            'details': forms.Textarea(attrs={'class': 'input-box'}),
        }



class ScheduleConfigForm(forms.ModelForm):
    DAY_CHOICES = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]
    
    no_meetings_days = forms.MultipleChoiceField(
        choices=DAY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'input-checkbox'}),
        required=False
    )


    class Meta:
        model = ScheduleConfig
        fields = ['work_hours_from', 'work_hours_to', 'no_meetings_hours_from', 'no_meetings_hours_to', 'no_meetings_days', 'tolerance']
        widgets = {
            'work_hours_from': forms.TimeInput(attrs={'class': 'input-box', 'type': 'time'}),
            'work_hours_to': forms.TimeInput(attrs={'class': 'input-box', 'type': 'time'}),
            'no_meetings_hours_from': forms.TimeInput(attrs={'class': 'input-box', 'type': 'time'}),
            'no_meetings_hours_to': forms.TimeInput(attrs={'class': 'input-box', 'type': 'time'}),
            'tolerance': forms.NumberInput(attrs={'class': 'input-box'}),
        }
        labels = {
            'tolerance': 'Tolerance (minutes)',
        }

    def __init__(self, *args, **kwargs):
        super(ScheduleConfigForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.no_meetings_days:
            # Convertimos la cadena separada por comas de la base de datos en una lista
            self.initial['no_meetings_days'] = self.instance.no_meetings_days.split(',')



    def save(self, commit=True):
        instance = super(ScheduleConfigForm, self).save(commit=False)
        
        # Convertimos la lista de días seleccionados en una cadena separada por comas
        instance.no_meetings_days = ','.join(self.cleaned_data.get('no_meetings_days', []))
        
        if commit:
            instance.save()
        return instance


class PriorityConfigForm(forms.ModelForm):
    DAY_CHOICES = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]
    
    priority_days = forms.MultipleChoiceField(
        choices=DAY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'input-checkbox'}),
        required=False
    )
    
    class Meta:
        model = PriorityConfig
        fields = ['priority_issues', 'priority_people', 'priority_hours_from', 'priority_hours_to', 'priority_days']
        widgets = {
            'priority_issues': forms.TextInput(attrs={'class': 'input-box'}),
            'priority_people': forms.TextInput(attrs={'class': 'input-box'}),
            'priority_hours_from': forms.TimeInput(attrs={'class': 'input-box', 'type': 'time'}),
            'priority_hours_to': forms.TimeInput(attrs={'class': 'input-box', 'type': 'time'}),
        }


    def __init__(self, *args, **kwargs):
        super(PriorityConfigForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.priority_days:
            # Convertimos la cadena separada por comas de la base de datos en una lista
            self.initial['priority_days'] = self.instance.priority_days.split(',')

    def save(self, commit=True):
        instance = super(PriorityConfigForm, self).save(commit=False)
        
        # No necesitas join en campos de tiempo, ya que son valores únicos
        instance.priority_hours_from = self.cleaned_data.get('priority_hours_from')
        instance.priority_hours_to = self.cleaned_data.get('priority_hours_to')
        
        # Para 'priority_days', que es un campo de tipo MultipleChoiceField, sí puedes usar join
        instance.priority_days = ','.join(self.cleaned_data.get('priority_days', []))
        
        if commit:
            instance.save()
        return instance



class EventConfigForm(forms.ModelForm):
    class Meta:
        model = EventConfig
        fields = ['meeting_duration', 'notify_meeting', 'propose_meeting', 'meeting_limit']
        widgets = {
            'meeting_duration': forms.NumberInput(attrs={'class': 'input-box'}),
            'notify_meeting': forms.CheckboxInput(attrs={'class': 'custom-checkbox', 'id': 'notifyMeeting'}),
            'propose_meeting': forms.CheckboxInput(attrs={'class': 'custom-checkbox', 'id': 'proposeMeeting'}),
            'meeting_limit': forms.NumberInput(attrs={'class': 'input-box'}),
        }


class CreateMeetingForm(forms.Form):
    meeting_name = forms.CharField(
        label='Meeting Name', 
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'input-box'})
    )
    meeting_day = forms.DateField(
        label='Meeting Day', 
        required=True, 
        widget=forms.SelectDateWidget(attrs={'class': 'input-box'})
    )
    meeting_start_time = forms.TimeField(
        label='Start Time', 
        required=True, 
        widget=forms.TimeInput(format='%H:%M', attrs={'class': 'input-box', 'type': 'time'})
    )
    meeting_duration = forms.IntegerField(
        label='Duration (minutes)', 
        required=True, 
        widget=forms.NumberInput(attrs={'class': 'input-box'})
    )
    meeting_participants = forms.CharField(
        label='Participants', 
        help_text='Separados por comas', 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'input-box'})
    )
    meeting_description = forms.CharField(
        label='Description', 
        widget=forms.Textarea(attrs={'class': 'input-box'}), 
        required=False
    )
    meeting_file = forms.FileField(
        label='Add file', 
        required=False, 
        widget=forms.ClearableFileInput(attrs={'class': 'file-input', 'id':'meeting_file'})
    )


class SendMessageForm(forms.Form):
    mensaje_email = forms.EmailField(
        label='Email receiver', 
        widget=forms.EmailInput(attrs={'class': 'input-box', 'multiple': 'multiple'}), 
        required=True
    )
    mensaje_subject = forms.CharField(
        label='Subjet', 
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'input-box'})
    )
    mensaje_description = forms.CharField(
        label='Brief description', 
        widget=forms.Textarea(attrs={'class': 'input-box'}), 
        required=True
    )
    mensaje_file = forms.FileField(
        label='Add file', 
        required=False, 
        widget=forms.ClearableFileInput(attrs={'class': 'input-box'})
    )
