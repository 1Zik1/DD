from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
import os

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, verbose_name="Пользователь", null=True, blank=True)
    last_name = models.CharField("Фамилия", max_length=50)
    first_name = models.CharField("Имя", max_length=50)
    middle_name = models.CharField("Отчество", max_length=50, blank=True, null=True)
    birth_date = models.DateField("Дата рождения")
    email = models.EmailField("Email", blank=True, null=True)
    phone = models.CharField("Телефон", max_length=20, blank=True, null=True)
    biography = models.TextField("Биография", blank=True, null=True)
    interests = models.TextField("Интересы", blank=True, null=True)
    teaching_problem = models.TextField("Педагогическая проблема", blank=True, null=True)
    photo = models.ImageField("Фото", upload_to='teacher_photos/', blank=True, null=True)

    CATEGORY_CHOICES = [
        ('No category', 'Без категории'),
        ('First', 'Первая'),
        ('Highest', 'Высшая'),
        ('Professor', 'Профессор'),
    ]
    category = models.CharField("Категория", max_length=50, choices=CATEGORY_CHOICES, default='No category')
    certification_date = models.DateField("Дата аттестации", blank=True, null=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'teachers'
        verbose_name = "Педагог"
        verbose_name_plural = "Педагоги"
        indexes = [
            models.Index(fields=['last_name', 'first_name']),  
        ]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    def get_education_files(self):
        """Возвращает файлы, связанные с образованием педагога"""
        return File.objects.filter(
            content_type=ContentType.objects.get_for_model(Education),
            education__teacher=self
        ).distinct()
    
    def get_qualification_files(self):
        """Возвращает файлы, связанные с квалификацией педагога"""
        return File.objects.filter(
            content_type=ContentType.objects.get_for_model(Qualification),
            qualification__teacher=self
        ).distinct()
    
    def get_experience_files(self):
        """Возвращает файлы, связанные с опытом работы педагога"""
        return File.objects.filter(
            content_type=ContentType.objects.get_for_model(Experience),
            experience__teacher=self
        ).distinct()
    
    def get_award_files(self):
        """Возвращает файлы, связанные с наградами педагога"""
        return File.objects.filter(
            content_type=ContentType.objects.get_for_model(Award),
            award__teacher=self
        ).distinct()


class Education(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Педагог", related_name="educations")
    institution = models.CharField("Учебное заведение", max_length=255)
    specialization = models.CharField("Специальность", max_length=255)
    degree = models.CharField("Степень", max_length=100)
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания", blank=True, null=True)

    EDUCATION_TYPE_CHOICES = [
        ('Basic', 'Основное'),
        ('Additional', 'Дополнительное'),
    ]
    education_type = models.CharField("Тип образования", max_length=50, choices=EDUCATION_TYPE_CHOICES, blank=True, null=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'education'
        verbose_name = "Образование"
        verbose_name_plural = "Образование"
        indexes = [
            models.Index(fields=['teacher_id']),  #  ускорения запросов по педагогу
        ]

    def __str__(self):
        return f"{self.institution} - {self.specialization}"


class Experience(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Педагог", related_name="experiences")
    organization = models.CharField("Организация", max_length=255)
    position = models.CharField("Должность", max_length=255)
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания", blank=True, null=True)

    EXPERIENCE_TYPE_CHOICES = [
        ('General', 'Общий'),
        ('Education', 'Образование'),
        ('College', 'Колледж'),
    ]
    experience_type = models.CharField("Тип стажа", max_length=50, choices=EXPERIENCE_TYPE_CHOICES)
    description = models.TextField("Описание", blank=True, null=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'experience'
        verbose_name = "Опыт работы"
        verbose_name_plural = "Опыт работы"
        indexes = [
            models.Index(fields=['teacher_id', 'start_date', 'end_date']),  #  ускорения запросов по датам
        ]

    def __str__(self):
        return f"{self.organization} - {self.position}"


class Qualification(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Педагог", related_name="qualifications")
    program = models.CharField("Программа", max_length=255)
    organization = models.CharField("Организация", max_length=255)
    issue_date = models.DateField("Дата выдачи")
    hours = models.IntegerField("Часы", validators=[MinValueValidator(1)])
    certificate_number = models.CharField("Номер сертификата", max_length=100, blank=True, null=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'qualification'
        verbose_name = "Квалификация"
        verbose_name_plural = "Квалификация"
        indexes = [
            models.Index(fields=['teacher_id']),  #  ускорения запросов по педагогу
        ]

    def __str__(self):
        return f"{self.program} - {self.organization}"


class Award(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Педагог", related_name="awards")
    name = models.CharField("Название", max_length=255)
    organization = models.CharField("Организация", max_length=255)
    received_date = models.DateField("Дата получения")

    LEVEL_CHOICES = [
        ('State', 'Государственная'),
        ('Regional', 'Региональная'),
        ('Departmental', 'Ведомственная'),
        ('Other', 'Другая'),
    ]
    level = models.CharField("Уровень", max_length=50, choices=LEVEL_CHOICES, blank=True, null=True)
    description = models.TextField("Описание", blank=True, null=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'awards'
        verbose_name = "Награда"
        verbose_name_plural = "Награды"
        indexes = [
            models.Index(fields=['teacher_id', 'level']),  #  ускорения запросов по уровню
        ]

    def __str__(self):
        return f"{self.name} ({self.level})"


class KnowledgeExchange(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Педагог", related_name="knowledge_exchanges")
    EVENT_TYPE_CHOICES = [
        ('Conference', 'Конференция'),
        ('Seminar', 'Семинар'),
        ('Webinar', 'Вебинар'),
        ('Masterclass', 'Мастер-класс'),
        ('Publication', 'Публикация'),
        ('Other', 'Другое'),
    ]
    event_type = models.CharField("Тип мероприятия", max_length=100, choices=EVENT_TYPE_CHOICES)
    title = models.CharField("Название", max_length=255)
    event_date = models.DateField("Дата")
    description = models.TextField("Описание", blank=True, null=True)

    ROLE_CHOICES = [
        ('Speaker', 'Докладчик'),
        ('Participant', 'Участник'),
        ('Organizer', 'Организатор'),
        ('Moderator', 'Модератор'),
    ]
    role = models.CharField("Роль", max_length=100, choices=ROLE_CHOICES)
    location = models.CharField("Место", max_length=255, blank=True, null=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'knowledge_exchange'
        verbose_name = "Обмен опытом"
        verbose_name_plural = "Обмен опытом"
        indexes = [
            models.Index(fields=['teacher_id', 'event_date']),  #  ускорения запросов по дате
        ]

    def __str__(self):
        return f"{self.title} ({self.event_date})"


class Discipline(models.Model):
    name = models.CharField("Название", max_length=255)
    cycle_code = models.CharField("Код цикла", max_length=50, blank=True, null=True)
    lecture_hours = models.IntegerField("Лекции", default=0)
    practice_hours = models.IntegerField("Практика", default=0)
    lab_hours = models.IntegerField("Лабораторные", default=0)

    ASSESSMENT_TYPE_CHOICES = [
        ('Exam', 'Экзамен'),
        ('Credit', 'Зачёт'),
        ('Coursework', 'Курсовая'),
        ('Differentiated credit', 'Диф. зачёт'),
    ]
    assessment_type = models.CharField("Форма аттестации", max_length=50, choices=ASSESSMENT_TYPE_CHOICES, blank=True, null=True)
    description = models.TextField("Описание", blank=True, null=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'disciplines'
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"

    def __str__(self):
        return self.name


class Group(models.Model):
    number = models.CharField("Номер группы", max_length=20, unique=True)
    specialty = models.CharField("Специальность", max_length=255, blank=True, null=True)
    course = models.IntegerField("Курс", validators=[
        MinValueValidator(1),
        MaxValueValidator(6)
    ])
    admission_year = models.IntegerField("Год набора", validators=[
        MinValueValidator(2000)
    ])
    description = models.TextField("Описание", blank=True, null=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'groups'
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.number


class TeachingLoad(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Педагог", related_name="teaching_loads")
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, verbose_name="Дисциплина", related_name="teaching_loads")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Группа", related_name="teaching_loads")
    semester = models.IntegerField("Семестр", validators=[
        MinValueValidator(1),
        MaxValueValidator(12)
    ])
    year = models.IntegerField("Год", validators=[
        MinValueValidator(2000)
    ])

    LESSON_TYPE_CHOICES = [
        ('Lecture', 'Лекция'),
        ('Practice', 'Практика'),
        ('Lab', 'Лабораторная'),
        ('Consultation', 'Консультация'),
        ('Exam', 'Экзамен'),
    ]
    lesson_type = models.CharField("Тип занятия", max_length=50, choices=LESSON_TYPE_CHOICES)
    hours = models.IntegerField("Часы", validators=[
        MinValueValidator(1)
    ])

    STUDY_FORM_CHOICES = [
        ('Full-time', 'Очная'),
        ('Part-time', 'Заочная'),
        ('Mixed', 'Очно-заочная'),
    ]
    study_form = models.CharField("Форма обучения", max_length=20, choices=STUDY_FORM_CHOICES, default='Full-time')

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'teaching_load'
        verbose_name = "Учебная нагрузка"
        verbose_name_plural = "Учебная нагрузка"
        indexes = [
            models.Index(fields=['teacher_id', 'discipline_id', 'group_id']),  #  ускорения запросов
        ]

    def __str__(self):
        return f"{self.teacher} - {self.discipline} ({self.group})"


class Student(models.Model):
    last_name = models.CharField("Фамилия", max_length=50)
    first_name = models.CharField("Имя", max_length=50)
    middle_name = models.CharField("Отчество", max_length=50, blank=True, null=True)
    record_book_number = models.CharField("Номер зачётки", max_length=20, unique=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Группа", related_name="students")
    admission_date = models.DateField("Дата поступления")
    dismissal_date = models.DateField("Дата отчисления", blank=True, null=True)

    STATUS_CHOICES = [
        ('Active', 'Активен'),
        ('Dismissed', 'Отчислен'),
        ('Academic', 'Академ'),
        ('Graduate', 'Выпускник'),
    ]
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='Active')

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'students'
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"
        indexes = [
            models.Index(fields=['group_id']),  #  ускорения запросов по группе
        ]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Студент", related_name="grades")
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, verbose_name="Дисциплина", related_name="grades")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Педагог", related_name="grades")

    CONTROL_TYPE_CHOICES = [
        ('Current', 'Текущий'),
        ('Interim', 'Рубежный'),
        ('Final', 'Итоговый'),
    ]
    control_type = models.CharField("Вид контроля", max_length=50, choices=CONTROL_TYPE_CHOICES)
    grade = models.IntegerField("Оценка", validators=[
        MinValueValidator(2),
        MaxValueValidator(5)
    ])
    score = models.DecimalField("Баллы", max_digits=4, decimal_places=2, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ], blank=True, null=True)
    date = models.DateField("Дата")
    description = models.CharField("Описание", max_length=255, blank=True, null=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'grades'
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
        indexes = [
            models.Index(fields=['student_id', 'discipline_id', 'teacher_id']),  #  ускорения запросов
        ]

    def __str__(self):
        return f"{self.student} - {self.discipline}: {self.grade}"


class Publication(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Педагог", related_name="publications")
    title = models.CharField("Название", max_length=500)

    TYPE_CHOICES = [
        ('Article', 'Статья'),
        ('Textbook', 'Учебное пособие'),
        ('Monograph', 'Монография'),
        ('Manual', 'Методичка'),
        ('Online course', 'Онлайн-курс'),
    ]
    type = models.CharField("Тип", max_length=50, choices=TYPE_CHOICES)
    publisher = models.CharField("Издательство", max_length=255, blank=True, null=True)
    year = models.IntegerField("Год", validators=[
        MinValueValidator(1900)
    ])
    issn_isbn = models.CharField("ISSN/ISBN", max_length=50, blank=True, null=True)
    url = models.URLField("Ссылка", blank=True, null=True)
    description = models.TextField("Описание", blank=True, null=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'publications'
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        indexes = [
            models.Index(fields=['teacher_id']),  #  ускорения запросов по педагогу
        ]

    def __str__(self):
        return f"{self.title} ({self.year})"


class Diploma(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Студент", related_name="diplomas")
    supervisor = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Руководитель", related_name="diplomas_supervised")
    topic = models.CharField("Тема", max_length=500)
    year = models.IntegerField("Год")
    grade = models.IntegerField("Оценка", validators=[
        MinValueValidator(2),
        MaxValueValidator(5)
    ], blank=True, null=True)
    abstract = models.TextField("Аннотация", blank=True, null=True)
    defense_date = models.DateField("Дата защиты", blank=True, null=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'diplomas'
        verbose_name = "Дипломная работа"
        verbose_name_plural = "Дипломные работы"
        indexes = [
            models.Index(fields=['supervisor_id']),  #  ускорения запросов по руководителю
        ]

    def __str__(self):
        return f"{self.student} - {self.topic}"


class Coursework(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Студент", related_name="courseworks")
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, verbose_name="Дисциплина", related_name="courseworks")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Педагог", related_name="courseworks")
    topic = models.CharField("Тема", max_length=500)
    year = models.IntegerField("Год")
    grade = models.IntegerField("Оценка", validators=[
        MinValueValidator(2),
        MaxValueValidator(5)
    ], blank=True, null=True)
    submission_date = models.DateField("Дата сдачи", blank=True, null=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'courseworks'
        verbose_name = "Курсовая работа"
        verbose_name_plural = "Курсовые работы"
        indexes = [
            models.Index(fields=['teacher_id', 'discipline_id']),  #  ускорения запросов
        ]

    def __str__(self):
        return f"{self.student} - {self.topic}"


class Olympiad(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Студент", related_name="olympiads")
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, verbose_name="Подготовивший педагог", blank=True, null=True, related_name="olympiads_prepared")
    name = models.CharField("Название", max_length=255)

    LEVEL_CHOICES = [
        ('School', 'Школная'),
        ('College', 'Колледжа'),
        ('City', 'Городская'),
        ('Regional', 'Региональная'),
        ('National', 'Всероссийская'),
        ('International', 'Международная'),
    ]
    level = models.CharField("Уровень", max_length=50, choices=LEVEL_CHOICES)
    place = models.IntegerField("Место", validators=[
        MinValueValidator(1),
        MaxValueValidator(3)
    ], blank=True, null=True)
    year = models.IntegerField("Год")
    event_date = models.DateField("Дата проведения")
    description = models.TextField("Описание", blank=True, null=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    # Связь с файлами (полиморфная)
    files = GenericRelation('File', verbose_name="Файлы")

    class Meta:
        db_table = 'olympiads'
        verbose_name = "Олимпиада"
        verbose_name_plural = "Олимпиады"
        indexes = [
            models.Index(fields=['teacher_id', 'level']),  
        ]

    def __str__(self):
        return f"{self.name} - {self.student}"


class FileManager(models.Manager):
    """Менеджер для удобной работы с файлами"""
    
    def create_for_object(self, obj, **kwargs):
        """Создает файл для указанного объекта"""
        return self.create(
            content_object=obj,
            **kwargs
        )

class File(models.Model):
    """
    Модель для хранения файлов, связанных с различными объектами системы.
    Использует GenericForeignKey для связи с любым типом объекта (образование, квалификация и т.д.).
    """
    
    # Связь с типом контента (модели Django)
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        verbose_name="Тип объекта",
    )
    
    # ID связанного объекта
    object_id = models.PositiveIntegerField()
    
    # Полиморфная ссылка на объект
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Информация о файле
    file_name = models.CharField("Имя файла", max_length=255)
    file_path = models.FileField("Файл", upload_to='files/')  
    FILE_TYPE_CHOICES = [
        ('PDF', 'PDF'),
        ('JPG', 'JPG'),
        ('JPEG', 'JPEG'),
        ('PNG', 'PNG'),
        ('DOC', 'DOC'),
        ('DOCX', 'DOCX'),
    ]
    file_type = models.CharField("Тип файла", max_length=50, choices=FILE_TYPE_CHOICES)
    file_size = models.BigIntegerField(
        "Размер", 
        default=0  
    )
    upload_date = models.DateTimeField("Дата загрузки", auto_now_add=True)
    description = models.CharField("Описание", max_length=255, blank=True, null=True)
    
    objects = FileManager()

    class Meta:
        db_table = 'files'
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(file_size__gt=0),
                name='files_file_size_check'
            ),
            models.CheckConstraint(
                check=models.Q(file_type__in=['PDF', 'JPG', 'JPEG', 'PNG', 'DOC', 'DOCX']),
                name='files_file_type_check'
            ),
            models.CheckConstraint(
                check=models.Q(object_id__gte=0),
                name='files_object_id_95b6785b_check'
            )
        ]

    def __str__(self):
        return self.file_name
    
    def save(self, *args, **kwargs):
   
        if self.file_path:
            if not self.file_name:
                self.file_name = self.file_path.name

            if not self.file_type and '.' in self.file_path.name:
                ext = self.file_path.name.split('.')[-1].upper()
                if ext in dict(self.FILE_TYPE_CHOICES):
                    self.file_type = ext

            if not self.file_size or self.file_size <= 0:
                try:
                    file_size = self.file_path.size
                    if file_size is not None and file_size > 0:
                        self.file_size = file_size
                    else:
                        raise ValueError("Загруженный файл пустой или его размер не может быть определен.")
                except (AttributeError, ValueError) as e:
                    raise ValueError(f"Ошибка при определении размера файла: {e}")

        if self.file_size is None or self.file_size <= 0:
            raise ValueError("Размер файла должен быть больше 0. Файл не может быть сохранен.")

        super().save(*args, **kwargs)
        
        if self.file_path and (self.file_size is None or self.file_size <= 0):
            try:
                file_path_on_disk = self.file_path.path
                if os.path.exists(file_path_on_disk):
                    actual_size = os.path.getsize(file_path_on_disk)
                    if actual_size > 0:
                        self.file_size = actual_size
                        File.objects.filter(pk=self.pk).update(file_size=self.file_size)
                    else:
                        self.delete()
                        if os.path.exists(file_path_on_disk):
                            os.remove(file_path_on_disk)
                        raise ValueError("Файл пустой")
            except Exception as e:
                try:
                    if self.file_path and hasattr(self.file_path, 'path'):
                        file_path_on_disk = self.file_path.path
                        if os.path.exists(file_path_on_disk):
                            os.remove(file_path_on_disk)
                except:
                    pass
                self.delete()
                raise e 
    
class TeacherExperience(models.Model):
    teacher_id = models.IntegerField(primary_key=True)
    fio = models.CharField(max_length=101)
    general_experience = models.FloatField(null=True)
    education_experience = models.FloatField(null=True)
    college_experience = models.FloatField(null=True)
    
    class Meta:
        managed = False
        db_table = 'teacher_experience'
        verbose_name = "Опыт педагога"
        verbose_name_plural = "Опыт педагогов"

class TeachingQuality(models.Model):
    teacher_id = models.IntegerField(primary_key=True)
    fio = models.CharField(max_length=101)
    discipline = models.CharField(max_length=255)
    group_number = models.CharField(max_length=20)
    year = models.IntegerField()
    semester = models.IntegerField()
    average_grade = models.FloatField(null=True)
    grade_count = models.IntegerField()
    percent_excellent = models.FloatField(null=True)
    
    class Meta:
        managed = False
        db_table = 'teaching_quality'
        verbose_name = "Качество обучения"
        verbose_name_plural = "Качество обучения"

class TeacherPortfolio(models.Model):
    teacher_id = models.IntegerField(primary_key=True)
    fio = models.CharField(max_length=101)
    education_count = models.IntegerField(null=True)
    general_experience_years = models.FloatField(null=True)
    taught_disciplines = models.TextField(null=True)
    student_average_grade = models.FloatField(null=True)
    diploma_count = models.IntegerField(null=True)
    publication_count = models.IntegerField(null=True)
    award_count = models.IntegerField(null=True)
    winner_count = models.IntegerField(null=True)
    
    class Meta:
        managed = False
        db_table = 'teacher_portfolio'
        verbose_name = "Портфолио педагога"
        verbose_name_plural = "Портфолио педагогов"