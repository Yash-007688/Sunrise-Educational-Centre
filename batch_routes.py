from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3

batch_bp = Blueprint('batch', __name__)

DATABASE = 'users.db'


def ensure_batch_meta_table():
	conn = sqlite3.connect(DATABASE)
	c = conn.cursor()
	c.execute('''
		CREATE TABLE IF NOT EXISTS batch_meta (
			class_id INTEGER PRIMARY KEY,
			image TEXT,
			start_date TEXT,
			end_date TEXT,
			description TEXT,
			FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
		)
	''')
	conn.commit()
	conn.close()


def get_all_classes_with_meta():
	ensure_batch_meta_table()
	conn = sqlite3.connect(DATABASE)
	c = conn.cursor()
	c.execute('SELECT id, name FROM classes ORDER BY id')
	classes = c.fetchall()
	c.execute('SELECT class_id, image, start_date, end_date, description FROM batch_meta')
	meta_rows = c.fetchall()
	conn.close()
	meta_map = {row[0]: {'image': row[1], 'start_date': row[2], 'end_date': row[3], 'description': row[4]} for row in meta_rows}
	enriched = []
	for cid, name in classes:
		enriched.append({
			'id': cid,
			'name': name,
			'meta': meta_map.get(cid, {'image': '', 'start_date': '', 'end_date': '', 'description': ''})
		})
	return enriched


def get_class_with_meta(class_id: int):
	ensure_batch_meta_table()
	conn = sqlite3.connect(DATABASE)
	c = conn.cursor()
	c.execute('SELECT id, name FROM classes WHERE id=?', (class_id,))
	row = c.fetchone()
	c.execute('SELECT image, start_date, end_date, description FROM batch_meta WHERE class_id=?', (class_id,))
	meta_row = c.fetchone()
	conn.close()
	if not row:
		return None
	meta = {'image': '', 'start_date': '', 'end_date': '', 'description': ''}
	if meta_row:
		meta = {'image': meta_row[0], 'start_date': meta_row[1], 'end_date': meta_row[2], 'description': meta_row[3]}
	return {'id': row[0], 'name': row[1], 'meta': meta}


# Public batch overview
@batch_bp.route('/batch')
def batch_overview_page():
    # Batch system removed → redirect to study resources
    return redirect(url_for('study_resources'))


# Public batch detail page
@batch_bp.route('/batch/<int:class_id>')
def batch_detail_page(class_id: int):
	# Batch system removed → redirect to study resources
	return redirect(url_for('study_resources'))


@batch_bp.route('/admin/batch-management', methods=['GET'])
def batch_management_page():
	# Batch system removed
	return redirect(url_for('admin_panel'))


@batch_bp.route('/admin/batch/create', methods=['POST'])
def create_batch_class():
	# Batch system removed
	return redirect(url_for('admin_panel'))


@batch_bp.route('/admin/batch/update/<int:class_id>', methods=['POST'])
def update_batch_class(class_id: int):
	# Batch system removed
	return redirect(url_for('admin_panel'))


@batch_bp.route('/admin/batch/delete/<int:class_id>', methods=['POST'])
def delete_batch_class(class_id: int):
	# Batch system removed
	return redirect(url_for('admin_panel'))