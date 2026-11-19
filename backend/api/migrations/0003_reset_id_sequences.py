from django.core.management.color import no_style
from django.db import migrations

MODEL_NAMES = ("Client", "Proposal", "ProposalItem")


def reset_id_sequences(apps, schema_editor):
    """
    Re-syncs PostgreSQL id sequences with existing rows.
    Rows inserted with explicit ids do not advance the sequence.
    """
    connection = schema_editor.connection
    if connection.vendor != "postgresql":
        return

    models = [apps.get_model("api", name) for name in MODEL_NAMES]
    statements = connection.ops.sequence_reset_sql(no_style(), models)

    with connection.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_alter_proposal_tax_rate"),
    ]

    operations = [
        migrations.RunPython(reset_id_sequences, migrations.RunPython.noop),
    ]
    