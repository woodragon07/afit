# routes/bookmark_routes.py 북마크 추가/조회/삭제 API와 북마크 뷰 페이지 라우트를 담당
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from bson.objectid import ObjectId
from extensions import mongo
from database import Bookmark

bp = Blueprint('bookmark', __name__)

@bp.route('/api/bookmarks', methods=['POST'])
def add_bookmark():
    if 'user' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    try:
        data = request.json
        user_id = session['user']['id']
        existing_bookmark = mongo.db.product_bookmark.find_one({
            'user_id': user_id,
            'item_id': data['item_id']
        })
        if existing_bookmark:
            return jsonify({'success': False, 'message': '이미 북마크된 상품입니다.'})
        bookmark = Bookmark(
            user_id=user_id,
            item_id=data['item_id'],
            title=data['title'],
            price=data['price'],
            mall_name=data['mall_name'],
            product_url=data['product_url'],
            image_url=data['image_url']
        )
        result = mongo.db.product_bookmark.insert_one(bookmark.to_dict())
        return jsonify({
            'success': True,
            'message': '북마크가 추가되었습니다.',
            'bookmark_id': str(result.inserted_id)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/bookmarks', methods=['GET'])
def get_bookmarks():
    if 'user' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    try:
        user_id = session['user']['id']
        bookmarks = list(mongo.db.product_bookmark.find({'user_id': user_id}))
        for bookmark in bookmarks:
            bookmark['_id'] = str(bookmark['_id'])
        return jsonify({
            'success': True,
            'bookmarks': bookmarks
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/bookmarks/<item_id>', methods=['DELETE'])
def remove_bookmark(item_id):
    if 'user' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    try:
        user_id = session['user']['id']
        result = mongo.db.product_bookmark.delete_one({
            'user_id': user_id,
            'item_id': item_id
        })
        if result.deleted_count > 0:
            return jsonify({
                'success': True,
                'message': '북마크가 삭제되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'message': '북마크를 찾을 수 없습니다.'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/bookmarks')
def view_bookmarks():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    user = session['user']
    bookmarks = list(mongo.db.product_bookmark.find({'user_id': user['id']}))
    for bookmark in bookmarks:
        bookmark['_id'] = str(bookmark['_id'])
    return render_template('KO/bookmarks.html', user=user, bookmarks=bookmarks)
