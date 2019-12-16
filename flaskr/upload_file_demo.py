from flask import Blueprint, request

from flask_uploads import UploadSet, IMAGES

bp = Blueprint('upload_file_demo', __name__, url_prefix='/upload')  # 如果不写url_prefix就是在 / 下

# 创建一个set（通过实例化UploadSet()类实现
# 这里的photos是set的名字，它很重要。因为接下来它就代表你已经保存的文件，对它调用save()方法保存文件，对它调用url()获取文件url，对它调用path()获取文件的绝对地址……
# （你可以把它类比成代表数据库的db）
photos = UploadSet('photos', IMAGES)

html = '''
    <!DOCTYPE html>
    <title>Upload File</title>
    <h1>图片上传</h1>
    <form method=post enctype=multipart/form-data>
         <input type=file name=photo>
         <input type=submit value=上传>
    </form>
    '''


@bp.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    if request.method == 'POST' and 'photo' in request.files:
        # 使用set的save()方法直接保存从request对象获取的文件
        filename = photos.save(request.files['photo'], name=request.files['photo'].filename)
        # 不必再创建新的视图函数来获取文件，Flask-Uploads自带了一个视图函数，当你对一个set（比如我们上面创建的photos）使用url()方法（传入文件名作为参数）, 它会返回一个文件的url
        file_url = photos.url(filename)

        return html + '<br><img src=' + file_url + '>'
    return html
