from flask import Blueprint, request, jsonify
from app.models import db, User, DateProposal
from datetime import datetime

bp = Blueprint('proposals', __name__, url_prefix='/proposals')

# 데이트 제안 생성
@bp.route('/create', methods=['POST'])
def create_proposal():
    data = request.json
    proposer_id = data.get('proposer_id')
    recipient_id = data.get('recipient_id')
    proposed_date = data.get('proposed_date')
    proposal_message = data.get('proposal_message', None)

    # 입력값 확인
    if not proposer_id or not recipient_id or not proposed_date:
        return jsonify({"error": "proposer_id, recipient_id, and proposed_date are required"}), 400

    # 사용자 존재 여부 확인
    proposer = User.query.get(proposer_id)
    recipient = User.query.get(recipient_id)
    if not proposer or not recipient:
        return jsonify({"error": "Proposer or recipient not found"}), 404

    # 차단된 사용자인지 확인
    if any(block.blocked_id == recipient_id for block in proposer.blocks):
        return jsonify({"error": "You cannot propose a date to a blocked user"}), 403

    # 데이트 제안 생성
    proposal = DateProposal(
        proposer_id=proposer_id,
        recipient_id=recipient_id,
        proposed_date=datetime.strptime(proposed_date, '%Y-%m-%d').date(),
        proposal_message=proposal_message,
        status='proposed'
    )

    db.session.add(proposal)
    db.session.commit()
    return jsonify({"message": "Date proposal created successfully", "proposal_id": proposal.id}), 201

# 데이트 제안 조회
@bp.route('/list/<int:user_id>', methods=['GET'])
def list_proposals(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 사용자가 보낸 제안과 받은 제안
    sent_proposals = DateProposal.query.filter_by(proposer_id=user_id).all()
    received_proposals = DateProposal.query.filter_by(recipient_id=user_id).all()

    sent_list = [{
        "proposal_id": p.id,
        "recipient_id": p.recipient_id,
        "proposed_date": p.proposed_date.strftime('%Y-%m-%d'),
        "status": p.status,
        "proposal_message": p.proposal_message,
        "response_message": p.response_message
    } for p in sent_proposals]

    received_list = [{
        "proposal_id": p.id,
        "proposer_id": p.proposer_id,
        "proposed_date": p.proposed_date.strftime('%Y-%m-%d'),
        "status": p.status,
        "proposal_message": p.proposal_message,
        "response_message": p.response_message
    } for p in received_proposals]

    return jsonify({"sent": sent_list, "received": received_list}), 200

# 데이트 제안 응답
@bp.route('/respond/<int:proposal_id>', methods=['PUT'])
def respond_proposal(proposal_id):
    data = request.json
    status = data.get('status')
    response_message = data.get('response_message', None)

    # 상태 값 검증
    if status not in ['accepted', 'rejected', 'ignored', 'reschedule']:
        return jsonify({"error": "Invalid status"}), 400

    # 제안 조회
    proposal = DateProposal.query.get(proposal_id)
    if not proposal:
        return jsonify({"error": "Proposal not found"}), 404

    # 응답 권한 확인
    if proposal.recipient_id != data.get('recipient_id'):
        return jsonify({"error": "You are not authorized to respond to this proposal"}), 403

    # 상태 및 응답 메시지 업데이트
    proposal.status = status
    proposal.response_message = response_message
    proposal.responded_at = datetime.utcnow()

    db.session.commit()
    return jsonify({"message": "Proposal response recorded successfully"}), 200