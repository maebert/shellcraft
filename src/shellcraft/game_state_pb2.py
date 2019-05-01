# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: game_state.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='game_state.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\x10game_state.proto\x1a\x1fgoogle/protobuf/timestamp.proto\"V\n\x06\x41\x63tion\x12\x0c\n\x04task\x18\x01 \x01(\t\x12\x0e\n\x06target\x18\x02 \x01(\t\x12.\n\ncompletion\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"`\n\x08\x46raction\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tinfluence\x18\x02 \x01(\x02\x12\x1a\n\x12missions_completed\x18\x03 \x01(\x05\x12\x17\n\x0fmissions_failed\x18\x04 \x01(\x05\"6\n\tResources\x12\x0c\n\x04\x63lay\x18\x01 \x01(\x02\x12\x0b\n\x03ore\x18\x02 \x01(\x02\x12\x0e\n\x06\x65nergy\x18\x03 \x01(\x02\"\'\n\x04Tool\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tcondition\x18\x02 \x01(\x02\"\xc9\x01\n\x07Mission\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06\x64\x65mand\x18\x02 \x01(\x05\x12\x0e\n\x06reward\x18\x03 \x01(\x05\x12\x13\n\x0b\x64\x65mand_type\x18\x04 \x01(\t\x12\x13\n\x0breward_type\x18\x05 \x01(\t\x12\x0b\n\x03\x64ue\x18\x06 \x01(\x05\x12,\n\x08\x64\x65\x61\x64line\x18\x07 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x14\n\x06writer\x18\x08 \x01(\x0b\x32\x04.NPC\x12\x15\n\rreward_factor\x18\t \x01(\x05\"E\n\x05Stats\x12\x1b\n\x13total_game_duration\x18\x01 \x01(\x02\x12\x1f\n\x0btotal_mined\x18\x02 \x01(\x0b\x32\n.Resources\"{\n\x03NPC\x12\r\n\x05\x66irst\x18\x01 \x01(\t\x12\x0e\n\x06middle\x18\x02 \x01(\t\x12\x0c\n\x04last\x18\x03 \x01(\t\x12\r\n\x05title\x18\x04 \x01(\t\x12\x10\n\x08nickname\x18\x05 \x01(\t\x12\x0f\n\x07\x64isplay\x18\x06 \x01(\t\x12\x15\n\rfraction_name\x18\x07 \x01(\t\"\xd6\x03\n\tGameState\x12\r\n\x05\x64\x65\x62ug\x18\x01 \x01(\x08\x12\x17\n\x06\x61\x63tion\x18\x02 \x01(\x0b\x32\x07.Action\x12\x14\n\x05tools\x18\x03 \x03(\x0b\x32\x05.Tool\x12\x1a\n\x08missions\x18\x04 \x03(\x0b\x32\x08.Mission\x12\x1d\n\tresources\x18\x05 \x01(\x0b\x32\n.Resources\x12\x15\n\rtools_enabled\x18\x06 \x03(\t\x12\x19\n\x11resources_enabled\x18\x07 \x03(\t\x12\x18\n\x10\x63ommands_enabled\x18\x08 \x03(\t\x12\x18\n\x10research_enabled\x18\t \x03(\t\x12\x1a\n\x12research_completed\x18\n \x03(\t\x12\x10\n\x08triggers\x18\x0b \x03(\t\x12%\n\x11mining_difficulty\x18\x0c \x01(\x0b\x32\n.Resources\x12/\n\x1bmining_difficulty_increment\x18\r \x01(\x0b\x32\n.Resources\x12\x18\n\x10trade_reputation\x18\x0e \x01(\x02\x12\x15\n\rtutorial_step\x18\x0f \x01(\x05\x12\x15\n\x05stats\x18\x10 \x01(\x0b\x32\x06.Stats\x12\x1c\n\tfractions\x18\x11 \x03(\x0b\x32\t.Fractionb\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_ACTION = _descriptor.Descriptor(
  name='Action',
  full_name='Action',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='task', full_name='Action.task', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='target', full_name='Action.target', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='completion', full_name='Action.completion', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=53,
  serialized_end=139,
)


_FRACTION = _descriptor.Descriptor(
  name='Fraction',
  full_name='Fraction',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='Fraction.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='influence', full_name='Fraction.influence', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='missions_completed', full_name='Fraction.missions_completed', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='missions_failed', full_name='Fraction.missions_failed', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=141,
  serialized_end=237,
)


_RESOURCES = _descriptor.Descriptor(
  name='Resources',
  full_name='Resources',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='clay', full_name='Resources.clay', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ore', full_name='Resources.ore', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='energy', full_name='Resources.energy', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=239,
  serialized_end=293,
)


_TOOL = _descriptor.Descriptor(
  name='Tool',
  full_name='Tool',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='Tool.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='condition', full_name='Tool.condition', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=295,
  serialized_end=334,
)


_MISSION = _descriptor.Descriptor(
  name='Mission',
  full_name='Mission',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='Mission.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='demand', full_name='Mission.demand', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='reward', full_name='Mission.reward', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='demand_type', full_name='Mission.demand_type', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='reward_type', full_name='Mission.reward_type', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='due', full_name='Mission.due', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='deadline', full_name='Mission.deadline', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='writer', full_name='Mission.writer', index=7,
      number=8, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='reward_factor', full_name='Mission.reward_factor', index=8,
      number=9, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=337,
  serialized_end=538,
)


_STATS = _descriptor.Descriptor(
  name='Stats',
  full_name='Stats',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='total_game_duration', full_name='Stats.total_game_duration', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='total_mined', full_name='Stats.total_mined', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=540,
  serialized_end=609,
)


