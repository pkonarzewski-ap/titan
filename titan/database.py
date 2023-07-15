from typing import Dict

from .schema import Schema
from .props import Props, IntProp, StringProp, TagsProp, FlagProp

from .resource2 import Resource, Namespace, ResourceDB


class Database(Resource):
    """
    CREATE [ OR REPLACE ] [ TRANSIENT ] DATABASE [ IF NOT EXISTS ] <name>
        [ CLONE <source_db>
                [ { AT | BEFORE } ( { TIMESTAMP => <timestamp> | OFFSET => <time_difference> | STATEMENT => <id> } ) ] ]
        [ DATA_RETENTION_TIME_IN_DAYS = <integer> ]
        [ MAX_DATA_EXTENSION_TIME_IN_DAYS = <integer> ]
        [ DEFAULT_DDL_COLLATION = '<collation_specification>' ]
        [ [ WITH ] TAG ( <tag_name> = '<tag_value>' [ , <tag_name> = '<tag_value>' , ... ] ) ]
        [ COMMENT = '<string_literal>' ]
    """

    resource_type = "DATABASE"
    namespace = Namespace.ACCOUNT
    props = Props(
        transient=FlagProp("transient"),
        data_retention_time_in_days=IntProp("data_retention_time_in_days"),
        max_data_extension_time_in_days=IntProp("max_data_extension_time_in_days"),
        default_ddl_collation=StringProp("default_ddl_collation"),
        tags=TagsProp(),
        comment=StringProp("comment"),
    )

    name: str
    transient: bool = False
    owner: str = None
    data_retention_time_in_days: int = None
    max_data_extension_time_in_days: int = None
    default_ddl_collation: str = None
    tags: Dict[str, str] = {}
    comment: str = None

    _schemas: ResourceDB

    def model_post_init(self, ctx):
        super().model_post_init(ctx)
        self._schemas = ResourceDB(Schema)
        self.add(
            Schema(name="PUBLIC", implicit=True),
            Schema(name="INFORMATION_SCHEMA", implicit=True),
        )

    @property
    def schemas(self):
        return self._schemas

    def add(self, *other_resources: Resource):
        for other_resource in other_resources:
            if other_resource.namespace and other_resource.namespace != Namespace.DATABASE:
                raise TypeError(f"Cannot add {other_resource} to {self}")
            # other_resource.database = self
            if isinstance(other_resource, Schema):
                self.schemas[other_resource.name] = other_resource
            # elif isinstance(other_resource, DatabaseRole):
            #     self.database_roles[other_resource.name] = other_resource
            else:
                raise TypeError(f"Cannot add {other_resource} to {self}")