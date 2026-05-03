Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot

$rollbackScript = @'
from django.contrib.auth import get_user_model
from chatbot.models import ChatMessage
from learning.models import LearningSession
from progress.models import DailyActivity, UserStreak, UserTopicProgress, UserVocabularyMastery

User = get_user_model()
seed_user = User.objects.filter(email='qa_postman@example.com').first()

if seed_user:
    ChatMessage.objects.filter(user=seed_user).delete()
    LearningSession.objects.filter(user=seed_user).delete()
    UserVocabularyMastery.objects.filter(user=seed_user).delete()
    UserTopicProgress.objects.filter(user=seed_user).delete()
    DailyActivity.objects.filter(user=seed_user).delete()
    UserStreak.objects.filter(user=seed_user).delete()
    seed_user.first_name = 'QA'
    seed_user.last_name = 'Postman'
    seed_user.username = 'qa_postman@example.com'
    seed_user.set_password('QaPass123!')
    seed_user.save(update_fields=['first_name', 'last_name', 'username', 'password'])

deleted_count, _ = User.objects.filter(email__startswith='qa_reg_').delete()

print('Rollback done. Deleted registered test users:', deleted_count)
'@

python manage.py shell --settings=core.settings_postman -c $rollbackScript
