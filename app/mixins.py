#カレンダー関連ビューを作るための部品
import calendar
from collections import deque 
import datetime
import itertools
from django import forms

class BaseCalendarMixin:
    """カレンダー関連Mixinの、基底クラス"""
    first_weekday=0 #０は月曜から、１は火曜から、６なら日曜からになる。
    week_names=['月','火','水','木','金','土','日'] #月曜から書くことを想定して

    def setup_calendar(self):
        """内部カレンダーの設定処理

        calender.Calenderクラスの機能を利用するため、インスタンス化します。
        Calenderクラスのmonthdatescalenderメソッドを利用していますが、デフォルトが月曜日からで
        火曜日から表示したい(first_weekday=1),といったケースに対応するためのセットアップ処理です。

        """
        self._calendar=calendar.Calendar(self.first_weekday)

    def get_week_names(self):
        """frist_weekday(最初に表示される曜日)に合わせて、week_namesをシフトする"""
        week_names=deque(self.week_names)
        week_names.rotate(-self.first_weekday)#リスト内の要素を右に一つずつ移動...なんてときは,dequeを使うとなかなか面白いです。
        return week_names

#月間カレンダー用のMixinクラス
class MonthCalendarMixin(BaseCalendarMixin):
    """月間カレンダーの機能を提供するMixin"""

    def get_previous_month(self,date):
        """前月を返す"""
        if date.month == 1:
            return date.replace(year=date.year-1,month=12,day=1)
        else:
            return date.replace(month=date.month-1,day=1)

    def get_next_month(self,date):
        if date.month ==12:
            return date.replace(year=date.year+1,month=1,day=1)
        else:
            return date.replace(month=date.month+1,day=1)
    
    def get_month_days(self,date):
        """その月の全ての日を返す"""
        return self._calendar.monthdatescalendar(date.year,date.month)

    def get_current_month(self):
        """現在の月を返す"""
        month=self.kwargs.get('month')
        year=self.kwargs.get('year')
        if month and year:
            month=datetime.date(year=int(year),month=int(month),day=1)
        else:
            month=datetime.date.today().replace(day=1)
        return month
    
    def get_month_calendar(self):
        """月間カレンダー情報の入った辞書を返す。"""
        self.setup_calendar()
        current_month=self.get_current_month()
        calendar_data={
            'now':datetime.date.today(),#現在の日付で、datetime.date型のオブジェクトを返す。これを使うと、その日が今日なら色を付ける・・・なんてこともできる。
            'month_days':self.get_month_days(current_month),#その月の全ての日を返す。二次元のリストになり、datetime.date型
            'month_current':current_month,#そのカレンダーが表示している月
            'month_previous':self.get_previous_month(current_month),#currentの前の月
            'month_next':self.get_next_month(current_month),#currentの次の月
            'week_names':self.get_week_names(),#曜日のリストを返す。これはBaseCalendarMixinで提供されている。
        }
        return calendar_data
    
class WeekCalendarMixin(BaseCalendarMixin):
    """週間カレンダーの機能を提供するMixin"""
    def get_week_days(self):
        """その週の日を全て返す"""
        month=self.kwargs.get('month')
        year =self.kwargs.get('year')
        day=self.kwargs.get('day')
        if month and year and day:
            date=datetime.date(year=int(year),month=int(month),day=int(day))
        else:
            date=datetime.date.today()
            
        for week in self._calendar.monthdatescalendar(date.year,date.month):
            if date in week: #週ごとに取り出され、中身は全てdatetime型、該当の日が含まれていれば、それが今回表示すべき週になる。
                return week
    
        
            
    def get_week_calendar(self):
        """週間カレンダーの情報の入った辞書を返す"""
        self.setup_calendar()
        days=self.get_week_days()
        first=days[0]
        last=days[-1]
        calendar_data={
            'now':datetime.date.today(),
            'week_days':days, #その週の全ての日を返している。7つのdatetimeオブジェクトが返される。月を跨いでいる日付が出ても、正しく跨いだ月でのdatetime.date型になっている。
            'week_previous':first - datetime.timedelta(days=7),
            'week_next':first + datetime.timedelta(days=7),
            'week_names':self.get_week_names(),
            'week_first':first,
            'week_last':last,
                }
        return calendar_data

