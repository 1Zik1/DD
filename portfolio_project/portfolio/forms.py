import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import File, Teacher, Education, Experience, Qualification, Award, KnowledgeExchange, Discipline, Group, TeachingLoad, Student, Grade, Publication, Diploma, Coursework, Olympiad
from datetime import date
from django.contrib.contenttypes.models import ContentType

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'last_name', 'first_name', 'middle_name', 'birth_date',
            'email', 'phone', 'biography', 'interests',
            'teaching_problem', 'photo', 'category', 'certification_date'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'certification_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'interests': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'teaching_problem': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 123-45-67'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_phone(self):
        """Валидация формата телефона"""
        phone = self.cleaned_data.get('phone')
        if phone:
            cleaned_phone = re.sub(r'[^\d\+]', '', phone)
            
            # Проверяем, начинается ли с плюса
            if not cleaned_phone.startswith('+'):
                cleaned_phone = '+' + cleaned_phone
            
            # Проверяем длину
            if len(cleaned_phone) < 11 or len(cleaned_phone) > 15:
                raise ValidationError(_('Некорректная длина номера телефона'))
            
            return cleaned_phone
        return phone
    
    def clean(self):
        """Проверка дат"""
        cleaned_data = super().clean()
        birth_date = cleaned_data.get('birth_date')
        certification_date = cleaned_data.get('certification_date')
        
        # Проверка даты рождения
        if birth_date and birth_date > date.today():
            self.add_error('birth_date', _('Дата рождения не может быть в будущем'))
        
        # Проверка даты аттестации
        if certification_date and certification_date > date.today():
            self.add_error('certification_date', _('Дата аттестации не может быть в будущем'))
        
        # Проверка, что дата аттестации не раньше даты рождения
        if birth_date and certification_date and certification_date < birth_date:
            self.add_error('certification_date', _('Дата аттестации не может быть раньше даты рождения'))
        
        return cleaned_data

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
            'institution', 'specialization', 'degree', 
            'start_date', 'end_date', 'education_type'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'degree': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        """Проверка дат"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Проверка, что дата окончания не раньше даты начала
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', _('Дата окончания не может быть раньше даты начала'))
        
        return cleaned_data

# Форма для опыта работы
class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = [
            'organization', 'position', 'start_date', 
            'end_date', 'experience_type', 'description'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        """Проверка дат"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Проверка, что дата окончания не раньше даты начала
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', _('Дата окончания не может быть раньше даты начала'))
        
        return cleaned_data

