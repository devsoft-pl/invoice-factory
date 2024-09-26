from rest_framework import serializers

from summary_recipients.models import SummaryRecipient


class SummaryRecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummaryRecipient
        fields = [
            "id",
            "description",
            "company",
            "day",
            "email",
            "settlement_types",
            "final_call",
            "is_last_day",
        ]
