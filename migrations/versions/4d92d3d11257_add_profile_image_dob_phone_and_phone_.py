"""Add profile_image, dob, phone, and phone_prefix columns to User model

Revision ID: 4d92d3d11257
Revises: 
Create Date: 2024-06-23 15:31:36.420096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d92d3d11257'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payment')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dob', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('phone', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('phone_prefix', sa.String(length=5), nullable=True))
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=200),
               existing_nullable=False)
        batch_op.alter_column('profile_image',
               existing_type=sa.TEXT(),
               type_=sa.String(length=200),
               existing_nullable=True,
               existing_server_default=sa.text("'default-profile.png'"))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('profile_image',
               existing_type=sa.String(length=200),
               type_=sa.TEXT(),
               existing_nullable=True,
               existing_server_default=sa.text("'default-profile.png'"))
        batch_op.alter_column('password',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=100),
               existing_nullable=False)
        batch_op.drop_column('phone_prefix')
        batch_op.drop_column('phone')
        batch_op.drop_column('dob')

    op.create_table('payment',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('stripe_customer_id', sa.VARCHAR(length=255), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('paid', sa.BOOLEAN(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('stripe_customer_id')
    )
    # ### end Alembic commands ###