# Форма для квалификации
class QualificationForm(forms.ModelForm):
    class Meta:
        model = Qualification
        fields = [
            'program', 'organization', 'issue_date', 
            'hours', 'certificate_number'
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'program': forms.TextInput(attrs={'class': 'form-control'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'certificate_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        """Проверка даты"""
        cleaned_data = super().clean()
        issue_date = cleaned_data.get('issue_date')
        
        # Проверка, что дата выдачи не в будущем
        if issue_date and issue_date > date.today():
            self.add_error('issue_date', _('Дата выдачи не может быть в будущем'))
        
        return cleaned_data

# Форма для наград
class AwardForm(forms.ModelForm):
    class Meta:
        model = Award
        fields = [
            'name', 'organization', 'received_date', 
            'level', 'description'
        ]
        widgets = {
            'received_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        """Проверка даты"""
        cleaned_data = super().clean()
        received_date = cleaned_data.get('received_date')
        
        # Проверка, что дата получения не в будущем
        if received_date and received_date > date.today():
            self.add_error('received_date', _('Дата получения не может быть в будущем'))
        
        return cleaned_data
    
# Форма для учебной нагрузки
class TeachingLoadForm(forms.ModelForm):
    class Meta:
        model = TeachingLoad
        fields = [
            'discipline', 'group', 'semester', 
            'year', 'lesson_type', 'hours', 'study_form'
        ]
        widgets = {
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'discipline': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'lesson_type': forms.Select(attrs={'class': 'form-control'}),
            'study_form': forms.Select(attrs={'class': 'form-control'}),
        }

# Форма для группы
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['number', 'specialty', 'course', 'admission_year', 'description']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'specialty': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.NumberInput(attrs={'class': 'form-control'}),
            'admission_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Форма для студента
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['last_name', 'first_name', 'middle_name', 'record_book_number', 'admission_date', 'dismissal_date', 'status']
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'record_book_number': forms.TextInput(attrs={'class': 'form-control'}),
            'admission_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dismissal_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

# Форма для дисциплины
class DisciplineForm(forms.ModelForm):
    class Meta:
        model = Discipline
        fields = [
            'name', 'cycle_code', 'lecture_hours', 'practice_hours', 
            'lab_hours', 'assessment_type', 'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'cycle_code': forms.TextInput(attrs={'class': 'form-control'}),
            'lecture_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'practice_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'lab_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'assessment_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Форма для публикации
class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = [
            'title', 'type', 'publisher', 'year', 
            'issn_isbn', 'url', 'description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'issn_isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year and (year < 1900 or year > date.today().year):
            raise ValidationError(_('Год должен быть между 1900 и текущим годом'))
        return year
    
# Форма для курсовой работы
class CourseworkForm(forms.ModelForm):
    class Meta:
        model = Coursework
        fields = [
            'student', 'discipline', 'topic', 'year', 
            'grade', 'submission_date'
        ]
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'discipline': forms.Select(attrs={'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'grade': forms.NumberInput(attrs={'class': 'form-control'}),
            'submission_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year and (year < 1900 or year > date.today().year):
            raise ValidationError(_('Год должен быть между 1900 и текущим годом'))
        return year

    def clean_grade(self):
        grade = self.cleaned_data.get('grade')
        if grade is not None and (grade < 2 or grade > 5):
            raise ValidationError(_('Оценка должна быть от 2 до 5'))
        return grade
    

# Форма для дипломной работы
class DiplomaForm(forms.ModelForm):
    class Meta:
        model = Diploma
        fields = [
            'student', 'topic', 'year', 
            'grade', 'abstract', 'defense_date'
        ]
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'grade': forms.NumberInput(attrs={'class': 'form-control'}),
            'abstract': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'defense_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year and (year < 1900 or year > date.today().year):
            raise ValidationError(_('Год должен быть между 1900 и текущим годом'))
        return year

    def clean_grade(self):
        grade = self.cleaned_data.get('grade')
        if grade is not None and (grade < 2 or grade > 5):
            raise ValidationError(_('Оценка должна быть от 2 до 5'))
        return grade
    
class OlympiadForm(forms.ModelForm):
    class Meta:
        model = Olympiad
        fields = [
            'student', 'name', 'level', 'place', 
            'year', 'event_date', 'description'
        ]
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'place': forms.NumberInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'event_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year and (year < 1900 or year > date.today().year):
            raise ValidationError(_('Год должен быть между 1900 и текущим годом'))
        return year

    def clean_place(self):
        place = self.cleaned_data.get('place')
        return place
    
class ObjectChoiceField(forms.ModelChoiceField):
    """Поле выбора объекта с кастомным отображением"""
    def label_from_instance(self, obj):
        if hasattr(obj, '__str__'):
            return str(obj)
        return f"{obj._meta.verbose_name} #{obj.pk}"

class FileForm(forms.ModelForm):
    
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(
            model__in=[
                'teacher', 'education', 'experience', 'qualification', 'award',
                'knowledgeexchange', 'discipline', 'group', 'teachingload',
                'student', 'grade', 'publication', 'diploma', 'coursework', 'olympiad'
            ]
        ),
        label='Тип объекта',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_content_type'}),
        empty_label="Выберите тип объекта"
    )

    object_id = forms.ModelChoiceField(
        queryset=None, 
        label='Объект',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_object_id'}),
        empty_label="Выберите объект",
        required=True 
    )
    
    description = forms.CharField(
        label='Описание (необязательно)',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta:
        model = File
        fields = ['file_path'] 
        widgets = {
            'file_path': forms.FileInput(attrs={
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx',
                'class': 'form-control'
            }),
        }
        labels = {
            'file_path': 'Выберите файл',
        }

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)

        self.fields['object_id'].queryset = self.get_initial_object_queryset()
        
        if 'content_type' in self.data or (self.instance and self.instance.pk and self.instance.content_type):
            
            content_type = None
            if 'content_type' in self.data:
                 try:
                     content_type_id = int(self.data.get('content_type'))
                     content_type = ContentType.objects.get_for_id(content_type_id)
                 except (ValueError, TypeError, ContentType.DoesNotExist):
                     content_type = None
            elif self.instance and self.instance.pk and self.instance.content_type:
                 content_type = self.instance.content_type
            
            if content_type:
                object_queryset = self.get_objects_for_content_type(content_type)
                self.fields['object_id'].queryset = object_queryset
                
                if 'object_id' in self.data:
                    try:
                        obj_id = int(self.data['object_id'])
                        self.fields['object_id'].initial = obj_id
                    except (ValueError, TypeError):
                        pass
                elif self.instance and self.instance.pk and self.instance.object_id:
                    try:
                        obj = object_queryset.get(pk=self.instance.object_id)
                        self.fields['object_id'].initial = obj
                    except object_queryset.model.DoesNotExist:
                        pass

    def get_initial_object_queryset(self):
        """Возвращает пустой queryset для начальной инициализации"""
        return Teacher.objects.none() 

    def get_objects_for_content_type(self, content_type):
        """Возвращает queryset объектов для данного content_type, отфильтрованный по пользователю"""
        model_class = content_type.model_class()
        queryset = model_class.objects.all()

        if self.teacher and model_class:
            if hasattr(model_class, 'teacher'):
                queryset = queryset.filter(teacher=self.teacher)
            elif model_class == Teacher: 
                queryset = queryset.filter(pk=self.teacher.pk)
            
        return queryset

    def clean_file_path(self):
        file = self.cleaned_data.get('file_path')
        if file:
            max_size = 10 * 1024 * 1024 # 10MB
            if file.size > max_size:
                raise forms.ValidationError(f'Размер файла не должен превышать {max_size / (1024*1024):.1f} МБ.')
        return file

    def clean(self):
        cleaned_data = super().clean()
        content_type = cleaned_data.get('content_type')
        object_instance = cleaned_data.get('object_id') 
        if content_type and not object_instance:
            raise forms.ValidationError("Пожалуйста, выберите объект.")

        if object_instance:
            cleaned_data['object_id_value'] = object_instance.pk
            cleaned_data['content_object'] = object_instance
        else:
             cleaned_data['object_id_value'] = None
             cleaned_data['content_object'] = None

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        content_type = self.cleaned_data.get('content_type')
        object_instance = self.cleaned_data.get('content_object')
        
        if content_type:
            instance.content_type = content_type
        if object_instance:
            instance.object_id = object_instance.pk
        
        if not instance.description:
             instance.description = self.cleaned_data.get('description', '')

        if commit:
            instance.save()
        return instance