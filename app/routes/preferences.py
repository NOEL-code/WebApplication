from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, MatchingPreference

bp = Blueprint('preferences', __name__, url_prefix='/preferences')

# 선호도 수정 페이지
@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_preferences():
    preference = MatchingPreference.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        # 폼 데이터 가져오기
        preferred_genders = ",".join(request.form.getlist('preferred_genders'))
        min_age = int(request.form.get('min_age', 18))
        max_age = int(request.form.get('max_age', 100))

        # 유효성 검사
        if min_age < 18 or max_age > 100 or min_age > max_age:
            flash("Invalid age range. Please try again.", "danger")
            return redirect(url_for('preferences.edit_preferences'))

        if not preference:
            preference = MatchingPreference(
                user_id=current_user.id,
                preferred_genders=preferred_genders,
                min_age=min_age,
                max_age=max_age
            )
            db.session.add(preference)
        else:
            preference.preferred_genders = preferred_genders if preferred_genders else ""
            preference.min_age = min_age
            preference.max_age = max_age

        #db.session.commit()
        #flash("Preferences updated successfully!", "success")
                # 데이터베이스에 커밋
        try:
            db.session.commit()
            flash("Preferences updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating preferences: {e}", "danger")
        return redirect(url_for('main.home'))

    return render_template('users/preference.html', preference=preference)

# 선호도 보기
@bp.route('/view', methods=['GET'])
@login_required
def view_preferences():
    preference = MatchingPreference.query.filter_by(user_id=current_user.id).first()

    if not preference:
        flash("No preferences set. Please update your preferences.", "warning")
        return redirect(url_for('preferences.edit_preferences'))

    return render_template('users/preference.html', preference=preference)