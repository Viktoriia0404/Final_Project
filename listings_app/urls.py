from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from listings_app.views.auth.login import LoginView
from listings_app.views.auth.logout import LogoutView
from listings_app.views.auth.register import RegisterView
from listings_app.views.booking import BookingViewSet

from listings_app.views.listing import SearchListingListView
from listings_app.views.review import ListingReviewView
from listings_app.views.search_query import SearchQueryListView
from django.urls import path

router = DefaultRouter()
router.register('listings', SearchListingListView, basename='listings')
urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    # path('search-listings/', SearchListingListView.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='search-listings'),



    path('listings/<int:listing_pk>/reviews/', ListingReviewView.as_view(), name='listing-review'),
    path('listings/<int:listing_pk>/bookings/',
         BookingViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='booking-list-create'),
    path('listings/<int:listing_pk>/bookings/<int:pk>/',
         BookingViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='booking-detail'),


    path('search-queries/', SearchQueryListView.as_view(), name='search-query-list'),
]
