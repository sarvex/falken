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

class ArgMaxOptions(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsArgMaxOptions(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = ArgMaxOptions()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def ArgMaxOptionsBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(buf, offset, b"\x54\x46\x4C\x33", size_prefixed=size_prefixed)

    # ArgMaxOptions
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # ArgMaxOptions
    def OutputType(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int8Flags, o + self._tab.Pos)
        return 0

def ArgMaxOptionsStart(builder): builder.StartObject(1)
def ArgMaxOptionsAddOutputType(builder, outputType): builder.PrependInt8Slot(0, outputType, 0)
def ArgMaxOptionsEnd(builder): return builder.EndObject()


class ArgMaxOptionsT(object):

    # ArgMaxOptionsT
    def __init__(self):
        self.outputType = 0  # type: int

    @classmethod
    def InitFromBuf(cls, buf, pos):
        argMaxOptions = ArgMaxOptions()
        argMaxOptions.Init(buf, pos)
        return cls.InitFromObj(argMaxOptions)

    @classmethod
    def InitFromObj(cls, argMaxOptions):
        x = ArgMaxOptionsT()
        x._UnPack(argMaxOptions)
        return x

    # ArgMaxOptionsT
    def _UnPack(self, argMaxOptions):
        if argMaxOptions is None:
            return
        self.outputType = argMaxOptions.OutputType()

    # ArgMaxOptionsT
    def Pack(self, builder):
        ArgMaxOptionsStart(builder)
        ArgMaxOptionsAddOutputType(builder, self.outputType)
        return ArgMaxOptionsEnd(builder)
