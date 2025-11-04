"""correction superadmin

Revision ID: a931f7ed68b8
Revises: 9fafc1af6479
Create Date: 2025-11-04 12:21:39.355224
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a931f7ed68b8'
down_revision: Union[str, Sequence[str], None] = '9fafc1af6479'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Adiciona o valor 'superadmin' ao tipo ENUM 'roles' (caso ainda não exista)
    op.execute("ALTER TYPE public.roles ADD VALUE IF NOT EXISTS 'superadmin';")


def downgrade() -> None:
    """Downgrade schema."""
    # O PostgreSQL não permite remover valores de ENUM diretamente.
    # Caso seja necessário reverter, é preciso recriar o tipo 'roles' manualmente.
    # Aqui apenas deixamos registrado o downgrade lógico.
    op.execute("-- downgrade não suportado para remoção de valores ENUM")