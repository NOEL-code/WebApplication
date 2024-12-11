from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from app.models import db, User, blocked_users

blocks_bp = Blueprint('blocks_bp', __name__, url_prefix='/blocks')

@blocks_bp.route('/block/<int:blocked_id>', methods=['POST'])
@login_required
def block_user(blocked_id):
    if current_user.id == blocked_id:
        flash("You cannot block yourself.", "danger")
        return redirect(url_for('profiles.browse_profiles'))

    blocked_user = User.query.get(blocked_id)
    if not blocked_user:
        flash("User not found.", "danger")
        return redirect(url_for('profiles.browse_profiles'))

    existing_block = db.session.execute(
        blocked_users.select().where(
            blocked_users.c.blocker_id == current_user.id,
            blocked_users.c.blocked_id == blocked_id
        )
    ).fetchone()

    if existing_block:
        flash("You have already blocked this user.", "warning")
    else:
        db.session.execute(
            blocked_users.insert().values(blocker_id=current_user.id, blocked_id=blocked_id)
        )
        db.session.commit()
        flash(f"You blocked {blocked_user.profile.first_name}.", "success")

    return redirect(url_for('profiles.browse_profiles'))

@blocks_bp.route('/unblock/<int:blocked_id>', methods=['POST'])
@login_required
def unblock_user(blocked_id):
    existing_block = db.session.execute(
        blocked_users.select().where(
            blocked_users.c.blocker_id == current_user.id,
            blocked_users.c.blocked_id == blocked_id
        )
    ).fetchone()

    if not existing_block:
        flash("You have not blocked this user.", "warning")
        return redirect(url_for('blocks_bp.blocked_users_list'))

    db.session.execute(
        blocked_users.delete().where(
            blocked_users.c.blocker_id == current_user.id,
            blocked_users.c.blocked_id == blocked_id
        )
    )
    db.session.commit()

    flash("Block removed successfully.", "success")
    return redirect(url_for('blocks_bp.blocked_users_list'))

@blocks_bp.route('/list', methods=['GET'])
@login_required
def blocked_users_list():
    blocked_rows = db.session.execute(
        blocked_users.select().where(blocked_users.c.blocker_id == current_user.id)
    ).fetchall()

    blocked_list = []
    for row in blocked_rows:
        user = User.query.get(row.blocked_id)
        if user:
            if user.profile.photo and user.profile.photo.file_extension:
                image_url = url_for(
                    'static', filename=f"photos/photo-{user.profile.user_id}.{user.profile.photo.file_extension}"
                )
            else:
                image_url = url_for('static', filename="images/default_profile.png")
            blocked_list.append({
                "id": user.id,
                "name": user.profile.first_name,
                "image_url": image_url,
            })

    return render_template(
        'blocks.html',
        page_title="Blocked Users",
        app_name="Dine & Date",
        blocked_users=blocked_list,
    )