from django.forms import IntegerField
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.db.models import Q, Avg, Count, Subquery, OuterRef, Sum, F, Case, When, FloatField
from django.db.models.functions import ExtractYear, Now
from django.utils.timezone import now
from django.views.decorators.cache import cache_page
from django.db.models import ExpressionWrapper, F, DurationField
from django.db.models.functions import ExtractDay
import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date
import os
from .forms import FileForm
from django.contrib import messages
import logging
from django.views.decorators.http import require_POST
import json
logger = logging.getLogger(__name__)

@login_required
@cache_page(60 * 15)  # Кэшировать на 15 минут
def home(request):
    # Получаем текущего педагога
    try:
        teacher = Teacher.objects.select_related('user').prefetch_related(
            'educations', 
            'experiences',
            'qualifications',
            'awards'
        ).get(user=request.user)
    except Teacher.DoesNotExist:
        teacher = None
    
    # Подготовка данных для отображения в шаблоне
    context = {
        'teacher': teacher,
    }
    
    # Если педагог существует, получаем дополнительные данные
    if teacher:
        # Получаем данные из представления teacher_portfolio
        try:
            # проверка, что модель TeacherPortfolio импортирована
            from .models import TeacherPortfolio
            portfolio = TeacherPortfolio.objects.get(teacher_id=teacher.id)
            context['portfolio'] = portfolio
        except (NameError, ImportError, TeacherPortfolio.DoesNotExist):
            # Образование
            education_count = Education.objects.filter(teacher=teacher).count()
            
            # Общий стаж - оптимизированный расчет через агрегацию
            experiences = Experience.objects.filter(
                teacher=teacher, 
                experience_type='General'
            ).annotate(
                duration=ExpressionWrapper(
                    Now() - F('start_date'),
                    output_field=DurationField()
                )
            )
            
            total_days = experiences.aggregate(
                total=ExpressionWrapper(
                    Sum(ExtractDay('duration')),
                    output_field=IntegerField()
                )
            )['total'] or 0
            total_years = total_days // 365
            
            context.update({
                'education_count': education_count,
                'general_experience': total_years,
            })
    
    return render(request, 'portfolio/home.html', context)

@login_required
def profile(request):
    """Просмотр и редактирование профиля педагога"""
    
    # Получаем профиль педагога
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = None
    
    # проверка, если пользователь хочет редактировать или удалить фото
    edit_mode = 'edit' in request.GET
    
    if request.method == 'POST':
        # Удаление фото
        if 'delete_photo' in request.POST and teacher:
            teacher.photo = None
            teacher.save()
            return redirect('portfolio:profile')
        # Сохранение формы редактирования
        elif edit_mode:
            form = TeacherForm(request.POST, request.FILES, instance=teacher)
            if form.is_valid():
                teacher = form.save(commit=False)
                if not teacher.user_id:
                    teacher.user = request.user
                teacher.save()
                return redirect('portfolio:profile')
    elif edit_mode and teacher:
        form = TeacherForm(instance=teacher)
    else:
        form = None
    
    return render(request, 'portfolio/profile.html', {
        'teacher': teacher,
        'form': form,
        'edit_mode': edit_mode,
    })

@login_required
def education_list(request):
    """Список образования для текущего педагога"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    educations = teacher.educations.all().order_by('-end_date', '-start_date')
    
    # Определяем список типов файлов, которые являются изображениями
    image_file_types = ['JPG', 'JPEG', 'PNG'] # <-- Добавлено
    
    return render(request, 'portfolio/education_list.html', {
        'teacher': teacher,
        'educations': educations,
        'image_file_types': image_file_types # <-- Передаём в контекст
    })

@login_required
def education_create(request):
    """Создание новой записи об образовании"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.teacher = teacher
            education.save()
            return redirect('portfolio:education_list')
    else:
        form = EducationForm()
    
    return render(request, 'portfolio/education_form.html', {
        'form': form,
        'title': 'Добавить образование',
        'button_text': 'Сохранить'
    })

