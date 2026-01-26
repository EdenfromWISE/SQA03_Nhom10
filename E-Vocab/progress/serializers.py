from rest_framework import serializers

class CalendarDaySerializer(serializers.Serializer):
    date = serializers.DateField()
    active = serializers.BooleanField()

class StreakSerializer(serializers.Serializer):
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    calendar = serializers.DictField()
