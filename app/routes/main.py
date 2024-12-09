from flask import Blueprint, render_template

# 메인 페이지 블루프린트 생성
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('main.html', title='Welcome to MyApp')
