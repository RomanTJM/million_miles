from alembic import op
import sqlalchemy as sa

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    op.create_table(
        'cars',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('source', sa.String(), server_default=sa.text("'carsensor'"), nullable=False),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cars_brand'), 'cars', ['brand'], unique=False)
    op.create_index(op.f('ix_cars_external_id'), 'cars', ['external_id'], unique=True)
    op.create_index(op.f('ix_cars_id'), 'cars', ['id'], unique=False)
    op.create_index(op.f('ix_cars_is_active'), 'cars', ['is_active'], unique=False)
    op.create_index(op.f('ix_cars_model'), 'cars', ['model'], unique=False)
    op.create_index(op.f('ix_cars_url'), 'cars', ['url'], unique=True)
    op.create_index(op.f('ix_cars_year'), 'cars', ['year'], unique=False)
    op.create_index('idx_brand_model_year', 'cars', ['brand', 'model', 'year'], unique=False)
    op.create_index('idx_active_updated', 'cars', ['is_active', 'updated_at'], unique=False)

    op.create_table(
        'scraper_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=True),
        sa.Column('items_scraped', sa.Integer(), server_default=sa.text('0'), nullable=True),
        sa.Column('items_created', sa.Integer(), server_default=sa.text('0'), nullable=True),
        sa.Column('items_updated', sa.Integer(), server_default=sa.text('0'), nullable=True),
        sa.Column('execution_time_seconds', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scraper_logs_created_at'), 'scraper_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_scraper_logs_id'), 'scraper_logs', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_scraper_logs_id'), table_name='scraper_logs')
    op.drop_index(op.f('ix_scraper_logs_created_at'), table_name='scraper_logs')
    op.drop_table('scraper_logs')
    op.drop_index('idx_active_updated', table_name='cars')
    op.drop_index('idx_brand_model_year', table_name='cars')
    op.drop_index(op.f('ix_cars_year'), table_name='cars')
    op.drop_index(op.f('ix_cars_url'), table_name='cars')
    op.drop_index(op.f('ix_cars_is_active'), table_name='cars')
    op.drop_index(op.f('ix_cars_model'), table_name='cars')
    op.drop_index(op.f('ix_cars_external_id'), table_name='cars')
    op.drop_index(op.f('ix_cars_id'), table_name='cars')
    op.drop_index(op.f('ix_cars_brand'), table_name='cars')
    op.drop_table('cars')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
