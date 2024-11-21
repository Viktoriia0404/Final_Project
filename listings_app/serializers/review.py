from rest_framework import serializers

from listings_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')  # Make user read-only, as it should be auto-assigned
    listing = serializers.SlugRelatedField(slug_field='slug', read_only=True)  # Display listing by slug, read-only

    class Meta:
        model = Review
        fields = ['id', 'listing', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'listing', 'created_at']  # Prevent modification of these fields

    def validate_rating(self, value):
        """
        Ensure the rating is between 1 and 5.
        """
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars.")
        return value

    def create(self, validated_data):
        """
        Customize the creation to ensure the current user and listing are set properly.
        """
        request = self.context.get('request')  # Get the request from the serializer context
        listing = self.context.get('listing')   # Listing passed to the serializer context

        return Review.objects.create(
            listing=listing,
            user=request.user,
            **validated_data
        )