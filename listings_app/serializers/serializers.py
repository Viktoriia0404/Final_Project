

from listings_app.models import Booking
from listings_app.models.listing import Listing

from listings_app.models.review import Review

from django.contrib.auth.models import User
from rest_framework import serializers

from listings_app.models.search_query import SearchQuery



class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", 'password']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class NotLandlordBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'listing', 'owner', 'start_date', 'end_date', 'is_confirmed', 'is_canceled']
        read_only_fields = ['listing', 'owner', 'is_confirmed' ]

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['id', 'listing', 'owner', 'start_date', 'end_date', 'is_canceled']


class LandlordListingSerializer(serializers.ModelSerializer):
    bookings = BookingSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ['id', 'owner', 'created_at', 'update_at']


class ListingSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    reviews = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ['avg_rating']


class ReviewReadSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')  # Отображаем имя пользователя, оставившего отзыв

    class Meta:
        model = Review
        fields = ['id', 'listing', 'user', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['listing', 'user', 'created_at']


class ReviewWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['user', 'rating']


class SearchQuerySerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    # print(hasattr(serializers,'source'))
    class Meta:
        model = SearchQuery
        fields = '__all__'
        read_only_fields = ['owner', 'created_at']
