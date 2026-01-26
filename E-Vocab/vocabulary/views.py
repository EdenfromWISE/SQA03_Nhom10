from rest_framework import generics, permissions
from .models import Course, Topic
from .serializers import CourseSerializer, TopicDetailSerializer


# View để lấy danh sách tất cả Course
class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

# View để lấy chi tiết một Course (bao gồm các Topic)
class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

# View để lấy chi tiết một Topic (bao gồm các từ vựng)
class TopicDetailView(generics.RetrieveAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
