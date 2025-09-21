"""Add enhanced stock categorization fields

Revision ID: enhanced_stock_categorization
Revises: previous_revision
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'enhanced_stock_categorization'
down_revision = None  # Replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add enhanced categorization fields to stocks table"""
    
    # Add new categorization fields
    op.add_column('stocks', sa.Column('subcategory', sa.String(100), nullable=True))
    op.add_column('stocks', sa.Column('brand', sa.String(100), nullable=True))
    
    # Enhanced special care fields
    op.add_column('stocks', sa.Column('special_care_types', sa.Text(), nullable=True))
    
    # Pet food enhancements
    op.add_column('stocks', sa.Column('pet_type', sa.String(50), nullable=True))
    
    # Storage and priority fields
    op.add_column('stocks', sa.Column('storage_type', sa.String(50), nullable=False, server_default='pantry'))
    op.add_column('stocks', sa.Column('priority_level', sa.String(20), nullable=False, server_default='important'))
    
    # Health and diet fields
    op.add_column('stocks', sa.Column('is_organic', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('stocks', sa.Column('is_gluten_free', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('stocks', sa.Column('is_vegan', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('stocks', sa.Column('is_diabetic_friendly', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('stocks', sa.Column('allergen_info', sa.Text(), nullable=True))
    
    # Family assignment fields
    op.add_column('stocks', sa.Column('assignment_type', sa.String(20), nullable=False, server_default='shared'))
    op.add_column('stocks', sa.Column('assignment_notes', sa.Text(), nullable=True))
    
    # Create indexes for better query performance
    op.create_index('idx_stocks_subcategory', 'stocks', ['subcategory'])
    op.create_index('idx_stocks_brand', 'stocks', ['brand'])
    op.create_index('idx_stocks_pet_type', 'stocks', ['pet_type'])
    op.create_index('idx_stocks_storage_type', 'stocks', ['storage_type'])
    op.create_index('idx_stocks_priority_level', 'stocks', ['priority_level'])
    op.create_index('idx_stocks_assignment_type', 'stocks', ['assignment_type'])
    op.create_index('idx_stocks_is_organic', 'stocks', ['is_organic'])
    op.create_index('idx_stocks_is_gluten_free', 'stocks', ['is_gluten_free'])
    op.create_index('idx_stocks_is_vegan', 'stocks', ['is_vegan'])
    op.create_index('idx_stocks_is_diabetic_friendly', 'stocks', ['is_diabetic_friendly'])


def downgrade() -> None:
    """Remove enhanced categorization fields from stocks table"""
    
    # Drop indexes
    op.drop_index('idx_stocks_subcategory', table_name='stocks')
    op.drop_index('idx_stocks_brand', table_name='stocks')
    op.drop_index('idx_stocks_pet_type', table_name='stocks')
    op.drop_index('idx_stocks_storage_type', table_name='stocks')
    op.drop_index('idx_stocks_priority_level', table_name='stocks')
    op.drop_index('idx_stocks_assignment_type', table_name='stocks')
    op.drop_index('idx_stocks_is_organic', table_name='stocks')
    op.drop_index('idx_stocks_is_gluten_free', table_name='stocks')
    op.drop_index('idx_stocks_is_vegan', table_name='stocks')
    op.drop_index('idx_stocks_is_diabetic_friendly', table_name='stocks')
    
    # Drop columns
    op.drop_column('stocks', 'assignment_notes')
    op.drop_column('stocks', 'assignment_type')
    op.drop_column('stocks', 'allergen_info')
    op.drop_column('stocks', 'is_diabetic_friendly')
    op.drop_column('stocks', 'is_vegan')
    op.drop_column('stocks', 'is_gluten_free')
    op.drop_column('stocks', 'is_organic')
    op.drop_column('stocks', 'priority_level')
    op.drop_column('stocks', 'storage_type')
    op.drop_column('stocks', 'pet_type')
    op.drop_column('stocks', 'special_care_types')
    op.drop_column('stocks', 'brand')
    op.drop_column('stocks', 'subcategory')