@login_required
def education_edit(request, pk):
    """Редактирование существующей записи об образовании"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    education = get_object_or_404(Education, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            return redirect('portfolio:education_list')
    else:
        form = EducationForm(instance=education)
    
    return render(request, 'portfolio/education_form.html', {
        'form': form,
        'title': 'Редактировать образование',
        'button_text': 'Обновить'
    })

@login_required
def education_delete(request, pk):
    """Удаление записи об образовании"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    education = get_object_or_404(Education, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        education.delete()
        return redirect('portfolio:education_list')
    
    return render(request, 'portfolio/education_confirm_delete.html', {
        'education': education
    })

# === Опыт работы ===
@login_required
def experience_list(request):
    """Список опыта работы для текущего педагога"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    experiences = teacher.experiences.all().order_by('-end_date', '-start_date')
    return render(request, 'portfolio/experience_list.html', {
        'teacher': teacher,
        'experiences': experiences
    })

@login_required
def experience_create(request):
    """Создание новой записи об опыте работы"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.teacher = teacher
            experience.save()
            return redirect('portfolio:experience_list')
    else:
        form = ExperienceForm()
    
    return render(request, 'portfolio/experience_form.html', {
        'form': form,
        'title': 'Добавить опыт работы',
        'button_text': 'Сохранить'
    })

@login_required
def experience_edit(request, pk):
    """Редактирование существующей записи об опыте работы"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    experience = get_object_or_404(Experience, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            return redirect('portfolio:experience_list')
    else:
        form = ExperienceForm(instance=experience)
    
    return render(request, 'portfolio/experience_form.html', {
        'form': form,
        'title': 'Редактировать опыт работы',
        'button_text': 'Обновить'
    })

@login_required
def experience_delete(request, pk):
    """Удаление записи об опыте работы"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    experience = get_object_or_404(Experience, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        experience.delete()
        return redirect('portfolio:experience_list')
    
    return render(request, 'portfolio/experience_confirm_delete.html', {
        'experience': experience
    })

# === Квалификация ===
@login_required
def qualification_list(request):
    """Список квалификации для текущего педагога"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    qualifications = teacher.qualifications.all().order_by('-issue_date')
    return render(request, 'portfolio/qualification_list.html', {
        'teacher': teacher,
        'qualifications': qualifications
    })

@login_required
def qualification_create(request):
    """Создание новой записи о квалификации"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    if request.method == 'POST':
        form = QualificationForm(request.POST)
        if form.is_valid():
            qualification = form.save(commit=False)
            qualification.teacher = teacher
            qualification.save()
            return redirect('portfolio:qualification_list')
    else:
        form = QualificationForm()
    
    return render(request, 'portfolio/qualification_form.html', {
        'form': form,
        'title': 'Добавить квалификацию',
        'button_text': 'Сохранить'
    })

@login_required
def qualification_edit(request, pk):
    """Редактирование существующей записи о квалификации"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    qualification = get_object_or_404(Qualification, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        form = QualificationForm(request.POST, instance=qualification)
        if form.is_valid():
            form.save()
            return redirect('portfolio:qualification_list')
    else:
        form = QualificationForm(instance=qualification)
    
    return render(request, 'portfolio/qualification_form.html', {
        'form': form,
        'title': 'Редактировать квалификацию',
        'button_text': 'Обновить'
    })

@login_required
def qualification_delete(request, pk):
    """Удаление записи о квалификации"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    qualification = get_object_or_404(Qualification, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        qualification.delete()
        return redirect('portfolio:qualification_list')
    
    return render(request, 'portfolio/qualification_confirm_delete.html', {
        'qualification': qualification
    })

# === Награды ===
@login_required
def award_list(request):
    """Список наград для текущего педагога"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    awards = teacher.awards.all().order_by('-received_date')
    return render(request, 'portfolio/award_list.html', {
        'teacher': teacher,
        'awards': awards
    })

@login_required
def award_create(request):
    """Создание новой записи о награде"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    if request.method == 'POST':
        form = AwardForm(request.POST)
        if form.is_valid():
            award = form.save(commit=False)
            award.teacher = teacher
            award.save()
            return redirect('portfolio:award_list')
    else:
        form = AwardForm()
    
    return render(request, 'portfolio/award_form.html', {
        'form': form,
        'title': 'Добавить награду',
        'button_text': 'Сохранить'
    })

