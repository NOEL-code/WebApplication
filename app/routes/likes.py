from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, liked_users_table
from sqlalchemy import select, and_

bp = Blueprint('likes', __name__, url_prefix='/likes')

@bp.route('/add/<int:liked_id>', methods=['POST'])
@login_required
def add_like(liked_id):
    # Prevent liking oneself
    if current_user.id == liked_id:
        flash("You cannot like yourself.", "danger")
        return redirect(url_for('profiles.browse_profiles'))

    # Check if the user to be liked exists
    liked_user = User.query.get(liked_id)
    if not liked_user:
        flash("User not found.", "danger")
        return redirect(url_for('profiles.browse_profiles'))

    # Check if the like already exists
    existing_like = db.session.execute(
        select(liked_users_table).where(
            and_(
                liked_users_table.c.liker_id == current_user.id,
                liked_users_table.c.liked_id == liked_id
            )
        )
    ).fetchone()

    if existing_like:
        flash("You have already liked this user.", "warning")
        return redirect(url_for('profiles.browse_profiles'))

    # Add the like
    db.session.execute(
        liked_users_table.insert().values(liker_id=current_user.id, liked_id=liked_id)
    )
    db.session.commit()

    flash(f"You liked {liked_user.profile.first_name}'s profile.", "success")
    return redirect(url_for('profiles.browse_profiles'))


@bp.route('/remove/<int:liked_id>', methods=['POST'])
@login_required
def remove_like(liked_id):
    # 좋아요 삭제
    db.session.execute(
        liked_users_table.delete().where(
            and_(
                liked_users_table.c.liker_id == current_user.id,
                liked_users_table.c.liked_id == liked_id
            )
        )
    )
    db.session.commit()

    flash("Like removed successfully.", "success")
    return redirect(url_for('likes.liked_users'))


@bp.route('/list', methods=['GET'])
@login_required
def liked_users():
    # Fetch the list of users liked by the current user
    liked_rows = db.session.execute(
        select(liked_users_table).where(liked_users_table.c.liker_id == current_user.id)
    ).fetchall()

    # Retrieve profiles for liked users
    liked_profiles = [User.query.get(row.liked_id).profile for row in liked_rows]

    return render_template(
        'likes.html',
        liked_profiles=[
            {
                "id": profile.user_id,
                "name": profile.first_name,
                "image_url": f"photos/profile-{profile.user_id}.jpg"
            }
            for profile in liked_profiles
        ]
    )