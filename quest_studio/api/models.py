from django.db import models
import uuid

class Profile(models.Model):
    """
    Профиль пользователя, храним идентификатор в формате UUID,
    т.к. аутентификация может быть в Supabase. 
    """
    user_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    nickname = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="Никнейм"
    )
    avatar_url = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="URL аватара"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Дата обновления"
    )

    class Meta:
        # Если хотим, чтобы Django полностью управлял таблицей, 
        # оставляем managed = True. Если нет — ставим False.
        managed = True
        db_table = 'profiles'
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Profile({self.user_id}) - {self.nickname or 'No Nickname'}"


class Quest(models.Model):
    """
    Модель квеста. date можно назвать start_time/finish_time,
    если нужна точная логика расписания.
    """
    id = models.AutoField(
        primary_key=True, 
        verbose_name="ID"
    )
    title = models.CharField(
        max_length=100, 
        verbose_name="Название квеста"
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Описание"
    )
    date = models.DateTimeField(
        blank=True, 
        null=True, 
        verbose_name="Дата и время"
    )
    difficulty = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="Сложность"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Дата обновления"
    )

    class Meta:
        managed = True
        db_table = 'quests'
        verbose_name = "Квест"
        verbose_name_plural = "Квесты"

    def __str__(self):
        return self.title


class Booking(models.Model):
    """
    Модель брони: связь (user_id - Quest).
    Если планируется реальная аутентификация через Django,
    лучше заменить user_id на ForeignKey к User или Profile.
    """
    id = models.AutoField(
        primary_key=True, 
        verbose_name="ID"
    )
    user_id = models.UUIDField(
        verbose_name="Идентификатор пользователя"
    )
    quest = models.ForeignKey(
        Quest, 
        on_delete=models.CASCADE, 
        related_name="bookings", 
        verbose_name="Квест"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата бронирования"
    )

    class Meta:
        managed = True
        db_table = 'bookings'
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        # Чтобы один и тот же пользователь не мог бронировать один квест несколько раз:
        unique_together = (('user_id', 'quest'),)

    def __str__(self):
        return f"Booking #{self.id} for Quest {self.quest_id} by user {self.user_id}"


class Rating(models.Model):
    """
    Модель рейтинга. user_id + quest => уникальная пара.
    """
    id = models.AutoField(
        primary_key=True, 
        verbose_name="ID"
    )
    user_id = models.UUIDField(
        verbose_name="Идентификатор пользователя"
    )
    quest = models.ForeignKey(
        Quest, 
        on_delete=models.CASCADE, 
        related_name="ratings", 
        verbose_name="Квест"
    )
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], 
        verbose_name="Оценка"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата выставления"
    )

    class Meta:
        managed = True
        db_table = 'ratings'
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинги"
        unique_together = (('user_id', 'quest'),)

    def __str__(self):
        return f"Rating {self.rating} by user {self.user_id} for quest {self.quest_id}"


class Comment(models.Model):
    """
    Модель комментария к квесту.
    """
    id = models.AutoField(
        primary_key=True, 
        verbose_name="ID"
    )
    user_id = models.UUIDField(
        verbose_name="Идентификатор пользователя"
    )
    quest = models.ForeignKey(
        Quest, 
        on_delete=models.CASCADE, 
        related_name="comments", 
        verbose_name="Квест"
    )
    text = models.TextField(
        verbose_name="Текст комментария"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата создания"
    )

    class Meta:
        managed = True
        db_table = 'comments'
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"Comment #{self.id} by user {self.user_id} for quest {self.quest_id}"