@login_required
def award_edit(request, pk):
    """Редактирование существующей записи о награде"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    award = get_object_or_404(Award, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        form = AwardForm(request.POST, instance=award)
        if form.is_valid():
            form.save()
            return redirect('portfolio:award_list')
    else:
        form = AwardForm(instance=award)
    
    return render(request, 'portfolio/award_form.html', {
        'form': form,
        'title': 'Редактировать награду',
        'button_text': 'Обновить'
    })

@login_required
def award_delete(request, pk):
    """Удаление записи о награде"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    award = get_object_or_404(Award, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        award.delete()
        return redirect('portfolio:award_list')
    
    return render(request, 'portfolio/award_confirm_delete.html', {
        'award': award
    })

# === УЧЕБНАЯ НАГРУЗКА ===
@login_required
def teaching_load_list(request):
    """Список учебной нагрузки педагога"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    teaching_loads = teacher.teaching_loads.all().select_related('discipline', 'group').order_by('-year', '-semester')
    return render(request, 'portfolio/teaching_load_list.html', {
        'teacher': teacher,
        'teaching_loads': teaching_loads
    })

@login_required
def teaching_load_create(request):
    """Создание новой учебной нагрузки"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    if request.method == 'POST':
        form = TeachingLoadForm(request.POST)
        if form.is_valid():
            teaching_load = form.save(commit=False)
            teaching_load.teacher = teacher
            teaching_load.save()
            return redirect('portfolio:teaching_load_list')
    else:
        form = TeachingLoadForm()
    
    return render(request, 'portfolio/teaching_load_form.html', {
        'form': form,
        'title': 'Добавить учебную нагрузку',
        'button_text': 'Сохранить'
    })

@login_required
def teaching_load_edit(request, pk):
    """Редактирование учебной нагрузки"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    teaching_load = get_object_or_404(TeachingLoad, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        form = TeachingLoadForm(request.POST, instance=teaching_load)
        if form.is_valid():
            form.save()
            return redirect('portfolio:teaching_load_list')
    else:
        form = TeachingLoadForm(instance=teaching_load)
    
    return render(request, 'portfolio/teaching_load_form.html', {
        'form': form,
        'title': 'Редактировать учебную нагрузку',
        'button_text': 'Обновить'
    })

@login_required
def teaching_load_delete(request, pk):
    """Удаление учебной нагрузки"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    teaching_load = get_object_or_404(TeachingLoad, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        teaching_load.delete()
        return redirect('portfolio:teaching_load_list')
    
    return render(request, 'portfolio/teaching_load_confirm_delete.html', {
        'teaching_load': teaching_load
    })

# === ДИСЦИПЛИНЫ ===
@login_required
def discipline_list(request):
    """Список всех дисциплин"""
    disciplines = Discipline.objects.all().order_by('name')
    return render(request, 'portfolio/discipline_list.html', {
        'disciplines': disciplines
    })

@login_required
def discipline_create(request):
    """Создание новой дисциплины"""
    if request.method == 'POST':
        form = DisciplineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('portfolio:discipline_list')
    else:
        form = DisciplineForm()
    
    return render(request, 'portfolio/discipline_form.html', {
        'form': form,
        'title': 'Создать дисциплину',
        'button_text': 'Создать'
    })

@login_required
def discipline_edit(request, pk):
    """Редактирование дисциплины"""
    discipline = get_object_or_404(Discipline, pk=pk)
    
    if request.method == 'POST':
        form = DisciplineForm(request.POST, instance=discipline)
        if form.is_valid():
            form.save()
            return redirect('portfolio:discipline_list')
    else:
        form = DisciplineForm(instance=discipline)
    
    return render(request, 'portfolio/discipline_form.html', {
        'form': form,
        'title': 'Редактировать дисциплину',
        'button_text': 'Обновить'
    })

