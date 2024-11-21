from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from listings_app.models import Listing, Review, Booking
from listings_app.permissions import IsNotLandlordForCreate
from listings_app.serializers.review import ReviewSerializer


class ListingReviewView(ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsNotLandlordForCreate]


    def get_queryset(self):
        listing_slug = self.kwargs['listing_pk']
        listing = get_object_or_404(Listing, id=listing_slug)
        return Review.objects.filter(listing=listing)

    def perform_create(self, serializer):
        listing = get_object_or_404(Listing, id=self.kwargs['listing_pk'])
        booking_exists = Booking.objects.filter(
            listing=listing,
            owner=self.request.user,
            is_confirmed=True,
            end_date__lt=timezone.now().date()
        ).exists()
        if booking_exists:
            serializer.save(listing=listing, user=self.request.user)
        else:
            raise ValidationError("You have not permissions to add review now")
