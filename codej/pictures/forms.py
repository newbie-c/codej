from starlette_wtf import StarletteForm
from wtforms.fields import FileField, SubmitField


class UploadFile(StarletteForm):
    image = FileField(
        'picture:',
        validators=[])
    submit = SubmitField('Выгрузить')
