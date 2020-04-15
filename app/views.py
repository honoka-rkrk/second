from django.shortcuts import redirect,render
from django.views import generic
from . import mixins
import datetime
from .models import Schedule

#ビューではMixinを継承し、テンプレートへ渡すcontextとしてget_month_calendar()を含めれば、あとはテンプレートに好きに書くことができる。
class MonthCalendar(mixins.MonthCalendarMixin,generic.TemplateView):
    """月間カレンダーを表示するビュー"""
    template_name='app/month.html'

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        calendar_context=self.get_month_calendar()
        context.update(calendar_context)
        return context

class WeekCalendar(mixins.WeekCalendarMixin,generic.TemplateView):
    """週間カレンダーを表示するビュー"""
    template_name='app/week.html'

    def get_context_data(self,**kwargs): #super()は親クラスの関数を呼び出すことができる
        context=super().get_context_data(**kwargs)
        calendar_context=self.get_week_calendar()
        context.update(calendar_context)
        return context