_NPC = _descriptor.Descriptor(
  name='NPC',
  full_name='NPC',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='first', full_name='NPC.first', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='middle', full_name='NPC.middle', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='last', full_name='NPC.last', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='title', full_name='NPC.title', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='nickname', full_name='NPC.nickname', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='display', full_name='NPC.display', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='fraction_name', full_name='NPC.fraction_name', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=611,
  serialized_end=734,
)


_GAMESTATE = _descriptor.Descriptor(
  name='GameState',
  full_name='GameState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='debug', full_name='GameState.debug', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='action', full_name='GameState.action', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tools', full_name='GameState.tools', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='missions', full_name='GameState.missions', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='resources', full_name='GameState.resources', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tools_enabled', full_name='GameState.tools_enabled', index=5,
      number=6, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='resources_enabled', full_name='GameState.resources_enabled', index=6,
      number=7, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='commands_enabled', full_name='GameState.commands_enabled', index=7,
      number=8, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='research_enabled', full_name='GameState.research_enabled', index=8,
      number=9, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='research_completed', full_name='GameState.research_completed', index=9,
      number=10, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='triggers', full_name='GameState.triggers', index=10,
      number=11, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='mining_difficulty', full_name='GameState.mining_difficulty', index=11,
      number=12, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='mining_difficulty_increment', full_name='GameState.mining_difficulty_increment', index=12,
      number=13, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='trade_reputation', full_name='GameState.trade_reputation', index=13,
      number=14, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tutorial_step', full_name='GameState.tutorial_step', index=14,
      number=15, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='stats', full_name='GameState.stats', index=15,
      number=16, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='fractions', full_name='GameState.fractions', index=16,
      number=17, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=737,
  serialized_end=1207,
)

_ACTION.fields_by_name['completion'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_MISSION.fields_by_name['deadline'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_MISSION.fields_by_name['writer'].message_type = _NPC
_STATS.fields_by_name['total_mined'].message_type = _RESOURCES
_GAMESTATE.fields_by_name['action'].message_type = _ACTION
_GAMESTATE.fields_by_name['tools'].message_type = _TOOL
_GAMESTATE.fields_by_name['missions'].message_type = _MISSION
_GAMESTATE.fields_by_name['resources'].message_type = _RESOURCES
_GAMESTATE.fields_by_name['mining_difficulty'].message_type = _RESOURCES
_GAMESTATE.fields_by_name['mining_difficulty_increment'].message_type = _RESOURCES
_GAMESTATE.fields_by_name['stats'].message_type = _STATS
_GAMESTATE.fields_by_name['fractions'].message_type = _FRACTION
DESCRIPTOR.message_types_by_name['Action'] = _ACTION
DESCRIPTOR.message_types_by_name['Fraction'] = _FRACTION
DESCRIPTOR.message_types_by_name['Resources'] = _RESOURCES
DESCRIPTOR.message_types_by_name['Tool'] = _TOOL
DESCRIPTOR.message_types_by_name['Mission'] = _MISSION
DESCRIPTOR.message_types_by_name['Stats'] = _STATS
DESCRIPTOR.message_types_by_name['NPC'] = _NPC
DESCRIPTOR.message_types_by_name['GameState'] = _GAMESTATE

Action = _reflection.GeneratedProtocolMessageType('Action', (_message.Message,), dict(
  DESCRIPTOR = _ACTION,
  __module__ = 'game_state_pb2'
  # @@protoc_insertion_point(class_scope:Action)
  ))
_sym_db.RegisterMessage(Action)

Fraction = _reflection.GeneratedProtocolMessageType('Fraction', (_message.Message,), dict(
  DESCRIPTOR = _FRACTION,
  __module__ = 'game_state_pb2'
  # @@protoc_insertion_point(class_scope:Fraction)
  ))
_sym_db.RegisterMessage(Fraction)

Resources = _reflection.GeneratedProtocolMessageType('Resources', (_message.Message,), dict(
  DESCRIPTOR = _RESOURCES,
  __module__ = 'game_state_pb2'
  # @@protoc_insertion_point(class_scope:Resources)
  ))
_sym_db.RegisterMessage(Resources)

Tool = _reflection.GeneratedProtocolMessageType('Tool', (_message.Message,), dict(
  DESCRIPTOR = _TOOL,
  __module__ = 'game_state_pb2'
  # @@protoc_insertion_point(class_scope:Tool)
  ))
_sym_db.RegisterMessage(Tool)

Mission = _reflection.GeneratedProtocolMessageType('Mission', (_message.Message,), dict(
  DESCRIPTOR = _MISSION,
  __module__ = 'game_state_pb2'
  # @@protoc_insertion_point(class_scope:Mission)
  ))
_sym_db.RegisterMessage(Mission)

Stats = _reflection.GeneratedProtocolMessageType('Stats', (_message.Message,), dict(
  DESCRIPTOR = _STATS,
  __module__ = 'game_state_pb2'
  # @@protoc_insertion_point(class_scope:Stats)
  ))
_sym_db.RegisterMessage(Stats)

NPC = _reflection.GeneratedProtocolMessageType('NPC', (_message.Message,), dict(
  DESCRIPTOR = _NPC,
  __module__ = 'game_state_pb2'
  # @@protoc_insertion_point(class_scope:NPC)
  ))
_sym_db.RegisterMessage(NPC)

GameState = _reflection.GeneratedProtocolMessageType('GameState', (_message.Message,), dict(
  DESCRIPTOR = _GAMESTATE,
  __module__ = 'game_state_pb2'
  # @@protoc_insertion_point(class_scope:GameState)
  ))
_sym_db.RegisterMessage(GameState)


# @@protoc_insertion_point(module_scope)
