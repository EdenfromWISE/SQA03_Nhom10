param(
    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot

$snapshotScript = @'
import json
from django.contrib.auth import get_user_model
from chatbot.models import ChatMessage
from learning.models import LearningSession, Question, UserAnswer
from progress.models import DailyActivity, UserStreak, UserTopicProgress, UserVocabularyMastery
from students.models import UserProfile

User = get_user_model()

seed_user = User.objects.filter(email='qa_postman@example.com').first()
qa_users = User.objects.filter(email__startswith='qa_')
reg_users = User.objects.filter(email__startswith='qa_reg_')

payload = {
    'users_total_qa_prefix': qa_users.count(),
    'users_registered_cases': reg_users.count(),
    'seed_user_exists': bool(seed_user),
    'seed_user_id': seed_user.id if seed_user else None,
    'seed_user_profile_rows': UserProfile.objects.filter(user=seed_user).count() if seed_user else 0,
    'seed_learning_sessions': LearningSession.objects.filter(user=seed_user).count() if seed_user else 0,
    'seed_learning_questions': Question.objects.filter(session__user=seed_user).count() if seed_user else 0,
    'seed_learning_answers': UserAnswer.objects.filter(session__user=seed_user).count() if seed_user else 0,
    'seed_vocab_mastery': UserVocabularyMastery.objects.filter(user=seed_user).count() if seed_user else 0,
    'seed_topic_progress': UserTopicProgress.objects.filter(user=seed_user).count() if seed_user else 0,
    'seed_streak_rows': UserStreak.objects.filter(user=seed_user).count() if seed_user else 0,
    'seed_daily_activity_rows': DailyActivity.objects.filter(user=seed_user).count() if seed_user else 0,
    'seed_chat_messages': ChatMessage.objects.filter(user=seed_user).count() if seed_user else 0,
}
print(json.dumps(payload))
'@

$json = python manage.py shell --settings=core.settings_postman -c $snapshotScript
$outputDir = Split-Path -Path $OutputPath -Parent
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}
Set-Content -Path $OutputPath -Value $json -Encoding utf8