@login_required
def discipline_delete(request, pk):
    """Удаление дисциплины"""
    discipline = get_object_or_404(Discipline, pk=pk)
    
    if request.method == 'POST':
        discipline.delete()
        return redirect('portfolio:discipline_list')
    
    return render(request, 'portfolio/discipline_confirm_delete.html', {
        'discipline': discipline
    })

@login_required
def my_disciplines(request):
    """Список дисциплин, которые преподаёт текущий педагог"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    # Получаем уникальные дисциплины из нагрузки педагога
    disciplines = Discipline.objects.filter(
        teaching_loads__teacher=teacher  
    ).distinct().order_by('name')
    
    return render(request, 'portfolio/my_disciplines.html', {
        'teacher': teacher,
        'disciplines': disciplines
    })

# === ГРУППЫ СТУДЕНТОВ ===
@login_required
def group_list(request):
    """Список групп"""
    groups = Group.objects.all().order_by('course', 'number')
    return render(request, 'portfolio/group_list.html', {'groups': groups})

@login_required
def group_create(request):
    """Создание новой группы"""
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('portfolio:group_list')
    else:
        form = GroupForm()
    
    return render(request, 'portfolio/group_form.html', {
        'form': form,
        'title': 'Создать группу',
        'button_text': 'Создать'
    })

@login_required
def group_edit(request, pk):
    """Редактирование группы"""
    group = get_object_or_404(Group, pk=pk)
    
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('portfolio:group_list')
    else:
        form = GroupForm(instance=group)
    
    return render(request, 'portfolio/group_form.html', {
        'form': form,
        'title': 'Редактировать группу',
        'button_text': 'Обновить'
    })

@login_required
def group_delete(request, pk):
    """Удаление группы"""
    group = get_object_or_404(Group, pk=pk)
    
    if request.method == 'POST':
        group.delete()
        return redirect('portfolio:group_list')
    
    return render(request, 'portfolio/group_confirm_delete.html', {'group': group})

@login_required
def group_detail(request, pk):
    """Детали группы и список студентов"""
    group = get_object_or_404(Group, pk=pk)
    students = group.students.all().order_by('last_name', 'first_name')
    
    return render(request, 'portfolio/group_detail.html', {
        'group': group,
        'students': students
    })


# УСПЕВАЕМОСТЬ СТУДЕНТОВ 
@login_required
def grades_list(request):
    """Список оценок студентов"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    # Получаем оценки педагога
    grades = teacher.grades.all().select_related('student', 'discipline', 'student__group').order_by('-date')
    
    return render(request, 'portfolio/grades_list.html', {
        'teacher': teacher,
        'grades': grades
    })


#  ПУБЛИКАЦИИ 
@login_required
def publication_list(request):
    """Список публикаций педагога"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    publications = teacher.publications.all().order_by('-year')
    return render(request, 'portfolio/publication_list.html', {
        'teacher': teacher,
        'publications': publications
    })

@login_required
def publication_create(request):
    """Создание новой публикации"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    if request.method == 'POST':
        form = PublicationForm(request.POST)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.teacher = teacher
            publication.save()
            return redirect('portfolio:publication_list')
    else:
        form = PublicationForm()
    
    return render(request, 'portfolio/publication_form.html', {
        'form': form,
        'title': 'Добавить публикацию',
        'button_text': 'Сохранить'
    })