class WeekWithScheduleMixin(WeekCalendarMixin):
    """スケジュール付きの、週間カレンダーを提供するMixin"""

    def get_week_schedules(self,start,end,days):
        """それぞれの日とスケジュールを返す"""
        lookup={'{}__range'.format(self.date_field):(start,end)}
        #例えば、Schedule.objects.filter(date_range=(1日、３１日))になる
        queryset=self.model.objects.filter(**lookup)

        #{１日のdatetime:１日のスケジュール全て、2日のdatetime:2日の全て・・・}のような辞書を作る
        day_schedules={day:[] for day in days} #{}で辞書の定義：でキーと値をかく
        for schedule in queryset:
            schedule_date=getattr(schedule,self.date_field) # getattr(object,name[default]:objectの指名された属性の値を返す。nameは文字列。文字列がオブジェクトの属性の一つであった場合、戻り値はその属性の値になる。
            day_schedules[schedule_date].append(schedule)
        return day_schedules

    def get_week_calendar(self):
        calendar_context=super().get_week_calendar() #あるクラス(子クラス)で別のクラス(親クラス)を継承できる。継承すると、親クラスのメソッドを子クラスから呼び出すことができる。その際に使うのがsuper()。
        calendar_context['week_day_schedules']=self.get_week_schedules(
            calendar_context['week_first'],
            calendar_context['week_last'],
            calendar_context['week_days']
        )
        return calendar_context

class MonthWithScheduleMixin(MonthCalendarMixin):
    """スケジュール付きの、月間カレンダーを提供するMixin"""

    def get_month_schedules(self,start,end,days):
        """それぞれの日とスケジュールを返す。"""
        lookup={
            '{}__range'.format(self.date_field):(start,end)
        }

        queryset=self.model.objects.filter(**lookup)

        day_schedules={day:[] for week in days for day in week}
        for schedule in queryset:
            schedule_date=getattr(schedule,self.date_field)
            day_schedules[schedule_date].append(schedule)
        
         #day_schedule辞書を、週毎に分割する.[{１日：１日のスケジュール・・・}、{8日：8日のスケジュール...}...]
         #7個ずつ取り出して分割している。各週のスケジュールを含んだリスト
        size=len(day_schedules)
        return [{key: day_schedules[key] for key in itertools.islice(day_schedules, i, i+7)} for i in range(0, size, 7)]

    def get_month_calendar(self):
        calendar_context=super().get_month_calendar()
        month_days=calendar_context['month_days']
        month_first=month_days[0][0]  #month_daysは週毎に二次元のリストになっている。二次元のリストの場合、[1~7]は０、[8~14]は１というようになる。さらに[1~7]のリストであれば、1は０、２は１、[8~14]であれば８は１というようになる。合わせると、[0][0]で１日、[-1][-1]=31
        month_last=month_days[-1][-1]
        calendar_context['month_day_schedules']=self.get_month_schedules(
            month_first,
            month_last,
            month_days
        )
        return calendar_context
"""スケジュール付きの、月間カレンダーを提供するMixin""""""それぞれの日と紐づくフォームを作成する"""
class MonthWithFormsMixin(MonthCalendarMixin):
    def get_month_forms(self,start,end,days):
        lookup={'{}__range'.format(self.date_field):(start,end)}
        #例えば、Schedule.objects.filter（date＿＿range=(1日、３１日))になる
        queryset=self.model.objects.filter(**lookup)
        days_count=sum(len(week) for week in days)
        FormClass=forms.modelformset_factory(self.model,self.form_class,extra=days_count) #modelformset_factory:Modelを元にformsetを作成できる
        if self.request.method == 'POST':
            formset=self.month_formset=FormClass(self.request.POST,queryset=queryset)
        else:
            formset=self.month_formset=FormClass(queryset=queryset)
        #{1日のdatetime:１日に関連するフォーム、２日のdatetime:2日のフォーム...}のような辞書を作る
        day_forms={day:[] for week in days for day in week}

        #各日に、新規作成用フォームを一つずつ配置、zip関数は、引数で与えた複数のiterable(※)から要素を集め、イテレータを作ります。(※)要素への順次アクセスが可能なオブジェクト。リスト、タプル、文字列など。
        for empty_form,(date,empty_list) in zip(formset.extra_forms,day_forms.items()):
            empty_form.initial={self.date_field: date}
            empty_list.append(empty_form)
        
        #スケジュールがある各日に、そのスケジュールの更新用フォームを配置
        for bound_form in formset.initial_forms:
            instance=bound_form.instance
            date=getattr(instance,self.date_field)
            day_forms[date].append(bound_form)
        
        #day_forms辞書を週毎に分割する。[{1日:1日のフォーム...},{8日:8日のフォーム...},...]
        #七個ずつ取り出して分割している
        return [{key: day_forms[key] for key in itertools.islice(day_forms, i, i+7)} for i in range(0, days_count, 7)]
    
    def get_month_calendar(self):
        calendar_context=super().get_month_calendar()
        month_days=calendar_context['month_days']
        month_first=month_days[0][0]
        month_last=month_days[-1][-1]
        calendar_context['month_day_forms']=self.get_month_forms(
            month_first,
            month_last,
            month_days
        )
        calendar_context['month_formset']=self.month_formset
        return calendar_context


 




