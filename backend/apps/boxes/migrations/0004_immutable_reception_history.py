"""History is immutable even through bulk SQL; no legacy receipts are invented."""

from django.db import migrations


def install(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("""
        CREATE FUNCTION boxes_reject_history_mutation() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'Historical records cannot be changed or deleted.'
                USING ERRCODE = '23514';
        END;
        $$;
        CREATE TRIGGER boxes_receipt_immutable
            BEFORE UPDATE OR DELETE ON boxes_receipt
            FOR EACH ROW EXECUTE FUNCTION boxes_reject_history_mutation();
        CREATE TRIGGER boxes_event_immutable
            BEFORE UPDATE OR DELETE ON boxes_boxevent
            FOR EACH ROW EXECUTE FUNCTION boxes_reject_history_mutation();
    """)


def uninstall(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("""
        DROP TRIGGER boxes_receipt_immutable ON boxes_receipt;
        DROP TRIGGER boxes_event_immutable ON boxes_boxevent;
        DROP FUNCTION boxes_reject_history_mutation();
    """)


class Migration(migrations.Migration):
    dependencies = [("boxes", "0003_boxevent_receipt")]
    operations = [migrations.RunPython(install, uninstall)]
