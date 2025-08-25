from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'portfolio' 

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('logout/confirm/', views.logout_confirm, name='logout_confirm'),
    
    # Образование
    path('education/', views.education_list, name='education_list'),
    path('education/create/', views.education_create, name='education_create'),
    path('education/<int:pk>/edit/', views.education_edit, name='education_edit'),
    path('education/<int:pk>/delete/', views.education_delete, name='education_delete'),
    
    # Опыт работы
    path('experience/', views.experience_list, name='experience_list'),
    path('experience/create/', views.experience_create, name='experience_create'),
    path('experience/<int:pk>/edit/', views.experience_edit, name='experience_edit'),
    path('experience/<int:pk>/delete/', views.experience_delete, name='experience_delete'),
    
    # Квалификация
    path('qualification/', views.qualification_list, name='qualification_list'),
    path('qualification/create/', views.qualification_create, name='qualification_create'),
    path('qualification/<int:pk>/edit/', views.qualification_edit, name='qualification_edit'),
    path('qualification/<int:pk>/delete/', views.qualification_delete, name='qualification_delete'),
    
    # Награды
    path('award/', views.award_list, name='award_list'),
    path('award/create/', views.award_create, name='award_create'),
    path('award/<int:pk>/edit/', views.award_edit, name='award_edit'),
    path('award/<int:pk>/delete/', views.award_delete, name='award_delete'),



    #УЧЕБНАЯ ДЕЯТЕЛЬНОСТЬ 
    #----------------------------------------------------------------------------------------------------#
    # Учебная нагрузка
    path('teaching-load/', views.teaching_load_list, name='teaching_load_list'),
    path('teaching-load/create/', views.teaching_load_create, name='teaching_load_create'),
    path('teaching-load/<int:pk>/edit/', views.teaching_load_edit, name='teaching_load_edit'),
    path('teaching-load/<int:pk>/delete/', views.teaching_load_delete, name='teaching_load_delete'),
    path('my-disciplines/', views.my_disciplines, name='my_disciplines'),  # Только мои дисциплины

    # Группы студентов
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),  # Детали группы

    # Дисциплины
    path('disciplines/', views.discipline_list, name='discipline_list'),
    path('disciplines/create/', views.discipline_create, name='discipline_create'),
    path('disciplines/<int:pk>/edit/', views.discipline_edit, name='discipline_edit'),
    path('disciplines/<int:pk>/delete/', views.discipline_delete, name='discipline_delete'),

    # Успеваемость студентов
    path('grades/', views.grades_list, name='grades_list'),


    #НАУЧНО-МЕТОДИЧЕСКАЯ РАБОТА

    # Научно-методическая работа
    path('publications/', views.publication_list, name='publication_list'),
    path('publications/create/', views.publication_create, name='publication_create'),
    path('publications/<int:pk>/edit/', views.publication_edit, name='publication_edit'),
    path('publications/<int:pk>/delete/', views.publication_delete, name='publication_delete'),

    # Курсовые работы
    path('courseworks/', views.coursework_list, name='coursework_list'),
    path('courseworks/create/', views.coursework_create, name='coursework_create'),
    path('courseworks/<int:pk>/edit/', views.coursework_edit, name='coursework_edit'),
    path('courseworks/<int:pk>/delete/', views.coursework_delete, name='coursework_delete'),

    # Дипломные работы
    path('diplomas/', views.diploma_list, name='diploma_list'),
    path('diplomas/create/', views.diploma_create, name='diploma_create'),
    path('diplomas/<int:pk>/edit/', views.diploma_edit, name='diploma_edit'),
    path('diplomas/<int:pk>/delete/', views.diploma_delete, name='diploma_delete'),

    # Работа со студентами -> Олимпиады
    path('olympiads/', views.olympiad_list, name='olympiad_list'),
    path('olympiads/create/', views.olympiad_create, name='olympiad_create'),
    path('olympiads/<int:pk>/edit/', views.olympiad_edit, name='olympiad_edit'),
    path('olympiads/<int:pk>/delete/', views.olympiad_delete, name='olympiad_delete'),
]