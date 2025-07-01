from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from aiserv.models import HistoryConfig  

class Command(BaseCommand):
    help = 'Deletes history records older than 5 days'

    def handle(self, *args, **kwargs):
        seven_days_ago = now() - timedelta(days=7)
        old_records = HistoryConfig.objects.filter(sent_date__lt=seven_days_ago)
        count = old_records.count()
        old_records.delete()

        self.stdout.write(f'{count} old history records deleted.')
