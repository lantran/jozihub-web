'''
Created on 25 Nov 2013

@author: michael
'''
import datetime

from django.db import models
from django.utils import timezone

from tunobase.corporate.media import constants as media_constants
from tunobase.core import models as core_models

from app.events import managers

class Event(core_models.ContentModel):
    '''
    Company event eg. Trade Show, Festival, Market
    '''
    default_image_category = 'event'

    venue_name = models.CharField(max_length=255)
    venue_address = models.TextField()
    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField(blank=True, null=True)
    
    repeat = models.PositiveSmallIntegerField(
        choices=media_constants.EVENT_REPEAT_CHOICES,
        default=media_constants.EVENT_REPEAT_CHOICE_DOES_NOT_REPEAT,
    )
    repeat_until = models.DateField(blank=True, null=True)
    external_link = models.URLField(max_length=255, blank=True, null=True)
    
    objects = managers.EventManager()
    
    class Meta:
        ordering = ['order', '-start']
        
    @property
    def is_in_past(self):
        return self.end < timezone.now()
    
    @property
    def is_present(self):
        return self.start <= timezone.now() <= self.end
    
    @property
    def is_in_future(self):
        return self.start > timezone.now()
        
    @property
    def duration(self):
        return self.end - self.start
    
    @property
    def in_same_month(self):
        if self.start.year == self.end.year and self.start.month == self.end.month:
            return True
        return False
    
    @property
    def same_day(self):
        if self.start == self.end:
            return True

    @property
    def next(self):
        now = timezone.now()
        # if the first iteration of the event has not yet ended
        if now < self.end:
            return self.start
        # calculate next repeat of event
        elif self.repeat != media_constants.EVENT_REPEAT_CHOICE_DOES_NOT_REPEAT and \
                (self.repeat_until is None or now.date() <= self.repeat_until):
            if now.timetz() < self.end.timetz() or self.duration > \
                    (self.start.replace(hour=23, minute=59, second=59,
                    microsecond=999999) - self.start):
                date = self._next_repeat(now.date())
            else:
                date = self._next_repeat(now.date() + timezone.timedelta(days=1))

            if self.repeat_until is None or date <= self.repeat_until:
                return datetime.datetime.combine(date, self.start.timetz())
        return None
    
    @property
    def last(self):
        if self.repeat == 'does_not_repeat':
            return self.start
        else:
            return datetime.datetime.combine(self.repeat_until, self.start.timetz())
        
    def save(self, *args, **kwargs):
        if not self.end:
            self.end = self.start
        
        super(Event, self).save(*args, **kwargs)