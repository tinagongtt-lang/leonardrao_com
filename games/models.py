from django.db import models


class ChessGame(models.Model):
    MODE_CHOICES = (
        ('ai', '人机对战'),
        ('pvp', '真人对战'),
    )
    STATUS_CHOICES = (
        ('waiting', '等待对手'),
        ('playing', '进行中'),
        ('finished', '已结束'),
    )

    code = models.CharField(max_length=16, unique=True)
    mode = models.CharField(max_length=8, choices=MODE_CHOICES)
    difficulty = models.PositiveSmallIntegerField(default=1)
    fen = models.CharField(max_length=200)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='waiting')
    result = models.CharField(max_length=32, blank=True, default='')
    white_key = models.CharField(max_length=64, blank=True, default='')
    black_key = models.CharField(max_length=64, blank=True, default='')
    last_move = models.CharField(max_length=8, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} ({self.get_mode_display()})'


class XiangqiGame(models.Model):
    MODE_CHOICES = (
        ('ai', '人机对战'),
        ('pvp', '真人对战'),
    )
    STATUS_CHOICES = (
        ('waiting', '等待对手'),
        ('playing', '进行中'),
        ('finished', '已结束'),
    )

    code = models.CharField(max_length=16, unique=True)
    mode = models.CharField(max_length=8, choices=MODE_CHOICES)
    difficulty = models.PositiveSmallIntegerField(default=1)
    fen = models.CharField(max_length=200)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='waiting')
    result = models.CharField(max_length=32, blank=True, default='')
    red_key = models.CharField(max_length=64, blank=True, default='')
    black_key = models.CharField(max_length=64, blank=True, default='')
    last_move = models.CharField(max_length=8, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} ({self.get_mode_display()})'


class GoGame(models.Model):
    MODE_CHOICES = (
        ('ai', '人机对战'),
        ('pvp', '真人对战'),
    )
    STATUS_CHOICES = (
        ('waiting', '等待对手'),
        ('playing', '进行中'),
        ('finished', '已结束'),
    )

    code = models.CharField(max_length=16, unique=True)
    mode = models.CharField(max_length=8, choices=MODE_CHOICES)
    difficulty = models.PositiveSmallIntegerField(default=1)
    size = models.PositiveSmallIntegerField(default=19)
    board = models.TextField()
    turn = models.CharField(max_length=8, default='black')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='waiting')
    result = models.CharField(max_length=32, blank=True, default='')
    black_key = models.CharField(max_length=64, blank=True, default='')
    white_key = models.CharField(max_length=64, blank=True, default='')
    last_move = models.CharField(max_length=8, blank=True, default='')
    ko_board = models.TextField(blank=True, default='')
    pass_streak = models.PositiveSmallIntegerField(default=0)
    captures_b = models.PositiveSmallIntegerField(default=0)
    captures_w = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} ({self.get_mode_display()})'


class GomokuGame(models.Model):
    MODE_CHOICES = (
        ('ai', '人机对战'),
        ('pvp', '真人对战'),
    )
    STATUS_CHOICES = (
        ('waiting', '等待对手'),
        ('playing', '进行中'),
        ('finished', '已结束'),
    )

    code = models.CharField(max_length=16, unique=True)
    mode = models.CharField(max_length=8, choices=MODE_CHOICES)
    difficulty = models.PositiveSmallIntegerField(default=1)
    board = models.TextField()
    turn = models.CharField(max_length=8, default='black')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='waiting')
    result = models.CharField(max_length=32, blank=True, default='')
    black_key = models.CharField(max_length=64, blank=True, default='')
    white_key = models.CharField(max_length=64, blank=True, default='')
    last_move = models.CharField(max_length=8, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} ({self.get_mode_display()})'
