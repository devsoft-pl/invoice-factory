from rest_framework import viewsets

from base.mixins import OwnedObjectsMixin
from summary_recipients.models import SummaryRecipient
from summary_recipients.serializers import SummaryRecipientSerializer


class SummaryRecipientViewSet(OwnedObjectsMixin, viewsets.ModelViewSet):
    queryset = SummaryRecipient.objects.all()
    serializer_class = SummaryRecipientSerializer
