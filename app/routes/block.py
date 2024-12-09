from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, blocks

bp = Blueprint('blocks', __name__, url_prefix='/blocks')

# 사용자 차단
@bp.route('/block/<int:blocked_id>', methods=['POST'])
@login_required
def block_user(blocked_id):
    # 자신을 차단하려는 경우 방지
    if current_user.id == blocked_id:
        flash("You cannot block yourself.", "danger")
        return redirect(url_for('profiles.browse_profiles'))

    # 차단할 사용자 존재 여부 확인
    blocked_user = User.query.get(blocked_id)
    if not blocked_user:
        flash("User not found.", "danger")
        return redirect(url_for('profiles.browse_profiles'))

    # 이미 차단한 사용자인지 확인
    existing_block = db.session.execute(
        blocks.select().where(blocks.c.blocker_id == current_user.id, blocks.c.blocked_id == blocked_id)
    ).fetchone()

    if existing_block:
        flash("You have already blocked this user.", "warning")
        return redirect(url_for('profiles.browse_profiles'))

    # 차단 추가
    db.session.execute(blocks.insert().values(blocker_id=current_user.id, blocked_id=blocked_id))
    db.session.commit()

    flash(f"You blocked {blocked_user.profile.first_name}.", "success")
    return redirect(url_for('profiles.browse_profiles'))

# 차단 취소
@bp.route('/unblock/<int:blocked_id>', methods=['POST'])
@login_required
def unblock_user(blocked_id):
    # 차단 기록 확인
    existing_block = db.session.execute(
        blocks.select().where(blocks.c.blocker_id == current_user.id, blocks.c.blocked_id == blocked_id)
    ).fetchone()

    if not existing_block:
        flash("You have not blocked this user.", "warning")
        return redirect(url_for('blocks.blocked_users'))

    # 차단 취소
    db.session.execute(
        blocks.delete().where(blocks.c.blocker_id == current_user.id, blocks.c.blocked_id == blocked_id)
    )
    db.session.commit()

    flash("Block removed successfully.", "success")
    return redirect(url_for('blocks.blocked_users'))

# 차단한 사용자 목록 조회
@bp.route('/list', methods=['GET'])
@login_required
def blocked_users():
    # 현재 사용자가 차단한 사용자 목록 조회
    blocked_users = db.session.execute(
        blocks.select().where(blocks.c.blocker_id == current_user.id)
    ).fetchall()

    # 차단한 사용자 프로필 데이터 가져오기
    blocked_list = [User.query.get(row.blocked_id) for row in blocked_users]

    return render_template('blocks/blocked_users.html', blocked_users=blocked_list)