from django import forms
from .models import Schedule

class BS4ScheduleForm(forms.ModelForm):#Modelクラスを元にFieldを自動的に生成してくれるクラス。登録・更新はModelForm,検索で使う入力項目はFormというように使い分け、validationを行う時にユニーク制約のチェックも行う為、複雑なModelになるほどModelFormが便利になります。
    """Bootstrapに対応するためのModelForm"""
    """メタクラスは「「class文の持つ定義する機能」を定義する機能」がある,class文の中に入れ子でMetaという名前のclass文を定義しておくと、そこから情報を読み取って定義しているクラス（ここでいうとBS4Schedule..の方）にデータベースアクセスに関連する追加の情報や機能を差し挟んでくれる"""
    class Meta:
        model=Schedule #メタクラスに定義されている変数の一つ。model:紐付けるモデルクラスを指定。Scheduleはmodels.pyに定義したクラス名
        fields=('summary','description','start_time','end_time') #fields:Modelから入力フォームを生成する対象のフィールドをタプル形式で指定します。
        widgets={
            'summary':forms.TextInput(attrs={
                'class':'form-control',
            }),
            'description':forms.Textarea(attrs={
                'class':'form-control',
            }),
            'start_time':forms.TextInput(attrs={
                'class':'form-control',
            }),
            'end_time':forms.TextInput(attrs={
                'class':'form-control',
            }),
        } #widgets:画面表示に使用するウィジェットを指定します。未指定の場合、デフォルトで設定されているウィジェットが使われます。attrs:個々のウィジェットの属性こ細かく指定するには、フィールドにカスタムの ウィジェットを指定して、ウィジェットのレンダリング時に使われる属性を指定する。それがattr.


    def clean_end_time(self):
        start_time=self.cleaned_data['start_time']
        end_time=self.cleaned_data['end_time']
        if end_time <= start_time:
            raise forms.ValidationError(
                '終了時間は、開始時間よりも後にしてください'
            )
        return end_time

class SimpleScheduleForm(forms.ModelForm):
    class Meta:
        model=Schedule
        fields=('summary','date',)
        widgets={
            'summary':forms.TextInput(attrs={
                'class':'form-control',
            }),
            'date':forms.HiddenInput,
        }
        