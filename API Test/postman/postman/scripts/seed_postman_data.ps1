Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot

python manage.py migrate --settings=core.settings_postman --noinput

$seedScript = @'
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

from learning.models import LearningConfig
from progress.models import UserVocabularyMastery
from vocabulary.models import Course, Topic, Vocabulary

User = get_user_model()

course, _ = Course.objects.update_or_create(
    id=900001,
    defaults={
        'title': 'QA Postman Course',
        'description': 'Seed data for Postman API regression.',
    },
)
topic, _ = Topic.objects.update_or_create(
    id=900001,
    defaults={
        'course': course,
        'title': 'QA Topic',
        'description': 'QA topic for automated API checks.',
    },
)

seed_words = [
    ('alpha', 'chu cai alpha'),
    ('beta', 'chu cai beta'),
    ('gamma', 'chu cai gamma'),
    ('delta', 'chu cai delta'),
    ('epsilon', 'chu cai epsilon'),
]

vocab_objects = []
for index, (word, meaning) in enumerate(seed_words):
    vocab_id = 900001 + index
    vocab, _ = Vocabulary.objects.update_or_create(
        id=vocab_id,
        defaults={
            'topic': topic,
            'word': word,
            'meaning': meaning,
            'word_type': 'noun',
            'pronunciation': f'/{word}/',
            'audio_url': '',
            'example_en': f'This is {word}.',
            'example_vi': f'Day la {word}.',
            'image_url': '',
        },
    )
    vocab_objects.append(vocab)

user, _ = User.objects.update_or_create(
    email='qa_postman@example.com',
    defaults={
        'username': 'qa_postman@example.com',
        'first_name': 'QA',
        'last_name': 'Postman',
        'is_active': True,
    },
)
user.set_password('QaPass123!')
user.save(update_fields=['password', 'username', 'first_name', 'last_name', 'is_active'])

cfg = LearningConfig.get_solo()
cfg.time_limit = 10
cfg.total_questions = 5
cfg.pass_score = 60
cfg.max_daily_exams_per_topic = 3
cfg.save()

if vocab_objects:
    mastery, _ = UserVocabularyMastery.objects.get_or_create(
        user=user,
        vocabulary=vocab_objects[0],
    )
    mastery.next_review_date = timezone.now() - timedelta(days=1)
    mastery.save(update_fields=['next_review_date'])

print('Postman seed completed.')
'@

python manage.py shell --settings=core.settings_postman -c $seedScript
