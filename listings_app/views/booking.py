from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status

from rest_framework.exceptions import  ValidationError

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from listings_app.models import Booking, Listing

from listings_app.serializers.serializers import NotLandlordBookingSerializer, BookingSerializer

def is_listing_owner(user, listing_pk=None):
    """
    Проверяет, является ли пользователь владельцем листинга.
    - Возвращает True, если пользователь является владельцем.
    - Возвращает False, если пользователь не является владельцем.
    - Возвращает None, если listing_pk не передан.
    """
    if listing_pk is None:
        return None

    listing = get_object_or_404(Listing, id=listing_pk)
    return listing.owner == user


def is_booking_owner(user, booking_pk=None):
    """
    Проверяет, является ли пользователь владельцем бронирования.
    - Возвращает True, если пользователь является владельцем.
    - Возвращает False, если пользователь не является владельцем.
    - Возвращает None, если booking_pk не передан.
    """
    if booking_pk is None:
        return None

    booking = get_object_or_404(Booking, id=booking_pk)
    return booking.owner == user

class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    #
    # def get(self, request, *args, **kwargs):
    #     """
    #     Возвращает список бронирований:
    #     - Если пользователь владелец листинга, используется BookingSerializer.
    #     - Если пользователь не владелец листинга, используется NotLandlordBookingSerializer.
    #     """
    #     listing_pk = self.kwargs.get("listing_pk")
    #     user = request.user
    #
    #     # Проверяем, является ли пользователь владельцем листинга
    #     is_owner = is_listing_owner(user, listing_pk)
    #
    #     if is_owner:
    #         # Пользователь владелец листинга, возвращаем все бронирования для него
    #         bookings = Booking.objects.filter(listing__id=listing_pk)
    #         serializer = BookingSerializer(bookings, many=True)
    #     else:
    #         # Пользователь не владелец листинга, возвращаем его собственные бронирования
    #         bookings = Booking.objects.filter(owner=user)
    #         serializer = NotLandlordBookingSerializer(bookings, many=True)
    #
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        """
        Динамически выбирает сериализатор:
        - Если пользователь владелец листинга, используется LandlordBookingSerializer.
        - Если пользователь не владелец листинга, используется NotLandlordBookingSerializer.
        """
        listing_pk = self.kwargs.get("listing_pk")
        if is_listing_owner(self.request.user, listing_pk):
            return BookingSerializer  # Сериализатор для владельца
        return NotLandlordBookingSerializer  # Сериализатор для других пользователей

    def get_queryset(self):
        """
        Возвращает список бронирований:
        - Для владельца листинга возвращаются все бронирования этого листинга.
        - Для других пользователей возвращаются только их собственные бронирования.
        """
        listing_pk = self.kwargs.get("listing_pk")
        user = self.request.user

        if is_listing_owner(user, listing_pk):
            return Booking.objects.filter(listing__id=listing_pk)
        else:
            return Booking.objects.filter(owner=user, listing__id=listing_pk)

    def perform_create(self, serializer):
        """
        Создание бронирования с проверкой пересекающихся дат.
        """
        listing_pk = self.kwargs.get("listing_pk")
        listing = get_object_or_404(Listing, id=listing_pk)

        if is_listing_owner(self.request.user, listing_pk):
            raise ValidationError("Владелец листинга не может создать бронирование для собственного объекта.")

        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']

        overlapping_bookings = Booking.objects.filter(
            listing=listing,
            start_date__lt=end_date,
            end_date__gt=start_date,
            is_canceled=False
        )
        if overlapping_bookings.exists():
            raise ValidationError("This listing is already booked for the selected dates.")

        serializer.save(owner=self.request.user, listing=listing)

    def partial_update(self, request, *args, **kwargs):
        """
        Позволяет владельцу листинга подтвердить бронирование (изменить `is_confirmed`).
        """
        booking = self.get_object()
        listings_pk = self.kwargs.get('listing_pk', None)
        # Если пользователь не является владельцем листинга, запретить доступ
        # if not is_listing_owner(request.user, booking.listing.id):
        #     raise PermissionDenied("Вы не являетесь владельцем этого листинга.")

        # Разрешаем редактировать только поле `is_confirmed`

        listings_owner = is_listing_owner(self.request.user, listing_pk=listings_pk)
        if listings_owner:
            serializer = self.get_serializer(booking, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            if 'is_confirmed' in serializer.validated_data:
                serializer.save()
            else:
                raise ValidationError("Вы можете изменять только поле 'is_confirmed'.")

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Логика для пользователя, не являющегося владельцем листинга
            serializer = NotLandlordBookingSerializer(booking, data=request.data, partial=True,
                                                      context={'request': request})
            serializer.is_valid(raise_exception=True)

            # Проверяем, что пользователь может редактировать только определённые поля
            # Например: `start_date`, `end_date`
            if 'start_date' in serializer.validated_data or 'end_date' in serializer.validated_data:
                # Проверка пересечения дат, если пользователь изменяет даты
                start_date = serializer.validated_data.get('start_date', booking.start_date)
                end_date = serializer.validated_data.get('end_date', booking.end_date)

                overlapping_bookings = Booking.objects.filter(
                    listing=booking.listing,
                    start_date__lt=end_date,
                    end_date__gt=start_date,
                    is_canceled=False
                ).exclude(id=booking.id)

                if overlapping_bookings.exists():
                    raise ValidationError("Эти даты уже забронированы.")

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):
        """
        Запрет на удаление бронирований, если пользователь не владелец бронирования.
        """
        booking_pk = kwargs.get("pk")
        if not is_booking_owner(request.user, booking_pk):
            return Response(
                {"error": "You are not allowed to delete this booking."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)
# class BookingViewSet(viewsets.ModelViewSet):
#     serializer_class = BookingSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         listing_pk = self.kwargs.get("listing_pk")
#         if listing_pk:
#             return Booking.objects.filter(listing__id=listing_pk, owner=self.request.user)
#         return Booking.objects.none()
#
#     def perform_create(self, serializer):
#         listing_pk = self.kwargs.get("listing_pk")
#         listing = get_object_or_404(Listing, id=listing_pk)
#
#         serializer.save(owner=self.request.user, listing=listing)
#
#    def destroy(self, request, *args, **kwargs):
#         raise MethodNotAllowed("DELETE")
#
#     def get_queryset(self):
#         # print(self.kwargs)
#         # Получаем ID объявления из маршрута и фильтруем бронирования по нему
#         listing_slug = self.kwargs.get("listing_slug")  # self.kwargs['listing_pk']
#         # print(listing_id,listing_id,listing_id,listing_id,listing_id,)
#         return Booking.objects.filter(listing__slug=listing_slug, listing__owner=self.request.user)
#
#     def perform_create(self, serializer):
#         listing = serializer.validated_data['listing']
#         start_date = serializer.validated_data['start_date']
#         end_date = serializer.validated_data['end_date']
#
#         # Проверка доступности объекта на указанные даты
#         overlapping_bookings = Booking.objects.filter(
#             listing=listing,
#             start_date__lt=end_date,
#             end_date__gt=start_date,
#             is_canceled=False
#         )
#         if overlapping_bookings.exists():
#             return Response(
#                 {"error": "This listing is already booked for the selected dates."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # Устанавливаем крайний срок отмены за 2 дня до начала бронирования
#         cancel_deadline = start_date - timedelta(days=2)
#         serializer.save(user=self.request.user, cancel_deadline=cancel_deadline)
