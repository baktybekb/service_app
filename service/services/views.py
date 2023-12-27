from django.db.models import Prefetch, F, Sum
from rest_framework.viewsets import ReadOnlyModelViewSet

from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name', 'user__email'))
    ).annotate(price=F('service__full_price') - F('service__full_price') * F('plan__discount_percent') / 100)
    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super(SubscriptionView, self).list(request, *args, **kwargs)
        temp_data = {'result': response.data}
        temp_data['total_amount'] = queryset.aggregate(total=Sum('price'))['total']
        response.data = temp_data
        return response
