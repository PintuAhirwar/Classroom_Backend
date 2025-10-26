from django.urls import path
from .views import CartListCreateAPIView, CartRemoveAPIView, CartClearAPIView

urlpatterns = [
    path('', CartListCreateAPIView.as_view(), name='cart-list-create'),  # GET all / POST add
    path('remove/<int:course_id>/', CartRemoveAPIView.as_view(), name='cart-remove'),  # DELETE
    path('clear/', CartClearAPIView.as_view(), name='cart-clear'),  # POST
]
