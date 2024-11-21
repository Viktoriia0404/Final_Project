from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from listings_app.models.profile import Profile
from listings_app.serializers.register_login import ProfileSerializer


class ProfileRetrieveUpdateDestroyView(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Проверка для Swagger схемы
        if getattr(self, 'swagger_fake_view', False):
            return None  # Возвращаем пустой объект или None для Swagger

        # Основная логика для получения объекта профиля
        obj = get_object_or_404(Profile, user=self.request.user)
        return obj

    def list(self, request, *args, **kwargs):
        return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)