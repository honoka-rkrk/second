from django.shortcuts import redirect,render
from django.views import generic
from . import mixins
import datetime
from .models import Schedule
from .forms import BS4ScheduleForm, SimpleScheduleForm

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

class WeekWithScheduleCalendar(mixins.WeekWithScheduleMixin,generic.TemplateView):
    """スケジュール付きの週間カレンダーを表示するビュー"""
    template_name='app/week_with_schedule.html'
    model=Schedule
    date_field='date'

    def get_context_data(self,**kwargs): #複数のキーワード引数を辞書として受け取る **をつければどの文字でもいいが、慣例としてkwargsが使われることが多い
        context=super().get_context_data(**kwargs)
        calendar_context = self.get_week_calendar()
        context.update(calendar_context)
        return context

class MonthWithScheduleCalendar(mixins.MonthWithScheduleMixin,generic.TemplateView):
    """スケジュール付きの月間カレンダーを表示するビュー"""
    template_name='app/month_with_schedule.html'
    model=Schedule
    date_field='date'

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        calendar_context=self.get_month_calendar()
        context.update(calendar_context)
        return context

class MyCalendar(mixins.MonthCalendarMixin,mixins.WeekWithScheduleMixin,generic.CreateView):#CreateViewはオブジェクトの新規作成フォーム画面の描画およびバリデーションエラー表示の機能を持つクラスです。
    """月間カレンダー、週間カレンダースケジュール登録画面のある欲張りビュー
    CreateViewを使うと、最低限やることは

       対象modelを指定する
       入力したいフィールドを指定する
       描画用HTMLを指定する
       更新後の遷移先を指定する
       だけになります。すべて指定するだけでよいです。


    """
    template_name='app/mycalendar.html'
    model=Schedule
    date_field='date'
    form_class=BS4ScheduleForm

    def get_context_data(self,**kwargs): #それぞれのMixinで定義している、カレンダー情報取得用のメソッドを呼び出す。・get_context_data(self, **kwargs)パラメータで受け取った値を編集したり、テンプレートに渡したい時
        context=super().get_context_data(**kwargs)
        week_calendar_context=self.get_week_calendar()
        month_calendar_context=self.get_month_calendar()
        context.update(week_calendar_context) #update():データベースのデータを一括更新
        context.update(month_calendar_context)
        return context
    
    def form_valid(self,form): #URLに年月日が情報としてあるので、それを使ってスケジュールを保存します。・form_valid(self, form)パラメータの値をフォーム送信時に設定する時
        month=self.kwargs.get('month') #self.kwargs.get()で指定しているカッコ内のパラメーターを取得できる。
        year=self.kwargs.get('year')
        day=self.kwargs.get('day')
        if month and year and day:
            date=datetime.date(year=int(year),month=int(month),day=int(day))
        else:
            date=datetime.date.today()
        schedule=form.save(commit=False)
        schedule.date=date
        schedule.save()
        return redirect('app:mycalendar',year=date.year,month=date.month,day=date.day)

class MonthWithFormsCalendar(mixins.MonthWithFormsMixin,generic.View):
    """フォーム付きの月間カレンダーを表示するビュー"""
    template_name='app/month_with_forms.html'
    model=Schedule
    date_field='date'
    form_class=SimpleScheduleForm 

    def get(self,request,**kwargs):
        context=self.get_month_calendar()
        return render(request,self.template_name,context)
    
    def post(self,request,**kwarsgs):
        context=self.get_month_calendar()
        formset=context['month_formset']
        if formset.is_valid():
            formset.save()
            return redirect('app:month_with_forms')
        
        return render(request,self.template_name,context)