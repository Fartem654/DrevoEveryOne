from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.db.transaction import atomic


# Create your models here.


class Person(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    patronymic = models.CharField(max_length=100, blank=True, verbose_name="Отчество")

    gender = models.CharField(max_length=20, choices=[('M', 'Муж'), ('W', 'Жен')], verbose_name="Пол")

    birth = models.DateField(verbose_name="Дата рождения", help_text="xx.xx.xxxx")
    death = models.DateField(null=True, blank=True, verbose_name="Дата смерти", help_text="xx.xx.xxxx")

    image = models.ImageField(default="photo/default_person_photo/default.png",
                              upload_to="photo/upload_photo/",
                              verbose_name="Фото",
                              )
    place_of_birth = models.TextField(blank=True, verbose_name="Место рождения",
                                      help_text="Россия, Пермский Край, Пермь ...",
                                      )
    description = models.TextField(blank=True, verbose_name="Описание")

    mother = models.ForeignKey('self',
                               blank=True,
                               null=True,
                               default=None,
                               on_delete=models.SET_NULL,
                               verbose_name="Мать",
                               related_name='children_from_mother',
                               )
    father = models.ForeignKey('self',
                               blank=True,
                               null=True,
                               default=None,
                               on_delete=models.SET_NULL,
                               verbose_name="Отец",
                               related_name='children_from_father',
                               )

    class Meta:
        verbose_name = "Человек"
        verbose_name_plural = "Люди"

    def __str__(self):
        return self.first_name + " " + self.last_name

    def clean(self):
        # Проверка поля "mother"
        if self.mother == self:  # МОЖНО ВЫНЕСТИ В ФОРМУ И СДЕЛАТЬ ПРОВЕРКУ В FORM!!!!!!!!!!!!!!!!!!
            raise ValidationError("Нельзя быть матерью самому себе")
        if self.mother and self.mother.gender != 'W':
            raise ValidationError("Мать не может быть мужского пола")

        # Проверка поля "father"
        if self.father == self:  # МОЖНО ВЫНЕСТИ В ФОРМУ И СДЕЛАТЬ ПРОВЕРКУ В FORM!!!!!!!!!!!!!!!!!!
            raise ValidationError("Нельзя быть отцом самому себе")
        if self.father and self.father.gender != 'M':
            raise ValidationError("Отец не может быть женского пола")

        # Проверка поля "spouse"
        if self.spouse == self:  # МОЖНО ВЫНЕСТИ В ФОРМУ И СДЕЛАТЬ ПРОВЕРКУ В FORM!!!!!!!!!!!!!!!!!!
            raise ValidationError("Нельзя быть супругом самому себе")
        # Проверка: указан ли партнер, отличается ли пол
        if self.spouse and self.spouse.gender == self.gender:
            raise ValidationError("Супруги не могут быть одного и того же пола")

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)

        if self.spouse and self.spouse.spouse != self:  # ПРИЕЧАНИЕ: Чтобы при обнулении супруга у одного человека,
            # у другого, поле spouse тоже становилось None, лучше будет изменять это поле у другого при
            # непосредственном получении значений в функции изменения.
            with atomic():
                if self.spouse.spouse:
                    self.spouse.spouse.spouse = None
                    self.spouse.spouse.save()
                self.spouse.spouse = self
                self.spouse.save()


class Marriage(models.Model):
    husband = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='marriages_as_husband', verbose_name="Муж")
    wife = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='marriages_as_wife', verbose_name="Жена")
    married_date = models.DateField(null=True, blank=True, verbose_name="<Дата женитьбы")
    divorced = models.BooleanField(default=False, verbose_name="В разводе")
    divorce_date = models.DateField(null=True, blank=True, verbose_name="Дата развода")

    class Meta:
        verbose_name = "Супруги"
        verbose_name_plural = "Супругов"

    def __str__(self):
        return f"{self.husband.first_name} и {self.wife.first_name} {self.husband.last_name}" #может возникуть ситуация
        # когда пара в разводе и их фамилии различаются