@login_required
def publication_edit(request, pk):
    """Редактирование публикации"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return redirect('portfolio:profile')
    
    publication = get_object_or_404(Publication, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        form = PublicationForm(request.POST, instance=publication)
        if form.is_valid():
            form.save()
            return redirect('portfolio:publication_list')
    else:
        form = PublicationForm(instance=publication)
    
    return render(request, 'portfolio/publication_form.html', {
        'form': form,
        'title': 'Редактировать публикацию',
        'button_text': 'Обновить'
    })

@login_required
def publication_delete(request, pk):
    """Удаление публикации"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return redirect('portfolio:profile')
    
    publication = get_object_or_404(Publication, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        publication.delete()
        return redirect('portfolio:publication_list')
    
    return render(request, 'portfolio/publication_confirm_delete.html', {
        'publication': publication
    })


#  КУРСОВЫЕ РАБОТЫ 
@login_required
def coursework_list(request):
    """Список курсовых работ педагога"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    courseworks = teacher.courseworks.all().select_related('student', 'discipline').order_by('-year')
    return render(request, 'portfolio/coursework_list.html', {
        'teacher': teacher,
        'courseworks': courseworks
    })

@login_required
def coursework_create(request):
    """Создание новой курсовой работы"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    if request.method == 'POST':
        form = CourseworkForm(request.POST)
        if form.is_valid():
            coursework = form.save(commit=False)
            coursework.teacher = teacher 
            coursework.save()
            return redirect('portfolio:coursework_list')
    else:
        form = CourseworkForm() 
    return render(request, 'portfolio/coursework_form.html', {
        'form': form,
        'title': 'Добавить курсовую работу',
        'button_text': 'Сохранить'
    })

@login_required
def coursework_edit(request, pk):
    """Редактирование курсовой работы"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return redirect('portfolio:profile')
    
    coursework = get_object_or_404(Coursework, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        form = CourseworkForm(request.POST, instance=coursework)
        if form.is_valid():
            form.save()
            return redirect('portfolio:coursework_list')
    else:
        form = CourseworkForm(instance=coursework)
    
    return render(request, 'portfolio/coursework_form.html', {
        'form': form,
        'title': 'Редактировать курсовую работу',
        'button_text': 'Обновить'
    })

@login_required
def coursework_delete(request, pk):
    """Удаление курсовой работы"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return redirect('portfolio:profile')
    
    coursework = get_object_or_404(Coursework, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        coursework.delete()
        return redirect('portfolio:coursework_list')
    
    return render(request, 'portfolio/coursework_confirm_delete.html', {
        'coursework': coursework
    })


#  ДИПЛОМНЫЕ РАБОТЫ 
@login_required
def diploma_list(request):
    """Список дипломных работ педагога (руководитель)"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    
    diplomas = teacher.diplomas_supervised.all().select_related('student').order_by('-year')
    return render(request, 'portfolio/diploma_list.html', {
        'teacher': teacher,
        'diplomas': diplomas
    })

@login_required
def diploma_create(request):
    """Создание новой дипломной работы"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    if request.method == 'POST':
        form = DiplomaForm(request.POST)
        if form.is_valid():
            diploma = form.save(commit=False)
            diploma.supervisor = teacher 
            diploma.save()
            return redirect('portfolio:diploma_list')
    else:
        form = DiplomaForm()
    return render(request, 'portfolio/diploma_form.html', {
        'form': form,
        'title': 'Добавить дипломную работу',
        'button_text': 'Сохранить'
    })

@login_required
def diploma_edit(request, pk):
    """Редактирование дипломной работы"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return redirect('portfolio:profile')
    
    # проверка, что текущий преподаватель является руководителем
    diploma = get_object_or_404(Diploma, pk=pk, supervisor=teacher)
    
    if request.method == 'POST':
        form = DiplomaForm(request.POST, instance=diploma)
        if form.is_valid():
            form.save()
            return redirect('portfolio:diploma_list')
    else:
        form = DiplomaForm(instance=diploma)
    
    return render(request, 'portfolio/diploma_form.html', {
        'form': form,
        'title': 'Редактировать дипломную работу',
        'button_text': 'Обновить'
    })

@login_required
def diploma_delete(request, pk):
    """Удаление дипломной работы"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return redirect('portfolio:profile')
    
    # проверка, что текущий преподаватель является руководителем
    diploma = get_object_or_404(Diploma, pk=pk, supervisor=teacher)
    
    if request.method == 'POST':
        diploma.delete()
        return redirect('portfolio:diploma_list')
    
    return render(request, 'portfolio/diploma_confirm_delete.html', {
        'diploma': diploma
    })

#  ОЛИМПИАДЫ 
@login_required
def olympiad_list(request):
    """Список олимпиад студентов, подготовленных педагогом"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    olympiads = teacher.olympiads_prepared.all().select_related('student', 'student__group').order_by('-year', '-event_date')
    return render(request, 'portfolio/olympiad_list.html', {
        'teacher': teacher,
        'olympiads': olympiads
    })

@login_required
def olympiad_create(request):
    """Создание новой записи об олимпиаде"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    if request.method == 'POST':
        form = OlympiadForm(request.POST)
        if form.is_valid():
            olympiad = form.save(commit=False)
            olympiad.teacher = teacher 
            olympiad.save()
            return redirect('portfolio:olympiad_list')
    else:
        form = OlympiadForm()
    return render(request, 'portfolio/olympiad_form.html', {
        'form': form,
        'title': 'Добавить олимпиаду',
        'button_text': 'Сохранить'
    })

@login_required
def olympiad_edit(request, pk):
    """Редактирование записи об олимпиаде"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return redirect('portfolio:profile')
    
    # проверка, что текущий преподаватель является подготовившим педагогом
    olympiad = get_object_or_404(Olympiad, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        form = OlympiadForm(request.POST, instance=olympiad)
        if form.is_valid():
            form.save()
            return redirect('portfolio:olympiad_list')
    else:
        form = OlympiadForm(instance=olympiad)
    
    return render(request, 'portfolio/olympiad_form.html', {
        'form': form,
        'title': 'Редактировать олимпиаду',
        'button_text': 'Обновить'
    })

@login_required
def olympiad_delete(request, pk):
    """Удаление записи об олимпиаде"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return redirect('portfolio:profile')
    
    olympiad = get_object_or_404(Olympiad, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        olympiad.delete()
        return redirect('portfolio:olympiad_list')
    
    return render(request, 'portfolio/olympiad_confirm_delete.html', {
        'olympiad': olympiad
    })

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def logout_confirm(request):
    """
    Страница подтверждения выхода.
    """
    return render(request, 'portfolio/logout_confirm.html')

# === ФАЙЛЫ ===
@login_required
def file_list(request):
    """Список всех файлов пользователя"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )
    
    # Получаем все файлы, связанные с объектами этого педагога
    files = File.objects.filter(
        content_type__in=ContentType.objects.get_for_models(
            Teacher, Education, Experience, Qualification, Award,
            KnowledgeExchange, Discipline, Group, TeachingLoad,
            Student, Grade, Publication, Diploma, Coursework, Olympiad
        ).values()
    ).select_related('content_type')
    
    # Фильтруем по объектам педагога
    teacher_files = []
    for file in files:
        try:
            if hasattr(file.content_object, 'teacher') and file.content_object.teacher == teacher:
                teacher_files.append(file)
            elif isinstance(file.content_object, Teacher) and file.content_object == teacher:
                teacher_files.append(file)
        except:
            continue
    
    return render(request, 'portfolio/file_list.html', {
        'files': teacher_files,
        'teacher': teacher
    })

import logging
logger = logging.getLogger(__name__)

@login_required
@login_required
def file_upload(request):
    """Загрузка нового файла"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.create(
            user=request.user,
            last_name=request.user.last_name or "Фамилия",
            first_name=request.user.first_name or "Имя",
            birth_date="1990-01-01"
        )

    if request.method == 'POST':
        logger.info("POST data received")
        # Логирование можно оставить для отладки
        # for key, value in request.POST.items():
        #     logger.info(f"POST {key}: {value}")
        # for key, value in request.FILES.items():
        #     logger.info(f"FILES {key}: {value.name}, size: {value.size}")

        # Передаем teacher в форму
        form = FileForm(request.POST, request.FILES, teacher=teacher)
        logger.info(f"Form is valid: {form.is_valid()}")
        if form.is_valid():
            logger.info("Form is valid, saving...")
            # logger.info(f"Form data: {form.cleaned_data}") # Для отладки
            try:
                file_obj = form.save()
                logger.info(f"File saved successfully with pk: {file_obj.pk}")
                messages.success(request, 'Файл успешно загружен.')
                return redirect('portfolio:file_list')
            except Exception as e:
                logger.error(f"Error saving file: {e}", exc_info=True)
                form.add_error(None, f'Произошла ошибка при сохранении файла: {e}')
        else:
            logger.error("Form is not valid. Errors: %s", form.errors)
            # messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = FileForm(teacher=teacher) # Передаем teacher при GET запросе

    return render(request, 'portfolio/file_form.html', {
        'form': form,
        'title': 'Загрузить файл',
        'button_text': 'Загрузить'
    })


@login_required
def file_delete(request, pk):
    """Удаление файла"""
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return redirect('portfolio:profile')
    
    file = get_object_or_404(File, pk=pk)
    
    # Проверяем, что файл принадлежит педагогу
    try:
        if hasattr(file.content_object, 'teacher') and file.content_object.teacher == teacher:
            pass  # Разрешаем удаление
        elif isinstance(file.content_object, Teacher) and file.content_object == teacher:
            pass  # Разрешаем удаление
        else:
            return redirect('portfolio:file_list')
    except:
        return redirect('portfolio:file_list')
    
    if request.method == 'POST':
        # Удаляем файл с диска
        if file.file_path and os.path.isfile(file.file_path.path):
            os.remove(file.file_path.path)
        file.delete()
        return redirect('portfolio:file_list')
    
    return render(request, 'portfolio/file_confirm_delete.html', {
        'file': file
    })

@login_required
@require_POST
def get_objects_for_content_type(request):
    """AJAX view для получения списка объектов по content_type_id"""
    try:
        # Получаем данные из тела запроса
        data = json.loads(request.body)
        content_type_id = data.get('content_type_id')

        if not content_type_id:
            return JsonResponse({'error': 'content_type_id is required'}, status=400)

        try:
            content_type = ContentType.objects.get_for_id(content_type_id)
        except ContentType.DoesNotExist:
            return JsonResponse({'error': 'Invalid content_type_id'}, status=400)

        # Получаем queryset для выбранного типа
        model_class = content_type.model_class()
        
        # Начинаем с пустого queryset
        queryset = model_class.objects.none() 

        try:
            teacher = request.user.teacher
            
            # --- Логика фильтрации объектов в зависимости от типа модели ---
            if model_class == Teacher:
                # Педагог может прикреплять файлы только к своему профилю
                queryset = model_class.objects.filter(pk=teacher.pk)
            
            elif hasattr(model_class, 'teacher'):
                # Для моделей, которые имеют поле 'teacher' (Education, Experience, и т.д.)
                queryset = model_class.objects.filter(teacher=teacher)
            
            elif model_class == Group:
                # Группы, по которым у педагога есть учебная нагрузка
                queryset = model_class.objects.filter(teaching_loads__teacher=teacher).distinct()
            
            elif model_class == Discipline:
                # Дисциплины, которые педагог преподает
                queryset = model_class.objects.filter(teaching_loads__teacher=teacher).distinct()
            
            elif model_class == Student:
                # Студенты групп, по которым у педагога нагрузка
                queryset = model_class.objects.filter(group__teaching_loads__teacher=teacher).distinct()
            
            # Добавьте другие условия фильтрации по мере необходимости
            # Например, для Grade, Publication и т.д., если нужно ограничить доступ
            
            # Если ни одно условие не подошло, queryset останется пустым (model_class.objects.none())

        except Teacher.DoesNotExist:
            # Если у пользователя нет связанного педагога, возвращаем пустой список
            pass # queryset уже пустой

        # Формируем список объектов для JSON ответа
        objects_data = []
        # Ограничиваем количество объектов для предотвращения перегрузки
        # Можно добавить пагинацию, если объектов много
        for obj in queryset[:100]: 
            # Формируем отображаемое имя
            # Используем __str__ модели, можно кастомизировать
            display_name = f"{obj} (ID: {obj.pk})" # Более информативное имя
            objects_data.append({
                'id': obj.pk,
                'display_name': str(display_name) # Убедимся, что это строка
            })

        return JsonResponse({'objects': objects_data})

    except json.JSONDecodeError:
        logger.error("Invalid JSON in get_objects_for_content_type request")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error in get_objects_for_content_type: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)