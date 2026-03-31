"""Initial migration with pgvector support

Revision ID: 001_initial
Revises: 
Create Date: 2026-03-30

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('email', sa.String(100), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), server_default='user'),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])
    
    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('config', sa.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()')),
    )
    
    op.create_table(
        'documents',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('format', sa.String(20), nullable=False),
        sa.Column('file_path', sa.String(1000)),
        sa.Column('content', sa.Text),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('metadata', sa.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_documents_status', 'documents', ['status'])
    
    op.create_table(
        'entities',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_id', UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='SET NULL')),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('type', sa.String(100)),
        sa.Column('confidence', sa.Float),
        sa.Column('properties', sa.JSON, server_default='{}'),
        sa.Column('embedding', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_entities_name', 'entities', ['name'])
    op.create_index('ix_entities_type', 'entities', ['type'])
    
    op.create_table(
        'triples',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_id', UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='SET NULL')),
        sa.Column('head_id', UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relation', sa.String(200), nullable=False),
        sa.Column('tail_id', UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('confidence', sa.Float),
        sa.Column('valid', sa.Boolean, server_default='true'),
        sa.Column('validation_result', sa.JSON),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_triples_relation', 'triples', ['relation'])
    
    op.create_table(
        'jobs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('progress', sa.Integer, server_default='0'),
        sa.Column('current_step', sa.String(100)),
        sa.Column('config', sa.JSON, server_default='{}'),
        sa.Column('result', sa.JSON, server_default='{}'),
        sa.Column('error_message', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('started_at', sa.DateTime),
        sa.Column('completed_at', sa.DateTime),
    )
    op.create_index('ix_jobs_status', 'jobs', ['status'])
    
    op.create_table(
        'prompt_templates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('template', sa.Text, nullable=False),
        sa.Column('variables', sa.JSON, server_default='[]'),
        sa.Column('is_default', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()')),
    )
    
    op.create_table(
        'system_configs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('key', sa.String(100), unique=True, nullable=False),
        sa.Column('value', sa.JSON, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_system_configs_key', 'system_configs', ['key'])
    
    op.create_table(
        'customers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('industry', sa.String(50), nullable=False),
        sa.Column('level', sa.String(20)),
        sa.Column('tags', sa.JSON, server_default='[]'),
        sa.Column('sentiment_score', sa.Float),
        sa.Column('properties', sa.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_customers_name', 'customers', ['name'])
    op.create_index('ix_customers_industry', 'customers', ['industry'])
    
    op.create_table(
        'sentiment_articles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('source_type', sa.String(20)),
        sa.Column('url', sa.String(1000)),
        sa.Column('content', sa.Text),
        sa.Column('publish_time', sa.DateTime),
        sa.Column('sentiment_score', sa.JSON),
        sa.Column('metadata', sa.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_sentiment_articles_source', 'sentiment_articles', ['source'])
    op.create_index('ix_sentiment_articles_publish_time', 'sentiment_articles', ['publish_time'])
    
    op.create_table(
        'sentiment_events',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('type', sa.String(50)),
        sa.Column('severity', sa.String(20)),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('start_time', sa.DateTime),
        sa.Column('end_time', sa.DateTime),
        sa.Column('sentiment_impact', sa.JSON),
        sa.Column('metadata', sa.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_sentiment_events_type', 'sentiment_events', ['type'])
    op.create_index('ix_sentiment_events_severity', 'sentiment_events', ['severity'])
    op.create_index('ix_sentiment_events_status', 'sentiment_events', ['status'])
    
    op.create_table(
        'sentiment_scores',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', UUID(as_uuid=True), nullable=False),
        sa.Column('score_overall', sa.Float),
        sa.Column('score_emotion', sa.Float),
        sa.Column('score_influence', sa.Float),
        sa.Column('score_timeliness', sa.Float),
        sa.Column('score_credibility', sa.Float),
        sa.Column('article_id', UUID(as_uuid=True)),
        sa.Column('dimensions', sa.JSON),
        sa.Column('calculated_at', sa.DateTime, server_default=sa.text('NOW()')),
    )
    
    op.create_table(
        'persons',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('position', sa.String(100)),
        sa.Column('company', sa.String(255)),
        sa.Column('metadata', sa.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_persons_name', 'persons', ['name'])


def downgrade() -> None:
    op.drop_table('persons')
    op.drop_table('sentiment_scores')
    op.drop_table('sentiment_events')
    op.drop_table('sentiment_articles')
    op.drop_table('customers')
    op.drop_table('system_configs')
    op.drop_table('prompt_templates')
    op.drop_table('jobs')
    op.drop_table('triples')
    op.drop_table('entities')
    op.drop_table('documents')
    op.drop_table('projects')
    op.drop_table('users')
    op.execute("DROP EXTENSION IF EXISTS vector")
    op.execute("DROP EXTENSION IF EXISTS \"uuid-ossp\"")
