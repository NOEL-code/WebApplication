from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # 여기에서 추가로 설정할 것이 있으면 추가
    # ex) app.config['SECRET_KEY'] = 'your_secret_key'

    # 블루프린트 등록
    from .views import main
    app.register_blueprint(main)

    return app
