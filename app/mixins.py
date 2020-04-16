#カレンダー関連ビューを作るための部品
import calendar
from collections import deque 
import datetime

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
