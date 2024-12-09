from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, MatchingPreference

bp = Blueprint('preferences', __name__, url_prefix='/preferences')

# 매칭 선호도 설정 및 수정
@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_preferences():
    # 매칭 선호도 조회 또는 기본값 설정
    preference = MatchingPreference.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        # 폼 데이터 가져오기
        preferred_genders = request.form.getlist('preferred_genders')
        min_age = int(request.form.get('min_age', 18))
        max_age = int(request.form.get('max_age', 100))

        # 입력값 검증
        if min_age < 18 or max_age > 100 or min_age > max_age:
            flash("Invalid age range. Please check your inputs.", "danger")
            return redirect(url_for('preferences.edit_preferences'))

        # 매칭 선호도 업데이트 또는 생성
        if not preference:
            preference = MatchingPreference(
                user_id=current_user.id,
                preferred_genders=preferred_genders,
                min_age=min_age,
                max_age=max_age
            )
            db.session.add(preference)
        else:
            preference.preferred_genders = preferred_genders
            preference.min_age = min_age
            preference.max_age = max_age

        db.session.commit()

        flash("Preferences updated successfully.", "success")
        return redirect(url_for('home.home'))

    return render_template('preferences_edit.html', preference=preference)

# 매칭 선호도 보기
@bp.route('/view', methods=['GET'])
@login_required
def view_preferences():
    preference = MatchingPreference.query.filter_by(user_id=current_user.id).first()

    if not preference:
        flash("No matching preferences found. Please set your preferences.", "warning")
        return redirect(url_for('preferences.edit_preferences'))

    return render_template('preferences_view.html', preference=preference)