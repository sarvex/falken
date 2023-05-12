# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# automatically generated by the FlatBuffers compiler, do not modify

# namespace: tflite

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class PadV2Options(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsPadV2Options(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = PadV2Options()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def PadV2OptionsBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(buf, offset, b"\x54\x46\x4C\x33", size_prefixed=size_prefixed)

    # PadV2Options
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

def PadV2OptionsStart(builder): builder.StartObject(0)
def PadV2OptionsEnd(builder): return builder.EndObject()


class PadV2OptionsT(object):

    # PadV2OptionsT
    def __init__(self):
        pass

    @classmethod
    def InitFromBuf(cls, buf, pos):
        padV2Options = PadV2Options()
        padV2Options.Init(buf, pos)
        return cls.InitFromObj(padV2Options)

    @classmethod
    def InitFromObj(cls, padV2Options):
        x = PadV2OptionsT()
        x._UnPack(padV2Options)
        return x

    # PadV2OptionsT
    def _UnPack(self, padV2Options):
        if padV2Options is None:
            return

    # PadV2OptionsT
    def Pack(self, builder):
        PadV2OptionsStart(builder)
        return PadV2OptionsEnd(builder)
