from django.core.management.base import NoArgsCommand
from django.db import transaction

from program.models import Show, TimeSlot, Schedule


class Command(NoArgsCommand):
    help = 'removes default shows without note'

    @transaction.commit_manually
    def handle_noargs(self, **options):

        default_show = Show.objects.get(pk=1)
        try:
            TimeSlot.objects.filter(show=default_show, note__isnull=True).delete()
            for schedule in Schedule.objects.filter(show=default_show):
                if schedule.timeslots.count() == 0:
                    schedule.delete()
        except:
            transaction.rollback()
        else:
            transaction.commit()