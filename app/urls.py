from django.urls import path
from . import views

app_name='app'

urlpatterns=[
    path('',views.MonthCalendar.as_view(),name='month'),
    path('month/<int:year>/<int:month>/',views.MonthCalendar.as_view(),name='month'),
    path('week/',views.WeekCalendar.as_view(),name='week'),
    path('week/<int:year>/<int:month>/<int:day>/',views.WeekCalendar.as_view(),name='week'),
    path('week_with_schedule/',views.WeekWithScheduleCalendar.as_view(),name='week_with_schedule'),
    path(
        'week_with_schedule/<int:year>/<int:month>/<int:day>/',
        views.WeekWithScheduleCalendar.as_view(),
        name='week_with_schedule'
    ),
    path(
        'month_with_schedule/',
        views.MonthWithScheduleCalendar.as_view(),name='month_with_schedule'
    ),
    path(
        'month_with_schedule/<int:year>/<int:month>/',
        views.MonthWithScheduleCalendar.as_view(),name='month_with_schedule'
    ),
    path('mycalendar/',views.MyCalendar.as_view(),name='mycalendar'),
    path(
        'mycalendar/<int:year>/<int:month>/<int:day>/',views.MyCalendar.as_view(),name='mycalendar'
    ),
]

"""●path('month/<int:year>/<int:month>/',これは、URLの設定、
   ●views.MonthCalendar.as_view()、これは、そのURLに使う関数の設定、これを設定しないと、その関数をページで使用できない
   ●name='month'),このURLパターンに名前をつけることが出来る。ここでつけた名前によって実際のurlを取得する事が出来る
"""