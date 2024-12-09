from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, DateProposal
from datetime import datetime

bp = Blueprint('proposals', __name__, url_prefix='/proposals')

# 데이트 제안 생성
@bp.route('/create/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def create_proposal(recipient_id):
    if request.method == 'POST':
        proposed_date = request.form.get('proposed_date')
        proposal_message = request.form.get('proposal_message', '')

        # 필수 필드 검증
        if not proposed_date:
            flash("Proposed date is required.", "danger")
            return redirect(url_for('proposals.create_proposal', recipient_id=recipient_id))

        recipient = User.query.get(recipient_id)
        if not recipient:
            flash("Recipient not found.", "danger")
            return redirect(url_for('browse.browse_profiles'))

        # 데이트 제안 생성
        new_proposal = DateProposal(
            proposer_id=current_user.id,
            recipient_id=recipient_id,
            proposed_date=datetime.strptime(proposed_date, '%Y-%m-%d').date(),
            proposal_message=proposal_message,
            status='Proposed'
        )
        db.session.add(new_proposal)
        db.session.commit()

        flash("Date proposal sent successfully.", "success")
        return redirect(url_for('browse.browse_profiles'))

    recipient = User.query.get(recipient_id)
    if not recipient:
        flash("Recipient not found.", "danger")
        return redirect(url_for('browse.browse_profiles'))

    return render_template('proposals/proposal_create.html', recipient=recipient)

# 데이트 제안 응답
@bp.route('/respond/<int:proposal_id>', methods=['GET', 'POST'])
@login_required
def respond_proposal(proposal_id):
    proposal = DateProposal.query.get(proposal_id)

    # 제안 유효성 검증
    if not proposal:
        flash("Proposal not found.", "danger")
        return redirect(url_for('proposals.list_proposals'))

    if proposal.recipient_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('proposals.list_proposals'))

    if request.method == 'POST':
        status = request.form.get('status')
        response_message = request.form.get('response_message', '')

        if status not in ['Accepted', 'Rejected', 'Ignored', 'Reschedule Requested']:
            flash("Invalid status.", "danger")
            return redirect(url_for('proposals.respond_proposal', proposal_id=proposal_id))

        # 상태 업데이트
        proposal.status = status
        proposal.response_message = response_message
        proposal.responded_at = datetime.utcnow()
        db.session.commit()

        flash("Response submitted successfully.", "success")
        return redirect(url_for('proposals.list_proposals'))

    return render_template('proposals/proposal_respond.html', proposal=proposal)

# 데이트 제안 리스트
@bp.route('/list', methods=['GET'])
@login_required
def list_proposals():
    sent_proposals = DateProposal.query.filter_by(proposer_id=current_user.id).all()
    received_proposals = DateProposal.query.filter_by(recipient_id=current_user.id).all()

    return render_template(
        'proposals/proposals_list.html',
        sent_proposals=sent_proposals,
        received_proposals=received_proposals
    )