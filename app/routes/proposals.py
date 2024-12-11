from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, DateProposal, ProposalStatusEnum
from datetime import datetime
from sqlalchemy import and_, or_

bp = Blueprint('proposals', __name__, url_prefix='/proposals')

@bp.route('/create/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def create_proposal(recipient_id):
    recipient = User.query.get(recipient_id)
    if not recipient:
        flash("Recipient not found.", "danger")
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        proposed_date = request.form.get('reservation_time')
        if not proposed_date:
            flash("Reservation time is required.", "danger")
            return redirect(url_for('proposals.create_proposal', recipient_id=recipient_id))

        new_proposal = DateProposal(
            proposer_id=current_user.id,
            recipient_id=recipient_id,
            proposed_date=datetime.strptime(proposed_date, '%Y-%m-%dT%H:%M'),
            status=ProposalStatusEnum.PROPOSED.name
        )
        db.session.add(new_proposal)
        db.session.commit()

        flash("Date proposal sent successfully.", "success")
        return redirect(url_for('main.home'))

    return render_template('proposals/reservation.html', other_user=recipient)

@bp.route('/respond/<int:proposal_id>', methods=['GET', 'POST'])
@login_required
def respond_to_proposal(proposal_id):  # Renamed to respond_to_proposal
    proposal = DateProposal.query.get(proposal_id)

    if not proposal:
        flash("Proposal not found.", "danger")
        return redirect(url_for('proposals.list_proposals'))

    if proposal.recipient_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('proposals.list_proposals'))

    if request.method == 'POST':
        status = request.form.get('status')

        if status not in [e.name for e in ProposalStatusEnum]:  # Enum 값 검증
            flash("Invalid status.", "danger")
            return redirect(url_for('proposals.respond_to_proposal', proposal_id=proposal_id))

        proposal.status = status
        proposal.responded_at = datetime.utcnow()
        db.session.commit()

        flash("Response submitted successfully.", "success")
        return redirect(url_for('proposals.list_proposals'))

    return render_template('proposals/response.html', proposal=proposal)

@bp.route('/list', methods=['GET'])
@login_required
def list_proposals():
    sent_proposals = []
    for proposal in DateProposal.query.filter_by(proposer_id=current_user.id).all():
        recipient_profile = proposal.recipient.profile
        image_url = (
            f"photos/photo-{recipient_profile.user_id}.{recipient_profile.photo.file_extension}"
            if recipient_profile and recipient_profile.photo
            else None
        )
        sent_proposals.append({
            "id": proposal.id,
            "recipient_name": recipient_profile.first_name,
            "recipient_image_url": image_url,
            "proposed_date": proposal.proposed_date,
            "status": proposal.status.value,
        })

    received_proposals = []
    for proposal in DateProposal.query.filter_by(recipient_id=current_user.id).all():
        proposer_profile = proposal.proposer.profile
        image_url = (
            f"photos/photo-{proposer_profile.user_id}.{proposer_profile.photo.file_extension}"
            if proposer_profile and proposer_profile.photo
            else None
        )
        received_proposals.append({
            "id": proposal.id,
            "proposer_name": proposer_profile.first_name,
            "proposer_image_url": image_url,
            "proposed_date": proposal.proposed_date,
            "status": proposal.status.value,
        })

    return render_template(
        'proposals/list.html',
        sent_proposals=sent_proposals,
        received_proposals=received_proposals
    )